# Patches mantidos pelo GNS3-FreeBSD

Esta pasta guarda os patches em formato `git format-patch`, prontos para envio como PR aos
repositórios upstream. A cópia aplicada pelo Ports fica em `ports/net/<port>/files/`.

## Previstos

| Patch | Alvo | Função | Status |
|---|---|---|---|
| `0001-tap-freebsd.patch` | GNS3/ubridge | restaurar TAP BSD (`/dev/tap%d`) sem `linux/if_tun.h` | a escrever |
| `0002-tap-ioctls.patch` | GNS3/ubridge | `TUNSIFHEAD`/`TUNSIFMODE`, MTU e flags | a escrever |
| `0003-pcap-freebsd.patch` | GNS3/ubridge | ajustes de captura/filtros em `/dev/bpf` | a avaliar |
| `0004-relax-pins.patch` | GNS3/gns3-server | relaxar pins de dependências para o Ports | a escrever |
| `0005-optional-sentry.patch` | GNS3/gns3-server | tornar Sentry opcional | a avaliar |

## Regras

1. Um patch = uma mudança lógica.
2. Cabeçalho com motivo, referência (issue/PR) e plataformas afetadas.
3. Sempre que possível, o patch deve ser aceitável upstream — nada de caminho específico do
   Ports dentro do código.
4. Ao ser aceito upstream, o patch é removido daqui e o port atualizado.
