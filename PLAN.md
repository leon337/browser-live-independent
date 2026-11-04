# Browser Live — plano

Missão: BROWSER-LIVE-INDEPENDENT-20261104
Responsável: MESTRE. Autoridade humana: LEANDRO.
Estado: MVP_VALIDADO_TECNICAMENTE (ainda com validação acústica e UI manual pendentes). Autorização: criação e operação autônoma solicitadas nesta conversa.

## Objetivo
Agente independente para conversar por voz em tempo real e executar pedidos no navegador, com interface própria, memória local e serviço persistente no notebook Linux Mint.

## Requisitos e arquitetura
- Gemini 3.8 Live para áudio bidirecional e ferramentas; Gemini 3.8 Flash para Browser Use, conforme catálogo autenticado.
- FastAPI em loopback 8918, WebSocket de áudio e eventos, interface PT-BR.
- Browser Use em ambiente virtual próprio, Brave visível e perfil persistente independente.
- Tarefa assíncrona: conversa continua durante execução. Resultado comunicado quando observado.
- STOP cancela tarefa e impede continuidade da execução antiga; ações já recebidas por sites podem ter efeito.
- SQLite e arquivos privados fora do Git; chave copiada localmente para configuração própria 0600, nunca entregue ao frontend.
- systemd --user e atalho desktop próprios. Nenhuma dependência operacional dos agentes MESTRE/HER/MBC/9Router.

## MVP e evolução
MVP: voz/texto, navegação, progresso, cancelamento, histórico, persistência, documentação e testes reais.
Futuro: conectores opcionais NVIDIA NIM, múltiplos agentes simultâneos; acesso remoto privado via Tailscale Serve na porta HTTPS 8461 já provisionado em 2026-11-04, ainda pendente validação no Android. Não são necessários para a primeira entrega.

## Riscos considerados
Rede/cota do provedor, erro de interpretação, tarefa parcialmente executada, interrupção de conexão Live, concorrência no navegador, exposição de credenciais e consumo de RAM. Perfil próprio evita disputa com o navegador das outras aplicações. Não copiar sessões autenticadas de perfis existentes.

## Critérios de aceite
Ver CHECKLIST.md. Evidência de cada teste deve identificar data e distinguir teste automatizado de validação acústica humana.

## Fontes
- https://github.com/leon337/multiagent-collaboration-framework
- https://aistudio.google.com/docs/live-api/session-management
- https://aistudio.google.com/docs/live-api/tools
- https://docs.browser-use.com/open-source/supported-models

## Extensão: observabilidade do Browser Live — 2026-11-04

Primeiro incremento implementado no próprio chat do Browser Live: canal `/view` autenticado, screenshot JPEG da aba que o agente usa, seletor de abas de observação, atualização periódica, integração HTTPS/WSS Tailscale e comportamento read-only. Não duplicar navegador/perfil.

Próximos incrementos (não entregues): display virtual isolado dos monitores, human takeover com lease exclusivo, reconciliação ao devolver controle, autenticação específica de convidados, adaptadores para agentes externos Playwright MCP.
