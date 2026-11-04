"""Read-only Browser Use viewport streaming with bounded viewers and shared frames.

A capture lock only coordinates the viewer. It does not serialize Browser Use's own CDP
watchdogs; sustained real-browser load tests are required before production approval.
"""
import asyncio
import logging
import time
from urllib.parse import urlsplit

from fastapi import WebSocketDisconnect

MAX_VIEWERS = 3
FRAME_TTL = 1.2
_VIEWERS = 0
_VIEWER_LOCK = asyncio.Lock()
_CAPTURE_LOCK = asyncio.Lock()
_LAST_FRAME = {}
_BACKOFF_UNTIL = 0.0
_FAILURES = 0
_METRICS = {"frames": 0, "failures": 0, "max_viewers": 0}


def display_url(value: str) -> str:
    try:
        parsed = urlsplit(value)
        if parsed.scheme not in ("http", "https"):
            return "Nova aba" if parsed.scheme in ("about", "chrome", "brave", "") else parsed.scheme + "://"
        if not parsed.hostname:
            return "Nova aba"
        host = parsed.hostname
        if parsed.port:
            host += ":" + str(parsed.port)
        return host + (parsed.path[:180] or "/")
    except (ValueError, TypeError):
        return "Página"


class CaptureBackoff(Exception):
    """Capture temporarily disabled to let Browser Use perform its own CDP work."""


async def capture_shared(browser, page, target_id):
    """Only one CDP capture from the viewer at a time; frames reused per target."""
    global _BACKOFF_UNTIL, _FAILURES
    async with _CAPTURE_LOCK:
        now = time.monotonic()
        if now < _BACKOFF_UNTIL:
            raise CaptureBackoff()
        # A recycled Browser object should never reuse a different browser's cached frame.
        key = (id(browser), target_id)
        cached = _LAST_FRAME.get(key)
        if cached and now - cached["at"] < FRAME_TTL:
            return cached["image"], cached["info"]
        started = time.monotonic()
        try:
            image = await asyncio.wait_for(page.screenshot(format="jpeg", quality=55), timeout=5)
            if not isinstance(image, str) or len(image) > 2_500_000:
                raise ValueError("Invalid/oversized screenshot")
            info = await asyncio.wait_for(page.get_target_info(), timeout=3)
        except asyncio.CancelledError:
            raise
        except Exception as error:
            _FAILURES += 1
            _METRICS["failures"] += 1
            delay = min(20, 2 ** min(_FAILURES, 4))
            _BACKOFF_UNTIL = time.monotonic() + delay
            logging.warning(
                "Viewer CDP capture failed type=%s latency_ms=%d failures=%d backoff_s=%d",
                type(error).__name__, round((time.monotonic()-started)*1000),
                _FAILURES, delay
            )
            raise CaptureBackoff() from None
        _FAILURES = 0
        _BACKOFF_UNTIL = 0.0
        _METRICS["frames"] += 1
        # Bounded cache; never keep more than 6 recent pages in memory.
        if len(_LAST_FRAME) >= 6:
            _LAST_FRAME.clear()
        _LAST_FRAME[key] = {"at": time.monotonic(), "image": image, "info": info}
        return image, info


async def stream_viewer(runtime, ws):
    """Per-client tab selection without changing the tab used by the agent."""
    global _VIEWERS
    async with _VIEWER_LOCK:
        if _VIEWERS >= MAX_VIEWERS:
            await ws.send_json({"type": "status", "state": "full", "text": "Limite de visualizações simultâneas atingido."})
            await ws.close(code=1013)
            return
        _VIEWERS += 1
        _METRICS["max_viewers"] = max(_METRICS["max_viewers"], _VIEWERS)
        logging.info("Viewer connected active=%s", _VIEWERS)

    selected_target = None
    closed = asyncio.Event()

    async def receive_commands():
        nonlocal selected_target
        try:
            while True:
                msg = await ws.receive_json()
                if not isinstance(msg, dict):
                    continue
                if msg.get("type") == "follow_agent":
                    selected_target = None
                elif msg.get("type") == "select_tab":
                    target = msg.get("target_id")
                    if isinstance(target, str) and 1 <= len(target) <= 128:
                        selected_target = target
        except (WebSocketDisconnect, RuntimeError, ValueError):
            pass
        finally:
            closed.set()

    receiver = asyncio.create_task(receive_commands())
    previous = None
    try:
        while not closed.is_set():
            browser = runtime.browser
            if browser is None or runtime.cdp_healthy is False:
                state = "idle" if browser is None else "cdp_unavailable"
                if previous != state:
                    await ws.send_json({
                        "type": "status", "state": state,
                        "text": "Aguardando navegador." if browser is None else "CDP indisponível. Captura pausada até recuperação."
                    })
                    previous = state
                await asyncio.sleep(2 if browser is None else 5)
                continue
            try:
                tabs = await asyncio.wait_for(browser.get_tabs(), timeout=3)
                valid_targets = {tab.target_id for tab in tabs}
                if selected_target not in valid_targets:
                    selected_target = None
                if selected_target:
                    from browser_use.actor.page import Page
                    page = Page(browser, selected_target)
                else:
                    page = await asyncio.wait_for(browser.get_current_page(), timeout=3)
                    if page is None and tabs:
                        from browser_use.actor.page import Page
                        page = Page(browser, tabs[0].target_id)

                if page is None:
                    if previous != "no_page":
                        await ws.send_json({"type": "status", "state": "no_page", "text": "Nenhuma página disponível."})
                        previous = "no_page"
                else:
                    target_id = selected_target or page._target_id
                    image, info = await capture_shared(browser, page, target_id)
                    tab_data = [{
                        "id": tab.target_id,
                        "title": (tab.title or "Nova aba")[:100],
                        "url": display_url(tab.url)
                    } for tab in tabs[:30]]
                    await asyncio.wait_for(ws.send_json({
                        "type": "frame", "image": image, "mime": "image/jpeg",
                        "target_id": info.get("targetId"),
                        "title": str(info.get("title") or "Nova aba")[:160],
                        "url": display_url(info.get("url", "")), "tabs": tab_data,
                        "following": selected_target is None, "timestamp": time.time()
                    }), timeout=3)
                    previous = "frame"
            except asyncio.CancelledError:
                raise
            except CaptureBackoff:
                if previous != "retrying":
                    await ws.send_json({"type": "status", "state": "retrying", "text": "Captura temporariamente pausada."})
                    previous = "retrying"
            except Exception as error:
                # Only log sanitized exception type. Never include page text, screenshot or URL.
                logging.warning("Viewer observation failed type=%s", type(error).__name__)
                if previous != "retrying":
                    try:
                        await ws.send_json({"type": "status", "state": "retrying", "text": "Visualização temporariamente indisponível."})
                    except Exception:
                        break
                    previous = "retrying"
            await asyncio.sleep(1.25)
    finally:
        receiver.cancel()
        await asyncio.gather(receiver, return_exceptions=True)
        async with _VIEWER_LOCK:
            _VIEWERS = max(0, _VIEWERS - 1)
            logging.info("Viewer disconnected active=%s", _VIEWERS)
