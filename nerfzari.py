"""
"""

import cmd2
import socket
import logging
import sys
import paramiko
import nerfzari

logging.basicConfig(filename='nerfzari.log', level=logging.DEBUG)
log = logging.getLogger(__name__)


DEFAULT_PORT = 4040


class Nerfzari(cmd2.Cmd):
	"""The main command loop of Nerfzari"""
	def do_register(self, args):
		self.poutput('hello world')


if __name__ == '__main__':
	# TODO: read config from a config file
	host_key = paramiko.RSAKey(filename='test/key.pem')
	ldap_host = 'localhost'
	# TODO: make this safer for a daemon
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(('', DEFAULT_PORT))
	except socket.error as err:
		log.error('Bind failed: {}'.format(str(err)))
		sys.exit(1)

	try:
		sock.listen()
		conn, addr = sock.accept()
	except socket.error as err:
		log.error('Listen / accpet failed: {}'.format(str(err)))
		sys.exit(1)

	try:
		trans = paramiko.Transport(conn)
		trans.set_gss_host(socket.getfqdn(''))
		trans.add_server_key(host_key)
		server = nerfzari.server.Server() # nerfzari.auth.LDAPAuthenticator(ldap_host)
		try:
			trans.start_server(server=server)
		except paramiko.SSHException:
			log.error('SSH negotiation failed')
			sys.exit(1)
		chan = trans.accept(20)
		if chan is None:
			log.error('No channel')
			sys.exit(1)
		server.event.wait(10)
		if not server.event.is_set():
			log.error('Client did not ask for shell')
			sys.exit(1)
		chan.send('Nerfing is true; everything is permitted\n')


	except Exception as ex:
		log.error('Unexpected exception occurred: {}'.format(str(ex)))
		sys.exit(1)
	finally:
		trans.close()