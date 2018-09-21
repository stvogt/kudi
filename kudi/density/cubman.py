#! /usr/bin/python

import sys
import commands, os

def sq_cube(cubefile):

  print "taking square of cubefile:  "+cubefile
  f = open(cubefile, 'r')
  lines = f.readlines()
  f.close()
  header=[]
  header.append(lines[0]) 
  header.append(lines[1]) 
  for lineNum in range(2,len(lines)):
    if len(lines[lineNum].split()) == 6:
      startline = lineNum
      break
    header.append(lines[lineNum])
  
  f = open(cubefile+"_sq",'w')

  for listitem in header:
  	f.write(listitem)
  
  for lineNum in range(startline,len(lines)):
    line_list = lines[lineNum].split()
    for lineitem in line_list:
      vol = lineitem
      vol_sq = float(vol)*float(vol)
      vol_sq_formated = "%6.5E" % vol_sq
      f.write(' '+str(vol_sq_formated)+' ')
    f.write('\n')
  f.close()
  return cubefile+"_sq"

def mult_cube(cubefile, factor):

  print "Multiplying cubefile:  "+cubefile+" by "+str(factor)
  f = open(cubefile, 'r')
  lines = f.readlines()
  f.close()

  header=[]
  header.append(lines[0]) 
  header.append(lines[1]) 
  
  for lineNum in range(2,len(lines)):
    if len(lines[lineNum].split()) == 6:
      startline = lineNum
      break
    header.append(lines[lineNum])
  
  f = open(cubefile+"_mult",'w')
  for listitem in header:
  	f.write(listitem)
  
  for lineNum in range(startline,len(lines)):
    line_list = lines[lineNum].split()
    for lineitem in line_list:
      vol = lineitem
      vol_mult = float(vol)*float(factor)
      vol_mult_formated = "%6.5e" % vol_mult
      f.write(' '+str(vol_mult_formated)+' ')
    f.write('\n')
  f.close()
  return cubefile+"_mult"

def sum_cube(cub1,cub2):
  f = open(cub1, 'r')
  lines1 = f.readlines()
  f.close()

  f = open(cub2, 'r')
  lines2 = f.readlines()
  f.close()

  header=[]
  header.append(lines[0]) 
  header.append(lines[1]) 

  for lineNum in range(2,len(lines1)):
    if len(lines1[lineNum].split()) == 6:
      startline = lineNum
      break
    header.append(lines[lineNum])
  
  f = open(cub1+cub2+"_add",'w')
  for listitem in header:
  	f.write(listitem)
  for lineNum in range(startline,len(lines1)):
    line_list1 = lines1[lineNum].split()
    line_list2 = lines2[lineNum].split()
    for lineitemNum in range(0,len(line_list1)):
      vol1 = line_list1[lineitemNum]
      vol2 = line_list2[lineitemNum]
      vol_add = float(vol1)+float(vol2)
      vol_add_formated = "%6.5E" % vol_add
      f.write(' '+str(vol_add_formated)+' ')
    f.write('\n')
  f.close()

def sum_total(cub1,cub2):
  print "obtainig the compounded sum of the cubes:  " +cub1+" and "+cub2
  f = open(cub1, 'r')
  lines1 = f.readlines()
  f.close()

  f = open(cub2, 'r')
  lines2 = f.readlines()
  f.close()

  header=[]
  header.append(lines1[0]) 
  header.append(lines1[1]) 

  for lineNum in range(2,len(lines1)):
    if len(lines1[lineNum].split()) == 6:
      startline = lineNum
      break
    header.append(lines1[lineNum])
  
  f = open(cub1, 'w')
  for listitem in header:
  	f.write(listitem)
  for lineNum in range(startline,len(lines1)):
    line_list1 = lines1[lineNum].split()
    line_list2 = lines2[lineNum].split()
    for lineitemNum in range(0,len(line_list1)):
      vol1 = line_list1[lineitemNum]
      vol2 = line_list2[lineitemNum]
      vol_add = float(vol1)+float(vol2)
      vol_add_formated = "%6.5E" % vol_add
      f.write(' '+str(vol_add_formated)+' ')
    f.write('\n')
  f.close()
  return cub1

def substract_cube(cub1,cub2):
  f = open(cub1, 'r')
  lines1 = f.readlines()
  f.close()

  f = open(cub2, 'r')
  lines2 = f.readlines()
  f.close()

  header=[]
  header.append(lines1[0]) 
  header.append(lines1[1]) 

  for lineNum in range(2,len(lines1)):
    if len(lines1[lineNum].split()) == 6:
      startline = lineNum
      break
    header.append(lines1[lineNum])
  
  f = open(cub1+cub2+".sub",'w')
  for listitem in header:
  	f.write(listitem)
  for lineNum in range(startline,len(lines1)):
    line_list1 = lines1[lineNum].split()
    line_list2 = lines2[lineNum].split()
    for lineitemNum in range(0,len(line_list1)):
      vol1 = line_list1[lineitemNum]
      vol2 = line_list2[lineitemNum]
      vol_add = float(vol1)-float(vol2)
      vol_add_formated = "%6.5E" % vol_add
      f.write(' '+str(vol_add_formated)+' ')
    f.write('\n')
  f.close()
  return cub1+cub2+".sub"

def generate_cube(orbital,fchk,cube_output,sq=False):
  cub = "orbital_"+str(orbital)+"_"+cube_output
  input1="cubegen 0 MO="+str(orbital)+" "+fchk+" "+cub+" 0 h" 
  print input1
  job1 = commands.getstatusoutput(input1)
  if sq:
    sq_cub = sq_cube(cub)
    os.system("rm "+cub)
    return sq_cub
  else:
    return cub

#Homo=sys.argv[1]
#Lumo=sys.argv[2]
#substract_cube(Lumo,Homo)
