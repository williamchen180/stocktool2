#!/usr/bin/python

import cPickle


T = {}

idx = 0

with open('ticker.txt','r') as ticket:
	with open('exchange.txt','r') as exchange:
		with open('country.txt','r') as country:

			for t in ticket.readlines():
				e = exchange.readline()
				c = country.readline()

				t = t.split('\n')[0]
				e = e.split('\n')[0]
				c = c.split('\n')[0]
				
				if T.has_key( c ) == False:
					T[c] = {} 
				T[c][t] = {}
				T[c][t]['EXCHANGE'] = e
				T[c][t]['INDEX'] = idx
				idx += 1

with open('pickle/ticker.cpickle2', 'wb') as f:
	cPickle.dump( T, f, protocol=2)

print idx

