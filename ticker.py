#!/usr/bin/python
#coding=UTF-8

import pprint
import cPickle
import os
import sys
import datetime
import time
import socket
import mechanize
from mechanize import Browser
from xlrd import open_workbook

class ticker():

	def __init__(self):
		self.pickle_file = 'pickle/ticker.cpickle2'
		self.dividend_file_format = 'history/%s.dividend'
		self.price_file_format = 'history/%s.price'
                self.png_file_format = 'PNG/%s.PNG'

		self.year = int(time.strftime('%Y'))
		self.month = int(time.strftime('%m'))
		self.day = int(time.strftime('%d'))

		self.now_month_index = self.year * 12 + self.month

		self.divurl = 'http://ichart.yahoo.com/table.csv?s=%s&c=%d&a=%d&b=%d&f=%d&d=%d&e=%d&g=v&ignore=.csv'
		self.priurl = 'http://ichart.yahoo.com/table.csv?s=%s&c=%d&a=%d&b=%d&f=%d&d=%d&e=%d&g=d&ignore=.csv'

		try:
			with open(self.pickle_file, 'rb') as f:
				self.ticker = cPickle.load(f)
		except Exception as e:
			self.init_data()
		finally:
			pass


	def __getitem__(self, key):
		return self.ticker[key]

	def __setitem__(self, key, value):
		self.ticker[key] = value

	def __iter__(self):
		return iter(self.ticker)

	def keys(self):
		return self.ticker.itemlist

	def values(self):
		return [self.ticker[key] for key in self.ticker]

	def itervalues(self):
		return (self[key] for key in self.ticker)

	def has_key(self,key):
		return self.ticker.has_key(key)

	def save(self):
		with open(self.pickle_file, 'wb') as f:
			cPickle.dump( self.ticker, f, protocol=2)

	def price_file(self, t ):
		return self.price_file_format % t 
	
	def dividend_file(self, t):
		return self.dividend_file_format % t

	def init_data(self, excel = 'Yahoo Ticker Symbols - Jan 2016.xlsx', sheets = ['Stock', 'ETF' ] ):
		T = {}
		ret = {}
		ret['DB'] = None
		ret['KIND'] = {}

		with open_workbook( excel ) as book:

			print 'Open:', excel


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
		with open( self.pickle_file, 'wb' ) as f:
			cPickle.dump( ret, f, protocol=2)

	def get_price_and_dividend(self):
		mech = Browser()
		skip_to = None 


		for t in self.ticker['DB']:

			print t

			divurl = self.divurl % (t, 1990, 1, 1, self.year, self.month, self.day ) 
			try:
				page = mech.open( divurl )
			except Exception as e:
				#print 'get dividend', e
				#print divurl
				pass
			else:
				try:
					html = page.read()
				except Exception as e:
					with open('history/errorlist.txt', 'a') as f:
						f.write( t + '\n')
				else:
					name = self.dividend_file_format % t
					print name
					with open( name, 'w') as f:
						f.write( '#' + html)

			priurl = self.priurl % (t, 1990, 1, 1, self.year, self.month, self.day )
			try:
				page = mech.open( priurl )
			except Exception as e:
				#print 'get price', e
				#print priurl
				pass
			else:
				try:
					html = page.read()
				except Exception as e:
					with open('history/errorlist.txt', 'a') as f:
						f.write( t + '\n')
				else:
					name = self.price_file_format % t
					print name
					with open( name, 'w') as f:
						f.write( '#' + html)

	def update_price( self, skip_to = None ):
		self.update_item( self.price_file_format, self.priurl, skip_to ) 

	def update_dividend( self, skip_to = None):
		self.update_item( self.dividend_file_format, self.divurl, skip_to ) 

	def update_item(self, filename, _url, skip_to = None, delete_cache = True):
		mech = Browser()
		for tname in self.ticker['DB']:

			t = self.ticker['DB'][tname]

			if t['AVAILABLE'] == False:
				continue

			print t['KIND'], tname, t['INDEX']

			if skip_to != None:
				if tname == skip_to:
					skip_to = None
				else:
					print 'skip'
					continue

			with open( filename % tname , 'r+') as f:
				l = f.readline()
				if len(l) == 0:
					continue
				if l[0] != '2':
					l = f.readline()
				if len(l) == 0:
					continue
				(year, month, day) = l[0:10].split('-')
				date = datetime.datetime( int(year), int(month), int(day) )
				date += datetime.timedelta(days=1)

				#print year, month, day, date.year, date.month, date.day

				if self.year == date.year and self.month == date.month and self.day == date.day:
					print 'No need to update'
					continue

				url = _url % (tname, date.year, date.month-1, date.day, self.year, self.month, self.day )

				#print '(%d,%d,%d) to (%d,%d,%d)' % (date.year, date.month, date.day, self.year, self.month, self.day )
				#print	url 

   
				while True:
					try:
						page = mech.open(url, timeout=5)
						#page = mech.open(url)
						html = page.read()
					except mechanize.URLError as exc:
						if isinstance(exc.reason, socket.timeout):
							print 'Timed out', exc
							continue
						else:
							print exc, url
							break
					else:
						#print html.split('\n')[1:]
						f.seek(0,0)
						lines = f.readlines()
						f.seek(0,0)
						f.truncate()
						
						for l in html.split('\n'):
							if len(l) == 0:
								continue
							if l[0] != '2':
								continue
							f.write(l+'\n')
						for l in lines:
							if len(l) == 0:
								continue
							if l[0] != '2':
								continue
							f.write(l)

						break

				if delete_cache == True:
					png_file = self.png_file_format % tname
                                        if os.path.isfile(png_file) == True:
                                            os.unlink( png_file )
					    


	def build_data(self):
		for tname in self.ticker['DB']:

			t = self.ticker['DB'][tname]
			
			price_file = self.price_file_format % tname
			dividend_file = self.dividend_file_format % tname

			if os.path.isfile( dividend_file ) == True and os.path.isfile( price_file) == True:
				t['AVAILABLE'] = True
			else:
				t['AVAILABLE'] = False
				continue

			#print '-->', t

			with open( price_file, 'r') as f:
				l = f.readline()
				if len(l) == 0:
					t['AVAILABLE'] = False
					continue
				if l[0] == '#':
					l = f.readline()
				if len(l) == 0:
					t['AVAILABLE'] = False
					continue

				last_price = float( l.split(',')[-1] )
				year = int(l[0:4])
				month = int(l[5:7])
				month_index = year * 12 + month

				if month_index < self.now_month_index:
					t['AVAILABLE'] = False
					#print month_index, self.now_month_index, year, month
					continue

				# Calculate how many years this company around
				try:
					f.seek(0,0)
					lines = f.readlines()
					l = lines[-1]
				except Exception as e:
					years_around = 0
					month_index = 0
				finally:
					year = int(l[0:4])
					month = int(l[5:7])
					month_index = year * 12 + month
					years_around = int((self.now_month_index - month_index) / 12)
					

			#print 'last price:', last_price
			#print 'years:', years_around

			dividend_one_year = 0.0
			dividend_two_year = 0.0
			dividend_three_year = 0.0
			dividend_four_year = 0.0
			dividend_five_year = 0.0

			ROI1 = 0
			ROI2 = 0
			ROI3 = 0
			ROI4 = 0
			ROI5 = 0

			with open( dividend_file, 'r') as f:
				dividends_last_year = 0
				for l in f.readlines():
					if len(l) == 0:
						continue
					if l[0] == '#':
						continue
					year = int(l[0:4])
					month = int(l[5:7])

					month_index = year * 12 + month

					dividend = float( l.split(',')[1] ) 

					if month_index > (self.now_month_index - 12*1):
						dividend_one_year += dividend
					if month_index > (self.now_month_index - 12*2):
						dividend_two_year += dividend 
					if month_index > (self.now_month_index - 12*3):
						dividend_three_year += dividend 
					if month_index > (self.now_month_index - 12*4):
						dividend_four_year += dividend
					if month_index > (self.now_month_index - 12*5):
						dividend_five_year += dividend 

					if (self.year-1) == year:
						dividends_last_year += 1

			#print dividends_last_year

			if last_price != 0:
				ROI1 = 100.0 * dividend_one_year / 1.0 / last_price
				ROI2 = 100.0 * dividend_two_year / 2.0 / last_price
				ROI3 = 100.0 * dividend_three_year / 3.0 / last_price
				ROI4 = 100.0 * dividend_four_year / 4.0 / last_price
				ROI5 = 100.0 * dividend_five_year / 5.0 / last_price

			dividends = ( dividend_one_year, dividend_two_year, dividend_three_year, dividend_four_year, dividend_five_year )
			ROI = (ROI1, ROI2, ROI3, ROI4, ROI5 )

			#print "DIVIDEND", dividends
			#print "ROI", ROI

			t['DIVIDEND'] = dividends
			t['ROI'] = ROI
			t['LASTPRICE'] = last_price
			t['YEARSAROUND'] = years_around
			t['DIVIDENDS'] = dividends_last_year

				
	def filte(self, kind = 'all', rate = 5, year = 5, country=['USA'], yearsaround = 0, pricelimit = 0, dividends = 0):

		#print rate, year, country, yearsaround

		if year > 5:
			year = 5
		if year < 1:
			year = 1

		ret = []

		for tname in self.ticker['DB']:

			t = self.ticker['DB'][tname]

			if t['AVAILABLE'] == False:
				continue

			if country[0] != 'all':
				found = False
				for c  in country:
					if c == t['COUNTRY']:
						found = True
						break
				if found == False:
					continue


			if kind != 'all':
				if t['KIND'] != kind:
					continue

			if dividends != 0:
				if dividends < 0 and t['DIVIDENDS'] < -dividends:
					continue
				if dividends > 0 and t['DIVIDENDS'] != dividends:
					continue

			if yearsaround != 0 and t['YEARSAROUND'] < yearsaround:
				continue

			if t.has_key('ROI') == False:
				continue

			if pricelimit != 0 and t['LASTPRICE'] < pricelimit:
				continue

			if t['ROI'][year-1] < float(rate):
				continue

			#print t
			#print t['ROI'][year-1], float(rate)
			#print t['YEARSAROUND']

			ret.append( t )
		return ret

	def select( self, target ):
		ret = []
		
		for tname in target:
			if self.ticker['DB'].has_key( tname ):
				ret.append( self.ticker['DB'][tname] )
		return ret

	def get_dividends( self, tname ):
		ret = []
		if self.ticker['DB'].has_key( tname ):
			with open( self.dividend_file( tname ), 'r') as f:
				for l in f.readlines():
					if len(l) == 0:
						continue
					if l[0] == '#':
						continue
					ret.append(l)
		return ret

	def html_list( self, stocks ):
		dst = []
		for x in stocks:
			dst.append( (x['ROI'][4], x ) )

		ddst = sorted( dst, reverse = True )

		print "Content-type:text/html; charset=utf-8\r\n\r\n"
		print '<html>'
		print '<meta http-equiv="Content-Type" content="text/html" charset="utf-8" />'
		print "<head>";
		print "<title>Stock information</title>"
		print "</head>"
		print "<body>"
		print "<p>"
                print u'<center><h1>搜尋出 %d 個項目</h1></center>'.encode('UTF-8') % len(stocks)

		for x in ddst:
			t = x[1]

			pngfile =  self.png_file_format % t['SYMBOL'] 
			if os.path.isfile( pngfile ):
				print '<hr>' 
				print u'<h1><center>%s @ %s [%s] </center></h1>'.encode('UTF-8') % (t['SYMBOL'], t['COUNTRY'], t['SHORT'] )
				for i in range(0,5):
					print u'<h3><center>過去 %d 年數股利 %.3f USD, 過去 %d 年ROI: %.3f %%</center></h3>'.encode('UTF-8') % ( i+1, t['DIVIDEND'][i], i+1, t['ROI'][i] ) 

				print '<center><textarea style="font-size: 16pt" rows="2" cols="40">'
				dividends = self.get_dividends( t['SYMBOL'] )
				for x in dividends:
					print x,
				print '</textarea></center>'
				print '<a href="http://finance.yahoo.com/q?s=%s" target="_blank"/>' % t['SYMBOL']
				print '<img border=10 src="/%s"/>' % pngfile 
				print '</a>'

		print "</p>"
		print "</body>"
		print "</html>"


if __name__ == '__main__':

	if len(sys.argv) == 1:
		print 'Usage: %s [init | get | build | update | filte | select ]'
		sys.exit(0)

	t = ticker()

	if sys.argv[1] == 'init':
		t.init_data()
	elif sys.argv[1] == 'update':
		t.update_price()
		t.update_dividend()
	elif sys.argv[1] == 'get':
		t.get_price_and_dividend()
	elif sys.argv[1] == 'build':
		t.build_data()
		t.save()
	elif sys.argv[1] == 'filte':
		numbers = 0
		ret = t.filte( kind = 'all', rate = 40, year = 5, country = ['USA'], yearsaround = 5, pricelimit = 1  )
		for x in ret:
			numbers += 1
			print x
	
		print numbers,  'stocks'
	elif sys.argv[1] == 'select':
		ret = t.select( ['MSFT', 'GOOD' ] )
		pprint.pprint(ret)


