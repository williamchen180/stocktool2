#!/usr/bin/env python
#coding=UTF-8

import sys
import cgi, cgitb 
from plot import plot
import time
import os


form = cgi.FieldStorage()

if form.getvalue('country'):
	country = form.getvalue('country')
else:
	country = 'USA'

if form.getvalue('ROI'):
	ROI = form.getvalue('ROI')
else:
	ROI = "10"

if form.getvalue('yearROI'):
	yearROI = form.getvalue('yearROI')
else:
	yearROI = "5"

if form.getvalue('yearCompany'):
	yearCompany = form.getvalue('yearCompany')
else:
	yearCompany = "5"

if form.getvalue('price'):
	price = form.getvalue('price')
else:
	price = "1" 

ROI = int(ROI)
yearROI = int(yearROI)
yearCompany = int(yearCompany)
price = int(price)


print "Content-type:text/html; charset=utf-8\r\n\r\n"
print '<html>'
print '<meta http-equiv="Content-Type" content="text/html" charset="utf-8" />'
print "<head>";
print "<title>Stock information</title>"
print "</head>"
print "<body>"
print country, ROI, yearROI, yearCompany, price
print "</body>"
