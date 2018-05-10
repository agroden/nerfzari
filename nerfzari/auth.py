"""
"""

import ldap3
from abc import ABC, abstractmethod


class Authenticator(ABC):
	"""Base class for all authenticators."""
	@abstractmethod
	def authenticate(self, username, password):
		"""
		:returns: True for authentication success or False for authentication failure.
		"""
		raise NotImplementedError()


class LDAPAuthenticator(Authenticator):
	"""An authenticator that uses LDAP to confirm credentials."""
	def __init__(self, host, port=389): # default port of LDAP is 389
		self._ldap_server = ldap3.Server(host, port, get_info=ldap3.ALL)
		self._err_msg = None

	@property
	def err_msg(self):
		return self._err_msg

	def authenticate(self, username, password):
		ret = False
		ldap_conn = ldap3.Connection(self._ldap_server,
			authentication=ldap3.SIMPLE,
			user=username, password=password,
			check_names=True,
			lazy=False,
			client_strategy=ldap3.SYNC,
			raise_exceptions=False)
		ldap_conn.open()
		ldap_conn.bind()
		if ldap_conn.result['result'] == 0: # 0: success, 49: invalidCredentials
			ret = True
			self._err_msg = None
		else:
			self.err_msg = ldap_conn.result['description']
		ldap_conn.unbind()
		return ret
