#!/bin/sh
#
# Registra os UIDs/GIDs usados pelos ports deste repositorio na arvore de
# Ports indicada. O framework (bsd.port.mk) exige que usuario e grupo
# estejam em UIDs/GIDs da arvore, mesmo antes do commit oficial.
#
# Uso:
#   doas ./scripts/register-ids.sh /usr/ports
#   doas ./scripts/register-ids.sh /poudriere/ports/gns3
#
set -eu

PORTS_TREE=${1:-/usr/ports}
HERE=$(cd "$(dirname "$0")" && pwd)

if [ ! -f "${PORTS_TREE}/UIDs" ] || [ ! -f "${PORTS_TREE}/GIDs" ]; then
	echo "erro: ${PORTS_TREE} nao parece ser uma arvore de Ports" >&2
	exit 1
fi

for kind in UIDs GIDs; do
	src="${HERE}/port-ids/${kind}"
	dst="${PORTS_TREE}/${kind}"
	while IFS= read -r line; do
		[ -n "${line}" ] || continue
		name=$(echo "${line}" | cut -d: -f1)
		id=$(echo "${line}" | cut -d: -f3)
		other=$(awk -F: -v id="${id}" -v name="${name}" \
			'$3 == id && $1 != name { print $1; exit }' "${dst}")
		if [ -n "${other}" ]; then
			echo "erro: ${kind}: ID ${id} ja esta em uso por ${other}" >&2
			exit 1
		fi
		if grep -q "^${name}:" "${dst}"; then
			current_id=$(awk -F: -v name="${name}" '$1 == name { print $3; exit }' "${dst}")
			if [ "${current_id}" != "${id}" ]; then
				echo "erro: ${kind}: ${name} ja existe com ID ${current_id}, esperado ${id}" >&2
				exit 1
			fi
			echo "${kind}: ${name} ja registrado"
		else
			tmp=$(mktemp "${dst}.XXXXXX")
			cp -p "${dst}" "${tmp}"
			awk -F: -v id="${id}" -v entry="${line}" '
				!inserted && $3 ~ /^[0-9]+$/ && $3 > id {
					print entry
					inserted = 1
				}
				{ print }
				END {
					if (!inserted)
						print entry
				}
			' "${dst}" > "${tmp}"
			mv "${tmp}" "${dst}"
			echo "${kind}: ${name} adicionado"
		fi
	done < "${src}"
done
