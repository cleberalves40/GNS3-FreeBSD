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

---

# Versão-alvo do uBridge (F2, 15/11/2026)

A tentativa inicial era a **1.3.2** (mais recente). O build no FreeBSD mostrou que o upstream
removeu, a partir da 1.2.0, o suporte a plataformas não-Linux: os módulos de *kernel data
plane* entram no `SRC` sem `#ifdef` e o TAP passou a exigir `linux/if_tun.h`.

Resultado medido com `cc` (FreeBSD 15.1 amd64), build limpo de cada tag:

| Versão | Build | Observação |
|---|---|---|
| 1.0.0 | ✅ | tem o ramo BSD de TAP (`/dev/tap%d`) |
| **1.1.1** | ✅ | **escolhida**: `Makefile` tem alvo `install` para `FreeBSD` com `chmod 4750`; `nio_tap.c` mantém `#ifdef __linux__` |
| 1.2.0 | ❌ | `linux/if_tun.h`, `linux/netlink.h` |
| 1.2.2 | ❌ | + `struct ucred`/`SO_PEERCRED` em `hypervisor.c` |
| 1.3.2 | ❌ | + `linux/bpf.h`, `tc_*`, `virtio_net` |

Erros representativos do 1.2.2/1.3.2:

```
src/nio_tap.c:30:10: fatal error: 'linux/if_tun.h' file not found
src/hypervisor.c:176:17: error: variable has incomplete type 'struct ucred'
src/hypervisor.c:179:35: error: use of undeclared identifier 'SO_PEERCRED'
src/hypervisor_brctl.c:30:10: fatal error: 'linux/netlink.h' file not found
```

**Decisão:** fixar o port em **1.1.1**. É a última release com suporte oficial a FreeBSD e
cobre todo o caminho de relay em user space que o servidor 3.x usa para switches (UDP tunnel,
TAP, UNIX socket, Ethernet, filtros BPF/pcap). O forward-port para 1.2/1.3 fica registrado como
**F2.1** no roadmap: guardar os módulos de kernel com `#ifdef __linux__`, trocar
`SO_PEERCRED` por `getpeereid(3)` e validar o TAP BSD.

# Validação do port 1.1.1

Executado com `PORTSDIR=/usr/ports` e `DISTDIR` local (sem root):

```
make makesum      → SHA256 9bf68e46…0d8, SIZE 94809
make stage        → compila e instala em STAGEDIR
make check-plist  → No pkg-plist issues found
make stage-qa     → sem erros (só o aviso de formato do pkg-message)
make package      → ubridge-1.1.1.pkg (36 KB)
```

O manifesto do pacote confirma o binário privilegiado como esperado:

```
/usr/local/bin/ubridge: uname=root, gname=wheel, perm=04755
shlibs_required: libc.so.7, libpcap.so.8, libthr.so.3
licenses: ["GPLv3"]
```

Testes funcionais (`scripts/smoke-ubridge.py`) contra o binário 1.1.1:

- relay UDP: `bridge create` → 2× `add_nio_udp` → `start` → `stop` → `delete` = todos `100-`;
- TAP: `bridge add_nio_tap br0 tap0` cria `/dev/tap0`; com um NIO UDP o bridge inicia e
  encaminha (`Source/Destination NIO listener thread started`);
- `ubridge -v` → `ubridge version 1.1.1`.

Pendências que passam para F4/F5: `poudriere testport` em 15.1 e 14.3 e envio dos patches
como PR upstream.
