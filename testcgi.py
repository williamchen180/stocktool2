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

print "Content-type:text/html; charset=utf-8\r\n\r\n"

print "cgitest returns"

pprint.pprint(form)
