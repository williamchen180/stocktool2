#!/usr/bin/env python
#coding=UTF-8

import sys
import cgi, cgitb 
from plot import plot
import time
import os
from ticker import ticker


form = cgi.FieldStorage()

if form.getvalue('country'):
	_country = form.getvalue('country')
else:
	_country = ['USA']

if form.getvalue('ROI'):
	_ROI = form.getvalue('ROI')
else:
	_ROI = "10"

if form.getvalue('yearROI'):
	_yearROI = form.getvalue('yearROI')
else:
	_yearROI = "5"

if form.getvalue('yearCompany'):
	_yearCompany = form.getvalue('yearCompany')
else:
	_yearCompany = "5"

if form.getvalue('price'):
	_price = form.getvalue('price')
else:
	_price = "1" 

_ROI = int(_ROI)
_yearROI = int(_yearROI)
_yearCompany = int(_yearCompany)
_price = int(_price)


print "Content-type:text/html; charset=utf-8\r\n\r\n"
print '<html>'
print '<meta http-equiv="Content-Type" content="text/html" charset="utf-8" />'
print "<head>";
print "<title>Stock information</title>"
print "</head>"
print "<body>"
print "<p>"
print u"<center><h1>ROI是根據過去%s年計算</h1></center>".encode('UTF-8') % _yearROI
print u"<Center><h2>以下根據目前的股價與過去一年的ROI由大到小排序<h2></center>".encode('UTF-8')


t = ticker()

ret = t.ROIgt( rate = _ROI, year = _yearROI, country = _country, yearsaround = _yearCompany )

print ret

stocks = {}

for x in ret:
	stocks[x] = []

for x in stocks:
	p = plot()
	ret = p.plot(symbol = x, path='PNG', years = _yearROI)
	stocks[x] = ret

time.sleep(1)


sortedBy = 0
if sortedBy == '0':
	for x, value in sorted( stocks.iteritems(), key=lambda(k,v): (v['yearsROI'],k), reverse=True):
	    pngfile =  'PNG/' + x + '.PNG';
	    if os.path.isfile( pngfile ):
		print '<hr>' 
		print '<h1><center>%s</center></h1>' % x
		print u'<h2><center>過去選擇年數股利 %.3f USD, 過去%s年股利: %.3f USD</center></h2>'.encode('UTF-8') % ( stocks[x]['last'], _yearROI, stocks[x]['total'] )
		print u'<h2><center>過去選擇年數平均股利: %.3f, 過去%s年平均股利: %.3f</center></h2>'.encode('UTF-8') % ( stocks[x]['lastAvg'], _yearROI, stocks[x]['totalAvg'] )
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
		print u'<h2><center>過去一年股利 %.3f USD, 過去%s年股利: %.3f USD</center></h2>'.encode('UTF-8') % ( stocks[x]['last'], _yearROI, stocks[x]['total'] )
		print u'<h2><center>過去一年平均股利: %.3f, 過去%s年平均股利: %.3f</center></h2>'.encode('UTF-8') % ( stocks[x]['lastAvg'], _yearROI, stocks[x]['totalAvg'] )
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




