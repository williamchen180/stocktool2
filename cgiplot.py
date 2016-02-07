#!/usr/bin/env python
#coding=UTF-8

import sys
import cgi, cgitb 
from plot import plot
import time
import os


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

stocks = {}

for x in text_content.splitlines():
    for xx in x.split('\t'):
        for xxx in xx.split(' '):
            if xxx != '':
                stocks[xxx.upper()] = []



for x in stocks:
    p = plot()
    ret = p.plot(symbol = x, path='PNG', years = int(years))
    stocks[x] = ret

time.sleep(1)


if sortedBy == '0':
	for x, value in sorted( stocks.iteritems(), key=lambda(k,v): (v['yearsROI'],k), reverse=True):
	    pngfile =  'PNG/' + x + '.PNG';
	    if os.path.isfile( pngfile ):
		print '<hr>' 
		print '<h1><center>%s</center></h1>' % x
		print u'<h2><center>過去選擇年數股利 %.3f USD, 過去%s年股利: %.3f USD</center></h2>'.encode('UTF-8') % ( stocks[x]['last'], years, stocks[x]['total'] )
		print u'<h2><center>過去選擇年數平均股利: %.3f, 過去%s年平均股利: %.3f</center></h2>'.encode('UTF-8') % ( stocks[x]['lastAvg'], years, stocks[x]['totalAvg'] )
		print u'<h2><center>根據當前股價與過去選擇年數股利計算出的報酬率: %.2f %%</center></h2>'.encode('UTF-8') % stocks[x]['yearsROI'] 
		print '<a href="http://finance.yahoo.com/q?s=%s" target="_blank"/>' % x
                print '<center><textarea style="font-size: 16pt" rows="4" cols="20">'
                for d in stocks[x]['all_dividends']:
                    print d,
                print '</textarea></center>'
		print '<img border=10 src="/%s"/>' % pngfile 
		print '</a>'
else:
	for x, value in sorted( stocks.iteritems(), key=lambda(k,v): (v['nowROI'],k), reverse=True):
	    pngfile =  'PNG/' + x + '.PNG';
	    if os.path.isfile( pngfile ):
		print '<hr>' 
		print '<h1><center>%s</center></h1>' % x
		print u'<h2><center>過去一年股利 %.3f USD, 過去%s年股利: %.3f USD</center></h2>'.encode('UTF-8') % ( stocks[x]['last'], years, stocks[x]['total'] )
		print u'<h2><center>過去一年平均股利: %.3f, 過去%s年平均股利: %.3f</center></h2>'.encode('UTF-8') % ( stocks[x]['lastAvg'], years, stocks[x]['totalAvg'] )
		print u'<h2><center>根據當前股價與過去一年股利計算出的報酬率: %.2f %%</center></h2>'.encode('UTF-8') % stocks[x]['nowROI'] 
                print '<center><textarea style="font-size: 16pt" rows="4" cols="20">'
                for d in stocks[x]['all_dividends']:
                    print d,
                print '</textarea></center>'
		print '<a href="http://finance.yahoo.com/q?s=%s" target="_blank"/>' % x
		print '<img border=10 src="/%s"/>' % pngfile 
		print '</a>'



print "</p>"
print "</body>"

