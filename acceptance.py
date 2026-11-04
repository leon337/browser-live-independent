"""Manual real-provider acceptance; synthetic local fixture only, no personal data."""
import asyncio,json,time,threading,base64
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import httpx
from urllib.parse import urlsplit,parse_qs
from websockets.asyncio.client import connect
PAGE=b"""<!doctype html><html><title>Browser Live Acceptance</title><h1>Formulario de teste</h1><label>Nome <input id="name"></label><button onclick="fetch('/confirm?name='+encodeURIComponent(document.getElementById('name').value)).then(r=>r.text()).then(t=>document.getElementById('result').textContent=t)">Confirmar</button><p id="result">Aguardando</p></html>"""
confirmations=[]
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path.startswith("/confirm?"):
   name=parse_qs(urlsplit(self.path).query).get("name",[""])[0][:80]
   confirmations.append(name)
   payload=("Reserva confirmada: "+name).encode()
  else: payload=PAGE
  self.send_response(200);self.send_header("Content-Type","text/html;charset=utf-8");self.end_headers();self.wfile.write(payload)
 def log_message(self,*args):pass
async def main():
 server=ThreadingHTTPServer(("127.0.0.1",8919),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 evidence={"started":time.time(),"audio_bytes":0,"tools":[],"transcript":[]}
 async with httpx.AsyncClient(base_url="http://127.0.0.1:8918",headers={"Origin":"http://127.0.0.1:8918"},timeout=40) as client:
  await client.get("/")
  evidence["status"]=(await client.get("/api/status")).json()
  cookie="; ".join(k+"="+v for k,v in client.cookies.items())
  async with connect("ws://127.0.0.1:8918/live",origin="http://127.0.0.1:8918",additional_headers={"Cookie":cookie},max_size=4000000) as ws:
   for _ in range(30):
    m=json.loads(await asyncio.wait_for(ws.recv(),40));print("setup",m,flush=True)
    if m["type"]=="ready":break
    if m["type"]=="error":raise RuntimeError(m)
   await ws.send(json.dumps({"type":"text","text":"Use execute_browser_task agora para abrir http://127.0.0.1:8919, preencher o campo Nome com Leandro, clicar Confirmar e verificar o texto Reserva confirmada: Leandro. É uma página local de teste autorizada. Depois me diga o resultado."}))
   deadline=time.monotonic()+240
   while time.monotonic()<deadline:
    try:m=json.loads(await asyncio.wait_for(ws.recv(),20))
    except asyncio.TimeoutError:
     state=(await client.get("/api/status")).json()["task"];print("poll",state,flush=True)
     if state and state["state"] in ["error","incomplete"]:break
     continue
    if m["type"]=="audio":evidence["audio_bytes"]+=len(base64.b64decode(m["data"]))
    if m["type"]=="tool":evidence["tools"].append(m);print("tool",m,flush=True)
    if m["type"]=="transcript":evidence["transcript"].append(m["text"]);print(m["text"],flush=True)
    if m["type"] in ["error","reconnecting"]:print("LIVE",m,flush=True)
    if m["type"]=="turn_complete":
     state=(await client.get("/api/status")).json()["task"]
     if state and state["state"]=="completed":evidence["task"]=state;break
  evidence["final_status"]=(await client.get("/api/status")).json()
 evidence["ended"]=time.time()
 evidence["confirmations"]=list(confirmations)
 evidence["verified"]=("Leandro" in confirmations and evidence["final_status"].get("task",{}).get("state")=="completed")
 out=Path.home()/".local/state/browser-live-independent/acceptance.json";out.write_text(json.dumps(evidence,indent=2,ensure_ascii=False))
 print("EVIDENCE",json.dumps(evidence,ensure_ascii=False),flush=True)
 server.shutdown()
asyncio.run(main())
