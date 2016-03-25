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
    #text_content = 'AWF GOF GDF EHI FCO HHY HIX MCR MPV PCN PFL PFN PHK PTY RCS WEA MMT FFC CGO ETO PFD PFO CHI CLM LOR GGT UTG GOOD LTC O ORC OLP WPC HCP NNN SNH MNR MFA NYMT PSA UHT JNK SJNK HYG PHB YYY REM VIG VNQ PFF CEFL PCEF PGX SPFF AMLP AMJ MLPI MLPN AMU MLPA PFLT SBR CODI DPM NGLS TGP TOO AHGP ARLP APU BPL CLMT CPLP EEP ETP GLP HHS MMLP NS NSH OKE OKS PAA SPH Ston TCP TLP CTL FGP PNNT SFL SSI TDW TK WMB RDS.A'
    text_content = 'MSFT GOOD NUS'
    #text_content = 'POWL'
    #text_content = 'bag csn fdp sog ite smj irv abc aht hcft mer nicl hils dph brk bnkr clln hlma imt cnc ba bmy jd ng hsp'

if form.getvalue('country'):
    country_ext = form.getvalue('country')
else:
    country_ext = 'None'
    #country_ext = 'UK'

ext_table = {'None':'', 'UK':'.L', 'Germany':'.DE', 'Singapore':'.SI', 'Hong Kong':'.HK' }

T = ticker()

target = []

for x in text_content.splitlines():
	for xx in x.split('\t'):
		for xxx in xx.split(' '):
			if xxx != '':
				target.append( xxx.upper() + ext_table[country_ext] )

print "Content-type:text/html; charset=utf-8\r\n\r\n"

stocks = T.select( target ) 

p = plot()
for x in target:
	p.plot(symbol = x, path='PNG' )

time.sleep(1)

result = []
for x in stocks:
    result.append(x['SYMBOL'])

missing = list( set(target) - set(result) )


T.html_list( stocks, missing )

#print target
#print missing
