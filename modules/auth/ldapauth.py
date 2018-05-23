"""
"""

import ldap3
from nerfzari import Authenticator
from nerfzari import ConfigStore

LDAP_CFG_PATH = 'ldap.json'
LDAP_CFG_SCHEMA = {
	"$schema": "http://json-schema.org/schema#",
	'description': 'Data needed by the LDAP authenticator',
	'type': 'object',
	'required': ['host'],
	'properties': {
		'host': { 'type': 'string' },
		'port': {
			'type': 'integer',
			'default': 389
		},
		'auth_method': {
			'enum': [
				'anonymous',
				'simple',
				'sasl',
				'ntlm'
			],
			'default': 'simple'
		},
	}
}
ConfigStore.register(
	LDAP_CFG_PATH,
	LDAP_CFG_SCHEMA
)

class LDAPAuthenticator(Authenticator):
	"""An authenticator that uses LDAP to confirm credentials."""
	auth_methods = {
		'anonymous': ldap3.ANONYMOUS,
		'simple': ldap3.SIMPLE,
		'sasl': ldap3.SASL,
		'ntlm': ldap3.NTLM
	}
	def __init__(self, host, port=389, method='simple'): # default port of LDAP is 389
		self._ldap_server = ldap3.Server(host, port, get_info=ldap3.ALL)
		self._err_msg = None
		self._auth_method = self.auth_methods[method]

	@staticmethod
	def from_cfg():
		cfg = ConfigStore.get(LDAP_CFG_PATH)
		return LDAPAuthenticator(cfg['host'], cfg['port'], cfg['auth_method'])

	@property
	def err_msg(self):
		return self._err_msg

	def authenticate(self, username, password):
		ret = False
		ldap_conn = ldap3.Connection(
			self._ldap_server,
			authentication=self._auth_method,
			user=username, password=password,
			check_names=True,
			lazy=False,
			client_strategy=ldap3.SYNC,
			raise_exceptions=False
		)
		ldap_conn.open()
		ldap_conn.bind()
		if ldap_conn.result['result'] == 0: # 0: success, 49: invalidCredentials
			ret = True
			self._err_msg = None
		else:
			self.err_msg = ldap_conn.result['description']
		ldap_conn.unbind()
		return ret
