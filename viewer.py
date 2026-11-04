"""Fluxo de observação do navegador. Somente leitura, sem CDP público e sem armazenamento de imagens."""
import asyncio
import time
from urllib.parse import urlsplit

from fastapi import WebSocketDisconnect


def display_url(value: str) -> str:
    """Remove credenciais, parâmetros e fragmentos de URLs mostradas na interface."""
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


async def stream_viewer(runtime, ws):
    """Cada espectador escolhe a aba que observa; nenhum espectador altera a aba do agente."""
    selected_target = None
    closed = asyncio.Event()

    async def receive_commands():
        nonlocal selected_target
        try:
            while True:
                message = await ws.receive_json()
                if not isinstance(message, dict):
                    continue
                if message.get("type") == "follow_agent":
                    selected_target = None
                elif message.get("type") == "select_tab":
                    target = message.get("target_id")
                    if isinstance(target, str) and 1 <= len(target) <= 128:
                        selected_target = target
        except (WebSocketDisconnect, RuntimeError, ValueError):
            pass
        finally:
            closed.set()

    receiver = asyncio.create_task(receive_commands())
    previous_status = None
    last_error_at = 0.0
    try:
        while not closed.is_set():
            browser = runtime.browser
            if browser is None:
                if previous_status != "idle":
                    await ws.send_json({
                        "type": "status", "state": "idle",
                        "text": "Aguardando o navegador dedicado ser iniciado."
                    })
                    previous_status = "idle"
                await asyncio.sleep(0.7)
                continue

            try:
                # Browser Use fornece targets e screenshots via CDP da MESMA sessão do agente.
                tabs = await asyncio.wait_for(browser.get_tabs(), timeout=4)
                valid_targets = {tab.target_id for tab in tabs}
                if selected_target and selected_target not in valid_targets:
                    selected_target = None

                if selected_target:
                    from browser_use.actor.page import Page
                    page = Page(browser, selected_target)
                else:
                    page = await asyncio.wait_for(browser.get_current_page(), timeout=4)
                    if page is None and tabs:
                        from browser_use.actor.page import Page
                        page = Page(browser, tabs[0].target_id)

                if page is None:
                    if previous_status != "no_page":
                        await ws.send_json({
                            "type": "status", "state": "no_page",
                            "text": "O navegador está conectado, mas não há página disponível."
                        })
                        previous_status = "no_page"
                else:
                    # 1 quadro/s, JPEG compacto. Imagem apenas na memória, sem arquivo ou log.
                    image = await asyncio.wait_for(
                        page.screenshot(format="jpeg", quality=55), timeout=8
                    )
                    if not isinstance(image, str) or len(image) > 2_500_000:
                        raise ValueError("Screenshot inválido ou acima do limite")
                    info = await asyncio.wait_for(page.get_target_info(), timeout=4)
                    tab_data = [{
                        "id": tab.target_id,
                        "title": (tab.title or "Nova aba")[:100],
                        "url": display_url(tab.url),
                    } for tab in tabs[:30]]
                    await ws.send_json({
                        "type": "frame",
                        "image": image,
                        "mime": "image/jpeg",
                        "target_id": info.get("targetId"),
                        "title": str(info.get("title") or "Nova aba")[:160],
                        "url": display_url(info.get("url", "")),
                        "tabs": tab_data,
                        "following": selected_target is None,
                        "timestamp": time.time(),
                    })
                    previous_status = "frame"
            except asyncio.CancelledError:
                raise
            except Exception:
                # Navegação, fechamento de aba e STOP podem interromper uma captura.
                # Não transmitir detalhes do erro/URL/credenciais ao cliente.
                if time.monotonic() - last_error_at > 4:
                    try:
                        await ws.send_json({
                            "type": "status", "state": "retrying",
                            "text": "A captura está indisponível durante a navegação. Tentando novamente."
                        })
                    except Exception:
                        break
                    last_error_at = time.monotonic()
            await asyncio.sleep(1.0)
    finally:
        receiver.cancel()
        await asyncio.gather(receiver, return_exceptions=True)
