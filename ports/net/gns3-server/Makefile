PORTNAME=	gns3-server
DISTVERSION=	3.0.6
CATEGORIES=	net
MASTER_SITES=	PYPI
DISTNAME=	gns3_server-${DISTVERSION}

MAINTAINER=	cleber@bsd.com.br
COMMENT=	GNS3 network simulation server
WWW=		https://github.com/GNS3/gns3-server

LICENSE=	GPLv3
LICENSE_FILE=	${WRKSRC}/LICENSE

BUILD_DEPENDS=	${PYTHON_PKGNAMEPREFIX}setuptools>=61:devel/py-setuptools@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}wheel>=0:devel/py-wheel@${PY_FLAVOR}

RUN_DEPENDS=	${PYTHON_PKGNAMEPREFIX}aiofiles>=25.1.0:devel/py-aiofiles@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}aiohttp>=3.13.3:www/py-aiohttp@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}aiosqlite>=0.21.0:databases/py-aiosqlite@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}alembic>=1.15.2:databases/py-alembic@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}bcrypt>=5.0.0:security/py-bcrypt@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}distro>=1.9.0:sysutils/py-distro@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}email-validator>=2.3.0:mail/py-email-validator@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}fastapi>=0.128.0:www/py-fastapi@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}Jinja2>=3.1.6:devel/py-Jinja2@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}joserfc>=1.6.1:security/py-joserfc@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}platformdirs>=2.4.0:devel/py-platformdirs@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}psutil>=7.2.1:sysutils/py-psutil@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}py-cpuinfo2>=9.0.0:sysutils/py-py-cpuinfo2@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}pydantic2>=2.12.5:devel/py-pydantic2@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}python-multipart>=0.0.20:www/py-python-multipart@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}sqlalchemy20>=2.0.43:databases/py-sqlalchemy20@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}truststore>=0.10.4:security/py-truststore@${PY_FLAVOR} \
		ubridge>=1.1.1:net/ubridge \
		${PYTHON_PKGNAMEPREFIX}uvicorn>=0.39.0:www/py-uvicorn@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}watchdog>=6.0.0:devel/py-watchdog@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}websockets>=15.0.1:devel/py-websockets@${PY_FLAVOR} \
		${PYTHON_PKGNAMEPREFIX}zstandard>=0.25.0:archivers/py-zstandard@${PY_FLAVOR}

USES=		python:3.11+
USE_PYTHON=	autoplist noflavors pep517

# Upstream probes /etc/gns3/gns3_server.conf; keep the same layout below
# PREFIX so the rc.d script can pass it explicitly with --config.
ETCDIR=		${PREFIX}/etc/gns3

USERS=		gns3
GROUPS=		gns3

NO_ARCH=	yes

USE_RC_SUBR=	gns3server

SUB_FILES=	pkg-message
SUB_LIST+=	PYTHON_CMD=${PYTHON_CMD} VARBASE=/var

post-install:
	@${MKDIR} ${STAGEDIR}${ETCDIR}
	@${MKDIR} ${STAGEDIR}/var/db/gns3 ${STAGEDIR}/var/log/gns3
	${INSTALL_DATA} ${FILESDIR}/gns3_server.conf.sample \
		${STAGEDIR}${ETCDIR}/gns3_server.conf.sample

.include <bsd.port.mk>
