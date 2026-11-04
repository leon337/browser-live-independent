# Browser Live — relatório de testes (04/11/2026)

Escopo: aplicativo independente local; testes no notebook leo-N43SM, Linux Mint; backend FastAPI em 127.0.0.1:8918; Brave visível, perfil próprio. Missão BROWSER-LIVE-INDEPENDENT-20261104.

## Incidente e correção

- O primeiro teste com Gemini 3.8 Flash falhou com HTTP 503 (alta demanda); repetição apresentou timeout de 75 s e demorou excessivamente.
- Modelo principal do Browser Use alterado para `gemini-3.5-flash-lite`; fallback configurado para `gemini-3.5-flash`, com limites explícitos de tempo. Gemini 3.8 Live foi mantido para a conversa por voz.
- STOP do teste anterior retornou `ok:true`, estado `stopped`, e o estado permaneceu acessível após restart do serviço.
- Reconexão de eventos da UI passou a renovar a sessão local após restart.

## Evidência E2E real (critério de sucesso)

O script `acceptance.py` hospedou um formulário temporário em 127.0.0.1:8919, iniciou Live via WebSocket e solicitou que a ferramenta `execute_browser_task` abrisse a página, preenchesse Nome=Leandro e confirmasse.

O navegador acionou `/confirm?name=Leandro` no servidor de testes. Este servidor registrou `confirmations: ["Leandro"]`; o executor retornou `task.state=completed`; o processo encerrou com código 0. Evidência `verified: true`. Áudio do Gemini Live recebido pelo cliente: **624000 bytes**. A conclusão não depende apenas da autodeclaração do agente.

O recibo detalhado com transcrições permanece exclusivamente no diretório privado `~/.local/state/browser-live-independent/acceptance.json`; não foi publicado.

## Testes adicionais

- `python -m unittest -v runtime_tests`: 2 testes aprovados (serialização/STOP/reinício; recuperação de tarefa interrompida).
- `python smoke.py`: 8 assertions de API, cookies de sessão, proteções Host/Origin, UI e histórico passaram.
- `python -m py_compile` em app.py, acceptance.py, smoke.py e runtime_tests.py: passou.
- `node --check static/app.js`: passou.
- Credencial local com modo 0600, diretório de estado 0700; nenhum padrão de chave encontrada nos arquivos de código/documentação analisados.
- Serviço systemd --user habilitado, ativo e respondendo em loopback.

## Limitações e pendências

- Áudio real do microfone e audição de LEANDRO não foram validados; o recebimento de áudio gerado é evidência automática, não de compreensão da fala do usuário.
- Interface em 1366×768, reconexão visual e reprodução acústica devem ser verificadas na sessão gráfica.
- Sessões autenticadas de sites reais e comportamento pós-restart dessas sessões não foram testados.
- Fallback está configurado, mas a comutação entre modelos sob falha não foi provocada no último teste.
- Sites reais podem conter CAPTCHAs, limites próprios, automação bloqueada e ações irreversíveis; STOP não desfaz efeitos externos.

**Decisão:** MVP validado tecnicamente em laboratório local; não confundir com homologação integral de produção/uso humano.
