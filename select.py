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
	_yearROI = "5"

if form.getvalue('yearCompany'):
	_yearCompany = form.getvalue('yearCompany')
else:
	_yearCompany = "5"

if form.getvalue('price'):
	_price = form.getvalue('price')
else:
	_price = "1" 

if form.getvalue('dividends'):
	_dividends = form.getvalue('dividends')
else:
	_dividends = "12"

_ROI = int(_ROI)
_yearROI = int(_yearROI)
_yearCompany = int(_yearCompany)
_price = float(_price)
_dividends = int(_dividends)

if type(_country) == str:
	_country = [_country]

T = ticker()


ret = T.filte( kind = _kind, rate = _ROI, year = _yearROI, country = _country, yearsaround = _yearCompany, pricelimit = _price, dividends = _dividends )

T.html_list( ret ) 

#print _kind, _ROI, _yearROI, _country, _yearCompany, _price, _dividends
