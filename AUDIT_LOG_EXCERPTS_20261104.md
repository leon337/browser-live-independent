# Trechos técnicos sanitizados — journal do Browser Live (04/11/2026)

Extraídos do journalctl --user -u browser-live-independent.service, 04:50–05:16 BRT. Apenas linhas com eventos técnicos selecionados foram incluídas. Não é uma cópia integral do log; URLs, IDs de target e possíveis segredos são suprimidos. Não confundir timestamp do journal com duração do evento.

| Timestamp BRT | Log filtrado |
|---|---|
| 2026-11-04T04:59:38-03:00 | WARNING  [cdp_use.client] Received duplicate response for request 3700 - ignoring |
| 2026-11-04T05:07:06-03:00 | WARNING  [cdp_use.client] Received duplicate response for request 10470 - ignoring |
| 2026-11-04T05:07:17-03:00 | WARNING  [cdp_use.client] Received duplicate response for request 10511 - ignoring |
| 2026-11-04T05:08:10-03:00 | WARNING  [cdp_use.client] Received duplicate response for request 13958 - ignoring |
| 2026-11-04T05:08:39-03:00 | WARNING  [bubus] ⚠️ EventBus_8562eff6🟢(⏳ 0  /  ▶️ 2  /  ✅ 48 ➡️ 31 👂) handler browser_use.browser.watchdog_base.DOMWatchdog.on_BrowserStateRequestEvent() has been running for >15s on event. Possible slow processing or deadlock. |
| 2026-11-04T05:08:48-03:00 | WARNING  [bubus] ⚠️ EventBus_8562eff6🟢(⏳ 0  /  ▶️ 2  /  ✅ 48 ➡️ 31 👂) handler browser_use.browser.watchdog_base.ScreenshotWatchdog.on_ScreenshotEvent() has been running for >15s on event. Possible slow processing or deadlock. |
| 2026-11-04T05:08:48-03:00 | WARNING  [bubus] ⏱️  TIMEOUT ERROR - Handling took more than 15.0s for EventBus_8562eff6.browser_use.browser.watchdog_base.ScreenshotWatchdog.on_ScreenshotEvent(?▶ ScreenshotEvent#7c95 ✅) |
| 2026-11-04T05:09:17-03:00 | WARNING  [BrowserSession] 📸 Clean screenshot timed out after 6 seconds - no handler registered or slow page? |
| 2026-11-04T05:09:17-03:00 | ERROR    [BrowserSession] Exception in background task [capture_screenshot]: TimeoutError: Event handler browser_use.browser.watchdog_base.ScreenshotWatchdog.on_ScreenshotEvent#0400(?▶ ScreenshotEvent#7c95 🏃) timed out after 15.0s |
| 2026-11-04T05:10:04-03:00 | TimeoutError: Event handler browser_use.browser.watchdog_base.ScreenshotWatchdog.on_ScreenshotEvent#0400(?▶ ScreenshotEvent#7c95 🏃) timed out after 15.0s |
| 2026-11-04T05:14:09-03:00 | WARNING  [BrowserSession] [SessionManager] Failed to enable monitoring for target [TARGET_REDACTED]: CDP method 'Page.enable' did not respond within 60s. The browser may be unresponsive (silent WebSocket — container crashed or proxy lost upstream). |
| 2026-11-04T05:14:09-03:00 | ERROR    [Agent] ⏰ Step 1 timed out after 110 seconds |
| 2026-11-04T05:14:09-03:00 | WARNING  [bubus] ⏱️  TIMEOUT ERROR - Handling took more than 30.0s for EventBus_8562eff6.browser_use.browser.watchdog_base.DOMWatchdog.on_BrowserStateRequestEvent(?▶ BrowserStateRequestEvent#f5da ✅) |
| 2026-11-04T05:14:12-03:00 | WARNING  [BrowserSession] [SessionManager] Failed to enable monitoring for target [TARGET_REDACTED]: WebSocket connection closed |
| 2026-11-04T05:14:12-03:00 | WARNING  [BrowserSession] 🔌 CDP WebSocket message handler exited unexpectedly (connection closed) |
| 2026-11-04T05:14:12-03:00 | future: <Future finished exception=ConnectionError('WebSocket connection closed')> |
| 2026-11-04T05:14:12-03:00 | ConnectionError: WebSocket connection closed |
| 2026-11-04T05:14:12-03:00 | WARNING  [BrowserSession] [SessionManager] Failed to enable monitoring for target [TARGET_REDACTED]: sent 1011 (internal error) keepalive ping timeout; no close frame received |
| 2026-11-04T05:14:12-03:00 | future: <Future finished exception=ConnectionError('WebSocket connection closed')> |
| 2026-11-04T05:14:12-03:00 | ConnectionError: WebSocket connection closed |
| 2026-11-04T05:14:12-03:00 | future: <Future finished exception=ConnectionError('WebSocket connection closed')> |
| 2026-11-04T05:14:12-03:00 | ConnectionError: WebSocket connection closed |
| 2026-11-04T05:14:12-03:00 | WARNING  [BrowserSession] 🔄 WebSocket reconnection attempt 1/3... |
| 2026-11-04T05:14:21-03:00 | WARNING  [BrowserSession] 🔄 Reconnection attempt 1 failed: TimeoutError: timed out during opening handshake |
| 2026-11-04T05:14:22-03:00 | WARNING  [BrowserSession] 🔄 WebSocket reconnection attempt 2/3... |
| 2026-11-04T05:14:25-03:00 | WARNING  [bubus] ⚠️ EventBus_8562eff6🟢(⏳ 2  /  ▶️ 1  /  ✅ 47 ➡️ 31 👂) handler browser_use.browser.watchdog_base.DOMWatchdog.on_BrowserStateRequestEvent() has been running for >15s on event. Possible slow processing or deadlock. |
| 2026-11-04T05:14:32-03:00 | WARNING  [BrowserSession] 🔄 Reconnection attempt 2 failed: TimeoutError: timed out during opening handshake |
| 2026-11-04T05:14:35-03:00 | WARNING  [BrowserSession] 🔄 WebSocket reconnection attempt 3/3... |
| 2026-11-04T05:14:40-03:00 | WARNING  [bubus] ⏱️  TIMEOUT ERROR - Handling took more than 30.0s for EventBus_8562eff6.browser_use.browser.watchdog_base.DOMWatchdog.on_BrowserStateRequestEvent(?▶ BrowserStateRequestEvent#5afd ✅) |
| 2026-11-04T05:14:45-03:00 | WARNING  [BrowserSession] 🔄 Reconnection attempt 3 failed: TimeoutError: timed out during opening handshake |
| 2026-11-04T05:14:45-03:00 | ERROR    [BrowserSession] 🔄 All 3 reconnection attempts failed |
| 2026-11-04T05:14:47-03:00 | ERROR    [tools] Action 'wait' failed with error: Error executing action wait: CDP client not initialized - browser may not be connected yet |
| 2026-11-04T05:15:31-03:00 | ERROR    [Agent] ❌ Result failed 3/3 times: Expected at least one handler to return a non-None result, but none did! ?▶ BrowserStateRequestEvent#a342 ✅ -> {'130291774301072.130291520129440': browser_use.browser.watchdog_base.DownloadsWatchdog.on_BrowserStateRequestEvent#9440() ✅, '130291774301072.130291520131520': browser_use.browser.watchdog_base. |
| 2026-11-04T05:15:32-03:00 | ERROR    [Agent] ❌ Stopping due to 2 consecutive failures |
| 2026-11-04T05:15:34-03:00 | ERROR    [BrowserSession] [StorageStateWatchdog] Error in monitoring loop: CDP client not initialized - browser may not be connected yet |
