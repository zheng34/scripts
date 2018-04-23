#!/usr/bin/env python

# byZheng liu, 2013-11-12
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
	fp2 = open(sys.argv[2],'r')
	lines2 = fp2.readlines()
	fp3 = open("outputfile", 'w')
	fp3.write("partilce\t"+"\t\t\t\t\t\t\t\t"+"\tangle"+"\t"+"distance\n")
	#dd = []
	for l in lines:
		tkns = l.split()
		if len(tkns) < 3 and len(tkns) >1:
			if tkns[0]== '_rlnAngleRot':
				phia=tkns[1]
				phiN=int(phia[1:]) -1	
			elif tkns[0]== '_rlnAngleTilt':
				thetaa=tkns[1]
				thetaN=int(thetaa[1:]) -1
			elif tkns[0]== '_rlnAnglePsi':
				psia=tkns[1]
				psiN=int(psia[1:]) -1	
			elif tkns[0]== '_rlnOriginX':
				Xshift=tkns[1]
				XshiftN=int(Xshift[1:])-1
			elif tkns[0]== '_rlnOriginY':
				Yshift=tkns[1]
				YshiftN=int(Yshift[1:])-1
			elif tkns[0]== '_rlnImageName':
				Image=tkns[1]
				ImageN=int(Image[1:])-1
		else:
			pass

	for k in lines:
		tkns = k.split()
		if len(tkns) > 3:
			ptcl = {}  
			img = tkns[ImageN]	
			ptcl["particle"] = img
			a= float(tkns[phiN])
			b= float(tkns[thetaN])
			c= float(tkns[psiN])
			t1=Transform({"type":"spider","phi":a,"theta":b,"psi":c})
			#ptcl["transform"] = t        
			xc = float(tkns[XshiftN])
			yc = float(tkns[YshiftN])
			ptcl["center"]=( float(xc), float(yc) )
			if img not in particles:
                                particles.append(img)
	
			for kk in lines2:
				tkns3 = kk.split()
				if len(tkns3) > 3:
					if tkns3[ImageN] == img:
						ptcl2 = {}
						img2 = tkns3[ImageN]
						a2= float(tkns3[phiN])
						b2= float(tkns3[thetaN])
						c2= float(tkns3[psiN])
						t2=Transform({"type":"spider","phi":a2,"theta":b2,"psi":c2})
						xc = float(tkns3[XshiftN])
						yc = float(tkns3[YshiftN])
						ptcl2["center"]=( float(xc), float(yc) )
						angle = compareAngle(t1,t2)
						ddd = distance (ptcl["center"],ptcl2["center"]) 
						ss = "%13.3f%13.3f\n" %( angle, ddd)
						fp3.write( img + ss)
	fp.close()
	fp2.close()
	fp3.close()
	sys.exit()

def compareAngle(t1,t2):
	return angleDifference(t1, t2)

def distance(d1, d2):
	x1,y1=d1
	x2,y2=d2
	q= sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))
	return q 

if __name__== "__main__":
    main()



