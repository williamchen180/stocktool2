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
    text_content = 'MSFT GOOD TAXI FUCK NONE'

if form.getvalue('country'):
    country_ext = form.getvalue('country')
else:
    country_ext = 'None'

ext_table = {'None':'', 'UK':'.L', 'Germany':'.DE', 'Singapore':'.SI', 'Hong Kong':'.HK' }


target = []

for x in text_content.splitlines():
	for xx in x.split('\t'):
		for xxx in xx.split(' '):
			if xxx != '':
				target.append( xxx.upper() + ext_table[country_ext] )





p = plot()
for x in target:
	p.plot(symbol = x, path='PNG' )

time.sleep(1)

T = ticker()
stocks = T.select( target ) 

result = []
for x in stocks:
    result.append(x['SYMBOL'])

missing = list( set(target) - set(result) )


T.html_list( stocks, missing )

#print target
#print missing
