"""Verificação real do stream observável; não salva pixels em arquivos."""
import asyncio
import base64
import json
import time

import httpx
from websockets.asyncio.client import connect

BASE = "http://127.0.0.1:8918"


async def main():
    async with httpx.AsyncClient(base_url=BASE, timeout=25) as client:
        page = await client.get("/")
        assert page.status_code == 200
        cookie = "; ".join(f"{key}={value}" for key, value in client.cookies.items())
        assert cookie
        async with connect(
            "ws://127.0.0.1:8918/view",
            origin=BASE,
            additional_headers={"Cookie": cookie},
            max_size=4_000_000,
        ) as ws:
            initial = json.loads(await asyncio.wait_for(ws.recv(), 12))
            print("INITIAL", initial.get("type"), initial.get("state", ""), flush=True)
            result = await client.post("/api/browser", headers={"Origin": BASE})
            print("OPEN_BROWSER", result.status_code, result.json(), flush=True)
            assert result.json().get("ok")
            end = time.monotonic() + 60
            received = []
            while time.monotonic() < end:
                message = json.loads(await asyncio.wait_for(ws.recv(), 20))
                if message.get("type") == "frame":
                    raw = base64.b64decode(message["image"], validate=True)
                    assert raw[:3] == b"\xff\xd8\xff", "frame must contain a valid JPEG"
                    assert message["tabs"] and message["target_id"]
                    received.append((len(raw), message["url"], len(message["tabs"])))
                    print("FRAME", len(raw), "bytes", message["url"], "tabs", len(message["tabs"]), flush=True)
                    if len(received) >= 2:
                        break
                elif message.get("type") == "status":
                    print("STATUS", message.get("state"), message.get("text"), flush=True)
            assert len(received) >= 2, "Two consecutive frames must be received"
            await ws.send(json.dumps({"type": "follow_agent"}))
            print("PASS: two JPEG screenshots from the real Browser Use profile", flush=True)


asyncio.run(main())
