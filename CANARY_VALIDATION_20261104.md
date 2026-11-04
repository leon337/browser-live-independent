# Validação isolada pós-reinício — Browser Live

**Data:** 2026-11-04 (America/Recife). **Branch sob teste:** `fix/cdp-health-viewer-resilience` (base `1f46a29`). **Status:** aprovado somente como *canary funcional*; **incidente de produção permanece aberto**.

## Isolamento e condições

- Notebook Linux Mint `leo-N43SM`, RAM física aproximada de 8 GiB. O serviço principal `browser-live-independent.service` permaneceu ativo, em `main` (`efb62ed`), na porta 8918, **sem reinício, merge nem alteração do unit file instalado**.
- Worktree temporário a partir do commit `1f46a29`, código do PR #1. Para execução isolada, houve **modificações somente no worktree temporário, não publicadas**: porta local configurável em 8920 e navegador em modo headless. O código de saúde CDP e resiliência do viewer permaneceu o da branch.
- `HOME` temporário e perfil do Brave totalmente separados do navegador pessoal; sem sessões pessoais no browser de teste. Acesso HTTP somente em loopback; fixture local na porta 8921.
- Processo `browser-live-canary.service` transitório sob systemd, com `CPUQuota=100%`, `MemoryHigh=1300M`, `MemoryMax=2200M` e `MemorySwapMax=256M`. Estes são **limites de teste**, diferentes dos valores propostos no arquivo `.service` do PR.
- Testes de browser/viewer iniciais sem chave Gemini válida; para E2E real, serviço temporário foi reiniciado com leitura de credencial autorizada por link local restrito. Nenhum valor de chave, cookie, perfil ou imagem foi versionado. Link removido após testes.

## Evidências executadas com Brave real

| Experimento | Resultado |
|---|---|
| Iniciar o Brave canary pelo `POST /api/browser` | HTTP 200; `browser_started=true`, `cdp_healthy=true` |
| 0 viewers | Observação leve por 10 s, sem falha |
| 1 viewer | 8 capturas JPEG válidas consecutivas |
| 2 viewers | 8 capturas válidas por viewer no teste inicial |
| 3 viewers | Aceitos no limite configurado; terceiro cliente recebeu capturas |
| 4º viewer | Rejeitado com mensagem de limite e WebSocket close 1013 |
| Página sintética | Navegação CDP para uma página HTML isolada; visualizador mostrou título `Teste CDP isolado` e JPEG real |
| Recuperação CDP | SIGTERM apenas no processo principal do Brave *canary*; `POST /api/browser` retornou 200, criou novo PID/porta CDP e `cdp_healthy=true` |
| Soak sintético 90 s com 2 viewers | 67 quadros válidos por espectador, sem exceção ou queda de serviço |
| E2E com modelo Gemini e 2 viewers | **Tarefa concluída em 2 etapas**: formulário HTTP sintético local em 127.0.0.1:8921 preenchido com `QA`, botão Confirmar acionado, resposta confirmada **pelo servidor fixture**; viewers seguiram o endereço; **62 quadros por espectador**; `cdp_healthy=true` no final |

A tarefa Gemini completa levou aproximadamente 90 segundos. O teste não usou sites públicos, contas pessoais nem ações de terceiros.

## Recursos observados

- Durante o soak de 90 s, temperatura máxima amostrada **58 °C**, pico de memória do *cgroup canary* **285 MB**, menor `MemAvailable` do host **3030 MB**, e `memory PSI full avg10=0` nas amostras.
- Após o E2E Gemini, pico acumulado do *cgroup canary* **354.508.800 bytes** (~338 MiB), `MemorySwapCurrent=0`; após o teste, temperaturas pontuais **64 °C e 71 °C** nas zonas térmicas; `memory PSI full avg10=0` no momento consultado. Os limiares programados de interrupção não foram atingidos.
- Nos logs da injeção de falha apareceram três reconexões CDP malsucedidas da *antiga* sessão, seguidas de logs do health-check marcando o CDP antigo como indisponível e descartando a sessão. A recuperação do processo novo foi confirmada. Essas mensagens eram esperadas após SIGTERM deliberado.
- O teste não mede CPU média sob sites pesados, uso prolongado de autenticação, pressão de dezenas de abas ou energia térmica em sessões longas.

## Limites e bloqueios

1. O Brave foi executado **headless**, não na interface gráfica *headed* da versão principal. A diferença precisa ser avaliada.
2. Soak de 90 segundos não substitui o plano de **30–60 minutos** com 0, 1, 2 espectadores, recursos e atividades reais.
3. O teste com Gemini usou uma página local simples, não páginas de terceiros com DOM, vídeo, scripts e múltiplas abas pesadas.
4. A coexistência dos viewers e da captura nativa do Browser Use em carga extrema continua hipótese a auditar; recuperação de uma única falha CDP não implica recuperação de todos os travamentos.
5. O `MemoryMax=4500M` no service versionado permanece não instalado/não homologado. Pode provocar OOM-kill e não necessariamente evita travamentos do notebook.
6. Revisão independente e critérios de rollback permanecem necessários antes do merge e do deployment.

## Encerramento

Serviços **somente de teste** `browser-live-canary.service` e `browser-live-fixture.service` foram desligados; portas 8920 e 8921 liberadas; link à credencial removido. Serviço principal `browser-live-independent.service` permanece ativo e não foi modificado.

**Decisão:** manter PR #1 em DRAFT; não mesclar em `main`; não ativar limites de memória nem considerar incidente resolvido até a validação prolongada e revisão independente.
