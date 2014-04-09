""":mod:`geofront.team` --- Team authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import collections.abc

from .identity import Identity
from .util import typed

__all__ = 'AuthenticationError', 'Team'


class Team:
    """Backend interface for team membership authentication.

    Authorization process consists of three steps (and therefore every
    backend subclass has to implement these three methods):

    1. :meth:`request_authentication()` makes the url to interact with
       the owner of the identity to authenticate.  I.e. the url to login
       web page of the backend service.
    2. :meth:`authenticate()` finalize authentication of the identity,
       and then returns :class:`~.identity.Identity`.
    3. :meth:`authorize()` tests the given :class:`~.identity.Identity`
       belongs to the team.  It might be a redundant step for several
       backends, but is a necessary step for some backends that distinguish
       identity authentication between team membership authorization.
       For example, Any Gmail users can authenticate they own their Gmail
       account, but only particular users can authenticate their account
       belongs to the configured Google Apps organization.

    """

    @typed
    def request_authentication(self,
                               auth_nonce: str,
                               redirect_url: str) -> str:
        """First step of authentication process, to prepare the "sign in"
        interaction with the owner.  It typically returns a url to
        the login web page.

        :param auth_nonce: a random string to guarantee it's a part of
                           the same process to following :meth:`authenticate()`
                           call which is the second step
        :type auth_nonce: :class:`str`
        :param redirect_url: a url that owner's browser has to redirect to
                             after the "sign in" interaction finishes
        :type redirect_url: :class:`str`
        :return: a url to the web page to interact with the owner
                 in their browser
        :rtype: :class:`str`

        """
        raise NotImplementedError('request_authentication() method has to '
                                  'be implemented')

    @typed
    def authenticate(self,
                     auth_nonce: str,
                     requested_redirect_url: str,
                     wsgi_environ: collections.abc.Mapping) -> Identity:
        """Second step of authentication process, to create a verification
        token for the identity.  The token is used by :meth:`authorize()`
        method, and the key store as well (if available).

        :param auth_nonce: a random string to guarantee it's a part of
                           the same process to :meth:`request_authentication()`
                           call followed by this which is the first step
        :type auth_nonce: :class:`str`
        :param requested_redirect_url: a url that was passed to
                                       :meth:`request_authentication()`'s
                                       ``redirect_url`` parameter
        :type requested_redirect_url: :class:`str`
        :param wsgi_environ: forwarded wsgi environ dictionary
        :type wsgi_environ: :class:`collections.abc.Mapping`
        :return: an identity which contains a verification token
        :rtype: :class:`~.identity.Identity`
        :raise geofront.team.AuthenticationError:
            when something goes wrong e.g. network errors,
            the user failed to verify their ownership

        """
        raise NotImplementedError('authenticate() method has to '
                                  'be implemented')

    @typed
    def authorize(self, identity: Identity) -> bool:
        """The last step of authentication process.
        Test whether the given ``identity`` belongs to the team.

        Note that it can be called every time the owner communicates with
        Geofront server, out of authentication process.

        :param identity: the identity to authorize
        :type identity: :class:`~.identity.Identity`
        :return: :const:`True` only if the ``identity`` is a member of the team
        :rtype: :class:`bool`

        """
        raise NotImplementedError('authorize() method has to be implemented')


class AuthenticationError(Exception):
    """Authentication exception which rise when the authentication process
    has trouble including network problems.

    .. todo:: Exception hierarchy is needed.

    """
