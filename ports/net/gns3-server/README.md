# net/gns3-server 3.0.6 (Fase 3 — implementação inicial)

Port inicial do servidor GNS3 3.x. Inclui:

- build PEP 517 do sdist do PyPI com dependências nativas `py-*` do Ports;
- `USERS=gns3` / `GROUPS=gns3`, dados em `/var/db/gns3` e logs em `/var/log/gns3`;
- `files/gns3server.in` (rc.d), `files/pkg-message.in` e configuração de exemplo;
- configuração em `${PREFIX}/etc/gns3`, passada explicitamente ao servidor por `--config`;
- Sentry omitido: upstream já o trata como opcional e o Ports tem 1.x, abaixo do mínimo 2.50.

Como é uma aplicação, o pacote não recebe prefixo de biblioteca/flavor Python:
o nome instalável é `gns3-server` (`pkg install gns3-server`), usando a versão
Python default do Ports. As dependências mantêm o prefixo do flavor Python.

O `pyproject.toml` do sdist declara `license-files`, que não é aceito pelo
`setuptools` 63 do Ports; `files/patch-pyproject.toml` remove apenas essa chave
de empacotamento. Dependências de runtime são declaradas no Makefile usando os
ports existentes, sem instalar via `pip`.

O pacote não inclui recursos de Docker: Docker não é suportado no FreeBSD e os
scripts de container do upstream têm shebangs de Linux. Limitações e o mapa de
dependências estão em [`docs/DEPENDENCIAS.md`](../../../docs/DEPENDENCIAS.md) e
[`docs/TESTES.md`](../../../docs/TESTES.md).
