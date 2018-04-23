#!/usr/bin/env python

# byZheng liu, 2013-11-12
# $Id$

#import EMAN2
from EMAN2 import *
import os, sys, math
from optparse import OptionParser

#_rlnOriginX #17 
#_rlnOriginY #18 
#_rlnAngleRot #19 
#_rlnAngleTilt #20 
#_rlnAnglePsi #21 
def main():
    boxsize = int (sys.argv[3])
    ptcls = []
    imageFile = sys.argv[1]
    fp = open(imageFile,'r')
    lines = fp.readlines()
    for l in lines:
        tkns = l.split()
        if len(tkns) < 3 and len(tkns) >1:
            if tkns[0]== '_rlnAngleRot':
                phia=tkns[1]
                phiN=int(phia[1:]) -1	
                print 'phiN is %d' %(phiN,)
            elif tkns[0]== '_rlnAngleTilt':
                thetaa=tkns[1]
                thetaN=int(thetaa[1:]) -1
                print 'thetaN is %d' %(thetaN,)
            elif tkns[0]== '_rlnAnglePsi':
                psia=tkns[1]
                psiN=int(psia[1:]) -1	
                print 'psiN is %d' %(psiN,)
            elif tkns[0]== '_rlnOriginX':
                Xshift=tkns[1]
                XshiftN=int(Xshift[1:])-1
                print 'XshiftN is %d' %(XshiftN,)
            elif tkns[0]== '_rlnOriginY':
                Yshift=tkns[1]
                YshiftN=int(Yshift[1:])-1
                print 'YshiftN is %d' %(YshiftN,)
            elif tkns[0]== '_rlnImageName':
                Image=tkns[1]
                ImageN=int(Image[1:])-1
                print 'ImageN is %d' %(ImageN,)
            else:
                #print 'adjugement is done'
                pass
	
    for k in lines:
        tkns = k.split()
        if len(tkns) > 3:
            ptcl = {}
            img = tkns[ImageN].split('@')[1]
            index = int(tkns[ImageN].split('@')[0]) -1 
            ptcl["index2"] = int(index)
            ptcl["file"] = img
# convert angles
#'%.4f'%
            a= float(tkns[phiN])
            b= float(tkns[thetaN])
            c= float(tkns[psiN])
            t=Transform({"type":"spider","phi":a,"theta":b,"psi":c})
            d1=t.get_params("eman")
            alt = d1["alt"]
            az = d1["az"]
            phi= d1["phi"]
            ptcl["euler"]=( float(alt), float(az), float(phi) )
# convert center
            dsize= int (boxsize/2)		
            xc = dsize +float(tkns[XshiftN])
            yc = dsize -float(tkns[YshiftN])
            yc = yc -1
            ptcl["center"]=( float(xc), float(yc) )
            ptcls.append(ptcl)



    fp2 = open(sys.argv[2], 'w+')
    fp2.write("#LST\n")
    for i, ptcl in enumerate(ptcls):
        imageP = ptcl["file"]
        no = ptcl["index2"]
        xc, yc = ptcl["center"]
        alt, az, phi = ptcl["euler"]
        fp2.write("%d\t%s\teuler=%g,%g,%g\tcenter=%g,%g\n" % (no, imageP, alt, az, phi,xc,yc))

    fp2.close()
   
    fp.close()
    sys.exit()

if __name__== "__main__":
    main()



