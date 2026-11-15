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
sysrc gns3_server_enable=YES
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
3. **Reprodutibilidade.** Todo build de validação roda em `poudriere` em jail limpa, nunca só
   na máquina de desenvolvimento.
4. **Sem privilégio desnecessário.** O servidor roda como usuário `gns3`; somente o `ubridge`
   é setuid, com modo restrito (`4750 root:wheel`).
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
- [ ] criar `ports/net/ubridge` e `ports/net/gns3-server` com esqueleto de Makefile;
- [ ] `scripts/dev.sh`: clona árvore de Ports rasa, copia os ports e roda `make stage`;
- [ ] `scripts/poudriere/`: `poudriere.conf`, lista de ports e jail de teste;
- [ ] CI no GitHub Actions com VM FreeBSD (`vmactions/freebsd-vm`):
      `portlint -AC`, `make makesum`, `make stage`, `make check-plist`, `pkg check -d`;
- [ ] `docs/TESTES.md` com a matriz de testes.

Aceite: pipeline verde em um push de teste, mesmo com ports ainda vazios.

---

### F2 — `net/ubridge` (primeira entrega real) · 4–6 dias

É o item de maior risco técnico e o que destrava todo o resto.

Tarefas:

- [ ] escolher versão-alvo (recomendado **1.3.2**, a mais recente; 1.2.2 como fallback);
- [ ] `USES=gmake`, sem `configure`; `CFLAGS`/`LDFLAGS` recebendo `-lpcap -lpthread`;
- [ ] **P1 — TAP no FreeBSD:** reintroduzir o ramo `#ifdef __FreeBSD__` do 1.0.0
      (`/dev/tap%d`, sem `linux/if_tun.h`), mantendo o caminho Linux intacto;
- [ ] **P2 — ioctls:** `TUNSIFHEAD`/`TUNSIFMODE` (cabeçalho de 4 bytes e modo ponto-a-ponto)
      e ajuste de MTU/`IFF_` flags;
- [ ] **P3 — pcap:** validar `net/libpcap` + BPF (`/dev/bpf`) para captura e filtros;
- [ ] **P4 — privilégio:** instalar com `@(root,wheel,4750) bin/ubridge`; documentar o risco
      e o modelo de execução (servidor como `gns3`, ubridge setuid);
- [ ] **P5 — data plane:** se o servidor 3.x tentar o caminho de kernel, garantir fallback para
      o relay em user space (o README do upstream diz que só o relay é portável);
- [ ] `pkg-descr`, `WWW`, `LICENSE=GPLv3` + `LICENSE_FILE`.

Aceite:

- `ubridge -v` reporta a versão e passa no `_check_ubridge_version` do servidor (mínimo 0.9.14);
- cria TAP (`/dev/tap0`), aceita `bridge add` e encaminha tráfego entre dois NIOs;
- `poudriere testport` limpo em 15.1 e 14.3;
- patches enviados como PR para `GNS3/ubridge`.

---

### F3 — `net/gns3-server` 3.0.6 · 7–10 dias

Tarefas:

- [ ] `USES=python:3.11+` e `USE_PYTHON=pep517 autoplist`; `DISTFILES` do sdist do PyPI;
- [ ] mapear cada dependência para um `py-*` do Ports e **relaxar os pins** via patch de
      metadados (ver [docs/DEPENDENCIAS.md](docs/DEPENDENCIAS.md));
- [ ] resolver os três bloqueadores reais:
      - `sentry-sdk >= 2.50` × Ports em **1.21.1** → atualizar `devel/py-sentry-sdk` ou tornar
        o Sentry opcional no server;
      - `aiohttp < 3.14` × Ports em **3.14.5** → validar e relaxar;
      - `platformdirs < 3` × Ports em **4.14.3** → validar API e relaxar;
- [ ] `USERS=gns3`, `GROUPS=gns3`; dados em `/var/db/gns3`, logs em `/var/log/gns3`;
- [ ] config de exemplo em `%%PREFIX%%/etc/xdg/GNS3/gns3_server.conf.sample` (`@sample`),
      aproveitando o caminho que o 3.0.6 já procura;
- [ ] `rc.d/gns3server` com `gns3_server_enable`, `_user`, `_group`, `_flags`, `pidfile`,
      `HOME=/var/db/gns3`, `required_files` apontando para o config;
- [ ] `pkg-message`: como habilitar, onde ficam projetos e imagens, dependências opcionais;
- [ ] `pkg-plist` completo (subcomandos `gns3server` e `gns3vmnet`);
- [ ] rodar a suíte upstream (`pytest`) contra as versões do Ports — é o gate que prova que
      relaxar pins não quebrou a API.

Aceite:

- `service gns3server start` sobe o servidor em `:3080` e `GET /v3/version` responde `3.0.6`;
- cria projeto, adiciona **Ethernet switch** (usa ubridge) e nós QEMU/Dynamips, liga e faz ping;
- reinício limpo, `pkg upgrade` preservando `/var/db/gns3` e o config;
- nenhum `pip` envolvido; `pkg check -d` limpo.

---

### F4 — QA e empacotamento · 4–5 dias

- [ ] `poudriere bulk -t` para `net/ubridge` e `net/gns3-server`;
- [ ] `portlint -AC`, `make stage-qa`, `make check-plist`, `make check-orphans`;
- [ ] matriz: 15.1 e 14.3, amd64 (+ aarch64 se houver runner), Python 3.11/3.12/3.13;
- [ ] teste de migração do estado atual: `pip uninstall`, `pkg install`, mover dados de
      `~/.config/GNS3` para `/var/db/gns3` e validar um projeto existente;
- [ ] medir tempo de build e tamanho instalado; ajustar `OPTIONS` se necessário;
- [ ] documentar limitações (sem KVM no FreeBSD → QEMU em TCG; sem Docker/libvirt/IOU).

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
- **Patch de pin (versão do Ports mais nova):** fastapi, uvicorn, pydantic2, sqlalchemy20,
  alembic, aiosqlite, joserfc, python-multipart, websockets, py-cpuinfo2, platformdirs.
- **Bloqueadores:** `sentry-sdk` (Ports 1.21.1 × mínimo 2.50) e `aiohttp` (Ports 3.14.5 ×
  exigência `<3.14`).

Estratégia recomendada: **relaxar pins para as versões do Ports e provar com a suíte de testes
do upstream**. Atualizar port só quando houver incompatibilidade real de API.

---

## 6. Riscos

| Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|
| uBridge 1.3.x não é portável sem reescrever o data plane | alta | alto | usar só o relay em user space; P1/P2 restauram o TAP do 1.0.0; fallback para 1.2.2 |
| Pins do gns3-server 3.x quebram com versões do Ports | alta | alto | suíte `pytest` upstream como gate; patches de metadados versionados |
| `sentry-sdk` 2.x exigir atualização que afeta outros ports | média | médio | avaliar `poudriere bulk` dos dependentes; ou tornar Sentry opcional |
| 3.x é reescrita recente (FastAPI) e muda rápido | média | médio | fixar em 3.0.6, acompanhar releases, patches pequenos |
| QEMU sem KVM no FreeBSD (TCG) | certa | médio | documentar desempenho; Dynamips cobre IOS; bhyve fora de escopo |
| Binário setuid como superfície de ataque | média | alto | modo 4750, dono root, documentar; avaliar Capsicum no futuro |
| Ausência de port do VPCS | média | baixo | documentar; opcional criar `net/vpcs` |
| Revisão no Bugzilla demorar | média | baixo | PRs pequenos e bem descritos; manter overlay próprio até o commit |

---

## 7. Decisões abertas

| ID | Decisão | Recomendação |
|---|---|---|
| D1 | GUI no escopo 1.0? | não; entregar servidor + Web UI primeiro |
| D2 | Categoria dos ports | `net/` para os três (GNS3 é simulador de rede) |
| D3 | Versão do uBridge | 1.3.2; fallback 1.2.2 se o TAP exigir muito retrabalho |
| D4 | Estratégia de pins | relaxar para o Ports + testes upstream |
| D5 | Sentry | tornar opcional no server antes de mexer no port global |
| D6 | uBridge setuid | manter `4750 root:wheel`; documentar; estudar Capsicum depois |
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
