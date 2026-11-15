PORTNAME=	ubridge
DISTVERSION=	1.1.1
CATEGORIES=	net
MASTER_SITES=	GH

MAINTAINER=	cleber@bsd.com.br
COMMENT=	User-space bridge used by GNS3 to interconnect emulated devices
WWW=		https://github.com/GNS3/ubridge

LICENSE=	GPLv3
LICENSE_FILE=	${WRKSRC}/LICENSE

USES=		gmake

USE_GITHUB=	yes
GH_ACCOUNT=	GNS3
GH_PROJECT=	ubridge
GH_TAGNAME=	v${DISTVERSION}

do-install:
	${INSTALL_PROGRAM} ${WRKSRC}/${PORTNAME} \
		${STAGEDIR}${PREFIX}/bin/${PORTNAME}

.include <bsd.port.mk>
