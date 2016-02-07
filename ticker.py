#!/usr/bin/python

import cPickle
import os
import sys
import datetime
import time
import socket
import mechanize
from mechanize import Browser

class ticker():

	def __init__(self):
		self.pickle_file = 'pickle/ticker.cpickle2'
		self.dividend_file_format = 'history/%s.dividend'
		self.price_file_format = 'history/%s.price'

		self.year = int(time.strftime('%Y'))
		self.month = int(time.strftime('%m'))
		self.day = int(time.strftime('%d'))

		self.now_month_index = self.year * 12 + self.month

		self.divurl = 'http://ichart.yahoo.com/table.csv?s=%s&c=%d&a=%d&b=%d&f=%d&d=%d&e=%d&g=v&ignore=.csv'
		self.priurl = 'http://ichart.yahoo.com/table.csv?s=%s&c=%d&a=%d&b=%d&f=%d&d=%d&e=%d&g=d&ignore=.csv'

		with open(self.pickle_file, 'rb') as f:
			self.ticker = cPickle.load(f)


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

	def update_price( self, skip_to = None ):
		self.update_item( self.price_file_format, self.priurl, skip_to ) 

	def update_dividend( self, skip_to = None):
		self.update_item( self.dividend_file_format, self.divurl, skip_to ) 

	def update_item(self, filename, _url, skip_to = None):
		mech = Browser()
		for c in self.ticker:
			for t in self.ticker[c]:
				if self.ticker[c][t]['AVAILABLE'] == True:
					print t, self.ticker[c][t]['INDEX']

					if skip_to != None:
						if t == skip_to:
							skip_to = None
						else:
							print 'skip'
							continue

					with open( filename % t , 'r+') as f:
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

						url = _url % (t, date.year, date.month-1, date.day, self.year, self.month, self.day )

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

	def update_ROI(self):

		month_index = self.year * 12 + self.month

		for c in self.ticker:
			for t in self.ticker[c]:
				

				dividend_file = 'history/' + t + '.dividend'
				price_file = 'history/' + t + '.price'

				if os.path.isfile( dividend_file ) == True and os.path.isfile( price_file) == True:
					self.ticker[c][t]['AVAILABLE'] = True
				else:
					self.ticker[c][t]['AVAILABLE'] = False
					continue

				price_file = self.price_file_format % t
				dividend_file = self.dividend_file_format % t

				#print '-->', t

				with open( price_file, 'r') as f:
					l = f.readline()
					if len(l) == 0:
						continue
					if l[0] == '#':
						l = f.readline()
					if len(l) == 0:
						continue

					last_price = float( l.split(',')[-1] )

					# Calculate how many years this company around
					try:
						lines = f.readlines()
						l = lines[-1]
					except Exception as e:
						years_around = 0
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

				self.ticker[c][t]['DIVIDEND'] = dividends
				self.ticker[c][t]['ROI'] = ROI
				self.ticker[c][t]['LASTPRICE'] = last_price
				self.ticker[c][t]['YEARSAROUND'] = years_around

				
	def ROIgt(self, rate, year = 5, country=['USA'], yearsaround = 0):

		#print rate, year, country, yearsaround

		if year > 5:
			year = 5
		if year < 1:
			year = 1

		ret = []
		for c in self.ticker:

			if len(country) != 0:
				found = False
				for x in country:
					if c == x: 
						found = True
						break
				if found == False:
					continue

			for t in self.ticker[c]:
				if self.ticker[c][t]['AVAILABLE'] == False:
					continue

				if yearsaround != 0 and self.ticker[c][t]['YEARSAROUND'] < yearsaround:
					continue

				if self.ticker[c][t].has_key('ROI') == False:
					continue

				if self.ticker[c][t]['ROI'][year-1] > float(rate):
                                        #print t
                                        #print self.ticker[c][t]['ROI'][year-1], float(rate)
                                        #print self.ticker[c][t]['YEARSAROUND']

					ret.append( t )
		return ret


if __name__ == '__main__':

	if len(sys.argv) == 1:
		print 'Usage: %s [update_price_and_dividend | update]'
		sys.exit(0)

	t = ticker()

	if sys.argv[1] == 'update_price_and_dividend':
		t.update_price()
		t.update_dividend()

	elif sys.argv[1] == 'update':
		t.update_ROI()
		t.save()
	else:
		numbers = 0
		ret = t.ROIgt( rate = 40, year = 5, country = ['USA'], yearsaround = 5 )
		for x in ret:
			numbers += 1
			print x
	
		print numbers,  'stocks'



