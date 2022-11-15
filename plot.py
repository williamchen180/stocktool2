#!/usr/bin/env python
#coding=UTF-8

# test commit
# edit something on branch test

import os.path
import get_history
import Gnuplot
import time
from mechanize import Browser
import sys
from yahoo_finance import Share
import datetime

L1 = 0.05
L2 = 0.07
L3 = 0.10


class	plot:

	def __init__(self):
            pass

	def plot( self, symbol, path = 'PNG', years = 5, cached = True ):

		png_file = './' + path + '/' + symbol + '.PNG'
		png_file2 = './' + path + '/' + symbol + '_4.PNG'

		if cached == True:
			if os.path.isfile( png_file ) and os.path.isfile( png_file2):
				return

		current_price = 0

		now = datetime.datetime.now()

		now_month_index = now.year * 12 + now.month

		self.path = path

		symbol = symbol.upper()

		dividend_file = 'history/%s.dividend' % symbol 
		price_file = 'history/%s.price' % symbol 
		ROI_file = 'history/%s.ROI' % symbol


		if os.path.isfile( dividend_file ) == False or os.path.isfile( price_file) == False:
			get_history.get_history().get(symbol)

		if os.path.isfile( dividend_file ) == False or os.path.isfile( price_file) == False:
			# Symbol not found
			return


		if os.path.isdir( path ) == False:
			os.mkdir( path )

		with open( price_file, 'r') as f:
			lines = f.readlines()
			for l in lines:
				if l[0] != '#':
					break

			x = l.split(',')
			current_price = float( x[-1] )

			last_x = x[0]
			left_x = lines[-1].split(',')[0]

			if len( lines ) > 260:
				year_date = lines[260].split(',')[0]
			else:
				year_date = None
			if len( lines ) > 60:
				three_month_date = lines[60].split(',')[0]
			else:
				three_month_date = None
			if len( lines ) > 20:
				month_date = lines[20].split(',')[0]
			else:
				month_date = None
			if len( lines ) > 7:
				week_date = lines[7].split(',')[0]
			else:
				week_date = None

		if True:
			date = datetime.datetime( int( last_x[0:4] ), int( last_x[5:7] ), int( last_x[8:10] ) )
			date += datetime.timedelta( days = 90 )
			right_x = '%d-%2.2d-%2.2d' % (date.year, date.month, date.day )

			date = datetime.datetime( int( left_x[0:4] ), int( left_x[5:7] ), int( left_x[8:10] ) )
			date += datetime.timedelta( days = -90 )
			left_x = '%d-%2.2d-%2.2d' % (date.year, date.month, date.day )



		with open( dividend_file, 'r') as f:
			div_total = 0.0
			div_last = 0.0

			for l in f.readlines():
				if l[0] == '#':
					continue
				datestring, dividend = l.split(',')
				( year, month, day ) = datestring.split('-')

				dividend = float( dividend )
				year = int(year)
				month = int(month)

				month_index = year * 12 + month

                                #print datestring, month_index, now_month_index, (now_month_index - month_index)

				if month_index > (now_month_index - 12*int(years) ):
					div_total += dividend

				if month_index > (now_month_index - 12):
					div_last += dividend
                                        #print datestring, dividend, div_last

		#print "Average 5 years dividend: ", div_total / 5.0
		#print "Last average dividend: ", div_last


		RRI9 = div_total / float(years) / L1 
		RRI11 = div_total / float(years) / L2
		RRI14= div_total / float(years) / L3 

		RRI9Last = div_last / L1
		RRI11Last = div_last / L2
		RRI14Last = div_last / L3

                
		p = Gnuplot.Gnuplot()

		p('reset')
		p('set key left')
		p('RRI9(x)=%f' % RRI9 ) 
		p('RRI11(x)=%f' % RRI11 ) 
		p('RRI14(x)=%f' % RRI14 ) 

		p('RRI9Last(x)=%f' % RRI9Last )
		p('RRI11Last(x)=%f' % RRI11Last )
		p('RRI14Last(x)=%f' % RRI14Last )

		p('set title "%s, Price: %.2f ' \
		' (5,7,10)%% = (%.2f, %.2f, %.2f) '
		' (5,7,10)%% = (%.2f, %.2f, %.2f)%%"' \
			% (symbol, current_price, \
			RRI9, RRI11, RRI14, RRI9Last, RRI11Last, RRI14Last ) )

		p('set terminal png size 1200,600')
		cmd = 'set output \'%s\'' % png_file 
		#print cmd
		p(cmd)
		p('set datafile sep ","')
		p('set timefmt "%Y-%m-%d"')
		p('set xdata time')
		p('set xrange [ "%s":"%s" ]' % (left_x, right_x))
		p('set format x ""')
		p('unset grid')
		p('set tmargin')
		p('set lmargin 10')
		p('set bmargin 0')
		p('set multiplot')
		p('set size 1, 0.4')
		p('set origin 0, 0.6')
		if os.path.isfile( ROI_file ) is False:
			p('plot RRI9(x) title "9%",RRI11(x) title "11%", RRI14(x) title "14%", "' + price_file + '" using 1:7 notitle with lines')
		else:
			cmd = 'plot "%s" using 1:3 title "9%%" with lines, "%s" using 1:4 title "11%%" with lines, "%s" using 1:5 title "14%%" with lines, "%s" using 1:7 notitle with lines' % (ROI_file, ROI_file, ROI_file, price_file )

			p(cmd)


		p('set grid')
		p('set title ""')
		p('set tmargin 0')
		p('set bmargin 0')
		p('set xdata time')
		p('set timefmt "%Y-%m-%d"')
		p('set xrange [ "%s":"%s" ]' % (left_x, right_x))
		p('set format x ""')
		p('set size 1.0, 0.3')
		p('set origin 0.0, 0.3')
		p('plot "' + price_file + '" using 1:($6/1000) title "volume x1000" with impulses')

		p('set xdata time')
		p('set timefmt "%Y-%m-%d"')
		p('set format x "%y/%m/%d"')
		#p('set xtics ("2010/01/01","2011/01/01")')
		p('set size 1.0, 0.3')
		p('set origin 0.0, 0.0')
		p('set bmargin')
		p('set xrange [ "%s":"%s" ]' % (left_x, right_x))
		p('plot "' + dividend_file + '" using 1:2 title "dividend" with linespoints')
		p('clear')
		p('set yr [GPVAL_DATA_Y_MIN*0.9:GPVAL_DATA_Y_MAX *1.1]')
		p('replot')
		p('unset multiplot')

		#time.sleep(1)
		#os.system( 'open %s' % (symbol + '.png') ) 

		p('reset')
		p('set key left')
		p('set output \'%s\'' % png_file2)
		p('set datafile sep ","')
		p('set timefmt "%Y-%m-%d"')
		p('set xdata time')
		p('unset grid')
		p('set multiplot layout 2,2')

		p('set xrange [ "%s":"%s" ]' % (year_date, last_x))
		p('plot "' + price_file + '" using 1:7 title "1 year" with lines ' )

		p('set xrange [ "%s":"%s" ]' % (three_month_date, last_x))
		p('plot "' + price_file + '" using 1:7 title "3 monthes" with lines ' )

		p('set xrange [ "%s":"%s" ]' % (month_date, last_x))
		p('plot "' + price_file + '" using 1:7 title "1 month" with linespoints pt 5' )

		p('set xrange [ "%s":"%s" ]' % (week_date, last_x))
		p('plot "' + price_file + '" using 1:7 title "1 week" with linespoints pt 5 ' )




if __name__ == '__main__':
	if len(sys.argv) == 1:
		print "Usage: ", sys.argv[0], " SYMBOL"
		sys.exit(0)

	for x in sys.argv[1:]:
                p = plot()
		p.plot( x, path='PNG', cached=False )
