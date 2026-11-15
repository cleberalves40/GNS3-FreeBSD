# net/gns3-server (Fase 3 — ainda não iniciado)

Este diretório receberá o port do servidor GNS3 3.x. O `Makefile` será criado
na F3, junto com:

- `USE_PYTHON=pep517 autoplist` e `USES=python:3.11+`;
- patch de metadados para relaxar os pins para as versões do Ports;
- `USERS=gns3` / `GROUPS=gns3`;
- `files/gns3server.in` (rc.d) e `files/pkg-message.in`;
- `@sample` em `%%PREFIX%%/etc/xdg/GNS3/gns3_server.conf`.

O mapeamento de dependências já está levantado em
[`docs/DEPENDENCIAS.md`](../../../docs/DEPENDENCIAS.md) e o plano de testes
em [`docs/TESTES.md`](../../../docs/TESTES.md).

Enquanto o port não existe, a instalação de referência continua sendo a do
`pip --user` (gns3-server 3.0.6), documentada em
[`docs/ESTADO-ATUAL.md`](../../../docs/ESTADO-ATUAL.md).
