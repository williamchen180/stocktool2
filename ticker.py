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

#
# self.ticker: type of dict
#
#	['DB']:	array of dict. Ticker
#	['KIND']: type of dict
#		{ 'Stock': 個數 }
#		{ 'ETF': 個數 }
#	
#	ticker: type of dict
#		'EXCHANGE': 交易所
#		'INDEX': 編號，沒什麼意義
#		'COUNTRY': 國家
#		'SYMBOL': symbol
#		'SHORT': 簡介
#		'KIND': Stock or ETF
#		'DIVIDEND': list。過去N年的股利總和 (-1, -2, -3, -4, -5)
#		'ROI': list。根據過去N年所計算出的ROI。(-1, -2, -3, -4, -5)
#		'LASTPRICE': 最近股價
#		'YEARSAROUND': 公司已成立幾年
#		'DIVIDENDS': 一年配發幾次股利。根據去年配發次數做計算
#		'ROIs': list。過去N(3)年每次配發股利時候的資料
#			[0]: '2011-05-31', [1]: 過去N年股利和, [2]: 過去N年股利平均, [3]: 此次股利, [4]: 當天價格 [5] 當時的ROI
#		'SIM': list。根據'ROIs'，當ROI在15%以上即買進。之後計算每次配股後的資產價值。
#			[0]: 當次ROI list, [1]: 配股之後股數 [2]: 配股之後股利價值總和 [3]: 目前股票市值 [3]:總值
#		'SIMRESULT': list。模擬結果
#			[0]: 買入日期 [1]: 買入價 [2]: 最後一次配股日期 [3]: 配股價格 [4] 股票價值ROI [5] 股利價值ROI [6] 總值ROI


# self.favlist: type: list
#	[ symbol, date, memo, category ]
#

class ticker():

	def __init__(self):
		self.pickle_file = 'pickle/ticker.cpickle2'
		self.dividend_file_format = 'history/%s.dividend'
		self.price_file_format = 'history/%s.price'
                self.png_file_format = 'PNG/%s.PNG'
		self.ROI_lines_data_format = 'history/%s.ROI'
		self.user_db_file = 'user/favlist.cpickle' 

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

	def load_favlist(self):
		try:
			with open( self.user_db_file, 'rb') as f:
				self.favlist = cPickle.load(f)
		except Exception as e:
			self.favlist = []

	def is_fav(self, symbol ):
		for x in self.favlist:
			if x[0] == symbol:
				return True
		return False


	def get_cate( self, symbol ):
		found = False
		for x in self.favlist:
			if x[0] == symbol:
				found = True
				break
		if found == True:
			return x[3]
		else:
			return None

	def get_cate_html( self, symbol ):
		cate = self.get_cate( symbol )
		cate_html = '<select name="%s" onchange="cate_selected(this)"><option value="None">None</option>' % symbol
		if cate == 'A':
			cate_html += '<option value="A" selected="selected">A</option>'
		else:
			cate_html += '<option value="A">A</option>'
		if cate == 'B':
			cate_html += '<option value="B" selected="selected">B</option>'
		else:
			cate_html += '<option value="B">B</option>'
		if cate == 'C':
			cate_html += '<option value="C" selected="selected">C</option>'
		else:
			cate_html += '<option value="C">C</option>'
		if cate == 'D':
			cate_html += '<option value="D" selected="selected">D</option>'
		else:
			cate_html += '<option value="D">D</option>'
		if cate == 'E':
			cate_html += '<option value="E" selected="selected">E</option>'
		else:
			cate_html += '<option value="E">E</option>'
		if cate == 'F':
			cate_html += '<option value="F" selected="selected">F</option>'
		else:
			cate_html += '<option value="F">F</option>'
		if cate == 'G':
			cate_html += '<option value="G" selected="selected">G</option>'
		else:
			cate_html += '<option value="G">G</option>'
		cate_html += '</select>'
		return cate_html

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

	def update_last_price( self ):
		for tname in self.ticker['DB']:

			t = self.ticker['DB'][tname]

			if t['AVAILABLE'] == False:
				continue
			price_file = self.price_file_format % tname

			if os.path.isfile( price_file) == False:
				continue

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

				last_price = float( l.split(',')[-3] )

			t['LASTPRICE'] = last_price

	def update_price( self, skip_to = None ):
		self.update_item( self.price_file_format, self.priurl, skip_to ) 

		self.update_last_price()

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

				
	def filte(self, kind = 'all', \
			rate = 5, \
			year = 5, \
			country=['USA'], \
			yearsaround = 0, \
			pricelimit = 0, \
			dividends = 0,
			total_dividends = 0,
			dividend_up = 0):

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

			if total_dividends != 0 or dividend_up != 0:
				with open( self.dividend_file( tname ), 'r') as f:
					lines = f.readlines()

					if total_dividends != 0:
						if len(lines) < total_dividends:
							continue

					if dividend_up != 0:
						last_dividend = 99999
						divup = True
						for l in lines:
							if len(l) == 0:
								continue
							if l[0] == '#':
								continue
							this_dividend = float(l.split(',')[1])

							if this_dividend > (last_dividend * dividend_up):
								divup = False
								break
							last_dividend = this_dividend
						if divup == False or last_dividend == 9999:
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
				if self.ticker['DB'][tname]['AVAILABLE'] == True:
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

		self.load_favlist()

		ddst = sorted( dst, reverse = True )

		#
		# Show HTML header & script
		#

		print '''Content-type:text/html; charset=utf-8\r\n\r\n
<!DOCTYPE html>
<html>
<meta http-equiv="Content-Type" content="text/html" charset="utf-8" />
<head>
<title>Stock information</title>
</head>
<body onload="myInit()">
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
table.sortable th:not(.sorttable_sorted):not(.sorttable_sorted_reverse):not(.sorttable_nosort):after { 
	content: " \\25B4\\25BE" 
}

#wrap {
   width:100%;
   margin:1 auto;
}
#left_col {
   float:left;
   width:50%;
}
#right_col {
   float:right;
   width:50%;
}

</style>
<script src="sorttable.js" type="text/javascript"></script><script>
function load_recent_change() {

	var xhttp;
	if (window.XMLHttpRequest) {
		// code for modern browsers
		xhttp = new XMLHttpRequest();
	} else {
		// code for IE6, IE5
		xhttp = new ActiveXObject("Microsoft.XMLHTTP");
	}
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			document.getElementById("recent_change").innerHTML = xhttp.responseText;
			document.getElementById("debug").innerHTML += xhttp.responseText;
			ele = document.getElementById('recent_change_table' );
			sorttable.makeSortable( ele ); 
		}
	};

	document.getElementById("recent_change").innerHTML = "載入中....";

	var table = document.getElementById( "main" );
	var rowCount = table.rows.length;
	var req = "";
	for(var i=1;i<rowCount; i++) {
		var row = table.rows[i];
		req += row.cells[1].childNodes[0].innerHTML + ",";
	}


	var ele = document.getElementById( "gdate" );


	if (ele != null) {
		var datestr = ele.value;
	} else {
		var datestr = "9999-99-99";
	}


	xhttp.open("POST", "recent_change.py", true);
	xhttp.setRequestHeader( "Content-type", "application/x-www-form-urlencoded");
	xhttp.send("list=" + req + "&date=" + datestr);
}
function myInit() {
	load_recent_change();
}
function save_fav() {
	var table = document.getElementById("main");
	var rowCount = table.rows.length;
	var gchkbox = table.rows[0].cells[0].childNodes[0];
	var idx = 0;
	var req = "";
	for( var i=1; i<rowCount; i++) {
		var row = table.rows[i];
		var chkbox = row.cells[0].childNodes[0];
		if (chkbox.checked == true) {
			req += "text" + idx + "=" + row.cells[1].childNodes[0].innerHTML + "&";
			req += "cate" + idx + "=" + row.cells[2].innerHTML + "&";
			idx += 1;
		}
	}

	var xhttp;
	if (window.XMLHttpRequest) {
		// code for modern browsers
		xhttp = new XMLHttpRequest();
	} else {
		// code for IE6, IE5
		xhttp = new ActiveXObject("Microsoft.XMLHTTP");
	}
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			alert('已儲存');
			document.getElementById("debug").innerHTML = xhttp.responseText;
		}
	};
	xhttp.open("POST", "favlist.py", true);
	xhttp.setRequestHeader( "Content-type", "application/x-www-form-urlencoded");
	xhttp.send("add_list=1&" + req );
}

function add2fav(target) {
	var chkbox = document.getElementById("chk" + target);

	if (document.getElementById("add2fav" + target).innerHTML == "已加入觀察名單") {
		document.getElementById("add2fav" + target).innerHTML = "加入觀察名單";
		chkbox.checked = false;
	} else {
		document.getElementById("add2fav" + target).innerHTML = "已加入觀察名單";
		chkbox.checked = true;
	}

}

function flick_check() {

	var table = document.getElementById("main");
	var rowCount = table.rows.length;
	var gchkbox = table.rows[0].cells[0].childNodes[0];
	for( var i=1; i<rowCount; i++) {
		var row = table.rows[i];
		var chkbox = row.cells[0].childNodes[0];
		chkbox.checked = !gchkbox.checked;
		chkbox.click();
	}
}

function select2_click(target) {
	var id = target.id;
	var len = id.length;

	var tmp = id.substring( 0, id.length - 1 );
	var end = id.substring( id.length -1 , id.length);
	if (end == "1") {
		var dst = tmp + "2";
	} else {
		var dst = tmp + "1";
	}
	var ele = document.getElementById( dst );

	ele.checked = target.checked;
}

function cate_selected( target ) {
	var ele = document.getElementById( target.name + "cate" );

	ele.innerHTML = target.value;

}

function orderPanel2() {
	var panel = document.getElementById( "panel" );
	var table = document.getElementById( "recent_change_table" );
	var rowCount = table.rows.length;
	var newOrder = [];
	for( var i=1; i<rowCount; i++) {
		var row = table.rows[i];
		var symbol = row.cells[1].childNodes[0].innerHTML;
		newOrder.push( document.getElementById( symbol ) );
	}
	while( panel.firstChild ) {
		panel.removeChild( panel.firstChild );
	}
	for( var i=0; i<newOrder.length; i++) {
		panel.appendChild( newOrder[i] );
	}
}
function sort_panel2() {
	setTimeout( function() { orderPanel2()}, 1000 );
}
function orderPanel() {
	var panel = document.getElementById( "panel" );
	var table = document.getElementById( "main" );
	var rowCount = table.rows.length;
	var newOrder = [];
	for( var i=1; i<rowCount; i++) {
		var row = table.rows[i];
		var symbol = row.cells[1].childNodes[0].innerHTML;
		newOrder.push( document.getElementById( symbol ) );
	}
	while( panel.firstChild ) {
		panel.removeChild( panel.firstChild );
	}
	for( var i=0; i<newOrder.length; i++) {
		panel.appendChild( newOrder[i] );
	}
}
function sort_panel() {
	setTimeout( function() { orderPanel()}, 1000 );
}
</script>

'''
                print u'<div align="center"><h1>搜尋出 %d 個項目</h1></div>'.encode('UTF-8') % len(stocks)

		print u'<div align="center"><button style="font-size: 16pt" onclick="save_fav()">儲存觀察名單</button></div>'.encode('UTF-8') 
		print '<hr>'

		#
		# Show management table
		#

		if True:
			print u'''<div align="center"><table id="main" class="sortable"><thead><tr>
				<th class="sorttable_nosort"><input type="checkbox" onclick="flick_check()"></th>
				<th><button onclick="sort_panel()">代號</button></th>
				<th><button onclick="sort_panel()">評等</button></th>
				<th><button onclick="sort_panel()">買進日期</button></th>
				<th><button onclick="sort_panel()">買進價位</button></th>
				<th><button onclick="sort_panel()">當前日期</button></th>
				<th><button onclick="sort_panel()">當前價位</button></th>
				<th><button onclick="sort_panel()">股票成長比率</button></th>
				<th><button onclick="sort_panel()">股利成長比率</button></th>
				<th><button onclick="sort_panel()">市值成長比率</button></th>
				</tr></thead>'''.encode('UTF-8')
			for x in stocks:
				if self.is_fav( x['SYMBOL' ] ) == True:
					print '<tr><td><input type="checkbox" checked id="chk%s1" onclick="select2_click(this)"></td>' % x['SYMBOL']
				else:
					print '<tr><td><input type="checkbox" id="chk%s1" onclick="select2_click(this)"></td>' % x['SYMBOL']

				print '<td><a href="#%s">%s</a></td>' % (x['SYMBOL'], x['SYMBOL'] )
				
				print '<td id="%scate">%s</td>' % ( x['SYMBOL'], self.get_cate( x['SYMBOL'] ) )

				if x.has_key('SIMRESULT') is True:
					sr = x['SIMRESULT']
					print '<td>%s</td><td>%.2f</td><td>%s</td><td>%.2f</td><td>%.2f</td><td>%.2f</td><td>%.2f</td></tr>' % sr
				else:
					print '<td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>' 

			print '</table></div><hr>'

		#
		# Show recent change table
		#

		if True:
			print '<div align="center">'
			print '<h2>根據日期計算近期變動</h2>'
			print '<input type="date" id="gdate" onchange="load_recent_change()" class="sortable"></div>'
			print '<br><p id="recent_change">'
			print '</p><hr>'

		#
		# Show missing part
		#

		if missing != []:
			print '<hr>'
			print u'<div align="center"><h1>找不到以下紀錄</h1>'.encode('UTF-8')
			for x in missing:
				print x + '<br>'
			print '</div><hr>'

		#
		# Show detail information: name, category, dividend, PNG
		#

		print '<div id="panel">'

		for x in ddst:
			t = x[1]

			cate_html = self.get_cate_html( t['SYMBOL'] )

			pngfile =  self.png_file_format % t['SYMBOL'] 
			if os.path.isfile( pngfile ):
				print '<div align="center" id="%s"><hr>' % t['SYMBOL']
				print u'<h1>%s @ %s [%s]</h1>'.encode('UTF-8') % (t['SYMBOL'], t['COUNTRY'], t['SHORT'] )


				'''
				if self.is_fav( t['SYMBOL'] ) == True: 
					status = u"已加入觀察名單".encode('UTF-8')
				else:
					status = u"加入觀察名單".encode('UTF-8')
				print u'<button id="add2fav%s" style="font-size: 16pt" onclick="add2fav(\'%s\')">%s</button>'.encode('UTF-8') % (t['SYMBOL'], t['SYMBOL'] , status )


				print u'<h1>評等'.encode('UTF-8')
				print cate_html
				print '</h1>'
				'''

				if self.is_fav( t['SYMBOL' ] ) == True:
					print '<input type="checkbox" id="chk%s2" checked onclick="select2_click(this)">' % t['SYMBOL']
				else:
					print '<input type="checkbox" id="chk%s2" onclick="select2_click(this)">' % t['SYMBOL']
				print cate_html


				print '<br>'

				print '<div id="wrap"><div id="left_col">'

				for i in range(0,5):
					print u'<h3>過去 %d 年數股利 %.3f USD, 過去 %d 年ROI: %.3f %%</h3>'.encode('UTF-8') % ( i+1, t['DIVIDEND'][i], i+1, t['ROI'][i] ) 
				print '</div>'
				print '<div id="right_col">'

				print '<textarea style="font-size: 16pt" rows="8" cols="40">'
				dividends = self.get_dividends( t['SYMBOL'] )
				for x in dividends:
					print x,
				print '</textarea>'
				print '</div></div>'
				print '<a href="http://finance.yahoo.com/q?s=%s" target="_blank">' % t['SYMBOL']
				print '<img border=10 src="%s"/>' % pngfile 
				print '</a>'
				print '</div>'

		print '</div>'

		print '''<br><hr><textarea id="debug" style="display:none" name="textcontent" cols="200" rows="40" placeholder="除錯"></textarea>'''
		#print '''<br><hr><textarea id="debug" name="textcontent" cols="200" rows="40" placeholder="除錯"></textarea>'''
		print "<br><br><br></body>"
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
			# result [0]: '2011-05-31', [1]: 過去N年股利和, [2]: 過去N年股利平均, [3]: 此次股利, [4]: 當天價格

			try:
				for x in result:
					if x[3] != 0:
						x.append( 100.0 * x[2] / x[4] )
					else:
						x.append( 0.0 )
			except Exception as e:
				continue


			# result [0]: '2011-05-31', [1]: dividend sum, [2]: dividend avg, [3]: this dividend, [4]: price, [5] ROI
			# result [0]: '2011-05-31', [1]: 過去N年股利和, [2]: 過去N年股利平均, [3]: 此次股利, [4]: 當天價格 [5] 當時的ROI
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

	def build_ROI_lines_data(self):
		for tname in self.ticker['DB']:
			if False:
				if tname != 'CRF':
					continue

			print tname
			S = self.ticker['DB'][tname]
			if S.has_key( 'ROIs') is False:
				continue

			with open( self.ROI_lines_data_format % tname, 'w') as f:

				last_divavg = 0
				last_ROI9 = 0
				last_ROI11 = 0
				last_ROI14 = 0

				first_record = True

				for r in S['ROIs']:
					datetime = r[0]
					divavg = r[2]

					ROI9 = divavg / 0.09
					ROI11 = divavg / 0.11
					ROI14 = divavg / 0.14

					if first_record == True:
						first_record = False
					else:
						f.write( '%s,%.2f,%.2f,%.2f,%.2f\n' % ( datetime, last_divavg,  last_ROI9, last_ROI11, last_ROI14) )
					f.write( '%s,%.2f,%.2f,%.2f,%.2f\n' % ( datetime, divavg,  ROI9, ROI11, ROI14) )

					last_divavg = divavg
					last_ROI9 = ROI9
					last_ROI11 = ROI11
					last_ROI14 = ROI14



	def get_price_by_date( self, symbol, target_date = '9999-99-99' ):

		if self.ticker['DB'].has_key( symbol ) == False:
			return 0

		price_file = self.price_file_format % symbol 

		if os.path.isfile( price_file) == False:
			return 0

		price = 0
		with open( price_file, 'r') as f:
			for l in f.readlines():
				if len(l) == 0:
					continue
				if l[0] == '#':
					continue

				date = l.split(',')[0]

				if target_date >= date:
					price = float(l.split(',')[-3])
					break
		return price

	def recent_change(self, strlist='GOOD,MSFT,TAXI', strdate='NOW'):

		print '''<TABLE id="recent_change_table" style="width:100%" border="1">
	<tr>
		<th><button onclick="sort_panel2()">No</button></th>
		<th><button onclick="sort_panel2()">代號</button></th>
		<th><button onclick="sort_panel2()">起始價格</button></th>
		<th><button onclick="sort_panel2()">當前價格</button></th>
		<th><button onclick="sort_panel2()">獲利</button></th>
		<th><button onclick="sort_panel2()">百分比</button></th>
	</tr>'''
		try:
			idx = 1
			for x in strlist.split(','):
				if len(x) == 0:
					continue

				if self.ticker['DB'].has_key( x ) == False:
					continue

				S = self.ticker['DB'][x]

			
				org_price = self.get_price_by_date( x, strdate )
				last_price = S['LASTPRICE']

				delta = last_price - org_price

				if org_price != 0:
					perc = 100.0 * delta / org_price
				else:
					perc = 0.0


				print '<tr><td>%d</td><td><a href="#%s">%s</a></td><td>%.2f</td><td>%.2f</td><td>%.2f</td><td>%.2f</td></tr>' % \
						(idx, x, x, org_price, last_price, delta, perc )
				idx += 1
		except Exception as e:
			print e

		print '''	</tbody><tfoot></tfoot></TABLE>'''



	def simulate(self):
		pass

if __name__ == '__main__':

	if len(sys.argv) == 1:
		print 'Usage: %s [init | get | build | update | filte | select | sim | recent_change ]'
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
		t.build_ROI_lines_data()
		t.save()
	elif sys.argv[1] == 'filte':
		numbers = 0
		ret = t.filte( kind = 'all', \
				rate = 0, \
				year = 3, \
				country = ['USA'], \
				yearsaround = 3, \
				pricelimit = 0, \
				dividends = -1,
				total_dividends = 10,
				dividend_up = 1)
		for x in ret:
			numbers += 1
			print x['SYMBOL']
		print numbers,  'stocks'
	elif sys.argv[1] == 'select':
		ret = t.select( ['MSFT', 'GOOD' ] )
		pprint.pprint(ret)
	elif sys.argv[1] == 'sim':
		t.simulate()
	elif sys.argv[1] == 'test':
		pass
	elif sys.argv[1] == 'recent_change':
		t.recent_change()



