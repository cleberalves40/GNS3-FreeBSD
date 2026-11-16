# Plano de testes

Todos os testes rodam em jail limpa do poudriere, com os ports deste repositório aplicados
sobre a árvore oficial.

## Estáticos (CI, a cada push)

| ID | Teste | Comando | Esperado |
|---|---|---|---|
| S1 | Lint | `portlint -AC` | sem erros fatais; avisos revisados |
| S2 | Somas | `make makesum` | `distinfo` atualizado |
| S3 | Estágio | `make stage` | árvore em `work/stage` |
| S4 | Plist | `make check-plist` | nenhum arquivo órfão/faltante |
| S5 | Stage QA | `make stage-qa` | sem erros |
| S6 | Dependências | `pkg check -d` | árvore consistente |

## uBridge (F2)

| ID | Teste | Como | Esperado |
|---|---|---|---|
| U1 | Versão | `ubridge -v` | reporta a versão do port |
| U2 | Compatibilidade | iniciar servidor e checar log | `_check_ubridge_version` aceita (>= 0.9.14) |
| U3 | TAP | criar link TAP em uma topologia | `/dev/tapN` abre sem erro |
| U4 | Relay | dois NIOs UDP interligados (`bridge add`) | pacotes atravessam |
| U5 | Captura | iniciar captura pcap em um link | arquivo `.pcap` válido em `/dev/bpf` |
| U6 | Permissão | `ls -l $(which ubridge)` | `-rwsr-xr-x root wheel` (restringível a `4750` conforme `pkg-message`) |
| U7 | Sem privilégio | rodar `ubridge` como usuário comum | falha de forma controlada, sem crash |

## Servidor (F3)

| ID | Teste | Como | Esperado |
|---|---|---|---|
| G1 | Serviço | `sysrc gns3server_enable=YES; service gns3server start` | PID criado, log em `/var/log/gns3` |
| G2 | API | `curl -s http://127.0.0.1:3080/v3/version` | JSON com `3.0.6` |
| G3 | Config | editar `/usr/local/etc/gns3/gns3_server.conf` e reiniciar | mudança aplicada |
| G4 | Projeto | criar projeto pela API/GUI | diretório em `/var/db/gns3/GNS3/projects` |
| G5 | Switch | adicionar Ethernet switch + 2 nós | processo `ubridge` filho |
| G6 | Ping | iniciar nós e pingar | tráfego passa pelo switch |
| G7 | Dynamips | adicionar roteador Dynamips | inicia com `dynamips-community` |
| G8 | QEMU | adicionar nó QEMU | inicia (TCG, sem KVM) |
| G9 | Upgrade | `pkg upgrade` simulando nova versão | config e projetos preservados |
| G10 | Migração | remover instalação pip, instalar pkg | projeto antigo abre |
| G11 | Usuário | `ps -o user` do processo | roda como `gns3`, não root |
| G12 | Sem pip | `pkg info -d gns3-server` | nenhuma dependência vinda de `pip` |

## GUI (F6)

| ID | Teste | Esperado |
|---|---|---|
| Q1 | Abrir com Wayland/Niri (`xwayland-satellite`) | janela funcional |
| Q2 | Abrir em X11 | janela funcional |
| Q3 | Conectar ao servidor local | topologia carregada |
| Q4 | Console serial de um nó | terminal abre |

## Matriz de plataformas

| Plataforma | Obrigatório em |
|---|---|
| FreeBSD 15.1 amd64 | F2, F3, F4 |
| FreeBSD 14.3 amd64 | F4 |
| FreeBSD 15.1 aarch64 | desejável (se houver runner) |
| Python 3.11 / 3.12 / 3.13 | F4 (build e import) |

## Evidência local de F3 (não substitui jail limpa)

- `make stage`, `make check-plist`, `make stage-qa` e `make package` passaram no
  FreeBSD 15.1 amd64; `gns3server --version` retorna `3.0.6`.
- Servidor staged respondeu `GET /v3/version` com `version: 3.0.6` usando as
  dependências já instaladas no host.
- O teste é repetível com `scripts/smoke-gns3-server.py`, apontando para o
  binário e a configuração staged.
- Na jail Poudriere 15.1 com as versões do Ports, o serviço iniciou/parou como
  `gns3`; `service status` reconheceu o PID e `GET /v3/version` retornou
  `3.0.6`. O banco SQLite, JWT secret e `gns3_controller.vars` foram criados
  nos caminhos/grupo esperados, e o WebSocket do compute local conectou após
  o retry de startup.
- `poudriere bulk -t` para `scripts/poudriere/ports.list` também passou; o
  servidor foi reconstruído e o uBridge reutilizado do `testport` já aprovado.
- `net/ubridge` também passou `poudriere testport` em jail 14.3 amd64, após
  usar `ALLOW_UNSUPPORTED_SYSTEM=yes`: a release 14.3 está EOL e o Ports avisa
  que não garante builds nessa base.
- `pkg-message` do uBridge foi convertido para UCL; `stage-qa` local agora passa
  sem o aviso de mensagem fora do formato.
- A suíte upstream ainda não foi executada: falta `pytest-asyncio` no ambiente
  local. Rodá-la com as versões do Ports em poudriere permanece gate de F4.
- Tentativa de `poudriere testport` em `15-amd64` não chegou ao port alvo:
  `ports-mgmt/pkg` 2.9.2 falhou no `extract` ao remover `.master_sites` e
  `.distfiles` em `/wrkdirs` (`Permission denied`) como usuário de build. Isso
  aponta para o ambiente/WRKDIR do poudriere. Repetido com a configuração
  temporária `BUILD_AS_NON_ROOT=no`, `net/ubridge` passou o ciclo completo de
  build, package, install, deinstall e detecção de arquivos extras em jail
  15.1 amd64. Essa execução como root é um workaround, não a configuração
  padrão de produção.
- Em 14.3, `testport` do servidor não chegou ao port alvo. Após 4h53 e 152 dos
  174 ports construídos, `lang/rust` falhou ao linkar `clang-23`: o linker
  terminou com segmentation fault. O kernel registrou `swap_pager: out of swap
  space` e sinal 11 em `ld.lld`; a compilação Rust usava `--jobs=1`, mas Poudriere
  tinha dois builders. Um retry com um builder foi iniciado para reduzir a
  pressão de memória e pausado manualmente durante `lang/rust` antes da
  reinicialização planejada; nenhum erro do port GNS3 foi observado em 14.3.
- A primeira tentativa de `testport` do servidor parou em `lang/rust`. O retry
  seguinte compilou as dependências Rust sem reconstruir o port `lang/rust`, e
  avançou até o port do servidor.
- O retry então falhou no build PEP 517: faltavam `setuptools` e `wheel` em
  `BUILD_DEPENDS`, requisitos do `pyproject.toml` com `--no-isolation`. Ambos
  foram adicionados ao Makefile. O retry seguinte passou em jail 15.1 amd64:
  build, package, install, deinstall e verificação de arquivos extras. O pkg foi
  montado com as versões do Ports (por exemplo FastAPI 0.142.2_1 e aiohttp 3.14.5).
- Para `USERS=gns3`/`GROUPS=gns3`, o Poudriere precisa do UID/GID no Ports base
  (`/usr/ports/UIDs` e `GIDs`); os arquivos desses IDs no overlay, isoladamente,
  não bastam. `scripts/register-ids.sh /usr/ports` resolveu o estágio.

## Critério de saída da F4

S1–S6 e U1–U7 verdes em 15.1 e 14.3; G1–G12 verdes em 15.1; limitações documentadas no README.
