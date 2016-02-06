#!/usr/bin/python

import MySQLdb
import os
import cPickle


skip_to = 0

conn=MySQLdb.connect(host="localhost",user="root",passwd="111111",charset="utf8", db='stock2')
cursor = conn.cursor()

sql = 'SELECT * FROM TICKER'

Total = cursor.execute( sql )

rows = cursor.fetchall()

idx = 0

TICKETS = {}

for row in rows:

	dividend_file = 'history/' + row[1] + '.dividend'
	dividend_pickle = 'pickle/' + row[1] + '.dividend'
	price_file = 'history/' + row[1] + '.price'
	price_pickle = 'pickle/' + row[1] + '.price'

	if os.path.isfile( dividend_file ) == False or os.path.isfile( price_file ) == False:
		continue

	idx += 1

	if skip_to != 0:
		if idx < skip_to:
			continue

	print idx , '/' , Total, ' ' , row[1]


	# 0: IDX 1: SYMBOL 2: EXCHANGE 3: COUNTRY

	if False:
		SYMBOL = row[1]
		EXCHANGE = row[2]
		COUNTRY = row[3]

		if TICKETS.has_key( COUNTRY ) == False:
			TICKETS[ COUNTRY ] = []

		TICKETS[ COUNTRY ].append( SYMBOL )

		# 0: date, 1: Open, 2: High, 3: Low, 4: Close, 5: Volume, 6: AdjClose
		with open( price_file, 'r') as f:
			price = {} 
			for l in f.readlines():
				if l[0] == '#':
					continue
				x = l.split(',')
				price[ x[0] ] = ( float(x[1]), float(x[2]), float(x[3]), float(x[4]), int(x[5]), float(x[6]) )

		with open( price_pickle, 'wb') as f:
			cPickle.dump( price, f, protocol=2 )

		with open( dividend_file, 'r') as f:
			dividend = {}
			for l in f.readlines():
				if l[0] == '#':
					continue
				x = l.split(',')
				dividend[x[0]] = float(x[1])
		with open( dividend_pickle, 'wb') as f:
			cPickle.dump( dividend, f, protocol=2)



	if True:
		sql = 'UPDATE TICKER SET AVAILABLE=1 WHERE SYMBOL=\'%s\'' % row[1]
		cursor.execute(sql)
		conn.commit()


	if False:
		with open( price_file, 'r') as f:
			for l in f.readlines():
				if l[0] == '#':
					continue
				x = l.split(',')
				sql = 'INSERT INTO PRICE (IDX, DATE, OPEN, HIGH, LOW, CLOSE, VOLUME, ADJCLOSE) VALUES '\
					'("%d", "%s", %s, %s, %s, %s, %s, %s )' % \
					(row[0], x[0], x[1], x[2], x[3], x[4], x[5], x[6] )
				try:
					cursor.execute(sql)
					conn.commit()
				except Exception as e:
					pass

#with open('pickle/TICKETS.cpickle','wb') as f:
#	cPickle.dump( TICKETS, f, protocol=2 )
	




