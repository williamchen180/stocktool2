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
    text_content = 'PFD AWF GOF GDF EHI FCO HHY HIX MCR PCN PFL PFN PHK PTY RCS WEA MMT FFC CGO ETO PFO CHI CLM LOR GGT UTG GOOD LTC O ORC OLP WPC HCP NNN SNH MNR MFA NYMT PSA UHT JNK SJNK HYG PHB YYY REM VIG VNQ PFF CEFL PCEF PGX SPFF AMLP AMJ MLPI MLPN AMU MLPA PFLT SBR CODI DPM NGLS TGP TOO AHGP ARLP APU BPL CLMT CPLP EEP ETP GLP HHS MMLP NS NSH OKE OKS PAA SPH Ston TCP TLP CTL FGP PNNT SFL SSI TDW TK WMB'

if form.getvalue('country'):
    country_ext = form.getvalue('country')
else:
    country_ext = 'None'

ext_table = {'None':'', 'UK':'.L', 'Germany':'.DE', 'Singapore':'.SI', 'Hong Kong':'.HK' }


target = []

for x in text_content.splitlines():
	for xx in x.split('\t'):
		for xxx in xx.split(' '):
			if xxx != '':
				target.append( xxx.upper() + ext_table[country_ext] )

#print "Content-type:text/html; charset=utf-8\r\n\r\n"


p = plot()
for x in target:
	p.plot(symbol = x, path='PNG' )

time.sleep(1)

T = ticker()
stocks = T.select( target ) 

result = []
for x in stocks:
    result.append(x['SYMBOL'])

missing = list( set(target) - set(result) )


T.html_list( stocks, missing )

#print target
#print missing
