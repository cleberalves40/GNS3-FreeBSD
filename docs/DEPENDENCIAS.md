# Matriz de dependências — gns3-server 3.0.6

Snapshot da árvore `/usr/ports` consultada em 15/11/2026, Python default 3.12.
As versões mudam com a árvore; o Makefile expressa mínimos compatíveis, não
pins, e cada dependência continua sendo um port nativo.

## Servidor

Além dos ports Python abaixo, `net/gns3-server` depende de
`net/ubridge>=1.1.1`, helper necessário para switches Ethernet.

| Dependência | Requisito upstream | Port / versão consultada | Tratamento no port |
|---|---|---|---|
| `fastapi` | `==0.128.0` | `www/py-fastapi` 0.142.2_1 | mínimo `>=0.128.0` |
| `uvicorn` | `==0.39.0` | `www/py-uvicorn` 0.54.0 | mínimo `>=0.39.0` |
| `pydantic` | `==2.12.5` | `devel/py-pydantic2` 2.14.3 | mínimo `>=2.12.5` |
| `sqlalchemy` | `==2.0.43` | `databases/py-sqlalchemy20` 2.0.57 | mínimo `>=2.0.43` |
| `alembic` | `==1.15.2` | `databases/py-alembic` 1.18.2 | mínimo `>=1.15.2` |
| `aiosqlite` | `==0.21.0` | `databases/py-aiosqlite` 0.22.1 | mínimo `>=0.21.0` |
| `joserfc` | `==1.6.1` | `security/py-joserfc` 1.8.0 | mínimo `>=1.6.1` |
| `python-multipart` | `==0.0.20` | `www/py-python-multipart` 0.0.33 | mínimo `>=0.0.20` |
| `websockets` | `==15.0.1` | `devel/py-websockets` 17.4 | mínimo `>=15.0.1` |
| `py-cpuinfo` | `>=9.0.0,<10.0` | `sysutils/py-py-cpuinfo2` 10.1.1 | mínimo `>=9.0.0` |
| `platformdirs` | `>=2.4,<3` | `devel/py-platformdirs` 4.14.5 | mínimo `>=2.4.0` |
| `bcrypt` | `==5.0.0` | `security/py-bcrypt` 5.0.0_9 | mínimo `>=5.0.0` |
| `email-validator` | `==2.3.0` | `mail/py-email-validator` 2.3.0 | mínimo `>=2.3.0` |
| `watchdog` | `==6.0.0` | `devel/py-watchdog` 7.1.0 | mínimo `>=6.0.0` |
| `zstandard` | `==0.25.0` | `archivers/py-zstandard` 0.25.0 | mínimo `>=0.25.0` |
| `aiofiles` | `>=25.1.0,<26.0` | `devel/py-aiofiles` 25.1.0 | mínimo `>=25.1.0` |
| `distro` | `>=1.9.0` | `sysutils/py-distro` 1.9.0 | mínimo `>=1.9.0` |
| `psutil` | `>=7.2.1` | `sysutils/py-psutil` 7.2.2_1 | mínimo `>=7.2.1` |
| `Jinja2` | `>=3.1.6,<3.2` | `devel/py-Jinja2` 3.1.6 | mínimo `>=3.1.6` |
| `truststore` | `>=0.10.4` | `security/py-truststore` 0.10.5 | mínimo `>=0.10.4` |
| `aiohttp` | `>=3.13.3,<3.14` | `www/py-aiohttp` 3.14.5 | mínimo `>=3.13.3` |
| `sentry-sdk` | `>=2.50.0,<3` | `devel/py-sentry-sdk` 1.21.1_1 | omitido: opcional upstream; versão insuficiente |
| `greenlet` | `==3.3.1` (Python 3.13+) | `devel/py-greenlet` 3.5.6 | dependência transitiva do SQLAlchemy |
| `async-timeout` | Python <3.11 | — | não necessário (`USES=python:3.11+`) |

## Decisões e validação

- O Makefile declara os ports de runtime diretamente em `RUN_DEPENDS`; não há
  `pip`, wheels vendorizados ou resolução de dependências durante a instalação.
- Os pins exatos publicados no metadata do sdist não são usados pelo `pkg(8)`.
  O port expressa os mínimos conhecidos; a validação de compatibilidade das
  versões mais novas com a suíte upstream continua sendo gate de F4.
- `sentry-sdk` não é dependência do pacote. `gns3server/crash_report.py` trata
  `ImportError` e desativa apenas o envio de crash reports quando Sentry falta.
  A versão disponível no Ports (1.21.1_1) é inferior ao requisito upstream.
- O sdist declara `license-files` no `pyproject.toml`, chave não reconhecida
  pelo `setuptools` 63.1 do Ports. `files/patch-pyproject.toml` remove somente
  essa chave de metadados para permitir o build PEP 517. `setuptools>=61` e
  `wheel` também estão em `BUILD_DEPENDS`, como exigido pelo backend do sdist.
- Starlette 1.10 removeu `FastAPI.add_event_handler`, usado pelo upstream 3.0.6.
  `files/patch-gns3server_api_server.py` migra esses hooks para `lifespan`; o
  serviço passou a iniciar e responder à API em jail 15.1 com as versões do Ports.
- `platformdirs` 4.x, `aiohttp` 3.14.5, `websockets` 17.x e as versões atuais
  dos demais ports precisam da suíte completa em jail limpa; o smoke test local
  comprovou inicialização e `GET /v3/version`, mas não substitui esse gate.

## GUI (F6, opcional)

O GUI tem dependências independentes, incluindo PyQt6/WebEngine e Sentry. Não
faz parte do escopo atual do port do servidor; a Web UI integrada é servida
pelo próprio `gns3-server`.
