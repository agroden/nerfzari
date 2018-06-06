"""

adjective / verb corpus pulled from:
http://wordrequest.com

"""

import random
from os.path import abspath, join, dirname

ADJECTIVE_FILE = abspath(join(dirname(__file__), 'adjective.txt'))
NOUN_FILE = abspath(join(dirname(__file__), 'noun.txt'))

def generate_username(adj_len=None, noun_len=None):
	def choose(path, maxlen=None):
		with open(path, 'r') as f:
			words = []
			while True:
				line = f.readline()
				if not line:
					break
				if maxlen is not None and  len(line) > maxlen:
						continue
				words.append(line)
		ret = random.choice(words)
		del words[:]
		return ret.strip()
	adjective = choose(ADJECTIVE_FILE, adj_len)
	noun = choose(NOUN_FILE, noun_len)
	return '{}{}'.format(adjective, noun.title())
'''
import time
try:
	while True:
		print(generate_username(6, 6))
		time.sleep(0.5)
except KeyboardInterrupt:
	pass
'''