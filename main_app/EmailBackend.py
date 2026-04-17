from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.mail.backends.smtp import EmailBackend as DjangoSMTPEmailBackend
from django.core.mail.utils import DNS_NAME


class SMTPCompatBackend(DjangoSMTPEmailBackend):
    """SMTP backend compatible with Python versions that reject keyfile/certfile in starttls."""

    def open(self):
        """Ensure STARTTLS is called without deprecated keyfile/certfile args."""
        if self.connection:
            return False

        # Django versions differ: some expose `ssl_context`, some do not.
        ssl_context = getattr(self, 'ssl_context', None)

        connection_params = {'local_hostname': DNS_NAME.get_fqdn()}
        if self.timeout is not None:
            connection_params['timeout'] = self.timeout
        if self.use_ssl and ssl_context is not None:
            connection_params['context'] = ssl_context

        try:
            self.connection = self.connection_class(
                self.host,
                self.port,
                **connection_params,
            )

            if not self.use_ssl and self.use_tls:
                # Do not pass keyfile/certfile; newer Python removes these params.
                if ssl_context is not None:
                    self.connection.starttls(context=ssl_context)
                else:
                    self.connection.starttls()

            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except OSError:
            if not self.fail_silently:
                raise


class EmailBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
