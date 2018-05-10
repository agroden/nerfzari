"""
"""

import threading
import paramiko
from nerfzari.auth import Authenticator
from abc import ABC, abstractmethod


class AcceptAllAuthenticator(Authenticator):
	def authenticate(self, username, password):
		return True


class Server(paramiko.ServerInterface):
	"""The Nerfzari SSH server"""
	def __init__(self, authenticator=AcceptAllAuthenticator()):
		self.event = threading.Event()
		self._auth = authenticator

	def check_channel_request(self, kind, chanid):
		"""
		The Nerfzari server only accepts session requests.
		"""
		if kind == 'session':
			return paramiko.OPEN_SUCCEEDED
		return paramiko.AUTH_FAILED

	def check_auth_password(self, username, password):
		"""
		The Nerfzari server only accepts password authentication.
		"""
		print(self._auth)
		if self._auth.authenticate(username, password):
			return paramiko.AUTH_SUCCESSFUL
		return paramiko.AUTH_FAILED

	def check_channel_shell_request(self, channel):
		self.event.set()
		return True

	def check_channel_pty_request(self, channel, term, width, height, pxwidth, pxheight, modes):
		return True
