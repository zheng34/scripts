#!/usr/bin/env python
###

import glob,sys,os,time,math,random,string,re,threading,Queue,uuid,pprint,fileinput,multiprocessing
from optparse import OptionParser
from collections import defaultdict

from subprocess import call

def main():
	(options, starfile) =  parse_command_line()
	args = (starfile, options)
	if starfile[0].find("star") != -1:
		micrographs = process_starfile(args)
		print "process_starfile is done"
	if starfile[0].find("box"):
		micrographs = process_boxfile(args) 
	#print micrographs	
	#if len(micrographs) > 10:
	pool = multiprocessing.Pool(processes=options.cpu)
	manager = multiprocessing.Manager()
	lock = manager.Lock()
	tasks = []
	if len(micrographs) > 2:
		for i, m in enumerate(micrographs):
			tasks += [ (micrographs, i, options, lock) ]
	results = pool.map(process_oneMics, tasks, chunksize=1)
	pool.close()
	pool.join()

	#(options, micrographs) =  parse_command_line()
	#args = (micrographs, options)
	#if processMics(args) == 0:
	#print "all polishings are done "


def process_starfile(args1):
	
	inputfile, options = args1
	inputfile1 = inputfile[0]
	outputfile = "reordered_" + inputfile1
	
	fp2 = open(inputfile1,'r')
	klines = fp2.readlines()
	fp3 = open(outputfile, 'w')

	nsize = int(options.boxsize)
	nx = int(options.nx)
	ny = int(options.ny)	

	fullmicrographs = []
	micrographs = []
	dd = defaultdict(list)
	for l in klines:
		#items = l.split()
		if len( l.split()) < 3 :
			fp3.write(l)
			if len( l.split()) > 0 :
				items = l.split()
				if items[0]=='_rlnImageName':
					particleNt = items[1]
					particleN = int(particleNt[1:]) -1
				elif items[0]=='_rlnMicrographName':
					micrographNt = items[1]
					micrographN = int(micrographNt[1:])-1
				elif items[0]=='_rlnCoordinateX':
					coordninateXNt = items[1]
                                	coordninateXN = int(coordninateXNt[1:])-1
				elif items[0]=='_rlnCoordinateY':
					coordninateYNt = items[1]
                                	coordninateYN = int(coordninateYNt[1:])-1
#				elif items[0]=='_rlnAutopickFigureOfMerit':
#					AutopickFigureOfMeritNt = items[1]
#					AutopickFigureOfMeritN = int(AutopickFigureOfMeritNt[1:])-1
				else:
					pass
	#nx = 3710
	#ny = 3838	
	for kk in klines:
		itemss = kk.split()
		if len(itemss) > 3 : 
			if itemss[micrographN] not in fullmicrographs:
				fullmicrographs.append(itemss[micrographN])
				f = re.split(r'/|\_D',itemss[micrographN])[1] 
				micrographs.append(f)
				dd[f].append(kk)
			elif itemss[micrographN] in fullmicrographs:		
				f = re.split(r'/|\_D',itemss[micrographN])[1]
				dd[f].append(kk)

	for i in fullmicrographs:
		#microitems = re.split(r'/|\.', i)
		microitems = re.split(r'/|\_D', i)
		autopickfile = open(microitems[1]+"_autopick.star",'w')
		boxfile = open(microitems[1]+ ".box",'w') #### add for box file
		autopickfile.write("\n")
		autopickfile.write("data_images\n")
		autopickfile.write("\n")
		autopickfile.write("loop_\n")
		autopickfile.write("_rlnCoordinateX #1\n")
		autopickfile.write("_rlnCoordinateY #2\n")
#		autopickfile.write("_rlnAutopickFigureOfMerit #3\n")
		coordfile = open(microitems[1]+".coord",'w')
		coordfile.write("\tx\ty\tdensity\n")
		size = 100 ### box file
		for index,pp in enumerate(dd[microitems[1]]):
			itemsa = pp.split()
			xpos_relion = int (float (itemsa[coordninateXN])) - int (size/2)
			ypos_relion = int (float (itemsa[coordninateYN])) - int (size/2)
			xposs=xpos_relion-size/2
			xposf=xpos_relion+size/2-1
			yposs=ypos_relion-size/2
			yposf=ypos_relion+size/2-1
			if xposs >= 1 and xposf <= nx:
				xwrite = xpos_relion
			elif xposs < 1:
				xwrite = size/2+1
				xpos_relion = size/2+1
			else:
				xwrite = nx-size/2
				xpos_relion= nx-size/2
			if yposs >= 1 and yposf <= ny:
				ywrite = ypos_relion
			elif yposs < 1:
				ywrite = size/2+1
				ypos_relio = size/2+1

			else:
				ywrite = ny-size/2
				ypos_relio = ny-size/2
			s = "\t%s\t%s\t%s\n" % ( str(xwrite), str(ywrite), "0.0")
			coordfile.write(s)
#			s2 = "%13.f%13.6f  %13.6f\n" % ( float(itemsa[coordninateXN]), float(itemsa[coordninateYN]), float(itemsa[AutopickFigureOfMeritN]))
#			autopickfile.write(s2)
			itemsb = pp.split(itemsa[particleN])
			reorderparticles = "%06d@%s" %( int(index)+1, itemsa[particleN].split('@')[1])
			#sss1 = 	
			fp3.write(itemsb[0]+reorderparticles+itemsb[1])
			
			s3= "%-d\t%-d\t%-d\t%-d\n" % ( xpos_relion, ypos_relion, size, size ) #########for box file
			boxfile.write (s3) ########box file

		autopickfile.close()
		coordfile.close()
		boxfile.close()
	#print micrographs
	return micrographs

#def process_coordfile():
#def process_boxfile(args):
#	boxfiles, options = args
#	nsize = int(options.boxsize)
#	nscale = int(options.scale)
#	nx = int(options.x)
#	ny = int(options.y)
#	micrographs = []
#	for f in boxfiles:
#		output=os.path.basename(f)
#		output1 = output.split(".")[0]
#		micrographs.append(output1)
#		newboxfile = "%s.coord" % (output1)
#		fp = open(newboxfile, 'w')
#		fp.write("\tx\ty\tdensity\n")
#		boxfile = open(f,'r')
#		klines = boxfile.readlines()
#		for l in klines:
#			items = l.split()
#			if len(items) < 4 and len(items) > 4:
#				print "File format is not correct!"
#			xpos_relion = (int(items[0])+int(items[2])/2)*nscale + 15
#			ypos_relion = (int(items[1])+int(items[3])/2)*nscale + 15
#
#			xposs=xpos_relion-nsize/2
#			xposf=xpos_relion+nsize/2-1
#			yposs=ypos_relion-nsize/2
#			yposf=ypos_relion+nsize/2-1
#
#			if xposs >= 1 and xposf <= nx:
#				xwrite = xpos_relion
#                                #print "Left edge is out"
#			elif xposs < 1:
#				xwrite = nsize/2+1
#				print "Right edge is out"
#			else:
#				xwrite = nx-nsize/2
#				print "Left edge is out"
#
#			if yposs >= 1 and yposf <= ny:
#				ywrite = ypos_relion
#			elif yposs < 1:
#				ywrite = nsize/2+1
#				print "Bottom edge is out"
#			else:
#				ywrite = ny-nsize/2
#				print "Top edge is out"
#			s = "\t%s\t%s\t%s\n" % ( str(xwrite), str(ywrite), "0.0")
#			fp.write(s)
#
#		fp.close()
#		boxfile.close()
#	return micrographs

#def process_oneMics(argss):
#	micrographs, index, options, lock = argss
#	m = micrographs[index].split('.')[0]
#	print "Processing %d/%d images: %s" % (index + 1, len(micrographs), m)
####################################################################################For .bz files##################
#	bzfile = "%s.frames.bz2" % (m)
#	stacksfile = "%s_0.mrcs" % (m) #### Here needs modify according to the frames names.
#	if os.path.exists(bzfile):
#		#o1 = 'unzip_'+os.path.basename(f)
#		if ncall(["bunzip2", "-c", bzfile], stacksfile) != 0:
#			print "Unzip failed"
#			sys.exit(1)
########################################################################################################
	#stacksfile = "%s.frames.mrc" % (m) #### Here needs modify according to the frames names.
#	print stacksfile
	#o = "gc_" + stacksfile
#	filestack = 0
##############Following section is for checking if the files have been generated #####################
#	polishedfile = "%s.pol.mrcs"  % (m)
#	if os.path.exists(polishedfile) and os.stat(polishedfile).st_size !=0  :
		#statinfo = os.stat(polishedfile)
#		return 0 
##############Above section is for checking if the files have been generated #####################

#	if options.gainR: 
#		o = "gc_" + stacksfile
#		templist = "%s.lst" % (m)
		#os.remove(temppwr)
#		logGain = "%s.gainlog" % (m)
#		cmd = "./dosefgpu_flat %s %s %s %s > %s" % (stacksfile, o, options.refmrc, options.gpuid, logGain)
#		print "\t %s gain reference begins" % (m)
#		if os.system(cmd) == 0:
#                       print "\t %s gain rerence is finished" % (m)
#			filestack = 1
	
#		cmd0 = "echo %s > %s " % (o,templist)

#               if os.system(cmd0) == 0:
 #                       print "\t making parameter files"
		
#	else:
#		templist = "%s.lst" % (m)
#		cmd0 = "echo %s > %s " % (stacksfile,templist)
#		if os.system(cmd0) == 0:
#			print "\t making parameter files for mrcs"
#
	#mrcfile = "%.mrcs"
#	tempout = "%s_Pol.log" % (m)
#	tempcoord = "%s.coord" % (micrographs[index])
#	tempcoordlist = "%s.clist" % (micrographs[index])
#	cmd4 = "echo %s > %s " % (tempcoord,tempcoordlist)
#	if os.system(cmd4) == 0:
#		print "\t making parameter files for coordinates"
	
#	pfp = os.popen("%s > %s" % (options.exeFile, tempout),"w")
#	print "\t %s particle polishing begins" % (micrographs[index])
#	pfp.write("%s\n" % (templist))      # input mrc file 
#	pfp.write("%s\n" % (tempcoordlist))   
#	pfp.write("%g,%g,%g,%g,%g,%g,%g\n" % (options.boxsize, options.subboxsize, options.ri, options.apix, options.nsigma, options.rmax1, options.rmax2))
#	pfp.write("%d,%g,%g\n" % (options.expflag, options.volt, options.expframe))
#	pfp.write("%g,%g,%g,%g,%g\n" % (options.bfactor, options.smooth, options.exaggerate, options.zeroframe, options.invflag))
#	pfp.write("%g,%g,%g\n" % (options.neiflag, options.maxparts, options.sigma))
#	pfp.write("%g,%g\n" % (options.framefirst, options.framelast))
#	pfp.write("%g,%g\n" % (options.selectframefirst, options.selectframelast))
#	pfp.write("%g\n" % (options.factr))
#	pfp.write("%s\n" % (options.vecext))
#	pfp.write("%s\n" % (options.stkext))
#	pfp.close()
#	print "\t %s  particle polishing is done" % (micrographs[index])
	
#	if filestack == 1 :
#		os.remove( o )
#		if os.path.exists(bzfile):
#			os.remove(stacksfile)
#	return 0

def parse_command_line():
	usage="%prog Falcon*box  --[options]"
	#description="A Python program "
	description = "A Python program together developed by Zheng Liu to process particle polishing for frames collected by Falcon camera.\n"
	description += " It contains following functions:\n"
	description += "1, convert the eman box to multiple files like coordinate file, autopick.star etc.\n"
	description += ".\n"
	description += "2, check the particle coordinates if they are out of micrographs.If so, the coordinates will be adjusted;\n"
	description += "3, run the particle polishing programs in parallel;\n"
	description += " ... ... If you have problems on runing it, you can contact Zheng Liu for help."

	parser = OptionParser(usage=usage, description=description, version="1.2")


	parser.add_option("--reference",dest = "refmrc",type = "str", help = "[Required] the reference file, in mrc format,default to gain_image.mrc",default = "gain_image.mrc")
	parser.add_option("--gpuid",dest = "gpuid",type = "int",metavar = "<int>",help = "[Required] gpuid like 0,default to 0", default = 0)
	parser.add_option("--gainR",dest="gainR",type="int",metavar="<0|1>",help="flag to turn on (1) or off (0) refrence gain,default to 1", default = 0)
	

	parser.add_option("--scale", dest="scale",type="int",metavar="<pixel>",help="[Required] size with which to do the local alignment,default to 360", default = 1)
	parser.add_option("--x", dest="x",type="int",metavar="<pixel>",help="[Required] micrograph size, default to 4096", default = 4096)
	parser.add_option("--y", dest="y",type="int",metavar="<pixel>",help="[Required] micrograph size, default to 4096", default = 4096)





	parser.add_option("--boxsize", dest="boxsize",type="int",metavar="<pixel>",help="[Required] size with which to do the local alignment,default to 400", default = 400)
	parser.add_option("--subboxsize", dest="subboxsize",type="int",metavar="<pixel>",help="[Required] region of box to output for averages of particles. Use this if you want to align a bigger box than you output. Use 0 for subboxsize=boxsize,default to 0", default = 0)
	parser.add_option("--ri", dest="ri",type="int",metavar="<pixel>",help="[Required] radius of particle in pixels (used for Relion-style floating and normalization from outside of mask values,default to 170", default = 170)
	parser.add_option("--apix", dest="apix",type="float",metavar="<Angstrom/pixel>",help="[Required] size of image pixel in Angstroms, in the unit of Angstrom/pixel,default to 1.05", default = 1.05)
	parser.add_option("--nsigma", dest="nsigma",type="float",metavar="<nsigma>",help=" set pixels to image mean if their intensity is this number of standard deviations away from the mean (e.g. hot pixels will be set to mean), default to 5", default = 5)
	parser.add_option("--rmax1", dest="rmax1", type="float", metavar="rmax1", help="lowest resolution information to include in alignment (in Angstroms),,default to 400", default = 400)
	parser.add_option("--rmax2", dest="rmax2", type="float", metavar="rmax2", help="highest resolution information to include in alignment (in Angstroms),,default to 40", default = 40)
	parser.add_option("--expflag", dest="expflag", type="int", metavar="<expflag>", help="expflag: flag to turn on (1) or off (0) exposure weighting, ,default to 1", default = 1)
	parser.add_option("--voltage", dest="volt",type="float",metavar="<voltage>",help="[Required] the microscope's accelerating voltage, in unit of kV;not used if expflag=0,default to  300", default = 300)
	parser.add_option("--expframe", dest="expframe", type="float",metavar="<expframe>", help="[Required] Exposure used in electrons per A^2 per frame (not used if expflag=0),default to 1", default = 1)
	parser.add_option("--bfactor", dest="bfactor", type="int", metavar="<bfactor>", help="[Required] Temperature factor with which to downweight high spatial frquencies in alignment (in A^2),default to 2000", default = 2000)
	parser.add_option("--smooth", dest="smooth", type="int", metavar="<smooth>", help="[Required] Penalty used to enforce smooth trajectories. 1d4 means 1x10^4 in double precision. 0 is no penalty. Corresponds to Lambda in the manuscript,default to 1.0e4", default = 1.0e4)
	parser.add_option("--exaggerate", dest="exaggerate", type="int",metavar="<exaggerate>", help="[Required] Exaggeration to apply to output particle shifts to allow plotting-for visualization only.For example:5, default to 5", default = 5)
	parser.add_option("--zeroframe", dest="zeroframe", type="int",metavar="<zeroframe>", help="[Required]The frame that is defined as unshifted (i.e. 1 for 1st frame),default to 1", default = 1)
	parser.add_option("--invflag", dest="invflag",type="int",metavar="<0|1>",help="should density from aligned and averaged particles be inverted? If yes, floating and normalization are done afterward ,default to 1", default = 1)
	parser.add_option("--neiflag",dest="neiflag",type="int",metavar="<0|1>",help="flag to turn on (1) or off (0) local averaging of trajectories,default to 1", default = 1)
	parser.add_option("--maxparts",dest="maxparts",type="int",metavar="maxparts",help="maximum number of particles that have been selected in any micrograph (not used if neiflag=0),default to 350", default = 350)
	parser.add_option("--sigma",dest="sigma",type="int",metavar="<sigma>",help="Describes Guassian (in pixels) used to apply weights to trajectories in local averaging. Corresponds to sigma in JR's manuscript (not used if neiflag=0),default to 500", default = 500)
	parser.add_option("--framefirst",dest="framefirst",type="int",metavar="<framefirst>", help="[Required] First frame in movie to use in analysis,default to 1", default = 1)
	parser.add_option("--framelast",dest="framelast",type="int",metavar="<framelast>",help="[Required] Last frame in movie to use in analysis (if set to 0, the last frame available will be used,default to 0)", default = 0)
	parser.add_option("--selectframefirst",dest="selectframefirst",type="int",metavar="<selectframefirst>", help="[Required] First frame in movie to use in averaging, default to 1", default = 1)
	parser.add_option("--selectframelast",dest="selectframelast",type="int",metavar="<selectframelast>",help="[Required] Last frame in movie to use in averaging (if set to 0, the last frame available will be used,default to 0)", default = 0)
	parser.add_option("--factr",dest="factr",type="int",metavar="<factr>",help="[Required] precision with to which optmizer is set. 1d7 means 1x10^7 in double precision and seems sufficient, 1e1 is stringent, 1e14 is relaxed, default to 1e7", default = 1e7)
	parser.add_option("--vecext",dest="vecext",type="str",metavar="<vecext>",help=" extension of output vector files, default to vecext", default = "vecext")
	parser.add_option("--stkext",dest="stkext",type="str",metavar="<stkext>",help=" extension of output stacks of partice image,default to pol.mrcs", default = "pol.mrcs")

	

	parser.add_option("--suffix",dest="suffix", metavar="frames.mrcs", type='str', help="the frame files suffix", default="frames.mrcs")
	#parser.add_option("--particle_size",dest="particle_size", metavar="<n>", type='int', help="this is paritcle size. default to 360", default=360)
	parser.add_option("--nx",dest="nx", metavar="<n>", type='int', help="number of pixels of the micrographs of x axis, default to 3710", default=3710)
	parser.add_option("--ny",dest="ny", metavar="<n>", type='int', help="number of pixels of the micrographs of y axis, default to 3838", default=3838)
	parser.add_option("--exefile",dest="exeFile",type="string",metavar="<filename>",help="alignparts_lmbfgs executable file. default to alignparts_lmbfgs.exe",default="/opt/drift_correct/alignparts_lmbfgs.exe")

	#parser.add_option("--exefile",dest="exeFile",type="string",metavar="<filename>",help="alignparts_lmbfgs executable file. default to alignparts_lmbfgs.exe",default="/opt/drift_correct_beta/alignparts_lmbfgs.exe")
	parser.add_option("--cpu",dest="cpu", metavar="<n>", type='int', help="number of cpus to run, default to 1", default=1)


        if len(sys.argv)==1:
                parser.print_help()
                sys.exit(-1)

        (options, micrographs)=parser.parse_args()
	print micrographs
        if not len(micrographs):
                parser.print_help()
                print "\nPlease specify the images to process"
                sys.exit(-1)

	if options.cpu<=0:
		options.cpu = multiprocessing.cpu_count()

	return (options, micrographs)


if __name__== "__main__":
        main()
