#!/usr/bin/env python
#this program is for changing groupname to groupNumber
# this program is prepared by Zheng Liu, any question about it could be contact to zl2354@columbia.edu

import os, sys, math
from optparse import OptionParser
import subprocess

def main():
	imageFile = sys.argv[1]
	outputfile = sys.argv[2]
	fp = open(imageFile,'r')
	tempout = fp.readlines()
	fp2 = open(outputfile,"w+")
	fp2.write("# micrograph\t\t\tdefocus\t\tdefocusU\tdefocusV\tastigAmp\tastigAng\t  cc\t     cs  voltage     ac     apix\n")
	#groups = []
	cs = 0.01
	volt = 300
	ac = 0.12
	apix = 1.045
	# parse the output log file for the final focus values
	resultLine = ""
	for k in tempout:
		aa = k.split(".")[0]
		mbase = k.split("_c")[0]
		file = "%s_ctffind3.log" % (aa)
		aa2 = "%sm" % (aa)
		print file
		for l in open(file):
			#print file  
			if l.find("Final Values")!=-1:
				resultLine = l
				break
                #os.remove(tempout)

		if resultLine:
			tokens = resultLine.split()
			focus1, focus2, astigAng, cc = tokens[:4]
			#focus1 = float(focus1)/1e4
			#focus2 = float(focus2)/1e4
			#focusMean = (focus1+focus2)/2.
			focus1 = float(focus1)
			focus2 = float(focus2)
			focusMean = (focus1+focus2)/2.
			focusAstig = abs(focus1-focus2)/2.
			#mbase = l.sp
			#mbase = os.path.splitext(os.path.basename(m))[0]
			s = "%12s\t%13.6f\t%13.6f\t%13.6f\t%8.6g\t%8s\t%8s%8g%8g%8g%8g" % (aa2,focusMean,focus1,focus2,focusAstig,astigAng,cc,cs,volt,ac,apix)
			print s
			fp2.write("%s\n" % (s))
			fp.close()
		#with lock:
		#	if os.path.exists(options.ctffile):
		#		fp = open(options.ctffile,"a")
		#	else:
		#		fp = open(options.ctffile,"w")
		#		fp.write("# micrograph\tdefocus\tastigAmp\tastigAng\tcc\t       cs  voltage       ac     apix\n")
		#		mbase = os.path.splitext(os.path.basename(m))[0]
		#		s = "%12s\t%8g\t%8g\t%8s\t%8s\t%8g\t%8g\t%8g\t%8g" % (mbase, focusMean, focusAstig, astigAng, cc, options.cs, options.volt, options.ac, options.apix)
		#		print s
		#		fp.write("%s\n" % (s))
		#		fp.close()
################################################################################################################################################################	
	fp.close()
	fp2.close()
	#outputfile2 = "%s2.txt" % (outputfile.split(".")[0])
	#cmd2 = "awk '!a[$0]++' %s > %s" % (outputfile,outputfile2)
	#os.system(cmd2)
	#os.link(outputfile)
	sys.exit()
if __name__=="__main__":
	main()
	
	
	
