# Checklist de entrega — 2026-11-04

- [x] Ambiente virtual e dependências próprios, versões registradas.
- [x] Serviço próprio ativo e habilitado para início na sessão do usuário.
- [x] Nenhuma importação ou chamada aos agentes MESTRE/HER/MBC/9Router no backend.
- [x] Chave apenas no backend, configuração privada 0600 e excluída do Git.
- [x] Modelo Live aceita conexão real e devolve áudio (teste automatizado, sem escuta humana).
- [x] Tarefa real Browser Use navega, preenche formulário e demonstra pós-condição com recibo no servidor.
- [x] Live aciona ferramenta e comunica conclusão em áudio gerado.
- [ ] Conversa humana simultânea durante a execução (API assíncrona implementada; teste com usuário pendente).
- [x] STOP cancela execução e estado antigo não avança após nova tarefa (teste real de STOP + regressão offline).
- [ ] Histórico e autenticação do perfil persistem após restart (estado de tarefa persistiu; sessões de sites não foram testadas).
- [x] Tarefa interrompida por restart é identificada como resultado incerto (regressão offline).
- [ ] Interface 1366×768 sem erros de JS em navegador visível (sintaxe JS passou; inspeção manual pendente).
- [ ] Microfone desliga ao encerrar voz e reprodução interrompida limpa (implementado, teste acústico/manual pendente).
- [x] Origin/Host inválidos recusados (smoke).
- [x] Varredura dos arquivos para padrões de chaves; código/versionamento sem banco, logs, perfis ou credenciais.
- [x] Limitações e testes não executados declarados no README e relatório.

Observação: a validação acústica da voz de LEANDRO e o teste visual do microfone devem ocorrer no notebook. Um teste de áudio sintético não substitui essas verificações.
