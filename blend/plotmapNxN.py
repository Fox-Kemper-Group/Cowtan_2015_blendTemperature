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


# area of a latitude band by index
def areas( grid ):
  area = grid*[0.0]
  for i in range(grid):
    area[i] = ( ( math.sin(math.radians(180.0*(i+1)/grid-90.0)) -
                  math.sin(math.radians(180.0*(i  )/grid-90.0)) ) /
                math.sin(math.radians(180.0/grid)) )
  return area


# plot and save a map
def plot( datafile, y1, m1, cmap ):
  # read data
  f = open( datafile )
  lines = f.readlines()
  f.close()

  # extract maps
  maps = read_map( open(datafile).readlines() )
  nmonths = len(maps)
  for m in range(0,nmonths):
    y2, m2, tmap = maps[m]
    if y1 == y2 and m1 == m2:
      break

  lons = np.arange(len(tmap[0])+1)*360/len(tmap[0])-180
  lats = np.arange(len(tmap)   +1)*180/len(tmap   )- 90
  #print tmap
  print(lons)
  print(lats)
  tmap = ma.masked_array( data=tmap, mask=numpy.isnan(tmap) )

  # create Basemap instance for map projection.
  w = 8.0
  h = 4.0
  fig = plt.figure(figsize=(w,h))
  ax = plt.axes([0.02,0.02,0.96,0.96])
  bl = 0
  if proj[0] == 'n': bl=45
  if proj[0] == 's': bl=-45
  m = Basemap(projection=proj,lat_0=0,lon_0=0,boundinglat=bl)
  x, y = m(*np.meshgrid(lons, lats))

  im1 = m.pcolor(x,y,tmap,shading='flat',cmap=cmap,vmin=v0,vmax=v1)
  plt.colorbar(im1,orientation='horizontal',extend='both',shrink=0.8,fraction=0.12,pad=0.02)
  # draw coastlines.
  m.drawcoastlines(linewidth=1.0)
  # draw a line around the map region.
  m.drawmapboundary(linewidth=0.5)
  # draw parallels and meridians.
  m.drawparallels(np.arange(-60.0,60.1,30.),linewidth=0.25)
  m.drawmeridians(np.arange(-120.0,120.1,60.),linewidth=0.25)
  # add a title.
  #plt.title(title)
  plt.savefig(datafile+".png")




# MAIN PROGRAM
v0,v1 = -1.0,1.0
proj = 'robin'
datafile = sys.argv[1]
y1 = float(sys.argv[2])
m1 = float(sys.argv[3])
if len(sys.argv)>4: v0 = float(sys.argv[4])
if len(sys.argv)>5: v1 = float(sys.argv[5])
if len(sys.argv)>6: proj = sys.argv[6]


import numpy as np
import numpy.ma as ma
import matplotlib
#matplotlib.use('AGG')
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt


cmap = matplotlib.cm.seismic

plot( datafile, y1, m1, cmap )

