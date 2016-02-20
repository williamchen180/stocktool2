#!/usr/bin/python
#coding=UTF-8
# Note: Date,Open,High,Low,Close,Volume,Adj Close

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

	def html_list( self, stocks, missing = [] ):
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
		print '''
<style type="text/css">
#main {
	padding: 5px;
	border-collapse: collapse; 
	border: 1px solid #000000;
	width: 100%;
}
#main td {
	border: 1px solid #000000;
	padding: 3px;
	font-size: .9em;
}
#main th {
	border: 1px solid #000000;
	background-color: #CCFFCC;
}
</style>'''
		print '<script src="sorttable.js" type="text/javascript"></script>'
		print "<p>"
                print u'<center><h1>搜尋出 %d 個項目</h1></center>'.encode('UTF-8') % len(stocks)

		if True:
			print u'''<center><table id="main" class="sortable"><thead><tr>
				<th>代號</th>
				<th>買進日期</th>
				<th>買進價位</th>
				<th>當前日期</th>
				<th>當前價位</th>
				<th>股票成長比率</th>
				<th>股利成長比率</th>
				<th>市值成長比率</th>
				</tr></thead>'''.encode('UTF-8')
			for x in stocks:
				if x.has_key('SIMRESULT') is False:
					continue

				sr = x['SIMRESULT']


				print '<tr><td><p><a href="#%s">%s</a></p></td>' % (x['SYMBOL'], x['SYMBOL'] )
				print '<td>%s</td><td>%.2f</td><td>%s</td><td>%.2f</td><td>%.2f</td><td>%.2f</td><td>%.2f</td></tr>' % sr

				
			print '<tfoot></tfoot></table></center><hr>'



		if missing != []:
			print '<hr>'
			print u'<center><h1>找不到以下紀錄</h1>'.encode('UTF-8')
			for x in missing:
				print x + '<br>'
			print '</center><hr>'

		for x in ddst:
			t = x[1]

			pngfile =  self.png_file_format % t['SYMBOL'] 
			if os.path.isfile( pngfile ):
				print '<hr>' 
				print u'<h1 id="%s"><center>%s @ %s [%s] </center></h1>'.encode('UTF-8') % (t['SYMBOL'], t['SYMBOL'], t['COUNTRY'], t['SHORT'] )
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


	def month_index( self, ts): 
		return int(ts[0:4]) * 12 + int( ts[5:7] ) 


	def build_simulation_data(self, years = 3):
		count = 0
		#skip_to = 'AKSO.OL'
		skip_to = None

		for tname in self.ticker['DB']:

			print tname

			if skip_to != None:
				if skip_to == tname:
					skip_to = None
				else:
					continue

			S = self.ticker['DB'][tname]

			if S['AVAILABLE'] == False:
				continue

			if S['YEARSAROUND'] > 5:
				count += 1

			with open( self.dividend_file_format % tname, 'r') as f:
				lines = f.readlines()


			org = []

			for l in lines:
				if len(l) is 0 or l[0] is '#':
					continue
				year = int(l[0:4])
				month = int(l[5:7])
				month_index = year * 12 + month
				dividend = float( l.split(',')[-1] )

				#print year, month, month_index, dividend
				org.append( (l.split(',')[0], year, month, month_index, dividend) )

			if len(org) is 0:
				continue
			
			result = []

			#print org

			# x: [0]: timestamp, [1]: year, [2]: month, [3]: month index, [4]: dividend
			for x in org:
				if org[-1][3] > (x[3] - 12*years):
					break
				#print x[0], 

				sum = 0.0
				for z in org:
					if z[3] <= x[3] and z[3] > (x[3] - 12*years):
						sum += z[4]
						#print '\t', z[0], z[4], sum

				result.append( [x[0], sum, sum/float(years), x[4] ] )

			# result [0]: '2011-05-31', [1]: dividend sum, [2]: dividend avg, [3]: this dividend
			#pprint.pprint(result)

			idx = 0

			length = len(result)

			if length is 0:
				continue

			with open( self.price_file_format % tname, 'r') as f:
				lines = f.readlines()
				for l in lines:

					if len(l) is 0 or l[0] == '#':
						continue

					now_timestamp = l.split(',')[0]
					now_price = float( l.split(',')[4] )

					if result[idx][0] == now_timestamp: 
						#print result[idx][0]
						result[idx].append( now_price ) 
						idx += 1
					elif result[idx][0] > now_timestamp:
						#print result[idx][0], now_timestamp
						result[idx].append( now_price )
						idx += 1

					if idx > length -1:
						break

					last_timestamp = now_timestamp
					last_price = now_price

			#pprint.pprint(result)
						


			# Dividend day
			# result [0]: '2011-05-31', [1]: dividend sum, [2]: dividend avg, [3]: this dividend, [4]: price

			try:
				for x in result:
					if x[3] != 0:
						x.append( 100.0 * x[2] / x[4] )
					else:
						x.append( 0.0 )
			except Exception as e:
				continue


			# result [0]: '2011-05-31', [1]: dividend sum, [2]: dividend avg, [3]: this dividend, [4]: price, [5] ROI
			#pprint.pprint(result)


			self.ticker['DB'][tname]['ROIs'] = result

			print '\t', count , '/', len(self.ticker['DB']) 


		print count

	def do_simulation(self):
		count = 0
		for x in self.ticker['DB']:
			S = self.ticker['DB'][x]

			if S.has_key('ROIs'):
				count += 1
			else:
				continue

			print x, count

			#pprint.pprint( S['ROIs'] )

			buy = False


			# SIM: [0]: ROIs, [1]: shares, [2]: dividends, [3]: current shares value, [4]: All value
			sim = []

			# ROIs [0]: '2011-05-31', [1]: dividend sum, [2]: dividend avg, [3]: this dividend, [4]: price, [5] ROI
			for r in reversed( S['ROIs'] ):
				if buy is False and r[4] > 15.0:
					buy = True

					sim.append( [ r, int(10000/r[4]), 0, 10000, 10000 ] )
					continue

				if buy is True:
					shares = sim[-1][1]
					last_dividends = sim[-1][2]
					current_dividend = r[3]
					current_price = r[4]

					dividend_value = last_dividends + shares * current_dividend
					current_shares_value = shares * current_price
					all_value = dividend_value + current_shares_value 


					sim.append( [ r, shares, dividend_value, current_shares_value, all_value ] )
			
			if len(sim) == 0:
				continue

			S['SIM'] = sim

			#pprint.pprint( S['SIM'] )

	def build_simulation_result(self):
		for tname in self.ticker['DB']:
			S = self.ticker['DB'][tname]

			if S.has_key('SIM') is False:
				continue

			#print tname
			#pprint.pprint( S['SIM'] )

			sim = S['SIM']

			buy_date = sim[0][0][0]
			buy_price = sim[0][0][4]
			buy_dividend_value = sim[0][2]
			buy_shares_value = sim[0][3]
			buy_all_value = sim[0][4]
			buy_month_index = self.month_index( buy_date )


			last_date = sim[-1][0][0]
			last_price = sim[-1][0][4]
			last_dividend_value = sim[-1][2]
			last_shares_value = sim[-1][3]
			last_all_value = sim[-1][4]
			last_month_index = self.month_index( last_date )

			years = ( last_month_index - buy_month_index ) / 12

			if years == 0:
				continue

			
			div_avg_ROI = last_dividend_value / 10000.0 * 100 / years
			sha_avg_ROI = (last_shares_value - buy_shares_value) / 10000.0 * 100 / years
			all_avg_ROI = (last_all_value - buy_all_value) / 10000.0 * 100 / years


			if False:
				print '%-16s 買進 %s %.2f 目前 %s %.2f 股票 %.2f%% 股利 %.2f%% 市值： %.2f%%' % \
						(tname, buy_date, buy_price, last_date, last_price, sha_avg_ROI, div_avg_ROI, all_avg_ROI)

			sim_result = (buy_date, buy_price, last_date, last_price, sha_avg_ROI, div_avg_ROI, all_avg_ROI)

			S['SIMRESULT'] = sim_result

	def simulate(self):
		pass

if __name__ == '__main__':

	if len(sys.argv) == 1:
		print 'Usage: %s [init | get | build | update | filte | select | sim ]'
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
		t.build_simulation_data()
		t.do_simulation()
		t.build_simulation_result()
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
	elif sys.argv[1] == 'sim':
		t.simulate()



