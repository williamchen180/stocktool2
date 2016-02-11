#!/usr/bin/python

import sys
import cPickle
from xlrd import open_workbook

book = open_workbook('Yahoo Ticker Symbols - Jan 2016.xlsx')

sheet = book.sheet_by_name('Stock')


T = {}

t_array = []
s_array = []
e_array = []
c_array = []


for t in sheet.col(0)[4:]:
	t_array.append(t.value.encode('ascii','ignore'))
for t in sheet.col(1)[4:]:
	s_array.append(t.value.encode('ascii','ignore'))
for t in sheet.col(2)[4:]:
	e_array.append(t.value.encode('ascii','ignore'))
for t in sheet.col(3)[4:]:
	c_array.append(t.value.encode('ascii','ignore'))

idx = 0

print len(t_array)
print len(s_array)
print len(e_array)
print len(c_array)

for t in t_array:
	s = s_array[idx]
	e = e_array[idx]
	c = c_array[idx]
	
	if T.has_key( c ) == False:
		T[c] = {} 
	T[c][t] = {}
	T[c][t]['EXCHANGE'] = e
	T[c][t]['INDEX'] = idx
	T[c][t]['COUNTRY'] = c
	T[c][t]['SYMBOL'] = t
	T[c][t]['SHORT'] = s

	idx += 1

with open('pickle/ticker.cpickle2', 'wb') as f:
	cPickle.dump( T, f, protocol=2)


