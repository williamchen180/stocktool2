#!/usr/bin/env python
#coding=UTF-8

#
# x[ 0:symbol, 1:date, 2:memo, 3. category, 4:origon price, 5:last price, 6:profit, 7:percentage ]
#

import sys
import cgi, cgitb 
import cPickle
import time
from ticker import ticker

dbfile = 'user/favlist.cpickle'

def get_favlist():
	favlist = load_favlist()
	T = ticker()
	print '''<div align="center">
<TABLE id="dataTable" style="width:100%" border="1" class="sortable">
	<thead>
		<th>選取</th>
		<th>項次</th>
		<th>代號</th>
		<th>起始價格</th>
		<th>當前價格</th>
		<th>獲利</th>
		<th class="sorttable_nosort">百分比</th>
		<th class="sorttable_nosort">日期<br>
			<input type="date" id="gdate" onchange="global_change_date(this)">
		</th>
		<th class="sorttable_nosort">評等<br>
			<select name="cate" onchange="global_change_cate(this)">
				<option value="None" selected="selected">None</option>
				<option value="A">A</option>
				<option value="B">B</option>
				<option value="C">C</option>
				<option value="D">D</option>
				<option value="E">E</option>
				<option value="F">G</option>
				<option value="G">G</option>
			</select>
		</th>
		<th>註解</th>
	</thead>
	<tbody>'''

	if len(favlist) == 0:
		print '''
		<tr>
			<TD><INPUT type="checkbox" name="chk"></TD>
			<TD> 1 </TD>
			<TD><INPUT type="text" id="text0" name="text0" value="" onchange="fav_onchange()"></TD>
			<TD></TD>
			<TD></TD>
			<TD></TD>
			<TD></TD>
			<TD><input type="date" id="date0" name="date0" value="" onchange="fav_onchange()"> </TD>
			<TD><select name="cate">
				<option value="None" selected="selected">None</option>
				<option value="A">A</option>
				<option value="B">B</option>
				<option value="C">C</option>
				<option value="D">D</option>
				<option value="E">E</option>
				<option value="F">G</option>
				<option value="G">G</option>
				</select>
			</TD>
			<TD><input type="text" id="memo0" name="memo0" value="" onchange="fav_onchange()"></TD>
		</tr>'''
	else:
		idx = 0
		for x in favlist:

			price = T.get_price_by_date( x[0] )

			delta = price - x[4]

			if x[4] != 0:
				perc = 100.0 * delta / x[4]
			else:
				perc = 0.0

			T.load_favlist()
			cate_html = T.get_cate_html( x[0] )

			print '''
		<tr>
			<TD><INPUT type="checkbox" name="chk"></TD>
			<TD> %d </TD>
			<TD><INPUT type="text" id="text%d" name="text%d" value="%s" onchange="fav_onchange()" ></TD>
			<TD>%.2f</TD>
			<TD>%.2f</TD>
			<TD>%.2f</TD>
			<TD>%.2f</TD>
			<TD class="sorttable_nosort"><input type="date" id="date%d" name="date%d" value="%s" onchange="fav_onchange()" > </TD>
			<th class="sorttable_nosort">%s</th>
			<TD class="sorttable_nosort" ><input type="text" id="memo%d" name="memo%d" value="%s" onchange="fav_onchange()" ></TD>
		</tr>''' % (idx+1, \
				idx, idx, x[0], \
				x[4], \
				price, \
				delta, \
				perc, \
				idx, idx, x[1], \
				cate_html, \
				idx, idx, x[2] )

			idx += 1

	print '''
	</tbody>
</TABLE>
</div>'''



def save_favlist( org ):

	T = ticker()
	pickle_file = 'pickle/ticker.cpickle2'
	with open(pickle_file, 'rb') as f:
		t = cPickle.load(f)



	favlist = []

	for x in org:
		if t['DB'].has_key( x[0] ) is True:
			if x[1] == None:
				year = int(time.strftime('%Y'))
				month = int(time.strftime('%m'))
				day = int(time.strftime('%d'))
				x[1] = "%d-%2.2d-%2.2d" % (year, month, day )

			if len(x[1]) == 10: 
				price = T.get_price_by_date( x[0], x[1])
			else:
				price = 0
			favlist.append( x[0:4] + [price] )

	with open( dbfile, 'wb') as f:
		cPickle.dump( favlist, f )

	get_favlist()


def load_favlist():
	try:
		with open( dbfile, 'rb') as f:
			favlist = cPickle.load( f )
	except Exception as e:
		favlist = []
	return favlist



form = cgi.FieldStorage() 

save_list = form.getvalue('save_list')
get_list = form.getvalue('get_list')
add_list = form.getvalue('add_list')



print "Content-type:text/html; charset=utf-8\r\n\r\n"


if save_list != None:
	favlist = []
	idx = 0
	while True:
		text = form.getvalue('text%d' % idx )
		date = form.getvalue('date%d' % idx )
		memo = form.getvalue('memo%d' % idx )
		cate = form.getvalue('cate%d' % idx )
		idx += 1
		if text is None:
			break
		favlist.append( [text.upper(), date, memo, cate ] )
	save_favlist( favlist )




if add_list != None:
	favlist = load_favlist()
	idx = 0
	while True:
		text = form.getvalue('text%d' % idx )
		date = form.getvalue('date%d' % idx )
		memo = form.getvalue('memo%d' % idx )
		cate = form.getvalue('cate%d' % idx )
		idx += 1
		if text is None:
			break
		text = text.upper()
		exist = False
		for x in favlist:
			if x[0] == text:
				if date != None:
					x[1] = date
				if memo != None:
					x[2] = memo
				if cate != None:
					x[3] = cate
				exist = True
				break
		if exist == False:
			if date == None:
				date = ''
			if memo == None:
				memo = ''
			if cate == None:
				cate = 'None'
			favlist.append( [text.upper(), date, memo, cate ] )
	save_favlist( favlist )


if get_list != None:
	get_favlist()
	

