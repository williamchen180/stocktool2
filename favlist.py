#!/usr/bin/env python
#coding=UTF-8

#
# x[ 0:symbol, 1:date, 2:memo, 3:origon price, last price, profit, percentage ]
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
	print '''
	<TABLE id="dataTable" width="350px" border="1" class="sortable">
		<tr>
			<th>選取</th>
			<th>項次</th>
			<th>代號</th>
			<th>日期<br><input type="date" id="gdate" onchange="global_change_date()"></th>
			<th>註解</th>
			<th>起始價格</th>
			<th>當前價格</th>
			<th>獲利</th>
			<th>百分比</th>
		</tr>'''

	if len(favlist) == 0:
		print '''
				<tr>
				<TD><INPUT type="checkbox" name="chk"></TD>
				<TD> 1 </TD>
				<TD><INPUT type="text" id="text0" name="text0" value="" onchange="fav_onchange()"/></TD>
				<TD><input type="date" id="date0" name="date0" value="" onchange="fav_onchange()"/> </TD>
				<TD><input type="text" id="memo0" name="memo0" value="" onchange="fav_onchange()"/></TD>
				<TD><input type="text" /></TD>
				<TD><input type="text" /></TD>
				<TD><input type="text" /></TD>
				<TD><input type="text" /></TD>
				</tr>'''
	else:
		idx = 0
		for x in favlist:

			price = T.get_price_by_date( x[0] )

			delta = price - x[3]

			if x[3] != 0:
				perc = 100.0 * delta / x[3]
			else:
				perc = 0.0

			print '''
		<tr>
			<TD><INPUT type="checkbox" name="chk"></TD>
			<TD> %d </TD>
			<TD><INPUT type="text" id="text%d" name="text%d" value="%s" onchange="fav_onchange()" /></TD>
			<TD><input type="date" id="date%d" name="date%d" value="%s" onchange="fav_onchange()" /> </TD>
			<TD><input type="text" id="memo%d" name="memo%d" value="%s" onchange="fav_onchange()" /></TD>
			<TD><input type="text" value="%.2f"/></TD>
			<TD><input type="text" value="%.2f"/></TD>
			<TD><input type="text" value="%.2f"/></TD>
			<TD><input type="text" value="%.2f %%"/></TD>
		</tr>''' % (idx+1, idx, idx, x[0], idx, idx, x[1], idx, idx, x[2], x[3], price, delta, perc )

			idx += 1

	print '''	</TABLE>'''



def save_favlist( org ):

	try:
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
                                favlist.append( x[0:3] + [price] )

		with open( dbfile, 'wb') as f:
			cPickle.dump( favlist, f )
	except Exception as e:
		print e

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

add_one = form.getvalue('add_one')

del_one = form.getvalue('del_one')

print "Content-type:text/html; charset=utf-8\r\n\r\n"

#print "form:" , form, '<br>'

if del_one != None:
	target = form.getvalue('target')
	print target

	favlist = load_favlist()
	for x in favlist:
		if x[0] == target:
			favlist.remove(x)
			break
	save_favlist( favlist )


if add_one != None:
	target = form.getvalue('target')
	print target

	favlist = load_favlist()

	year = int(time.strftime('%Y'))
	month = int(time.strftime('%m'))
	day = int(time.strftime('%d'))

	timestr = "%d-%2.2d-%2.2d" % (year, month, day )

	found = False
	for x in favlist:
		if x[0] == target:
			x[1] = timestr
			found = True
			break

	if found == False:
		favlist.append( [target, timestr, ""] )

	save_favlist( favlist )



if save_list != None:
	favlist = []
	idx = 0
	while True:
		text = form.getvalue('text%d' % idx )
		date = form.getvalue('date%d' % idx )
		memo = form.getvalue('memo%d' % idx )
		idx += 1
		if text is None:
			break
		favlist.append( [text.upper(), date, memo ] )
	save_favlist( favlist )


if get_list != None:

	get_favlist()
	

