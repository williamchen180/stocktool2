#!/usr/bin/env python
#coding=UTF-8


import sys
import cgi, cgitb 
import cPickle

dbfile = 'user/favlist.cpickle'

form = cgi.FieldStorage() 

save_list = form.getvalue('save_list')

get_list = form.getvalue('get_list')

print "Content-type:text/html; charset=utf-8\r\n\r\n"

#print "form:" , form, '<br>'

if save_list != None:

	favlist = []

	idx = 0
	while True:
		text = form.getvalue('text%d' % idx )
		print text
		date = form.getvalue('date%d' % idx )
		print date
		memo = form.getvalue('memo%d' % idx )
		print memo

		idx += 1

		if text is None:
			break

		favlist.append( (text, date, memo ) )

		print favlist, '<br>'

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
		</tr>
		<tr>'''

	if len(favlist) == 0:
		print '''
				<TD><INPUT type="checkbox" name="chk"></TD>
				<TD> 1 </TD>
				<TD><INPUT type="text" id="text0" name="text0" value=""></TD>
				<TD><input type="date" id="date0" name="date0" value=""/> </TD>
				<TD><input type="text" id="memo0" name="memo0" valye=""/></TD>'''
	else:
		idx = 0
		for x in favlist:
			print '<tr><TD><INPUT type="checkbox" name="chk"></TD>\
				<TD> %d </TD>\
				<TD><INPUT type="text" id="text%d" name="text%d" value="%s"></TD>\
				<TD><input type="date" id="date%d" name="date%d" value="%s"/> </TD>\
				<TD><input type="text" id="memo%d" name="memo%d" value="%s"/></TD></tr>' % \
				(idx+1, idx, idx, x[0], idx, idx, x[1], idx, idx, x[2] )
			idx += 1

	print '''</tr></TABLE>'''

