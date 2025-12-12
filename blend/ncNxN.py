# Calculate area weighted monthly temperatures from map data
# Usage:
#  python temp.py my.dat > my.temp


import math
import sys

import netCDF4
import numpy
import scipy.stats


# write a month of map data
def write_map(year, month, tmap):
  lines = ["%4d %2d\n" % (year, month)]
  for i in reversed(range(tmap.shape[0])):
    s = ""
    for j in range(tmap.shape[1]):
      val = tmap[i, (j + tmap.shape[1] // 2) % tmap.shape[1]]
      if not numpy.isnan(val):
        s += "%7.3f " % (val)
      else:
        s += "-99.9 "
    lines.append(s[:-1] + "\n")
  return lines


# MAIN PROGRAM
# default values

nc = netCDF4.Dataset(sys.argv[1], "r")
print(nc.variables.keys(), file=sys.stderr)
lats1 = nc.variables["lat"][:]
lons1 = nc.variables["lon"][:]
temp = nc.variables[sys.argv[2]][:]
times = nc.variables["time"][:] / 10000
nc.close()
print(temp.shape, file=sys.stderr)


# dates
dates = numpy.floor(times) + numpy.floor(100 * (times % 1.0)) / 12 - 1.0 / 24
print(dates, file=sys.stderr)

# output final map
for i in range(dates.shape[0]):
  y = int(dates[i])
  m = int(12 * dates[i]) % 12 + 1
  for line in write_map(y, m, temp[i, :, :]):
    sys.stdout.write(line)

