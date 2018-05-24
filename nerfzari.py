"""
"""

import socket
import logging
import sys
import paramiko
from nerfzari import ConfigStore, Authenticator, SSHServer, SSHCmd


logging.basicConfig(filename='nerfzari.log', level=logging.DEBUG)
log = logging.getLogger(__name__)


NERFZARI_CFG_PATH = 'nerfzari.json'
NERFZARI_CFG_SCHEMA = {
	'$schema': 'http://json-schema.org/draft-06/schema#',
	'description': 'Data needed by the Nerfzari server',
	'type': 'object',
	'default': {},
	'required': ['rsa_key'],
	'properties': {
		'listen_port': {
			'type': 'integer',
			'default': 4040
		},
		'rsa_key': { 'type': 'string' },
		'auth_cls': {
			'type': 'string',
			'default': 'AcceptAll'
		},
		'module_dir': {
			'type': 'string',
			'default':	'modules'
		}
	}
}
ConfigStore.register(
	NERFZARI_CFG_PATH,
	NERFZARI_CFG_SCHEMA
)


class NerfzariCmd(SSHCmd):
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
	prompt = '>'
	def do_hello(self, args):
		"""say hello"""
		out = 'world'
		if args:
			out = args
		self.poutput('Hello {}'.format(out))

	greetings = ['Alice', 'Adam', 'Bob', 'Barbara']
	def complete_hello(self, text, line, begidx, endidx):
		if not text:
			ret = self.greetings[:]
		else:
			ret = [x for x in self.greetings if x.startswith(text)]
		return ret
	
	def do_input(self, args):
		recv = self.terminput('input>', False)
		self.poutput('You entered: {}'.format(recv))

	def do_exit(self, args):
		"""exit the terminal"""
		self.poutput('exiting...')
		return True
		
	def postloop(self):
		self.poutput('goodbye')


if __name__ == '__main__':
	ConfigStore.load_all()
	cfg = ConfigStore.get(NERFZARI_CFG_PATH)
	addr = ('', cfg['listen_port'])
	key_path = cfg['rsa_key']
	auth_cls = Authenticator.get(cfg['auth_cls'])
	try:
		with SSHServer(addr, key_path, NerfzariCmd, auth_cls) as server:
			server.serve_forever()
	except KeyboardInterrupt:
		server.shutdown()

	'''
	# TODO: make this safer for a daemon
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(('', cfg['listen_port']))
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
		auth = Authenticator.make(cfg['auth_cls'])
		server = SSHServer(auth)
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
		term.cmdloop('nerfing is true; everything is permitted')

	except Exception as ex:
		log.error('Unexpected exception occurred: {}'.format(str(ex)))
		sys.exit(1)
	finally:
		trans.close()
'''