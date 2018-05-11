"""
"""

import cmd2
import threading
import select
import io
import tty
import paramiko
import socket
from nerfzari.auth import Authenticator
from abc import ABC, abstractmethod


class AcceptAllAuthenticator(Authenticator):
	def authenticate(self, username, password):
		return True


class SSHServer(paramiko.ServerInterface):
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


def cmd_shell(chan, cmd_cls):
	strin = io.StringIO()
	strout = io.StringIO()
	cmd_cls(stdin=strin, stdout=strout)
	try:
		tty.setraw(strin.fileno())
		tty.setcbreak(strin.fileno())
		chan.settimeout(0.0)
		while True:
			r, w, e = select.select([chan, strin], [], [])
			if chan in r:
				try:
					x = chan.recv(1024)
					if len(x) == 0:
						strout.write('\r\n*** EOF\r\n')
						break
					strout.write(x)
					strout.flush()
				except socket.timeout:
					pass
			if strin in r:
				x = strin.read(1)
				if len(x) == 0:
					break
				chan.send(x)
	finally:
		strin.close()
		strout.close()
