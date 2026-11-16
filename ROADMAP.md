# Roadmap — GNS3 nativo no FreeBSD Ports

**Projeto:** `GNS3-FreeBSD`
**Mantenedor:** Cleber Alves do Nascimento (`cleberalves40`)
**Alvo inicial:** GNS3 **3.0.6** no FreeBSD **15.1-STABLE amd64** (com suporte a 14.3 e aarch64)
**Início:** 15/11/2026
**Estimativa total:** 5–6 semanas (dedicação parcial)

---

## 1. Objetivo

Substituir a instalação atual por `pip --user` + `ubridge` compilado à mão por **três ports
nativos**:

| Port | Origem | O que resolve |
|---|---|---|
| `net/ubridge` | GNS3/ubridge | helper de rede (TAP, Ethernet, UDP tunnel, filtros) compilado para FreeBSD, instalado com as permissões corretas e registrado no pkg |
| `net/gns3-server` | GNS3/gns3-server | servidor 3.x (FastAPI/uvicorn), serviço `rc.d`, config em `/usr/local/etc`, dados em `/var/db/gns3` |
| `net/gns3-gui` (F6) | GNS3/gns3-gui | cliente desktop PyQt6, opcional |

Resultado esperado, em uma instalação limpa:

```sh
pkg install gns3-server ubridge dynamips-community qemu
sysrc gns3server_enable=YES
service gns3server start
# GUI/web conecta em http://127.0.0.1:3080
```

Sem `pip`, sem venv, sem baixar binário privilegiado por fora do pkg.

---

## 2. Baseline verificado (F0)

Máquina de referência: FreeBSD 15.1-STABLE amd64, Python **3.12.15** (default do Ports).

| Item | Situação hoje |
|---|---|
| `gns3-server` | 3.0.6 em `/home/cleber/.local/lib/python3.12/site-packages` (pip `--user`) |
| `gns3-gui` | 3.0.6, mesmo local, importa **PyQt6** |
| `ubridge` | **1.0.0** em `/usr/local/bin`, `-rwsr-x--- root:wheel`, **fora do banco do pkg** |
| Fonte do ubridge local | `~/ubridge` = clone limpo do upstream **1.2.2** (sem patches) |
| Fonte antiga | `~/Downloads/ubridge-1.0.0` — **contém o ramo BSD de TAP** que o 1.2.2 perdeu |
| `dynamips` | `dynamips-community-0.2.17_1` do Ports |
| `qemu` | disponível no Ports |
| VPCS | **sem port** no FreeBSD |
| Ports existentes de GNS3 | apenas `emulators/py-gns3-converter` (ferramenta 2.x) |
| API do servidor 3.0.6 | prefixo **`/v3`** (ex.: `GET /v3/version`) |
| Config | procura `~/.config/GNS3/...` e **`/etc/xdg/GNS3/gns3_server.conf`** |

Teste de compilação do uBridge 1.2.2 no FreeBSD (feito nesta fase):

```
src/nio_tap.c:30:10: fatal error: 'linux/if_tun.h' file not found
```

O upstream declara no README que o uBridge é **Linux-only** e que o *kernel data plane*
(veth, VXLAN, tc/netem, AF_PACKET) é específico do Linux. O ramo BSD existente no 1.0.0
(`/dev/tap%d`) foi removido — é exatamente esse patch que precisamos forward-portar.

Detalhes em [docs/ESTADO-ATUAL.md](docs/ESTADO-ATUAL.md).

---

## 3. Princípios de execução

1. **Nada de wheels vendorizados.** Toda dependência Python vem de `py-*` do Ports; quando
   faltar ou estiver defasada, a correção vai para o Ports (novo port ou atualização), não
   para dentro do nosso port.
2. **Patch mínimo e documentado.** Cada patch tem um `.patch` nomeado, comentário no Makefile
   e, quando possível, PR upstream.
3. **Reprodutibilidade.** Build local é feedback rápido; aceite de release roda em jail limpa
   via `poudriere`, não apenas na máquina de desenvolvimento.
4. **Sem privilégio desnecessário.** O servidor roda como usuário `gns3`; somente o `ubridge`
   é setuid (`4755 root:wheel` por padrão, opcionalmente restrito a `4750 root:gns3`).
5. **Upstream primeiro.** Se o GNS3 precisar mudar para suportar FreeBSD, abrimos PR lá antes
   de carregar o patch para sempre.

---

## 4. Fases

### F0 — Reconhecimento e decisões · ✅ concluída (15/11/2026)

Entregáveis:

- inventário do ambiente (versões, caminhos, permissões) — `docs/ESTADO-ATUAL.md`;
- matriz de dependências pin × Ports — `docs/DEPENDENCIAS.md`;
- identificação do bloqueio do uBridge (`linux/if_tun.h`) e da regressão 1.0.0 → 1.2.2;
- escopo fechado (servidor + ubridge; GUI opcional).

Aceite: documentos revisados e decisões D1–D4 registradas.

---

### F1 — Repositório, layout e CI · 2 dias

Tarefas:

- [x] criar `cleberalves40/GNS3-FreeBSD` com README, ROADMAP, LICENSE e docs;
- [x] criar `ports/net/ubridge` (port completo) e `ports/net/gns3-server` (esqueleto);
- [x] `scripts/dev.sh`: valida os ports contra `PORTS_TREE` sem root;
- [x] `scripts/poudriere/`: config de exemplo, `ports.list` e instruções;
- [x] CI no GitHub Actions com VM FreeBSD (`vmactions/freebsd-vm`);
- [x] `docs/TESTES.md` com a matriz de testes;
- [x] `scripts/smoke-ubridge.py`: teste funcional do hypervisor (UDP e TAP).

Aceite: pipeline definido e reproduzível; `net/ubridge` valida localmente com
`makesum`, `make stage`, `check-plist`, `stage-qa` e `make package`.

---

### F2 — `net/ubridge` (primeira entrega real) · 4–6 dias · ✅ concluída (15/11/2026)

É o item de maior risco técnico e o que destrava todo o resto.

**Versão-alvo: 1.1.1** — não a 1.3.2. Evidência levantada nesta fase (build com `cc` do
FreeBSD 15.1):

| Versão | Resultado |
|---|---|
| 1.0.0 | compila limpo; mantém o ramo BSD de TAP |
| **1.1.1** | **compila limpo**; `Makefile` tem alvo `install` explícito para `FreeBSD` (`chmod 4750`); `nio_tap.c` preserva `#ifdef __linux__` com fallback `/dev/tap%d` |
| 1.2.0 | `linux/if_tun.h` e `linux/netlink.h` incondicionais |
| 1.2.2 | idem + `struct ucred`/`SO_PEERCRED` em `hypervisor.c`; módulos de kernel Linux (`nio_linux_raw`, `hypervisor_brctl`, `hypervisor_link`, `hypervisor_tc`, `netlink/`) entram no `SRC` sem guarda |
| 1.3.2 | todos os erros acima + `linux/bpf.h`, `tc_*`, `virtio_net` |

A 1.1.1 é a última release com suporte oficial a FreeBSD. As séries 1.2/1.3 removeram o
código de plataforma e compilam os módulos de *kernel data plane* do Linux sem `#ifdef`,
o que exige um forward-port maior (ver F2.1).

Tarefas:

- [x] escolher versão-alvo: **1.1.1** (última com suporte oficial a FreeBSD);
- [x] `USES=gmake`, sem `configure`; `CFLAGS`/`LDFLAGS` herdados do framework;
- [x] **P1/P2 — TAP no FreeBSD:** o ramo `/dev/tap%d` já existe na 1.1.1; validado criando
      `tap0` e encaminhando tráfego TAP↔UDP;
- [x] **P3 — pcap:** linka contra `libpcap.so.8`; captura/filtros herdados do upstream;
- [x] **P4 — privilégio:** instalado como `@(root,wheel,4755) bin/ubridge`; `pkg-message`
      documenta como restringir a `4750 root:gns3`;
- [x] **P5 — data plane:** como a 1.1.1 não traz os módulos de kernel Linux, o único caminho
      é o relay em user space — exatamente o que o servidor 3.x usa para switches;
- [x] `pkg-descr`, `WWW`, `LICENSE=GPLv3` + `LICENSE_FILE`.

Aceite:

- [x] `ubridge -v` reporta `1.1.1` (acima do mínimo 0.9.14 exigido pelo servidor);
- [x] cria TAP (`/dev/tap0`), aceita `bridge add` e encaminha tráfego entre dois NIOs;
- [x] `make stage`, `check-plist`, `stage-qa` e `make package` limpos localmente;
      `portlint -AC` só acusa o que é esperado antes do commit;
- [x] `poudriere testport` limpo em FreeBSD 15.1 amd64 (F4; temporariamente com
      `BUILD_AS_NON_ROOT=no` para contornar o problema de permissões de extração no host);
- [x] `poudriere testport` em FreeBSD 14.3 amd64 (F4; release EOL, com
      `ALLOW_UNSUPPORTED_SYSTEM=yes` apenas para a validação);
- [ ] patches enviados como PR para `GNS3/ubridge` (F5).

Evidências: `scripts/smoke-ubridge.py` (relay UDP), teste TAP `tap0` + UDP, e manifesto do
pacote com `perm: "04755"`. Detalhes em [docs/ESTADO-ATUAL.md](docs/ESTADO-ATUAL.md).

#### F2.1 — forward-port para 1.2.x/1.3.x (backlog, pós-1.0)

- [ ] guardar com `#ifdef __linux__` todos os módulos de kernel (`nio_linux_raw`,
      `hypervisor_brctl`, `hypervisor_link`, `hypervisor_tc`, `hypervisor_vxlan`,
      `hypervisor_docker`, `netlink/`) e removê-los do `SRC` no FreeBSD;
- [ ] trocar `struct ucred`/`SO_PEERCRED` por `getpeereid(3)` em `hypervisor.c`;
- [ ] reintroduzir/validar o caminho TAP BSD em `nio_tap.c` e `hypervisor_tap.c`;
- [ ] reenviar como PR upstream; só então atualizar `net/ubridge`.

---

### F3 — `net/gns3-server` 3.0.6 · 7–10 dias · 🔄 port inicial passou em jail 15.1

Tarefas:

- [x] `USES=python:3.11+`, `USE_PYTHON=pep517 autoplist noflavors`, sdist do PyPI e
      dependências de build `setuptools`/`wheel` declaradas para PEP 517;
- [x] dependências de runtime mapeadas para `py-*` do Ports com limites relaxados no
      `RUN_DEPENDS` (sem pip); tabela em [docs/DEPENDENCIAS.md](docs/DEPENDENCIAS.md);
- [x] `RUN_DEPENDS` em `net/ubridge>=1.1.1` para fornecer o helper de switches Ethernet;
- [x] Sentry omitido: opcional no upstream e Ports oferece 1.21.1, abaixo do mínimo 2.50;
      `aiohttp`, `platformdirs`, `websockets` e `py-cpuinfo` usam os ports atuais, ainda
      sujeitos à suíte upstream em F4;
- [x] `USERS=gns3`, `GROUPS=gns3`; dados em `/var/db/gns3`, logs em `/var/log/gns3`;
- [x] config de exemplo em `${PREFIX}/etc/gns3/gns3_server.conf.sample` (`@sample`), passada
      explicitamente com `--config` porque o upstream procura `/etc/gns3`;
- [x] `rc.d/gns3server` com `gns3server_enable`, `_user`, `_group`, `_flags`, pidfile,
      `HOME=/var/db/gns3` e `required_files`;
- [x] `pkg-message` documenta operação, caminhos e dependências opcionais;
- [x] `USE_PYTHON=autoplist noflavors` inclui entry points `gns3server` e `gns3vmnet`; config/rc.d e
      diretórios de dados são mantidos explicitamente na plist;
- [x] scripts Docker, exclusivos de Linux e com shebangs inválidos em FreeBSD, excluídos do
      pacote (nós Docker estão fora de escopo);
- [x] registro privado do UID/GID `gns3` para overlay, necessário até aceitação na árvore oficial;
- [x] patch pequeno para a chave `license-files`, não reconhecida pelo `setuptools` 63 do Ports;
- [x] patch de compatibilidade: migrar startup/shutdown para `lifespan` (Starlette 1.x removeu
      `FastAPI.add_event_handler`);
- [x] smoke test do servidor staged: `gns3server --version` e `GET /v3/version` → `3.0.6`;
- [x] `poudriere testport` em FreeBSD 15.1 amd64: build/package/install/deinstall passaram;
- [x] serviço `rc.d` iniciado/parado como `gns3`; `GET /v3/version` → `3.0.6` usando as versões
      atuais do Ports; conexão WebSocket do compute local confirmada após inicialização;
- [ ] rodar a suíte upstream (`pytest`) contra as versões do Ports — gate que prova que
      relaxar pins não quebrou a API; `pytest-asyncio` não está instalado no host local.

Aceite:

- `service gns3server start` sobe o servidor em `:3080` e `GET /v3/version` responde `3.0.6`;
- cria projeto, adiciona **Ethernet switch** (usa ubridge) e nós QEMU/Dynamips, liga e faz ping;
- reinício limpo, `pkg upgrade` preservando `/var/db/gns3` e o config;
- nenhum `pip` envolvido; `pkg check -d` limpo.

---

### F4 — QA e empacotamento · 4–5 dias · 🔄 validação em jail iniciada

- [x] `poudriere testport` de `net/ubridge` em jails 15.1 e 14.3 amd64: build/package/install/
      deinstall passaram; 14.3 é EOL e exigiu `ALLOW_UNSUPPORTED_SYSTEM=yes`;
- [x] `poudriere testport` de `net/gns3-server` em jail 15.1 amd64: build/package/install/
      deinstall passaram após declarar `setuptools`/`wheel` e registrar o GID/UID no Ports base;
- [x] serviço na jail: `service gns3server start/status/stop`, usuário `gns3`, banco, segredos e
      variáveis do controller gravados; API respondeu `3.0.6` com FastAPI 0.142.2_1/Starlette 1.10.0;
- [x] `poudriere bulk -t` com a lista do projeto: `net/gns3-server` construído; `net/ubridge`
      reutilizado do `testport` limpo já aprovado;
- [x] `portlint -AC`, `make stage-qa`, `make check-plist` nos dois ports; `make check-orphans`
      também passou para `net/gns3-server`;
- [ ] `net/gns3-server` em FreeBSD 14.3 amd64 (pausado para reinicialização após pressão de swap
      em `lang/rust`; retomar com um builder; release EOL e `ALLOW_UNSUPPORTED_SYSTEM=yes`);
- [ ] matriz adicional Python 3.11/3.12/3.13 e aarch64 (se houver runner);
- [ ] teste de migração do estado atual: `pip uninstall`, `pkg install`, mover dados de
      `~/.config/GNS3` para `/var/db/gns3` e validar um projeto existente;
- [ ] medir tempo de build e tamanho instalado; ajustar `OPTIONS` se necessário;
- [x] documentar limitações (sem KVM no FreeBSD → QEMU em TCG; sem Docker/libvirt/IOU/VPCS).

Aceite: relatório de QA anexado ao repositório e todos os checks verdes.

---

### F5 — Upstream e submissão ao FreeBSD · 3–5 dias

- [ ] PR `GNS3/ubridge`: suporte FreeBSD no TAP + build instructions;
- [ ] PR `GNS3/gns3-server`: relaxar pins/metadados e nota de plataforma (se aceito, reduz
      nossos patches a quase zero);
- [ ] Bugzilla FreeBSD: `[NEW PORT] net/ubridge` e `[NEW PORT] net/gns3-server`, com
      `git format-patch`/shar, mantenedor `cleberalves40` e `WWW` corretos;
- [ ] responder ao review; ajustar categoria (`net/` vs `emulators/`) conforme orientação;
- [ ] após commit: acompanhar `portscout`, `pkg-fallout` e atualizações upstream.

Aceite: ports commitados na árvore oficial ou, no mínimo, PRs abertos com review em curso.

---

### F6 — `net/gns3-gui` (opcional) · 5–8 dias

- [ ] dependências: `py312-qt6-pyqt` 6.11.0 e `py312-qt6-webengine` (ambos no Ports);
- [ ] testar em Wayland/Niri com `xwayland-satellite` e em X11;
- [ ] alternativa de menor custo: entregar só o servidor + **GNS3 Web UI** no navegador;
- [ ] decidir se o GUI entra no escopo 1.0 ou vira port separado.

---

## 5. Dependências — resumo

Matriz completa em [docs/DEPENDENCIAS.md](docs/DEPENDENCIAS.md). Situação:

- **OK (usar direto):** aiofiles, Jinja2, psutil, distro, bcrypt, email-validator, watchdog,
  zstandard, truststore.
- **Limites relaxados em `RUN_DEPENDS`:** fastapi, uvicorn, pydantic2, sqlalchemy20,
  alembic, aiosqlite, joserfc, python-multipart, websockets, py-cpuinfo2, platformdirs.
- **Sem bloqueador de empacotamento conhecido:** Sentry é opcional e omitido; versões atuais de
  `aiohttp`, `platformdirs`, `websockets` e `py-cpuinfo` excedem os limites upstream e precisam
  passar pela suíte upstream em F4.

Estratégia recomendada: **relaxar pins para as versões do Ports e provar com a suíte de testes
do upstream**. Atualizar port só quando houver incompatibilidade real de API.

---

## 6. Riscos

| Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|
| uBridge 1.2+/1.3.x não é portável sem reescrever o data plane | alta | alto | fixar em **1.1.1**, que ainda tem o TAP BSD e alvo `install` para FreeBSD; forward-port em F2.1 |
| Pins do gns3-server 3.x quebram com versões do Ports | alta | alto | suíte `pytest` upstream como gate; patches de metadados versionados |
| Mudanças de API nas versões mais novas dos ports Python | média | alto | executar a suíte upstream em jail limpa; manter os limites/revisões no Makefile |
| 3.x é reescrita recente (FastAPI) e muda rápido | média | médio | fixar em 3.0.6, acompanhar releases, patches pequenos |
| QEMU sem KVM no FreeBSD (TCG) | certa | médio | documentar desempenho; Dynamips cobre IOS; bhyve fora de escopo |
| Binário setuid como superfície de ataque | média | alto | `4755 root:wheel` por padrão; documentar redução para `4750 root:gns3`; avaliar Capsicum |
| Ausência de port do VPCS | média | baixo | documentar; opcional criar `net/vpcs` |
| Revisão no Bugzilla demorar | média | baixo | PRs pequenos e bem descritos; manter overlay próprio até o commit |

---

## 7. Decisões abertas

| ID | Decisão | Recomendação |
|---|---|---|
| D1 | GUI no escopo 1.0? | não; entregar servidor + Web UI primeiro |
| D2 | Categoria dos ports | `net/` para os três (GNS3 é simulador de rede) |
| D3 | Versão do uBridge | **1.1.1** (última com suporte oficial a FreeBSD); forward-port para 1.2/1.3 em F2.1 |
| D4 | Estratégia de pins | relaxar para o Ports + testes upstream |
| D5 | Sentry | tornar opcional no server antes de mexer no port global |
| D6 | uBridge setuid | `4755 root:wheel` para operação imediata; opcional `4750 root:gns3`; estudar Capsicum depois |
| D7 | VPCS | fora do escopo 1.0; port futuro |
| D8 | Onde vivem os patches | `patches/` no repo + PR upstream; remover ao serem aceitos |

---

## 8. Cronograma sugerido

| Semana | Foco | Marco |
|---|---|---|
| 1 (17–21/11) | F1 + início da F2 | repo com CI verde; primeiro build do ubridge |
| 2 (24–28/11) | F2 | **M1:** `net/ubridge` instalável e funcional |
| 3–4 (01–12/12) | F3 | **M2:** `net/gns3-server` sobe e cria topologia com switch + Dynamips |
| 5 (15–19/12) | F4 | **M3:** QA em poudriere e migração do pip validadas |
| 6 (22–29/12) | F5 | **M4:** PRs upstream e submissão no Bugzilla |
| — | F6 | opcional, após o commit dos ports |

---

## 9. Definição de pronto (1.0)

1. `pkg install gns3-server` em jail limpa 15.1 e 14.3, sem tocar em `pip`.
2. `service gns3server start` + `curl http://127.0.0.1:3080/v3/version` → `3.0.6`.
3. Topologia de teste com Ethernet switch (ubridge) e roteador Dynamips funcional, com ping.
4. `poudriere testport`, `portlint -AC`, `check-plist` e `stage-qa` limpos.
5. Patches do uBridge publicados e PRs upstream abertos.
6. Documentação de limitações, migração do pip e operação do serviço.
7. Ports submetidos ao Bugzilla do FreeBSD com `MAINTAINER= cleberalves40`.
