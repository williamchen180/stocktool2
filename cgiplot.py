#!/usr/bin/env python
#coding=UTF-8

import sys
import cgi, cgitb 
from plot import plot
import time
import os
from ticker import ticker
import pprint


# Create instance of FieldStorage 
form = cgi.FieldStorage() 

# Get data from fields
if form.getvalue('textcontent'):
    text_content = form.getvalue('textcontent')
else:
    text_content = 'MSFT GOOD TAXI'

if form.getvalue('years'):
    years = form.getvalue('years')
else:
    years = '5'

if form.getvalue('sort'):
	sortedBy = form.getvalue('sort')
else:
	sortedBy = '0'

target = []

for x in text_content.splitlines():
	for xx in x.split('\t'):
		for xxx in xx.split(' '):
			if xxx != '':
				target.append( xxx.upper() )



for x in target:
	p = plot()
	ret = p.plot(symbol = x, path='PNG' )

time.sleep(1)



T = ticker()
stocks = T.select( target ) 


T.html_list( stocks )

