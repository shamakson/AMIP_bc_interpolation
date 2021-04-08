#!/usr/bin/python3

import xarray as xr
import numpy as np
import sys, getopt
from cdo import Cdo
import glob

cdo=Cdo()

def main(argv):
   infile = ''
   outfile = ''
   closure = 'cyclic'
   try:
      opts, args = getopt.getopt(argv,"c:hi:o:",["infile=","outfile="])
   except getopt.GetoptError:
      print('modify_ocean_bc.py -i <infile> -o <outfile> -c <closure>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('modify_ocean_bc.py -i <infile> -o <outfile> -c <closure>')
         sys.exit()
      elif opt in ("-i", "--infile"):
         infile = arg
      elif opt in ("-o", "--outfile"):
         outfile = arg
      elif opt in ("-c", "--closure"):
         closure = arg

   return(infile,outfile,closure)

# if __name__ == "__main__":
infile, outfile, closure = main(sys.argv[1:])

print('Input file is '+infile)
print('Output file is '+outfile)
print('using '+closure+' closure criterium.')

print("open infile and read dimensions...")

varname=cdo.showvar(input=infile)
var=str(varname[0])

dsin=xr.open_dataset(infile)

lon=dsin.lon
lat=dsin.lat
time=dsin.time

nlon=lon.shape[0]
nlat=lat.shape[0]
ntime=time.shape[0]

print("Dimensions:")
print("nlon: "+str(nlon))
print("nlat: "+str(nlat))
print("ntime: "+str(ntime))

U=np.zeros([ntime,ntime])

print("Creating matrix to solve system of linear equation...")

if closure == "cyclic":
   U[0,]=np.concatenate([np.array([1,1/6]),np.zeros(ntime-3),np.array([1/6])])
   U[ntime-1,]=np.concatenate([np.array([1/6]),np.zeros(ntime-3),np.array([1/6,1])])
   istart=1
elif closure == "f_prescr_l_const":
   U[0,]=np.concatenate([np.array([4/3,-1/6]),np.zeros(ntime-2)])
   U[1,]=np.concatenate([np.array([0,4/3,1/6]),np.zeros(ntime-3)])
   U[ntime-1,]=np.concatenate([np.zeros(ntime-2),np.array([1/6,7/6])])
   istart=2
elif closure == "f_prescr_l_prescr":
   U[0,]=np.concatenate([np.array([4/3]),np.zeros(ntime-1)])
   U[1,]=np.concatenate([np.array([0,4/3,1/6]),np.zeros(ntime-3)])
   U[ntime-1,]=np.concatenate([np.zeros(ntime-1),np.array([4/3])])
   istart=2
elif closure == "f_const_l_prescr":
   U[0,]=np.concatenate([np.array([7/6,1/6]),np.zeros(ntime-2)])
   U[ntime-1,]=np.concatenate([np.zeros(ntime-1),np.array([4/3])])
   istart=1
elif closure == "f_const_l_const":
   U[0,]=np.concatenate([np.array([7/6,1/6]),np.zeros(ntime-2)])
   U[ntime-1,]=np.concatenate([np.zeros(ntime-2),np.array([1/6,7/6])])
   istart=1

for i in range(istart,ntime-1):
   U[i,]=np.concatenate([np.zeros(i-1),np.array([1/6,1,1/6]),np.zeros(ntime-2-i)])

print("Matrix created (closure criterion was: "+closure+")")
print("Inverting matrix...")

Uinv=np.linalg.inv(U)

print(Uinv)

print("Matrix inverted.")
print("Create outputfile: "+outfile)

out=np.zeros((ntime,nlat,nlon))

print("Outputfile created.")

for x in range(0,nlon):

   print("Compute SSTs for longitude "+str(x+1)+" of "+str(nlon))

   for y in range (0,nlat):

      if var == "sst":
         S=dsin.sst.isel(lon=x,lat=y)
      elif var == "sic":    
         S=dsin.sic.isel(lon=x,lat=y)

      T=4/3*np.matmul(S,Uinv)

      for z in range(0,ntime):
         out[z][y][x]=T[z]

dsout = xr.Dataset({var: (('time', 'lat', 'lon'), out)},coords={'time': time,'lat': lat,'lon': lon})
dsout.to_netcdf(outfile)

print("complete.")

quit()
