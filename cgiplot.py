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
print u"<center><h1>ROI是根據過去%s年計算</h1></center>".encode('UTF-8') % years
print u"<Center><h2>以下根據目前的股價與過去一年的ROI由大到小排序<h2></center>".encode('UTF-8')

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


pprint.pprint(ddst)


for x in ddst:
	t = x[1]

	pngfile =  'PNG/' + t['SYMBOL'] + '.PNG';
	if os.path.isfile( pngfile ):
		print '<hr>' 
		print u'<h1><center>代號：%s 國家：%s</center></h1>'.encode('UTF-8') % (t['SYMBOL'], t['COUNTRY'] )
		print u'<h1><center>簡介：%s</h1>'.encode('UTF-8') % t['SHORT']
		print '<center><textarea style="font-size: 16pt" rows="6" cols="40">'
			
		for i in range(0,5):
			print u'<h2><center>過去 %d 年數股利 %.3f USD, 過去 %d 年ROI: %.3f</center></h2>'.encode('UTF-8') % ( i+1, t['DIVIDEND'][i], i+1, t['ROI'][i] ) 

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

