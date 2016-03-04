#!/usr/bin/python

import cPickle
import pprint

with open('user/favlist.cpickle') as f:
	favlist = cPickle.load( f )

	pprint.pprint(favlist)
