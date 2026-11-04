# Tarefas — verificação 2026-11-04

1. [x] Inspecionar recursos e aplicações sem expor segredos.
2. [x] Definir aplicação independente e porta própria.
3. [x] Consultar catálogo autenticado de modelos Gemini.
4. [x] Implementar runtime Browser Use e perfil persistente.
5. [x] Implementar voz Live, reconexão e comunicação da conclusão (validado com áudio sintético).
6. [x] Implementar interface PT-BR, texto, microfone e STOP (teste humano/visual pendente).
7. [x] Corrigir concorrência, cancelamento e recuperação após reinício; regressão offline passou.
8. [x] Executar testes de API, navegador, Live e voz sintética com confirmação pelo servidor.
9. [x] Instalar serviço persistente e atalho; serviço systemd ativo/habilitado.
10. [ ] Revisar manualmente UI e áudio físico, finalizar homologação e publicar evidências de uso humano.

Ver TEST_REPORT_20261104.md para as provas e pendências.

11. [x] Provisionar HTTPS privado Tailscale Serve na porta 8461, adaptando o backend e WebSockets seguros.
12. [ ] Verificar abertura e microfone diretamente no Realme 9i com Tailscale ativo.

## Observabilidade no chat — 2026-11-04

13. [x] Screenshot via CDP da mesma sessão usada pelo agente (Browser Use).
14. [x] WebSocket /view com autenticação local e verificação de Origin/Host.
15. [x] Painel no chat, seletor de abas e seguimento automático da aba do agente.
16. [x] Teste real de stream JPEG e acompanhamento de tarefa até página de teste.
17. [ ] Verificação visual e de usabilidade diretamente no Realme 9i.
18. [ ] Human takeover com exclusividade, pausa e reconciliação.
19. [ ] Browser headed em display virtual, separado dos monitores físicos.
20. [ ] Autorização diferenciada para convidados e integração de outros agentes via gateway.

## Recuperação de CDP — branch de experimento (04/11/2026)

21. [x] Conferir main remoto e preservar branch de backup.
22. [x] Procurar patch original e notebook Colab; patch original não estava acessível.
23. [x] Implementar versão independente de saúde CDP e proteções do viewer no branch.
24. [x] Rodar 12/12 testes unitários com navegador falso.
25. [x] Registrar limites de memória no arquivo .service, sem alterar a unidade instalada.
26. [ ] Revisão independente do código, incluindo concorrência/cancelamento e segurança.
27. [ ] Baseline real 0/1/2 viewers durante 30–60 min, CPU/RAM/swap/PSI, Brave + Tailscale; validar retorno real após falha CDP antes de dizer resolvido.
28. [ ] Estudar Xvfb e captura fora do CDP em branch separado, após evidências do passo 27.
