"""Tests status/auth in a running local instance; never starts browser work."""
import httpx
BASE="http://127.0.0.1:8918"
with httpx.Client(base_url=BASE,timeout=8) as client:
    assert client.post("/api/stop",headers={"Origin":BASE}).status_code==403
    page=client.get("/")
    assert page.status_code==200 and "browser_live_session" in client.cookies
    assert client.get("/api/status").status_code==200
    status=client.get("/api/status").json()
    assert status["ready"] and status["independent"]
    assert client.get("/api/history").status_code==200
    assert client.post("/api/task",json={"objective":"teste"},headers={"Origin":"http://invalid.example"}).status_code==403
    assert client.get("/api/status",headers={"Host":"invalid.example"}).status_code==403
    assert client.get("/static/app.js").status_code==200
print("SMOKE: 8 assertions OK; authenticated loopback, origin/host guards, UI, history")
