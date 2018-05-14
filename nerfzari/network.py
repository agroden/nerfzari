"""
"""

import cmd
import paramiko
import threading
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


class AcceptAllAuthenticator(Authenticator):
	"""Simple authenticator that accepts anything"""
	def authenticate(self, username, password):
		"""
		:returns: Always returns True.
		"""
		return True


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
		if self._auth.authenticate(username, password):
			return paramiko.AUTH_SUCCESSFUL
		return paramiko.AUTH_FAILED

	def check_channel_shell_request(self, channel):
		self.event.set()
		return True

	def check_channel_pty_request(self, channel, term, width, height, pxwidth, pxheight, modes):
		return True


class SSHCmd(cmd.Cmd):
	"""The command handler of Nerfzari."""
	use_rawinput = False # never use raw input
	hidden_cmds = ['do_EOF',]
	max_history = 1024
	def __init__(self, chan):
		super().__init__()
		self._chan = chan
		self._cmd_history = []

	def poutput(self, msg, end='\r\n'):
		"""Tweaked poutput to use Paramiko channel."""
		if msg is not None:
			msg_str = '{}'.format(msg)
			self._chan.send(msg_str)
			if not msg_str.endswith(end):
				self._chan.send(end)

	def _cmdloop(self, prompt):
		"""Major modification was required to emulate vt100 stuff"""
		def clear_prompt(curr_line, curr_pos):
			self._chan.send('\010'*pos)
			self._chan.send('\000'*len(curr_line))
			self._chan.send('\010'*len(curr_line))

		def add_line_to_history(curr_line):
			self._cmd_history.append(curr_line)
			if len(self._cmd_history) > self.max_history:
				self._cmd_history.pop(0)

		self.poutput(prompt, end='')
		line = []
		pos = 0
		history_idx = len(self._cmd_history)
		last_line = None
		tab_ctr = 0
		tab_line = []
		while True:
			data = self._chan.recv(12)
			print(data)
			data = data.decode('utf-8')
			if tab_ctr > 0 and data != '\t':
				tab_ctr = 0
				tab_line = ''
			if data.startswith('\x1b'):
				if data == '\x1b[A': # up arrow key
					#print('up')
					if history_idx == len(self._cmd_history):
						last_line = line
					if history_idx > 0:
						history_idx -= 1
						#print('history_idx: {}, history len: {}'.format(history_idx, len(self._cmd_history)))
						clear_prompt(line, pos)
						line = self._cmd_history[history_idx]
						self._chan.send(''.join(line).strip())
						pos = len(line)

				elif data == '\x1b[B': # down arrow key
					#print('down')
					if history_idx < len(self._cmd_history):
						history_idx += 1
						clear_prompt(line, pos)
						#print('history_idx: {}, history len: {}'.format(history_idx, len(self._cmd_history)))
						if history_idx == len(self._cmd_history):
							line = last_line
						else:
							line = self._cmd_history[history_idx]
						self._chan.send(''.join(line).strip())
						pos = len(line)

				elif data == '\x1b[C': # right arrow key
					#print('right')
					if pos < len(line):
						#print('pos: {}, line len: {}'.format(pos, len(line)))
						self._chan.send(data)
						pos += 1
				elif data == '\x1b[D': # left arrow key
					#print('left')
					if pos > 0:
						#print('pos: {}, line len: {}'.format(pos, len(line)))
						self._chan.send(data)
						pos -= 1
				elif data == '\x1b[3~': # delete key
					#print('delete')
					if len(line) > 0:
						if pos > 0 and pos < len(line):
							#print('delete at {}'.format(pos))
							l = line[:pos]
							r = line[pos+1:]
							#print('left: {}, right: {}'.format(''.join(l), ''.join(r)))
							for x in r:
								#print('sending: {}'.format(x))
								self._chan.send(x)
							self._chan.send('\000')
							self._chan.send('\010'*(len(line)-pos))
							line = l + r
							#print('line: {}'.format(''.join(line)))
							#print('pos: {}, line len: {}'.format(pos, len(line)))
							if len(line) < pos:
								pos = len(line)
								self._chan.send('\000')

			elif data == '\x7f': # backspace key
				if len(line) > 0:
					if pos > 0 and pos < len(line):
						pos -= 1
						#print('backspace at {}'.format(pos))
						l = line[:pos]
						r = line[pos+1:]
						#print('left: {}, right: {}'.format(''.join(l), ''.join(r)))
						#print('sending: backspace')
						self._chan.send('\010')
						for x in r:
							#print('sending: {}'.format(x))
							self._chan.send(x)
						self._chan.send('\000')
						self._chan.send('\010'*(len(line)-pos))
						line = l + r
						#print('line: {}'.format(''.join(line)))
						#print('pos: {}, line len: {}'.format(pos, len(line)))
					else:
						self._chan.send('\010\000\010')
						line = line[:-1]
						pos -= 1

			elif data == '\t': # tab
				#print('tab')
				if len(line) == 0:
					cmd, args, foo = self.parseline(''.join(line))
					#print('cmd: {}, args: {}, foo: {}'.format(cmd, args, foo))
					if cmd == None or cmd == '':
						compfunc = self.completedefault
					else:
						try:
							compfunc = getattr(self, 'complete_' + cmd)
						except AttributeError:
							compfunc = self.completedefault
				else:
					compfunc = self.completenames
				if tab_ctr == 0:
					tab_line = line
				#print('tab_line: {}'.format(''.join(tab_line)))
				self.completion_matches = compfunc(''.join(tab_line), ''.join(tab_line), 0, len(tab_line))
				if tab_ctr >= 1 and len(self.completion_matches) == 1:
					continue
				#print('matches: {}'.format(self.completion_matches))
				clear_prompt(line, pos)
				line = list(self.completion_matches[tab_ctr % len(self.completion_matches)])
				self._chan.send(''.join(line).strip())
				pos = len(line)
				tab_ctr += 1

			else:
				if '\r' in data:
					self.poutput('')
					break
				if data >= '\x00' and data <= '\x1a':
					print('ctrl character')
					continue
				if pos < len(line):
					#print('inserting at {}'.format(pos))
					r = line[pos:]
					line.insert(pos, data)
					#print('line: {}'.format(''.join(line)))
					#print('pos: {}, line len: {}'.format(pos, len(line)))
					self._chan.send(data)
					for x in r:
						self._chan.send(x)
					pos += 1
					self._chan.send('\010'*(len(line)-pos))
				else:
					line.append(data)
					self._chan.send(data)
					pos += 1
		add_line_to_history(line)
		return ''.join(line).strip()

	def cmdloop(self, intro=None):
		""""""
		if intro is not None:
			self.intro = intro
		if self.intro:
			self.poutput(str(self.intro))
		stop = None
		while not stop:
			if self.cmdqueue:
				line = self.cmdqueue.pop(0)
			else:
				line = self._cmdloop(self.prompt)
				if not len(line):
					line = 'EOF'
				else:
					line = line.rstrip('\r\n')
			line = self.precmd(line)
			stop = self.onecmd(line)
			stop = self.postcmd(stop, line)
		self.postloop()

	def default(self, line):
		"""Called on an input line when the command prefix is not recognized"""
		self.poutput('*** Unknown syntax: {}'.format(line))

	def get_names(self):
		return [n for n in dir(self.__class__) if n not in self.hidden_cmds]

	def do_EOF(self, arg):
		return True

	def do_help(self, arg):
		"""List available commands with "help" or detailed help with "help cmd"."""
		if arg:
			try:
				func = getattr(self, 'help_' + arg)
			except AttributeError:
				try:
					doc=getattr(self, 'do_' + arg).__doc__
					if doc:
						self.poutput('{}'.format(str(doc)))
						return
				except AttributeError:
					pass
				self.poutput('{}'.format(str(self.nohelp % (arg,))))
				return
			func()
		else:
			names = self.get_names()
			cmds_doc = []
			cmds_undoc = []
			help = {}
			for name in names:
				if name[:5] == 'help_':
					help[name[5:]]=1
			names.sort()
			# There can be duplicates if routines overridden
			prevname = ''
			for name in names:
				if name[:3] == 'do_':
					if name == prevname:
						continue
					prevname = name
					cmd=name[3:]
					if cmd in help:
						cmds_doc.append(cmd)
						del help[cmd]
					elif getattr(self, name).__doc__:
						cmds_doc.append(cmd)
					else:
						cmds_undoc.append(cmd)
			self.poutput('{}'.format(str(self.doc_leader)))
			self.print_topics(self.doc_header,   cmds_doc,   15,80)
			self.print_topics(self.misc_header,  help.keys(),15,80)
			self.print_topics(self.undoc_header, cmds_undoc, 15,80)

	def print_topics(self, header, cmds, cmdlen, maxcol):
		if cmds:
			self.poutput('{}'.format(str(header)))
			if self.ruler:
				self.poutput('{}'.format(str(self.ruler * len(header))))
			self.columnize(cmds, maxcol-1)
			self.poutput('')

	def columnize(self, list, displaywidth=80):
		""""""
		if not list:
			self.poutput("<empty>\n")
			return
		nonstrings = [i for i in range(len(list)) if not isinstance(list[i], str)]
		if nonstrings:
			raise TypeError("list[i] not a string for i in %s" % ", ".join(map(str, nonstrings)))
		size = len(list)
		if size == 1:
			self.poutput('{}'.format(str(list[0])))
			return
		for nrows in range(1, len(list)):
			ncols = (size+nrows-1) // nrows
			colwidths = []
			totwidth = -2
			for col in range(ncols):
				colwidth = 0
				for row in range(nrows):
					i = row + nrows*col
					if i >= size:
						break
					x = list[i]
					colwidth = max(colwidth, len(x))
				colwidths.append(colwidth)
				totwidth += colwidth + 2
				if totwidth > displaywidth:
					break
			if totwidth <= displaywidth:
				break
		else:
			nrows = len(list)
			ncols = 1
			colwidths = [0]
		for row in range(nrows):
			texts = []
			for col in range(ncols):
				i = row + nrows*col
				if i >= size:
					x = ''
				else:
					x = list[i]
				texts.append(x)
			while texts and not texts[-1]:
				del texts[-1]
			for col in range(len(texts)):
				texts[col] = texts[col].ljust(colwidths[col])
			print('columize sending: {}'.format("  ".join(texts)))
			self.poutput('{}'.format(str("  ".join(texts))))

