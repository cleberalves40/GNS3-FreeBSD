# Convenções dos ports deste repositório

Layout espelhando a árvore oficial:

```
ports/
└── net/
    ├── ubridge/
    │   ├── Makefile
    │   ├── distinfo
    │   ├── pkg-descr
    │   ├── pkg-plist
    │   └── files/
    │       ├── patch-src_nio_tap.c
    │       └── ubridge.rc.in          (se necessário)
    └── gns3-server/
        ├── Makefile
        ├── distinfo
        ├── pkg-descr
        ├── pkg-plist
        └── files/
            ├── gns3server.in
            ├── patch-pyproject.toml
            └── pkg-message.in
```

## Regras

- **Nunca** editar arquivos gerados (`distinfo`, `pkg-plist` autoplist) à mão sem rodar
  `make makesum` / `make makeplist`.
- Patches sempre com nome completo do caminho (`patch-src_nio_tap.c`), nunca `patch-01`.
- `patches/` na raiz guarda o patch em formato `git format-patch`, pronto para PR upstream;
  `ports/.../files/` guarda a versão aplicada pelo Ports.
- `net/ubridge`: `USES=gmake`, `LICENSE=GPLv3`, instalação com `@(root,wheel,4750)`.
- `net/gns3-server`: `USES=python:3.11+`, `USE_PYTHON=pep517 autoplist`, `USERS=gns3`,
  `GROUPS=gns3`, config via `@sample` em `%%PREFIX%%/etc/xdg/GNS3/`.
- `MAINTAINER= cleberalves40`.
- Toda alteração de dependência vem acompanhada da linha correspondente em
  [`docs/DEPENDENCIAS.md`](../docs/DEPENDENCIAS.md).

## Fluxo de validação

```sh
# cópia para a árvore
cp -R ports/net/ubridge        /usr/ports/net/
cp -R ports/net/gns3-server    /usr/ports/net/

cd /usr/ports/net/ubridge && make makesum && portlint -AC && make stage
cd /usr/ports/net/gns3-server && make makesum && portlint -AC && make stage

# validação real
poudriere testport -j 151amd64 net/ubridge
poudriere testport -j 151amd64 net/gns3-server
```
