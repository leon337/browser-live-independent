# Browser Live

Agente independente para conversa ao vivo e tarefas no navegador. Aplicação nova, com runtime, interface, ambiente virtual, memória, serviço e perfil próprios.

**Estado em 2026-11-04:** MVP operacional no notebook, com teste E2E real e confirmação independente pelo servidor. Validação acústica humana, microfone físico e inspeção visual manual ainda pendentes. Consulte CHECKLIST.md e TEST_REPORT_20261104.md.

## Uso no notebook

Interface: http://127.0.0.1:8918

- **Iniciar conversa ao vivo** ativa o microfone e a conversa Gemini Live.
- Digite um pedido: com voz ativa, o texto entra na conversa; sem voz, inicia tarefa no navegador.
- **Abrir navegador** mostra o Brave dedicado. Entre nas contas que deseja usar nesse perfil.
- **Parar tarefa** interrompe a execução. Confira o site antes de repetir uma operação interrompida.
- **Silenciar** controla a captura de áudio durante a conversa.

As contas e cookies dos outros navegadores não são copiados. A credencial Gemini autorizada foi reaproveitada apenas no notebook e armazenada na configuração independente.

## Arquitetura

Gemini 3.8 Live conduz a conversa e chama ferramentas. Browser Use executa objetivos no Brave visível com Gemini 3.5 Flash-Lite, com fallback configurado para Gemini 3.5 Flash. A seleção evita a lentidão/indisponibilidade observada com Gemini 3.8 Flash neste ambiente. FastAPI coordena áudio, tarefas, eventos e histórico SQLite. O processo não depende de MESTRE Agent, HER, MESTRE Browser Control ou 9Router.

Áudio e contexto necessário da navegação são processados pela API Google configurada. A chave permanece no backend. Dados privados ficam em ~/.config/browser-live-independent e ~/.local/state/browser-live-independent, fora do repositório.

## Limites

A capacidade depende do site, permissões nativas, autenticação e disponibilidade/cota da API. O agente pode errar; resultados devem trazer evidência observada. STOP não desfaz ações já aceitas por sites. A interface local não é um serviço publicado na internet. O início automático é vinculado à sessão do usuário Linux.

## Planejamento e evidências

- PLAN.md: objetivo, requisitos, arquitetura, riscos e escopo.
- TASKS.md: etapas de implementação.
- CHECKLIST.md: critérios de aceite e validações pendentes.
- TEST_REPORT_20261104.md: evidências da primeira validação e limitações.

## Desenvolvimento

Python 3.12 em .venv própria, dependências fixadas em requirements.lock, servidor systemd --user instalado e habilitado. Testes: `.venv/bin/python -m unittest -v runtime_tests`, `.venv/bin/python smoke.py` e `.venv/bin/python acceptance.py` (último acessa a API real e cria uma página de teste local). O serviço usa `systemctl --user status browser-live-independent.service`; a interface é acessível apenas no próprio notebook. Não versione credenciais, bancos, perfis, áudios, screenshots ou logs pessoais.
