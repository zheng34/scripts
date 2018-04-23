#!/bin/bash
#echo input starting name
COUNTER=10000
for i in "$@" ; do
                echo $i 
#                COUNTER=100

                ln -s $i ${COUNTER}.mrc
                # while [  $COUNTER -lt $classNumber ]; do
                #nn=`awk -v class=$COUNTER '{ if ($22==class) print $10 }' $i | wc -l `
                #echo The iteration $i  class$COUNTER $nn  
                let COUNTER=COUNTER+1

done
