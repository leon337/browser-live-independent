# Visualização do navegador dentro do chat — relatório técnico

Data: 2026-11-04 · Aplicativo: Browser Live Independent · Notebook: leo-N43SM.

## Entrega

- Canal `/view` no FastAPI. Reutiliza checagem `authorized_ws` de Host, Origin e cookie de sessão.
- Módulo `viewer.py` captura a página via `browser_use.actor.page.Page.screenshot(format='jpeg', quality=55)`. A observação não redireciona os cliques e não cria processo/navegador ou perfil adicional.
- Até 1 imagem/segundo por conexão (taxa inicial); imagens JPEG em base64 apenas no WebSocket; nenhum screenshot é salvo em arquivo ou adicionado ao SQLite.
- Registro de abas a partir de `BrowserSession.get_tabs()`; o usuário pode fixar a aba observada ou seguir automaticamente a aba ativa do agente sem modificar a seleção do agente.
- `static/viewer.js`, `static/viewer.css` e interface `static/index.html`: painel dentro do chat, seletor de abas, título, endereço sanitizado, status, recuperação de conexão e exibição automática para tarefas novas.
- CSP permite `img-src data:` para o JPEG local. Protocolo WebSocket é `ws` no loopback HTTP e `wss` no HTTPS Tailscale já existente. API /view exige autenticação.

## Evidências executadas

1. Serviço systemd reiniciado; HTTP / retornou 200, `/static/viewer.js` retornou 200, verificação sintática Python e Node passou.
2. `viewer_acceptance.py` iniciou o Brave pelo backend, conectou no WebSocket `/view` com cookie/Origin válidos e recebeu **dois quadros JPEG válidos consecutivos** (assinatura FF D8 FF, tamanhos 6255 e 12634 bytes) da sessão.
3. Teste integrado com servidor HTTP temporário em 127.0.0.1:8919: viewer acompanhou o agente e recebeu quadro JPEG da URL da página de teste, enquanto Browser Use executava a ação. **12 quadros** foram vistos; tarefa terminou `completed`, 2 etapas; servidor de testes registrou confirmação `Leandro`.
4. Testes de API previamente existentes (`smoke.py`, 8 assertions) e de runtime (`runtime_tests.py`, 2 casos) passaram após alteração.
5. O componente foi testado em laboratório local, não diretamente no dispositivo móvel.

## Limitações explícitas

- Exibe somente o **viewport da página** capturado por CDP; não é screencast do desktop e não inclui barra nativa do navegador. Lista de abas e endereço são elementos da UI própria.
- Intervalo aproximado de 1 segundo por frame, não vídeo contínuo com 30 fps.
- **Não implementa** tomada de controle manual, bloqueio exclusivo de entradas, sincronização do agente, ou display virtual isolado. O Brave dedicado continua sendo uma janela física do notebook quando iniciado em modo headed.
- O acesso Web pelo Tailscale autoriza quem já consegue abrir a aplicação na tailnet. Não compartilhar a URL com convidados sem controles específicos de identidade e permissões.
- Screenshots podem conter informação sensível visível na página; não são persistidos no servidor, mas são enviados ao navegador do espectador autorizado.
- Conexão/visualização real e latência no Realme 9i ainda precisam de teste direto.
- Adaptadores para o ChatGPT Playwright MCP e demais agentes não foram ligados a este MVP.

## Regressão sugerida

```bash
.venv/bin/python -m unittest -q runtime_tests
.venv/bin/python smoke.py
.venv/bin/python viewer_acceptance.py
node --check static/app.js
node --check static/viewer.js
```

O teste `viewer_acceptance.py` valida duas capturas da sessão real e não modifica sites externos. Para verificação integrada de navegação, usar a página sintética em 127.0.0.1:8919; não tratar declaração do LLM como prova sem confirmar servidor/página.
