#!/usr/bin/python

import time
from mechanize import Browser
import sys

class get_history:
	
	def __init__( self ):
		self.divurl = 'http://ichart.yahoo.com/table.csv?s=%s&c=1990&a=1&b=1&f=%s&d=%s&e=%s&g=v&ignore=.csv'
		self.priurl = 'http://ichart.yahoo.com/table.csv?s=%s&c=1990&a=1&b=1&f=%s&d=%s&e=%s&g=d&ignore=.csv'
		self.year = time.strftime('%Y')
		self.month = time.strftime('%m')
		self.day = time.strftime('%d')

		self.mech = Browser()

	def get( self, symbol ):

		found_price = False
		found_dividend = False 


		try:
			url = self.divurl % (symbol, self.year, self.month, self.day)
			#print url
			page = self.mech.open( url ) 
		except Exception as e:
			#print e
                        pass
		else:
			try:
				html = page.read()
			except Exception as e:
				#print html
				with open('history/errorlist.txt', 'a') as f:
					f.write( symbol + '\n' )
			else:
				f = open('history/' + symbol + '.dividend', 'w')
				f.write( '#' + html )
				f.close()

				found_dividend = True

		try:
			url = self.priurl % (symbol, self.year, self.month, self.day)
			#print url
			page = self.mech.open( url ) 
		except Exception as e:
			#print e
                        pass
		else:
			try:
				html = page.read()
			except Exception as e:
				#print html
                                pass
				with open('history/errorlist.txt', 'a') as f:
					f.write( symbol + '\n' )
			else:
				f = open('history/' + symbol + '.price', 'w')
				f.write( '#' + html )
				f.close()

				found_price = True

		if found_dividend is True and found_price is True:
			return True
		else:
			return False

	

	

if __name__ == '__main__':
	h = get_history()
	for x in sys.argv[1:]:
		ret = h.get( x ) 
		if ret == True:
			print 'found the records for ' + x 

