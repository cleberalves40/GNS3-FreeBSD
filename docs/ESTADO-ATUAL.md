# Estado atual (reconhecimento — F0, 15/11/2026)

## Máquina de referência

| Item | Valor |
|---|---|
| SO | FreeBSD 15.1-STABLE `stable/15-n286112-a4dc618ab4d8` amd64 |
| Python do sistema | 3.12.15 (`python312`) |
| Ports | árvore em `/usr/ports`; `pkg` 2.9.0 |
| Gerenciador de pacotes | `pkg` (nenhum GNS3 registrado) |

## Instalação atual (a ser substituída)

| Componente | Versão | Caminho | Observação |
|---|---|---|---|
| `gns3-server` | 3.0.6 | `~/.local/lib/python3.12/site-packages` | instalado por `pip --user` |
| `gns3-gui` | 3.0.6 | idem | importa **PyQt6** |
| `ubridge` | **1.0.0** | `/usr/local/bin/ubridge` | `-rwsr-x--- root:wheel` (4750), **fora do pkg** |
| `dynamips` | 0.2.17_1 | `/usr/local/bin/dynamips` | vem de `emulators/dynamips-community` |

Estado do usuário: `~/.config/GNS3` e `~/GNS3` existem (config e projetos atuais).

## Fontes do uBridge encontradas

| Caminho | Conteúdo |
|---|---|
| `~/ubridge` | clone limpo do upstream, versão **1.2.2**, sem patches, `git status` limpo |
| `~/Downloads/ubridge-1.0.0` | fonte da versão **1.0.0**, que ainda tem o ramo BSD de TAP |

Diferença relevante em `src/nio_tap.c`:

- **1.0.0** tem `#ifdef __linux__` em volta de `linux/if_tun.h` e um `#else` que abre
  `/dev/tap%d` (comportamento BSD/macOS);
- **1.2.2** removeu o `#else` e passou a exigir `linux/if_tun.h` incondicionalmente.

Tentativa de build do 1.2.2 nesta máquina:

```
src/nio_tap.c:30:10: fatal error: 'linux/if_tun.h' file not found
```

Ou seja: **o port precisa carregar o patch de TAP para FreeBSD**. O README do upstream declara
o uBridge como Linux-only, e o *kernel data plane* (veth, VXLAN, kernel bridge, tc/netem,
AF_PACKET) não é portável. O relay em user space (UDP tunnel, Ethernet, TAP, UNIX socket,
filtros BPF) é o caminho viável.

O binário 1.0.0 instalado confirma o caminho: `strings` mostra `/dev/tap%d`.

## Versão do servidor e API

- `gns3server --version` → `3.0.6`
- rotas montadas com prefixo **`/v3`** (`gns3server/api/server.py`), ex.: `GET /v3/version`
- configuração procurada em, nesta ordem: `~/.config/GNS3/...`, `/etc/xdg/GNS3/gns3_server.conf`,
  `/etc/xdg/GNS3.conf` — o port deve usar `@sample` em `%%PREFIX%%/etc/xdg/GNS3/`.

## O que já existe no Ports

| Necessidade | Port | Situação |
|---|---|---|
| Dynamips | `emulators/dynamips-community` | ✅ 0.2.17_1 |
| QEMU | `emulators/qemu` | ✅ |
| Conversão de projetos 2.x | `emulators/py-gns3-converter` | ✅ |
| uBridge | — | ❌ inexistente |
| gns3-server | — | ❌ inexistente |
| gns3-gui | — | ❌ inexistente |
| VPCS | — | ❌ inexistente |
| PyQt6 do GUI | `devel/py-qt6-pyqt` 6.11.0 | ✅ |
| QtWebEngine do GUI | `www/py-qt6-webengine` / `www/qt6-webengine` | ✅ |

Não há registro no Bugzilla do FreeBSD para ports de GNS3 — trabalho inédito, sem duplicidade.

## Conclusão da fase

O caminho é viável e o escopo está fechado: **uBridge primeiro** (destrava tudo e é o único
componente com patch de plataforma), **servidor depois** (trabalho de dependências e
empacotamento, sem código C), GUI por último e opcional.
