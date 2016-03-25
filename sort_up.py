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


target_date = form.getvalue('date_up')


print "Content-type:text/html; charset=utf-8\r\n\r\n"


T = ticker()

ret = T.sort_price_diff( target_date )

p = plot()
for x in ret:
	p.plot( symbol = x['SYMBOL'] )  

T.html_list( ret  ) 

