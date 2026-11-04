# Saúde CDP e resiliência do Viewer — branch de revisão

**Data:** 2026-11-04 (America/Recife)
**Branch:** `fix/cdp-health-viewer-resilience`
**Base:** `efb62edd9580b6c325a43f370209d88b05c9f836`

## Proveniência

O usuário forneceu a transcrição de uma revisão produzida por outra IA, com referência ao patch `0001-fix-verificar-saude-do-CDP-e-tornar-o-viewer-resilie.patch` e ao commit `c4995b1`. Nenhum dos dois estava disponível no notebook, no Colab informado ou no material conectado consultado. Por isso esta branch foi implementada **novamente**, usando os requisitos descritos, e **não reproduz nem autentica aquele commit original**.

## Entrega em código, ainda não implantada

- `Runtime.check_cdp()` usa a chamada CDP real `Browser.getVersion()`, com timeout de 3 s por tentativa e duas tentativas na reutilização. A propriedade `is_cdp_connected` evita chamada quando o socket já fechou.
- `Runtime.get_browser()` descarta sessão comprovadamente não responsiva e cria outra quando nenhum agente está executando. Se `self.agent` estiver ativo, proíbe descarte/kill do navegador.
- `Runtime.monitor_cdp()`: a cada 15 segundos, consulta saúde, mas não executa probe CDP ativa em paralelo a tarefas do agente; tampouco reinicia ou encerra navegador. `/api/status` inclui `cdp_healthy` e último timestamp conhecido. Valor `null` pode significar navegador ainda não iniciado.
- `db()` agora é context manager de fechamento explícito de SQLite.
- `viewer.py`: limite global de três espectadores, captura serial por frame, reutilização em cache da aba por aproximadamente 1,2 s, backoff exponencial e limite de imagem 2,5 MB em base64. Uma falha de captura entra em cooldown. Não inclui URLs, imagens ou dados de sessão nos logs.
- `browser-live-independent.service`: `MemoryHigh=3500M`, `MemoryMax=4500M`, `MemorySwapMax=512M`, **somente no arquivo versionado**. Valores iniciais, sem teste de estabilidade no notebook.

## Validação executada

```sh
.venv/bin/python -m unittest -v runtime_tests resilience_tests
.venv/bin/python -m py_compile app.py viewer.py resilience_tests.py
git diff --check
```

**12/12 testes passaram com navegador falso** (10 novos e 2 existentes). Não foram realizados teste prolongado, falha induzida no Brave real, teste do app a partir do Android nem deploy da versão nova.

## Pontos que um auditor precisa verificar

1. Testar se a sondagem CDP compete com operações de navegação e se o monitor passivo realmente evita isso.
2. Confirmar que a sessão reconstruída libera o processo antigo e o perfil sem conflito de lock.
3. Verificar a segurança de `get_browser()` se STOP ocorrer durante uma sondagem; validar cancelamento real.
4. Em versões com vários espectadores, avaliar se cache e serialização do viewer reduzem a pressão sobre CDP na prática.
5. Testar desconexões WebSocket e limite de espectadores; inspecionar liberação de recursos.
6. Verificar se `MemoryHigh` causa throttling degradante sob pressão de swap. `MemoryMax` **pode matar processos do grupo** (cgroup OOM); não é apenas aviso. Ajustar limites à linha de base e ao hardware real.
7. Validar `cdp_healthy` como um estado amostrado (não equivalência a prontidão instantânea) e rechecagem antes de executar ações.
8. Priorizar a linha de base 0/1/2 espectadores por 30–60 min, CPU, RAM, swap e PSI, antes do Xvfb.

## Política de implantação

- Nada foi instalado nem reiniciado durante a criação deste branch; o serviço local continua executando o código carregado antes da alteração.
- Não homologar produção até validar passo 27; esse branch se destina a pull request/revisão.
- A branch de segurança `backup/antes-cdp-health` referencia o HEAD original local (não altera main).
