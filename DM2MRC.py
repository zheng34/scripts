#!/usr/bin/env python
# byZheng liu, 2017-08-31
# $Id$

from EMAN2 import *
import os, sys, math
from optparse import OptionParser
from collections import defaultdict

def main():
   
	particles = []
	imageFile1 = sys.argv[1]
	fp = open(imageFile1,'r')
	lines = fp.readlines()
	
	fp2 = open(cmdfile, 'wt')

	for l in lines:
		tkns = l.split()
			
		cmd = " e2proc2d.py %s-*.dm4 %s.mrcs " % (tkns,tkns)
					
        	#os.system("e2proc2d.py %s-%4d.dm4 %s.mrcs"%(tkns,j,i))
		print cmd
                fp2.write("%s\n" % (cmd))
				
	fp.close()
	fp2.close()
	cmd = "runpar proc=%s file=%s nofs" % (progs, cmdfile)
	print cmd
	os.system(cmd)
	sys.exit()


if __name__== "__main__":
    main()
