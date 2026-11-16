# GNS3-FreeBSD

Ports nativos do FreeBSD para o **[GNS3](https://www.gns3.com/) 3.x**, sem `pip`, `pipx` ou
ambientes virtuais: tudo instalado e atualizado pelo **pkg(8)**, com ciclo de vida de Ports.

O objetivo é que um `pkg install gns3-server` entregue um servidor GNS3 funcional no FreeBSD,
com **uBridge** compilado nativamente e registrado como helper de rede do aplicativo.

## Estado

| Fase | Entrega | Estado |
|---|---|---|
| F0 | Reconhecimento do ambiente e do upstream | ✅ concluída (15/11/2026) |
| F1 | Repositório, layout de Ports e CI | ✅ concluída (15/11/2026) |
| F2 | `net/ubridge` 1.1.1 (helper de rede, setuid) | ✅ concluída (15/11/2026) — valida e empacota |
| F3 | `net/gns3-server` 3.0.6 | ✅ `testport`, serviço e API passaram em 15.1; suíte upstream pendente |
| F4 | QA: poudriere, plist, testes de fumaça | 🔄 15.1 passou; ubridge passou em 14.3 EOL; server 14.3 pausado para reinicialização |
| F5 | Upstream + submissão ao FreeBSD (Bugzilla) | ⏳ planejada |
| F6 | `net/gns3-gui` (PyQt6) — opcional | ⏳ planejada |

Roadmap completo: [ROADMAP.md](ROADMAP.md).

## Problema que este repositório resolve

O GNS3 3.0.6 hoje funciona nesta máquina apenas porque foi instalado com `pip --user`
(`gns3server` e `gns3-gui` em `~/.local`) e o `ubridge` foi compilado à mão e instalado como
`/usr/local/bin/ubridge` **setuid root, sem registro no banco do pkg**. Isso cria três
problemas: atualização manual, mistura de dependências Python do sistema com as do usuário e
um binário privilegiado invisível para auditoria de pacotes.

## Escopo

**Dentro:** `net/ubridge`, `net/gns3-server`, integração com `dynamips-community` e `qemu`
(já presentes no Ports).

**Fora:** nós Docker, VirtualBox, IOU/IOL (binários Linux), NAT cloud via libvirt, data plane
de kernel do uBridge (veth/VXLAN/tc/netem) e a GNS3 VM.

No FreeBSD, QEMU executa em TCG (emulação por software), sem aceleração KVM; VPCS ainda não tem
port. O helper uBridge cobre o relay em user space (TAP/UDP/UNIX/Ethernet), não os recursos de
kernel exclusivos de Linux.

## Estrutura do repositório

```
GNS3-FreeBSD/
├── README.md
├── ROADMAP.md
├── LICENSE
├── docs/
│   ├── ESTADO-ATUAL.md      reconhecimento da máquina e do upstream
│   ├── DEPENDENCIAS.md      matriz pin do upstream × versão no Ports
│   └── TESTES.md            plano de testes e critérios de aceite
├── ports/
│   ├── README.md            convenções dos ports deste repositório
│   ├── net/ubridge/         port do helper de rede (F2)
│   └── net/gns3-server/     port do servidor (F3)
├── patches/                 patches mantidos por nós (uBridge/FreeBSD)
└── scripts/                 ambiente de desenvolvimento e poudriere
```

## Licença

O conteúdo deste repositório (Makefiles, patches, documentação) é distribuído sob
**BSD-2-Clause**. Os programas portados mantêm suas licenças originais — GNS3 server, GUI e
uBridge são **GPLv3** — e os patches aplicados a eles herdam a GPLv3.
