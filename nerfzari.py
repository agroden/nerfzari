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

# actions:
# create game - need start date, name, game type
# register for game (before game start)
# unregister from game (before game start)
# personal status (games, IDs, overall K/D ratio, ranking)
# game status - game ID or current (who has been killed, K/D ratio)
# leaderboard
# game history
# kill - ID of participant
# suicide - remove yourself from game

class NerfzariCmd(nerfzari.SSHCmd):
	def do_hello(self, args):
		"""say hello"""
		self.poutput('Hello world')
	
	def do_exit(self, args):
		"""exit the terminal"""
		self.poutput('exiting...')
		return True

	def do_EOF(self, args):
		self.poutput('EOF')
		
	def postloop(self):
		self.poutput('goodbye')


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
	print('0')
	try:
		sock.listen()
		conn, addr = sock.accept()
	except socket.error as err:
		log.error('Listen / accpet failed: {}'.format(str(err)))
		sys.exit(1)
	print('1')
	try:
		trans = paramiko.Transport(conn)
		trans.set_gss_host(socket.getfqdn(''))
		trans.add_server_key(host_key)
		server = nerfzari.SSHServer() # nerfzari.LDAPAuthenticator(ldap_host)
		try:
			trans.start_server(server=server)
			print('server started')
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
		print('2')
		term = NerfzariCmd(chan)
		term.cmdloop('Nerfing is true; everything is permitted')

	except Exception as ex:
		log.error('Unexpected exception occurred: {}'.format(str(ex)))
		raise ex
		sys.exit(1)
	finally:
		trans.close()