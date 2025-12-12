import sys

import math
import numpy


# read map data
def read_map( lines ):
  # get latitude
  nlat = len(lines)-1
  for i in range(1,len(lines)):
    if len(lines[i].split()) == len(lines[0].split()):
      nlat = i-1
      break
  print("Lat ", nlat, file=sys.stderr)
  # get data
  data = []
  for k in range(0,len(lines),nlat+1):
    w = lines[k].split()
    month,year = sorted( [int(w[0]),int(w[1])] )
    date = year+month/12.0-1.0/24.0
    smap = []
    for j in range(nlat):
      row = []
      w = lines[j+k+1].split()
      for i in range(len(w)):
        if not '.' in w[i]:
          t = 0.01*float(w[i])
        else:
          t = float(w[i])
        if t <= -99.0: t = numpy.nan
        row.append(t)
      smap.append(row)
    smap.reverse()
    data.append( ( year, month, smap ) )
  return data


# write a month of map data
def write_map( year, month, smap ):
  tmap = reversed( smap )
  lines = ["%4d %2d\n"%(year,month)]
  for row in tmap:
    s = ""
    for val in row:
      if not numpy.isnan(val):
        s += "%7.3f "%(val)
      else:
        s += "-99.9 "
    lines.append( s[:-1] + "\n" )
  return lines


# anomalise maps
def anomalise( maps ):
  area = areas(len(maps))
  for year,month,map in maps:
    s, w = 0.0, 0.0
    for i in range(len(map)):
      for j in range(len(map[i])):
        if not numpy.isnan( map[i][j] ):
          s += area[i]*map[i][j]
          w += area[i]
    s /= w
    for i in range(len(map)):
      for j in range(len(map[i])):
        if not numpy.isnan( map[i][j] ):
          map[i][j] -= s


# calculate anomaly
def trend( maps, date1, date2, nmin ):
  year,month,tmap = maps[0]
  smap = [ [ 0.0 for j in range(len(tmap[i])) ] for i in range(len(tmap)) ]
  nmap = [ [   0 for j in range(len(tmap[i])) ] for i in range(len(tmap)) ]
  for i in range(len(smap)):
    for j in range(len(smap[i])):
      x = []
      y = []
      for year,month,tmap in maps:
        date = year+month/12.0-1.0/24.0
        if date1 < date < date2:
          if not numpy.isnan( tmap[i][j] ):
            x.append(date)
            y.append(tmap[i][j])
      if len(x) > nmin:
        c = numpy.polyfit( x, y, 1 )
        smap[i][j] = 10.0*c[0]
      nmap[i][j]=len(x)
  #for i in range(len(nmap)):
  #  s = ""
  #  for j in range(len(nmap[i])):
  #    s += str(min(nmap[i][j],9))
  #  print s
  return smap


# MAIN PROGRAM
# default values
datafile = sys.argv[1]
date11 = float(sys.argv[2])
date21 = float(sys.argv[3])
nmin1 = int(sys.argv[4])

# read data
maps = read_map( open(datafile).readlines() )
nmonths = len(maps)

trmap = trend( maps, date11, date21, nmin1 )

for l in write_map( 0, 0, trmap ): print(l, end="")
