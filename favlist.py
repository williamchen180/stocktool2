#!/usr/bin/env python
#coding=UTF-8


import sys
import cgi, cgitb 
import cPickle

dbfile = 'user/favlist.cpickle'

form = cgi.FieldStorage() 

save_list = form.getvalue('save_list')

get_list = form.getvalue('get_list')

add_one = form.getvalue('add_one')

print "Content-type:text/html; charset=utf-8\r\n\r\n"

#print "form:" , form, '<br>'

if add_one != None:
	target = form.getvalue('target')
	print target



if save_list != None:

	print "form:" , form, '<br>'

	favlist = []

	idx = 0
	while True:
		text = form.getvalue('text%d' % idx )
		date = form.getvalue('date%d' % idx )
		memo = form.getvalue('memo%d' % idx )

		idx += 1

		if text is None:
			break

		favlist.append( (text, date, memo ) )

		print 'favlist:', favlist, '<br>'

	try:
		with open( dbfile, 'wb') as f:
			cPickle.dump( favlist, f )
	except Exception as e:
		print e


if get_list != None:
	try:
		with open( dbfile, 'rb') as f:
			favlist = cPickle.load( f )
	except Exception as e:
		favlist = []

	print '''
	<TABLE id="dataTable" width="350px" border="1">
		<tr>
			<th>選取</th>
			<th>項次</th>
			<th>代號</th>
			<th>日期</th>
			<th>註解</th>
		</tr>'''

	if len(favlist) == 0:
		print '''
				<tr>
				<TD><INPUT type="checkbox" name="chk"></TD>
				<TD> 1 </TD>
				<TD><INPUT type="text" id="text0" name="text0" value="" onchange="fav_onchange()"/></TD>
				<TD><input type="date" id="date0" name="date0" value="" onchange="fav_onchange()"/> </TD>
				<TD><input type="text" id="memo0" name="memo0" value="" onchange="fav_onchange()"/></TD>
				</tr>'''
	else:
		idx = 0
		for x in favlist:
			print '''
		<tr>
			<TD><INPUT type="checkbox" name="chk"></TD>
			<TD> %d </TD>
			<TD><INPUT type="text" id="text%d" name="text%d" value="%s" onchange="fav_onchange()" /></TD>
			<TD><input type="date" id="date%d" name="date%d" value="%s" onchange="fav_onchange()" /> </TD>
			<TD><input type="text" id="memo%d" name="memo%d" value="%s" onchange="fav_onchange()" /></TD>
		</tr>''' % (idx+1, idx, idx, x[0], idx, idx, x[1], idx, idx, x[2] )

			idx += 1

	print '''	</TABLE>'''

