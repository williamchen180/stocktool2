#!/usr/bin/python

import sys
import cPickle
from xlrd import open_workbook




def process_sheet( _file = 'Yahoo Ticker Symbols - Jan 2016.xlsx', sheets = ['Stock', 'ETF' ] , T = {}):
	ret = {}
	ret['DB'] = None
	ret['KIND'] = {}
	with open_workbook('Yahoo Ticker Symbols - Jan 2016.xlsx') as book:

		for K in sheets:
			print 'process sheet:', K
			sheet = book.sheet_by_name( K )

			ticker_array = []
			short_array = []
			exchange_array = []
			country_array = []


			for t in sheet.col(0)[4:]:
				ticker_array.append(t.value.encode('ascii','ignore'))
			for t in sheet.col(1)[4:]:
				short_array.append(t.value.encode('ascii','ignore'))
			for t in sheet.col(2)[4:]:
				exchange_array.append(t.value.encode('ascii','ignore'))
			for t in sheet.col(3)[4:]:
				country_array.append(t.value.encode('ascii','ignore'))

			idx = 0

			for ticker in ticker_array:
				short = short_array[idx]
				exchange = exchange_array[idx]
				country = country_array[idx]

				T[ ticker ] = {}
				T[ ticker ]['EXCHANGE'] = exchange
				T[ ticker ]['INDEX'] = idx
				T[ ticker ]['COUNTRY'] = country
				T[ ticker ]['SYMBOL'] = ticker
				T[ ticker ]['SHORT' ] = short
				T[ ticker ]['KIND' ] = K 
				
				idx += 1

			print idx , ' items processed'

			ret['KIND'][K] = idx

	ret['DB'] = T
	return ret

if __name__ == '__main__':

	T = process_sheet()
	with open('pickle/ticker.cpickle2', 'wb') as f:
		cPickle.dump( T, f, protocol=2)

	for x in T['KIND']:
		print x, T['KIND'][x]

	


