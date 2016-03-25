#!/usr/bin/env python
#coding=UTF-8

import sys
import cgi, cgitb 
from plot import plot
import time
import os
from ticker import ticker


form = cgi.FieldStorage()

if form.getvalue('kind'):
	_kind = form.getvalue('kind')
else:
	_kind = 'all'

if form.getvalue('country'):
	_country = form.getvalue('country')
else:
	_country = ['all']

if form.getvalue('ROI'):
	_ROI = form.getvalue('ROI')
else:
	_ROI = "5"

if form.getvalue('yearROI'):
	_yearROI = form.getvalue('yearROI')
else:
	_yearROI = "3"

if form.getvalue('yearCompany'):
	_yearCompany = form.getvalue('yearCompany')
else:
	_yearCompany = "3"

if form.getvalue('price'):
	_price = form.getvalue('price')
else:
	_price = "1" 

if form.getvalue('dividends'):
	_dividends = form.getvalue('dividends')
else:
	_dividends = "-1"

if form.getvalue('total_dividends'):
	_total_dividends = form.getvalue('total_dividends')
else:
	_total_dividends = 10

if form.getvalue('dividend_up'):
	_dividend_up = form.getvalue('dividend_up')
else:
	_dividend_up = 1

if form.getvalue('date_up'):
	_date_up = form.getvalue('date_up')
else:
	_date_up = '2016-01-01'

_ROI = int(_ROI)
_yearROI = int(_yearROI)
_yearCompany = int(_yearCompany)
_price = float(_price)
_dividends = int(_dividends)
_total_dividends = int(_total_dividends)
_dividend_up = float(_dividend_up)

if type(_country) == str:
	_country = [_country]

T = ticker()


ret = T.filte( kind = _kind, \
		rate = _ROI, \
		year = _yearROI, \
		country = _country, \
		yearsaround = _yearCompany, \
		pricelimit = _price, \
		dividends = _dividends, \
		total_dividends = _total_dividends, \
		dividend_up = _dividend_up,
		target_date = _date_up)

p = plot()
for x in ret:
	p.plot( symbol = x['SYMBOL'] )  

T.html_list( ret  ) 

#print _kind, _ROI, _yearROI, _country, _yearCompany, _price, _dividends
