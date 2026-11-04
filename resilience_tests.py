"""Offline resilience tests. They do NOT prove recovery of a real Brave session."""
import asyncio
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import app
import viewer


class FakeCDPVersion:
    def __init__(self, exception=None):
        self.calls = 0
        self.exception = exception

    async def getVersion(self):
        self.calls += 1
        if self.exception:
            raise self.exception
        return {"product": "FakeBrowser/1"}


class FakeBrowser:
    def __init__(self, connected=True, exception=None, **kwargs):
        self.is_cdp_connected = connected
        self.version = FakeCDPVersion(exception)
        self.cdp_client = type("CdpClient", (), {
            "send": type("Sender", (), {"Browser": self.version})()
        })()
        self.starts = 0
        self.kills = 0

    async def start(self):
        self.starts += 1

    async def kill(self):
        self.kills += 1


class FakePage:
    def __init__(self, error=None):
        self.error = error
        self.captures = 0
        self._target_id = "a"

    async def screenshot(self, **kwargs):
        self.captures += 1
        if self.error:
            raise self.error
        return "aGVsbG8="

    async def get_target_info(self):
        return {"targetId": "a", "title": "Test", "url": "https://example.test/page?secret=redacted"}


class FakeWS:
    def __init__(self):
        self.messages = []
        self.closed = None

    async def send_json(self, obj):
        self.messages.append(obj)

    async def close(self, code):
        self.closed = code


class ResilienceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="bl-resilience-")
        self.previous_state = app.STATE
        app.STATE = Path(self.temp.name)
        viewer._LAST_FRAME.clear()
        viewer._BACKOFF_UNTIL = 0
        viewer._FAILURES = 0
        viewer._VIEWERS = 0

    async def asyncTearDown(self):
        app.STATE = self.previous_state
        self.temp.cleanup()

    async def test_probe_healthy_cdp_response(self):
        runtime = app.Runtime()
        browser = FakeBrowser()
        runtime.browser = browser
        self.assertTrue(await runtime.check_cdp())
        self.assertTrue(runtime.cdp_healthy)
        self.assertEqual(browser.version.calls, 1)

    async def test_probe_closed_socket_retries_twice(self):
        runtime = app.Runtime()
        browser = FakeBrowser(connected=False)
        runtime.browser = browser
        self.assertFalse(await runtime.check_cdp())
        self.assertFalse(runtime.cdp_healthy)
        self.assertEqual(browser.version.calls, 0)

    async def test_probe_remote_error(self):
        runtime = app.Runtime()
        browser = FakeBrowser(exception=ConnectionError("socket down"))
        runtime.browser = browser
        self.assertFalse(await runtime.check_cdp(browser, attempts=1))
        self.assertFalse(runtime.cdp_healthy)

    async def test_reuse_live_browser_without_killing(self):
        runtime = app.Runtime()
        browser = FakeBrowser()
        runtime.browser = browser
        self.assertIs(await runtime.get_browser(), browser)
        self.assertEqual(browser.kills, 0)

    async def test_rebuild_stale_browser_only_when_idle(self):
        runtime = app.Runtime()
        stale = FakeBrowser(connected=False)
        new = FakeBrowser()
        runtime.browser = stale
        with patch("browser_use.Browser", return_value=new):
            result = await runtime.get_browser()
        self.assertIs(result, new)
        self.assertEqual(stale.kills, 1)
        self.assertEqual(new.starts, 1)
        self.assertTrue(runtime.cdp_healthy)

    async def test_does_not_kill_browser_during_active_task(self):
        runtime = app.Runtime()
        browser = FakeBrowser(connected=False)
        runtime.browser = browser
        runtime.agent = object()
        with self.assertRaisesRegex(RuntimeError, "CDP indisponível"):
            await runtime.get_browser()
        self.assertEqual(browser.kills, 0)

    async def test_shared_frame_for_two_viewers(self):
        browser = object()
        page = FakePage()
        one = await viewer.capture_shared(browser, page, "a")
        two = await viewer.capture_shared(browser, page, "a")
        self.assertEqual(one, two)
        self.assertEqual(page.captures, 1)

    async def test_failed_capture_enters_cooldown(self):
        page = FakePage(error=TimeoutError())
        browser = object()
        with self.assertRaises(viewer.CaptureBackoff):
            await viewer.capture_shared(browser, page, "a")
        self.assertGreater(viewer._BACKOFF_UNTIL, time.monotonic())
        with self.assertRaises(viewer.CaptureBackoff):
            await viewer.capture_shared(browser, page, "a")
        self.assertEqual(page.captures, 1)

    async def test_fourth_viewer_rejected(self):
        viewer._VIEWERS = viewer.MAX_VIEWERS
        ws = FakeWS()
        runtime = app.Runtime()
        await viewer.stream_viewer(runtime, ws)
        self.assertEqual(ws.closed, 1013)
        self.assertEqual(ws.messages[-1]["state"], "full")
        self.assertEqual(viewer._VIEWERS, viewer.MAX_VIEWERS)

    async def test_url_excludes_tokens_and_credentials(self):
        value = viewer.display_url("https://user:password@example.org:443/a?token=hidden#secret")
        self.assertEqual(value, "example.org:443/a")
        self.assertNotIn("password", value)
        self.assertEqual(viewer.display_url("about:blank"), "Nova aba")


if __name__ == "__main__":
    unittest.main(verbosity=2)
