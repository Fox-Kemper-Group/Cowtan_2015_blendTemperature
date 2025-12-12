# Calculate area weighted monthly temperatures from map data
# Usage:
#  python temp.py my.dat > my.temp


import sys, numpy, scipy.stats, math
from Scientific.IO import NetCDF 


# write a month of map data
def write_map( year, month, tmap ):
  lines = ["%4d %2d\n"%(year,month)]
  for i in reversed(range(tmap.shape[0])):
    s = ""
    for j in range(tmap.shape[1]):
      val = tmap[i,(j+tmap.shape[1]/2)%tmap.shape[1]]
      if not numpy.isnan(val):
        s += "%7.3f "%(val)
      else:
        s += "-99.9 "
    lines.append( s[:-1] + "\n" )
  return lines


# MAIN PROGRAM
# default values

nc = NetCDF.NetCDFFile(sys.argv[1], "r")
print >> sys.stderr, nc.variables.keys()
lats1 = nc.variables["lat"].getValue()
lons1 = nc.variables["lon"].getValue()
temp = nc.variables[sys.argv[2]].getValue()
times = nc.variables["time"].getValue()/10000
nc.close()
print >> sys.stderr, temp.shape


# dates
dates = numpy.floor(times)+numpy.floor(100*(times%1.0))/12-1.0/24
print >> sys.stderr, dates

# output final map
for i in range(dates.shape[0]):
  y = int(dates[i])
  m = int(12*dates[i])%12+1
  for l in write_map(y,m,temp[i,:,:]): print l,

