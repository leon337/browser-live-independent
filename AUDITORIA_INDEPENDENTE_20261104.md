# Auditoria independente — Incidente de CDP e streaming do Browser Live

**Missão:** BROWSER-LIVE-INDEPENDENT / AUDIT-20261104
**Data:** 04/11/2026 (America/Recife, UTC−03:00)
**Repositório:** https://github.com/leon337/browser-live-independent
**Escopo:** diagnóstico e handoff para uma IA revisora independente. Este documento não constitui aprovação nem correção.
**Estado do código durante o incidente:** main em a10bd71c48920d097b08dafd643df9d4b7ba711f (visualização do navegador no chat).
**Estado do aplicativo durante a investigação:** serviço systemd ativo e HTTP local 200; automação via Browser Use/CDP degradada.

## 1. Resultado executivo

O serviço HTTP **não estava parado**. O processo FastAPI respondia na porta 8918 e o Tailscale Serve ainda apontava para essa porta. A parte que falhou foi o **canal CDP de automação e captura de estado da janela Brave**, deixando o agente incapaz de interagir e verificar páginas. A última tarefa consultada terminou como **incomplete, 3 steps**, sem conclusão confirmada.

O primeiro timeout operacional evidente nos logs ocorreu às 05:08:48 (ScreenshotWatchdog); às 05:09:17 também havia timeout da captura de screenshot. Às 05:14:09 o método CDP Page.enable excedeu 60 segundos e o passo do agente excedeu 110 segundos. Em seguida o WebSocket CDP fechou; três tentativas de reconexão falharam até 05:14:45. O agente encerrou por falhas consecutivas às 05:15:32.

**Causa técnica imediata comprovada:** perda de responsividade/conectividade CDP e timeouts de captura/observação do Browser Use.
**Causa raiz de origem não comprovada:** possível disputa/concorrência de capturas CDP com o streaming novo, agravada por pressão de CPU/memória/swap e/ou travamento específico do Brave. Precisa de reprodução controlada, sem conclusões apressadas.

## 2. Evidências observadas (somente leitura)

| Horário BRT | Evidência nos logs ou na máquina | Interpretação |
|---|---|---|
| 04:53:58 | Unidade browser-live-independent.service iniciou o processo atualmente em execução. | Processo permaneceu ativo; não há evidência de crash do FastAPI nesse período. |
| 04:55:31 | Primeiro WebSocket /view aceito pelo serviço. | Visualizador conectado antes da degradação; correlação temporal, não prova causalidade. |
| 04:59:38 | [cdp_use.client] Received duplicate response for request. | Indício de anomalia/problema de sincronização CDP; mecanismo exato desconhecido. |
| 05:04:00 e 05:04:10 | Mais dois WebSockets /view aceitos. | Houve múltiplas conexões, sem prova de simultaneidade exata de todos os clientes. |
| 05:07–05:08 | Mais três avisos duplicate response; primeiro DOMWatchdog lento; evento ScreenshotWatchdog excede 15 s às 05:08:48. | Degradação CDP e do pipeline de observação. |
| 05:09:17 | Clean screenshot timed out after 6 seconds; background capture_screenshot gerou TimeoutError. | Captura usada pelo próprio Browser Use já não respondia. |
| 05:10:04 | ScreenshotWatchdog.on_ScreenshotEvent timed out after 15.0s. | Confirma novo timeout interno do Browser Use. |
| 05:14:09 | Page.enable did not respond within 60s; Agent step 1 timed out after 110s; BrowserStateRequestEvent ficou pendente por centenas de segundos. | CDP/estado do browser indisponível para o agente. |
| 05:14:12 | CDP WebSocket message handler exited unexpectedly; ping timeout 1011; WebSocket connection closed. | Canal CDP se perdeu. |
| 05:14:12–05:14:45 | Três tentativas de reconexão falharam por opening handshake timeout. | Recuperação automática falhou. |
| 05:14:47 | Action 'wait' failed: CDP client not initialized. | Ferramentas de navegação não podiam operar. |
| 05:15:31–05:15:34 | Agent: consecutive failures; StorageStateWatchdog: CDP client not initialized. | Tarefa encerrada sem conclusão verificada. |

**Contagens no intervalo 04:54–05:16 (174 linhas do journal; filtro por mensagem):** três entradas de conexão /view, sete de /live, sete de /events, quatro avisos duplicate CDP response, três ocorrências com a expressão TIMEOUT ERROR e três registros de tentativa de reconexão do WebSocket CDP. Contagem de aceites **não equivale a simultaneidade** nem ao número de usuários únicos.

**Recursos e estado (amostragem posterior ao incidente):** unidade browser-live-independent.service tinha MemoryPeak=4.376.367.104 bytes (aprox. 4,08 GiB), MemoryMax=infinity, MemorySwapMax=infinity, TasksCurrent=127. A máquina Linux dispunha de cerca de 7,7 GiB RAM e swap configurada de 2,0 GiB, praticamente totalmente utilizada (5,8 MiB livre na amostra). /proc/pressure/memory indicava full avg300 aproximadamente 32%; kswapd0 consumia CPU. O snapshot foi capturado **depois** dos primeiros timeouts; não prova que a pressão de recursos começou antes do primeiro erro. Nenhuma mensagem OOM foi encontrada no trecho de journal -k consultado; ausência de mensagem não descarta falha interna do processo/renderer.

**Estado HTTP/Tailscale:** systemctl --user mostrava serviço active (running), habilitado, e GET http://127.0.0.1:8918/ retornava HTTP 200. O endereço privado HTTPS Tailscale porta 8461 permaneceu registrado como tailnet only. HTTP 200 mede API/UI, **não** prontidão real do CDP.

**Bibliotecas instaladas:** browser-use 0.13.14, cdp-use 1.4.5, fastapi 0.162.0. Navegador: Brave com perfil isolado em ~/.local/state/browser-live-independent/browser-profile, iniciado em modo headed. Os logs locais completos permanecem no journal do notebook e **não** foram publicados por conter potencialmente conteúdo sensível.

## 3. Pistas no código a revisar

### P0 — Falha funcional confirmada: estado de prontidão enganoso

Em app.py, Runtime.get_browser() devolve self.browser quando o objeto já existe, sem verificar saúde da sessão CDP. Em /api/status, browser_started é apenas a verificação de self.browser is not None. Assim um processo HTTP saudável e objeto Browser existente podem mascarar um CDP quebrado. O aplicativo não possui circuit breaker/rotina comprovada de reconstrução automática do browser em caso de perda irreversível de CDP.

### P1 — Concorrência e pressão de screenshots

Em viewer.py, stream_viewer() roda um laço **por cliente WebSocket**, chama browser.get_tabs(), browser.get_current_page() e page.screenshot(format='jpeg', quality=55), espera cerca de um segundo e repete. Não há produtor global único de frames, lock de captura por sessão, contagem máxima de espectadores, fila com descarte dos frames antigos, orçamento de CPU, nem pausa automática diante de timeout CDP. O Browser Use também utiliza ScreenshotWatchdog/DOMWatchdog no mesmo browser. Uma causa plausível é contenção de comandos CDP e carga de renderização; o relatório não prova que as requisições do viewer causaram o travamento.

### P1 — Pressão de hardware

A instância dedicada do Brave e outros navegadores já rodavam no notebook, e a swap estava exaurida na amostra. Não há MemoryMax/MemorySwapMax ou política de queda adaptativa de FPS no serviço. Coletar PSI/memória por processo em testes para distinguir saturação de recursos de bug/latência de CDP.

### P2 — Observabilidade insuficiente do streamer

Em viewer.py, exceções de captura são tratadas genericamente e não geram registro de contagem/tipo/duração no journal (para não expor dados de páginas), impedindo distinguir falha de frame do visualizador de falha interna do Browser Use. Instrumentação segura deveria registrar tipos de erro, tempos, ocupação da fila, número de viewers e métricas de CDP — sem URL, cookies, imagem, DOM ou token.

### P2 — Lacunas do critério de aceite

viewer_acceptance.py passou com duas capturas de uma aba vazia e o teste integrado passou com 12 quadros em uma página sintética; isso não cobre sessão longa, múltiplos viewers, interação real da voz via celular e sites pesados. A revisão independente deve procurar também riscos de cancelamento, reconexão e segurança, sem assumir que os testes anteriores garantiram robustez.

## 4. Experimentos sugeridos à revisão independente

1. Reproduzir sob supervisão em **ambiente descartável ou com perfil de teste**, sem usar contas pessoais nem repetir ações externas sensíveis.
2. Estabelecer linha de base sem nenhum cliente /view: cinco execuções de tarefa sintética, latência CDP, uso de CPU, memória, swap e PSI; comparar com estado original.
3. Repetir com um cliente /view a 1 FPS e depois dois ou mais clientes; observar timeouts, crescimento de memória e mensagens CDP duplicadas.
4. Testar produtor único/broadcast de frames com taxa adaptativa ou isolamento do canal de captura; comparar com a linha de base. Não declarar sucesso sem efeito mensurável.
5. Verificar diferenças com Chromium/Chrome dedicado vs. Brave no mesmo cenário e com versões fixadas, sem misturar perfis.
6. Simular queda de CDP e verificar saúde de get_browser(), /api/status e recuperação após failure; preservar tarefa como resultado incerto.
7. Checar se tarefas do viewer são canceladas ao desconectar, se frame backlog é descartado, se há limite de viewers e se eventos de áudio/stop continuam responsivos.
8. Cobrir testes automatizados de 30–60 min com monitoramento de recursos e relatório de performance, antes de dizer que está pronto para produção.

Esses são **planos**, não testes executados pela investigação atual.

## 5. Limites e segurança da auditoria

- Não houve restart, kill, alteração de perfil, remoção de dados, mudança de modelo ou implementação de correção durante esta investigação. Preservar o incidente para avaliação independente.
- Não publicar journal bruto, screenshots de sessão, perfis, cookies, chaves de API, arquivos de estado, dados de clientes ou tokens de autenticação.
- A auditoria de código pode ocorrer com o repositório privado; o agente revisor precisa de **acesso autorizado** ao GitHub. O link isolado não libera acesso.
- Execução de testes de carga, mudança de serviço, push de código, merge e publicação são tarefas distintas e requerem autorização compatível.
- Distinguir sempre: **CONFIRMADO** = diretamente visto no código/log; **HIPÓTESE** = mecanismo plausível; **PENDENTE** = requer experimento.

## 6. Arquivos para inspeção

- app.py — Runtime, Browser Use, get_browser, /api/status e WebSockets.
- viewer.py — screenshot CDP e laço de frames por cliente.
- static/viewer.js, static/app.js — conexões, reconexão e consumo de frames.
- static/viewer.css, static/index.html — UI.
- requirements.lock — versões fixadas.
- browser-live-independent.service — processo e limites do serviço.
- viewer_acceptance.py e acceptance.py — testes de aceite anteriores.
- runtime_tests.py, smoke.py — testes unitários/básicos.
- VIEWER_REPORT_20261104.md, TEST_REPORT_20261104.md e TAILSCALE_ACCESS.md — resultados anteriores e premissas.

**Solicitação ao auditor independente:** emitir decisão APPROVE/REQUEST_CHANGES com evidência de arquivos/linhas, riscos P0/P1/P2, hipóteses rivais, plano de reprodução e ordem de correções. Não confundir disponibilidade HTTP com disponibilidade do browser CDP.
