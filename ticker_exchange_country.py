#!/usr/bin/python

import sys
import cPickle
from xlrd import open_workbook

book = open_workbook('Yahoo Ticker Symbols - Jan 2016.xlsx')

sheet = book.sheet_by_name('Stock')

idx = 4 

T = {}

for name in sheet.col(0)[4:]:
	short = sheet.col(1)[idx].value
	e = sheet.col(2)[idx].value
	c = sheet.col(3)[idx].value
	t = name.value

	idx += 1
	print t, c, short 

	if T.has_key( c ) == False:
		T[c] = {} 
	T[c][t] = {}
	T[c][t]['EXCHANGE'] = e
	T[c][t]['INDEX'] = idx
	T[c][t]['COUNTRY'] = c
	T[c][t]['SYMBOL'] = t
	T[c][t]['SHORT'] = short


if False:
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
					T[c][t]['COUNTRY'] = c
					T[c][t]['SYMBOL'] = t
					idx += 1

with open('pickle/ticker.cpickle2', 'wb') as f:
	cPickle.dump( T, f, protocol=2)


