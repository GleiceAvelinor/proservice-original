"""
============================================================
CUSTOM EMAIL BACKEND — Suporte a SSL/TLS no Windows / Gmail
============================================================
Evita falhas de verificação de certificado SSL (SSLCertVerificationError)
em ambientes locais no Windows ao conectar ao SMTP do Gmail.
"""

import ssl
from django.core.mail.backends.smtp import EmailBackend


class SSLEmailBackend(EmailBackend):
    """
    Subclasse do EmailBackend padrão do Django.
    Aplica um SSLContext permissivo para evitar falhas de certificado no Windows.
    """

    @property
    def ssl_context(self):
        if getattr(self, "_ssl_context", None) is None:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            self._ssl_context = ctx
        return self._ssl_context

    @ssl_context.setter
    def ssl_context(self, value):
        self._ssl_context = value
