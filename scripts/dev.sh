#!/bin/sh
#
# Valida os ports deste repositorio contra uma arvore de Ports do FreeBSD,
# sem precisar de root e sem copiar nada para /usr/ports.
#
# Uso:
#   ./scripts/dev.sh ubridge          # makesum + portlint + stage + check-plist
#   ./scripts/dev.sh all              # todos os ports de ports/net
#   ./scripts/dev.sh -c ubridge       # limpa o work/ antes
#
# Variaveis:
#   PORTS_TREE  arvore de Ports (default: /usr/ports)
#   DISTDIR     cache de distfiles (default: ~/.cache/gns3-freebsd/distfiles)
#
set -eu

PORTS_TREE=${PORTS_TREE:-/usr/ports}
DISTDIR=${DISTDIR:-${HOME}/.cache/gns3-freebsd/distfiles}
CLEAN=0
REPO_DIR=$(cd "$(dirname "$0")/.." && pwd)

# O PATH do ambiente de desenvolvimento pode conter diretorios com espacos
# (ex.: "Code - OSS"), o que quebra o env(1) usado pelo bsd.port.mk.
SAFE_PATH=/sbin:/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin

if [ ! -d "${PORTS_TREE}/Mk" ]; then
	echo "erro: arvore de Ports nao encontrada em ${PORTS_TREE}" >&2
	echo "      defina PORTS_TREE ou instale/baixe a arvore" >&2
	exit 1
fi

if [ "${1:-}" = "-c" ]; then
	CLEAN=1
	shift
fi

if [ $# -eq 0 ]; then
	set -- ubridge
fi

if [ "$1" = "all" ]; then
	set -- $(cd "${REPO_DIR}/ports/net" && ls -d */ 2>/dev/null | tr -d '/')
fi

mkdir -p "${DISTDIR}"

for port in "$@"; do
	dir="${REPO_DIR}/ports/net/${port}"
	if [ ! -f "${dir}/Makefile" ]; then
		echo "==> ${port}: sem Makefile, ignorando"
		continue
	fi

	echo
	echo "==================== ${port} ===================="
	cd "${dir}"

	[ "${CLEAN}" -eq 1 ] && env PATH="${SAFE_PATH}" make clean >/dev/null 2>&1 || true

	env PATH="${SAFE_PATH}" PORTSDIR="${PORTS_TREE}" DISTDIR="${DISTDIR}" \
		make makesum
	env PATH="${SAFE_PATH}" PORTSDIR="${PORTS_TREE}" DISTDIR="${DISTDIR}" \
		make stage
	env PATH="${SAFE_PATH}" PORTSDIR="${PORTS_TREE}" DISTDIR="${DISTDIR}" \
		make check-plist
	portlint -AC || true
done

echo
echo "Concluido. Limpe com: make -C ports/net/<port> clean"
