# Browser Live

Agente independente para conversa ao vivo e tarefas no navegador. Aplicação nova, com runtime, interface, ambiente virtual, memória, serviço e perfil próprios.

**Estado em 2026-11-04:** MVP operacional no notebook, com teste E2E real e confirmação independente pelo servidor. Validação acústica humana, microfone físico e inspeção visual manual ainda pendentes. Consulte CHECKLIST.md e TEST_REPORT_20261104.md.

## Uso no notebook

Interface no notebook: http://127.0.0.1:8918

Interface privada no telefone (Tailscale ligado): **https://mcf-leo-n43sm.tail582305.ts.net:8461/**

O link HTTPS é disponibilizado por `tailscale serve --bg --https=8461 http://127.0.0.1:8918` e **não** por Funnel. Requer telefone pertencente à mesma tailnet, autenticado e com conexão Tailscale ativada. A porta 8461 é privada. Consulte `TAILSCALE_ACCESS.md` para diagnóstico e evidências.

- **Iniciar conversa ao vivo** ativa o microfone e a conversa Gemini Live.
- Digite um pedido: com voz ativa, o texto entra na conversa; sem voz, inicia tarefa no navegador.
- **Abrir navegador** mostra o Brave dedicado. Entre nas contas que deseja usar nesse perfil.
- **Parar tarefa** interrompe a execução. Confira o site antes de repetir uma operação interrompida.
- **Silenciar** controla a captura de áudio durante a conversa.

As contas e cookies dos outros navegadores não são copiados. A credencial Gemini autorizada foi reaproveitada apenas no notebook e armazenada na configuração independente.

## Arquitetura

Gemini 3.8 Live conduz a conversa e chama ferramentas. Browser Use executa objetivos no Brave visível com Gemini 3.5 Flash-Lite, com fallback configurado para Gemini 3.5 Flash. A seleção evita a lentidão/indisponibilidade observada com Gemini 3.8 Flash neste ambiente. FastAPI coordena áudio, tarefas, eventos e histórico SQLite. O processo não depende de MESTRE Agent, HER, MESTRE Browser Control ou 9Router.

Áudio e contexto necessário da navegação são processados pela API Google configurada. A chave permanece no backend. Dados privados ficam em ~/.config/browser-live-independent e ~/.local/state/browser-live-independent, fora do repositório.

## Ver o navegador dentro do chat

Durante a tarefa, o chat abre automaticamente **Ver ao vivo**. É possível também abrir/ocultar pelo botão **◉ Ver ao vivo**. O painel mostra **a página/aba do Brave que o agente está observando**, atualizada por screenshots JPEG via canal WebSocket `/view` (1 quadro/s), com título, endereço sem query strings e seletor de abas. Ao selecionar uma aba, você apenas muda o que assiste; o agente continua operando a aba dele. O botão **Seguir agente** restaura o modo automático.

A visualização funciona também no celular via Tailscale: https://mcf-leo-n43sm.tail582305.ts.net:8461/ . Não transmite pixels da área de trabalho nem grava imagens. O painel de observação é **somente leitura**; assumir o controle, retornar controle, convidados e display virtual ainda não estão implementados.

O módulo `viewer.py` é independente do mecanismo Gemini e utiliza a sessão `Browser Use` existente; há testes em `viewer_acceptance.py` e o relatório `VIEWER_REPORT_20261104.md`.

## Limites

A capacidade depende do site, permissões nativas, autenticação e disponibilidade/cota da API. O agente pode errar; resultados devem trazer evidência observada. STOP não desfaz ações já aceitas por sites. A interface local não é um serviço publicado na internet. O início automático é vinculado à sessão do usuário Linux.

## Planejamento e evidências

- PLAN.md: objetivo, requisitos, arquitetura, riscos e escopo.
- TASKS.md: etapas de implementação.
- CHECKLIST.md: critérios de aceite e validações pendentes.
- TEST_REPORT_20261104.md: evidências da primeira validação e limitações.
- TAILSCALE_ACCESS.md: configuração HTTPS privada para o telefone e testes de acesso.

## Desenvolvimento

Python 3.12 em .venv própria, dependências fixadas em requirements.lock, servidor systemd --user instalado e habilitado. Testes: `.venv/bin/python -m unittest -v runtime_tests`, `.venv/bin/python smoke.py` e `.venv/bin/python acceptance.py` (último acessa a API real e cria uma página de teste local). O serviço usa `systemctl --user status browser-live-independent.service`; a interface é acessível apenas no próprio notebook. Não versione credenciais, bancos, perfis, áudios, screenshots ou logs pessoais.
