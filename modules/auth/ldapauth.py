"""
"""

import ldap3
from nerfzari import Authenticator
from nerfzari import ConfigStore, Configurable

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
		'sasl_mechanism': {
			'enum': [
				'external',
				'digest-md5',
				'gssapi'
			]
		}
	}
}
ConfigStore.register(
	LDAP_CFG_PATH,
	LDAP_CFG_SCHEMA
)

class LDAPAuthenticator(Authenticator, Configurable):
	"""An authenticator that uses LDAP to confirm credentials."""
	auth_methods = {
		'anonymous': ldap3.ANONYMOUS,
		'simple': ldap3.SIMPLE,
		'sasl': ldap3.SASL,
		'ntlm': ldap3.NTLM
	}
	sasl_mech = {
		'external': ldap3.EXTERNAL,
		'digest-md5': ldap3.DIGEST_MD5,
		'gssapi': ldap3.GSSAPI
	}
	def __init__(self, host, port=389, method='simple', sasl_mech=None):
		self._ldap_server = ldap3.Server(host, port, get_info=ldap3.ALL)
		self._err_msg = None
		self._auth_method = self.auth_methods[method]
		self._sasl_mech = sasl_mech

	@classmethod
	def from_cfg(cls):
		cfg = ConfigStore.get(LDAP_CFG_PATH)
		mech = None
		if 'sasl_mechanism' in cfg:
			mech = cfg['sasl_mechanism']
		return LDAPAuthenticator(
			cfg['host'],
			cfg['port'],
			cfg['auth_method'],
			mech
		)

	@property
	def err_msg(self):
		return self._err_msg

	def authenticate(self, username, password):
		ret = False
		if self._auth_method == ldap3.SASL and self._sasl_mech is not None:
			ldap_conn = ldap3.Connection(
				self._ldap_server,
				authentication=self._auth_method,
				user=username, password=password,
				check_names=True,
				lazy=False,
				client_strategy=ldap3.SYNC,
				raise_exceptions=False,
				sasl_mechanism=self._sasl_mech
			)
		else:
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

# register this as an authenticator
Authenticator.register(LDAPAuthenticator)

