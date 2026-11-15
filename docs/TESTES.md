# Plano de testes

Todos os testes rodam em jail limpa do poudriere, com os ports deste repositório aplicados
sobre a árvore oficial.

## Estáticos (CI, a cada push)

| ID | Teste | Comando | Esperado |
|---|---|---|---|
| S1 | Lint | `portlint -AC` | sem avisos |
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
| U6 | Permissão | `ls -l $(which ubridge)` | `-rwsr-x--- root wheel` |
| U7 | Sem privilégio | rodar `ubridge` como usuário comum | falha de forma controlada, sem crash |

## Servidor (F3)

| ID | Teste | Como | Esperado |
|---|---|---|---|
| G1 | Serviço | `sysrc gns3_server_enable=YES; service gns3server start` | PID criado, log em `/var/log/gns3` |
| G2 | API | `curl -s 127.0.0.1:3080/v3/version` | JSON com `3.0.6` |
| G3 | Config | editar `gns3_server.conf` e reiniciar | mudança aplicada |
| G4 | Projeto | criar projeto pela API/GUI | diretório em `/var/db/gns3/projects` |
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

## Critério de saída da F4

S1–S6 e U1–U7 verdes em 15.1 e 14.3; G1–G12 verdes em 15.1; limitações documentadas no README.
