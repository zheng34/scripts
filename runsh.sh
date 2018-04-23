#!/bin/bash

for i in ?????.hdf; do
	if [ ! -f ${i%.hdf}.new.lst ]; then
		screenImage $i
	fi
done
#for i in ?????.hdf;
#	 if [ ! -f ${i%.hdf}.new.lst ] ; then ;  do screenI
