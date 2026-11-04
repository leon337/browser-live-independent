# Browser Live — acesso privado no telefone via Tailscale

Data do provisionamento: 2026-11-04.

## Endereços

- Notebook local: http://127.0.0.1:8918
- Telefone na tailnet: **https://mcf-leo-n43sm.tail582305.ts.net:8461/**
- IP tailnet do notebook (diagnóstico somente): 100.83.95.44
- Serviço de aplicação: `browser-live-independent.service`, systemd --user
- Serviço Tailscale: `mcf-tailscale-user.service`, systemd --user; usuários de rede Tailscale predixaibr

O notebook usa `tailscaled --tun=userspace-networking`. Portanto, a ausência da interface kernel `tailscale0` e a resolução DNS pública do domínio em comandos normais no próprio notebook não provam falha do Serve privado.

## Para usar no Android

1. Abra o aplicativo Tailscale no Realme 9i.
2. Ative a VPN Tailscale e confirme acesso à mesma tailnet que contém `mcf-leo-n43sm`.
3. Abra o link HTTPS acima no Chrome ou navegador móvel e permita o uso do microfone.
4. Clique em **Iniciar conversa ao vivo**. O Brave automatizado aparecerá no notebook; a UI e a voz funcionam pelo telefone.

O dispositivo Realme 9i já consta no cadastro da tailnet, mas aparecia offline no momento do provisionamento. A conexão Android e a captura de microfone físico devem ser testadas pelo usuário.

## Provisionamento aplicado

```bash
tailscale serve --bg --https=8461 http://127.0.0.1:8918
```

Essa configuração é privada (Tailscale Serve, **não Funnel**), persiste na configuração do daemon e não modifica outros ports/serviços. Para inspeção:

```bash
tailscale serve status
systemctl --user is-active mcf-tailscale-user.service browser-live-independent.service
```

Para **desabilitar somente** esse acesso, sem tocar nas outras rotas:

```bash
tailscale serve --https=8461 off
```

A aplicação continua ouvindo somente em 127.0.0.1:8918. O acesso pelo nome de domínio é HTTPS, o que permite solicitar a permissão de microfone em navegador moderno; as conexões WebSocket são atualizadas dinamicamente para WSS no HTTPS. As proteções de Host, Origin e cookies continuam exigidas; o acesso à página que emite o cookie depende de pertencer à tailnet e de suas regras ACL.

## Evidências verificadas

- `tailscale serve status` mostra **:8461 (tailnet only)** proxy para 127.0.0.1:8918.
- Requisição `GET /` via SOCKS5 interno do daemon `127.0.0.1:10555`: **HTTP 200**.
- `GET /api/status` com cookie de sessão: **HTTP 200**, `ready: true`, `independent: true`.
- `GET /static/app.js`: **HTTP 200**.
- `GET /api/status` sem cookie: **HTTP 403**.
- `POST /api/stop` com Origin inválido: **HTTP 403**.
- Upgrade WSS em `/events` e `/live`: **HTTP 101 Switching Protocols** via Tailscale Serve privado.
- Verificado que `mcf-tailscale-user.service` e `browser-live-independent.service` estavam ativos e habilitados.
- Configuração pública Funnel existente para outras portas não foi alterada.

Para reproduzir a verificação HTTPS na arquitetura Tailscale userspace do notebook, use a opção `--socks5-hostname 127.0.0.1:10555` do curl. Sem isso, o sistema operacional pode resolver o domínio via DNS público do Funnel e a porta privada 8461 não responderá, mesmo estando disponível na tailnet.

## Limitações

- Teste real de navegador e microfone no Android ainda pendente enquanto Tailscale do Realme 9i está offline.
- O link funciona apenas para dispositivos autorizados na tailnet, conforme ACLs vigentes.
- O notebook e serviços devem estar ligados. A persistência de ambos foi configurada, mas a reinicialização física ainda não foi repetida após esta alteração.
- Outros serviços no mesmo Tailscale podem ter Funnel público; isso não torna a porta 8461 pública.
