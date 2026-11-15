# Matriz de dependências — gns3-server 3.0.6

Comparação entre o que o pacote declara (`requires_dist` do PyPI) e o que existe hoje no Ports
desta máquina (Python 3.12). Serve de base para os patches de metadados da F3.

## Servidor

| Dependência | Exigência do 3.0.6 | Ports (py312) | Situação |
|---|---|---|---|
| `fastapi` | `==0.128.0` | 0.142.2_1 | patch de pin |
| `uvicorn` | `==0.39.0` | 0.54.0 | patch de pin |
| `pydantic` | `==2.12.5` | 2.14.2 (`py312-pydantic2`) | patch de pin |
| `sqlalchemy` | `==2.0.43` | 2.0.55 (`py312-sqlalchemy20`) | patch de pin |
| `alembic` | `==1.15.2` | 1.18.2 | patch de pin |
| `aiosqlite` | `==0.21.0` | 0.22.1 | patch de pin |
| `joserfc` | `==1.6.1` | 1.7.7 | patch de pin |
| `python-multipart` | `==0.0.20` | 0.0.32 | patch de pin |
| `websockets` | `==15.0.1` | 17.4 | patch de pin |
| `py-cpuinfo` | `>=9.0.0,<10.0` | 10.1.1 (`py312-py-cpuinfo2`) | validar e relaxar |
| `platformdirs` | `>=2.4,<3` | 4.14.3 | validar API e relaxar |
| `bcrypt` | `==5.0.0` | 5.0.0_9 | ok |
| `email-validator` | `==2.3.0` | 2.3.0 | ok |
| `watchdog` | `==6.0.0` | 6.0.0 | ok |
| `zstandard` | `==0.25.0` | 0.25.0 | ok |
| `aiofiles` | `>=25.1.0,<26.0` | 25.1.0 | ok |
| `distro` | `>=1.9.0` | 1.9.0 | ok |
| `psutil` | `>=7.2.1` | 7.2.2_1 | ok |
| `Jinja2` | `>=3.1.6,<3.2` | 3.1.6 | ok |
| `truststore` | `>=0.10.4` | 0.10.5 | ok |
| `aiohttp` | `>=3.13.3,<3.14` | **3.14.5** | **conflito** |
| `sentry-sdk` | `>=2.50.0,<3` | **1.21.1_1** | **bloqueador** |
| `greenlet` | `==3.3.1` (só Python 3.13) | 3.5.6 | irrelevante em 3.12 |
| `async-timeout` | `>=5.0.1,<5.1` (só Python <3.11) | — | irrelevante em 3.12 |

## GUI (F6, opcional)

| Dependência | Exigência | Ports | Situação |
|---|---|---|---|
| `PyQt6` | import direto no código | `devel/py-qt6-pyqt` 6.11.0 | ok |
| `sentry-sdk` | `>=2.50,<3` | 1.21.1_1 | mesmo bloqueador do servidor |
| `jsonschema` | `>=4.25.1,<4.26` | verificar versão atual | provável patch |
| `psutil`, `distro`, `truststore` | — | ok | ok |

## Bloqueadores e plano

### 1. `sentry-sdk` 2.x

O Ports está em 1.21.1; o GNS3 3.x exige 2.50+. Opções, em ordem de preferência:

1. **Tornar o Sentry opcional** no gns3-server (patch pequeno, telemetria não é essencial);
2. atualizar `devel/py-sentry-sdk` para a série 2.x, avaliando dependentes com
   `poudriere bulk -a` nos ports que o consomem;
3. carregar `py-sentry-sdk` 2.x como port versionado (último recurso, evita o conflito).

### 2. `aiohttp` 3.14.5 × `<3.14`

O pin do GNS3 é conservador e provavelmente reflete uma incompatibilidade histórica de API.
Plano: build com 3.14.5, rodar a suíte upstream e exercitar a API REST; se estável, relaxar o
pin no patch.

### 3. `platformdirs` 4.x × `<3`

A API usada pelo server é mínima (diretórios de config/dados). Validar com teste de inicialização
e de leitura de config; relaxar se não houver regressão. Se houver, manter o pin e adicionar
`py-platformdirs` mais antigo como dependência específica.

## Regra geral adotada

Nenhum wheel é vendorizado. Quando a versão do Ports for mais nova, o patch de metadados relaxa
o pin; a suíte de testes do upstream é o gate. Quando a versão do Ports for **mais antiga que o
mínimo exigido** (caso do Sentry), a correção vai para o Ports ou o recurso é tornado opcional.
