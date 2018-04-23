#!/usr/bin/env python

# byZheng liu, 2017-11-29
# $Id$

#import EMAN2
#from EMAN2 import *
import os, sys, math
from optparse import OptionParser
import glob,sys,os,time,math,random,string,re,threading,Queue,uuid,pprint,fileinput,multiprocessing
from optparse import OptionParser
from collections import defaultdict



digits_upper = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
digits_lower = digits_upper.lower()
digits_upper_values = dict([pair for pair in zip(digits_upper, range(36))])
digits_lower_values = dict([pair for pair in zip(digits_lower, range(36))])

def encode_pure(digits, value):
	"encodes value using the given digits"
	assert value >= 0
	if (value == 0): return digits[0]
	n = len(digits)
	result = []
	while (value != 0):
		rest = value // n
		result.append(digits[value - rest * n])
		value = rest
	result.reverse()
	return "".join(result)

def decode_pure(digits_values, s):
	"decodes the string s using the digit, value associations for each character"
	result = 0
	n = len(digits_values)
	for c in s:
		result *= n
		result += digits_values[c]
	return result

def hy36encode(width, value):
	"encodes value as base-10/upper-case base-36/lower-case base-36 hybrid"
	i = value
	if (i >= 1-10**(width-1)):
		if (i < 10**width):
			return ("%%%dd" % width) % i
		i -= 10**width
		if (i < 26*36**(width-1)):
			i += 10*36**(width-1)
			return encode_pure(digits_upper, i)
		i -= 26*36**(width-1)
		if (i < 26*36**(width-1)):
			i += 10*36**(width-1)
			return encode_pure(digits_lower, i)
	raise ValueError("value out of range.")


def main():
   
	inputPDBfile = sys.argv[1]
	fp = open(inputPDBfile,'r')
	lines = fp.readlines()
	fp2 = open(sys.argv[2], 'w+')
	newl = " "
	for l in lines:
		tkns = l.split()
		if len(tkns) < 13 :
			fp2.write(l)
		if len(tkns) == 13 and int(tkns[1]) < 100000:
			fp2.write(l)
		if len(tkns) == 13 and int(tkns[1]) > 99999:
			kk = hy36encode ( 5, int(tkns[1]))
			print kk 
			#print "hehe"
			newl = "%s  %s  %-4s%3s %s %s%12s%8s%8s  %s %s%7s%5s\n" % ( tkns[0], kk, tkns[2], tkns[3],tkns[4],tkns[5],tkns[6],tkns[7],tkns[8],tkns[9],tkns[10],tkns[11], tkns[12] )
			#newl = l.replace (l, tkns[1], str(kk))
			fp2.write(newl)
	
    	fp2.close()
	fp.close()
	sys.exit()

if __name__== "__main__":
	main()



