#!/usr/bin/env python
#coding=UTF-8

import sys
import cgi, cgitb 
import time
import os
from ticker import ticker
import pprint


# Create instance of FieldStorage 
form = cgi.FieldStorage() 

strlist = form.getvalue('list')

strdate = form.getvalue('date')

if strlist == None:
	strlist = 'MSFT,GOOD,TAXI,'

if strdate == None:
	strdate = '9999-99-99'

print "Content-type:text/html; charset=utf-8\r\n\r\n"


T = ticker()


T.recent_change( strlist, strdate )


