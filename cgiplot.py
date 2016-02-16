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

print "Content-type:text/html; charset=utf-8\r\n\r\n"
print '<html>'
print '<meta http-equiv="Content-Type" content="text/html" charset="utf-8" />'
print "<head>";
print "<title>Stock information</title>"
print "</head>"
print "<body>"
print "<p>"

target = []

for x in text_content.splitlines():
	for xx in x.split('\t'):
		for xxx in xx.split(' '):
			if xxx != '':
				target.append( xxx.upper() )



for x in target:
	p = plot()
	ret = p.plot(symbol = x, path='PNG', years = int(years))

time.sleep(1)


T = ticker()
stocks = T.select( target ) 



dst = []

for x in stocks:
	dst.append( (x['ROI'][int(years)-1], x ) )


ddst = sorted( dst, reverse = True )


#pprint.pprint(ddst)


for x in ddst:
	t = x[1]

	pngfile =  'PNG/' + t['SYMBOL'] + '.PNG';
	if os.path.isfile( pngfile ):
		print '<hr>' 
		print u'<h1><center>%s @ %s [%s] </center></h1>'.encode('UTF-8') % (t['SYMBOL'], t['COUNTRY'], t['SHORT'] )
		for i in range(0,5):
			print u'<h3><center>過去 %d 年數股利 %.3f USD, 過去 %d 年ROI: %.3f %%</center></h3>'.encode('UTF-8') % ( i+1, t['DIVIDEND'][i], i+1, t['ROI'][i] ) 

		print '<center><textarea style="font-size: 16pt" rows="2" cols="40">'
		dividends = T.get_dividends( t['SYMBOL'] )
		for x in dividends:
			print x,
		print '</textarea></center>'
		print '<a href="http://finance.yahoo.com/q?s=%s" target="_blank"/>' % t['SYMBOL']
		print '<img border=10 src="/%s"/>' % pngfile 
		print '</a>'

print "</p>"
print "</body>"
print "</html>"

