# Calculate blended temperatures using HadCRUT4 method
# Usage:
#  python ncblendhadcrut.py tas.nc tos.nc sic.nc sftof.nc CRU.nc SST.nc > blend.temp
#
#  see README for more details


import sys, numpy, scipy.stats, math
import netCDF4


# cell areas, used for calculating area weighted averages
def areas( grid ):
  area = grid*[0.0]
  for i in range(grid):
    area[i] = ( ( math.sin(math.radians(180.0*(i+1)/grid-90.0)) -
                  math.sin(math.radians(180.0*(i  )/grid-90.0)) ) /
                math.sin(math.radians(180.0/grid)) )
  return area


# downscale to 5x5
def downscale( data, w ):
  datah = numpy.zeros([data.shape[0],36,72], numpy.float32)
  datah.fill( -1.0e30 )
  for i in range(datah.shape[1]):
    for j in range(datah.shape[2]):
      wcell = numpy.tile( w[5*i:5*i+5,5*j:5*j+5], (data.shape[0],1) ).reshape([data.shape[0],25])
      tcell = data[:,5*i:5*i+5,5*j:5*j+5].reshape([data.shape[0],25])
      wcell[tcell<-500] = 0.0
      m1 = numpy.mean( wcell*tcell, axis=1 )
      m2 = numpy.mean( wcell      , axis=1 )
      msk = m2 != 0.0
      datah[msk,i,j] = m1[msk]/m2[msk]
  return datah


# MAIN PROGRAM

# read tas.nc
nc = netCDF4.Dataset(sys.argv[1], "r")
print >> sys.stderr, nc.variables.keys()
lats1 = nc.variables["lat"][:]
lons1 = nc.variables["lon"][:]
tas = numpy.ma.filled(nc.variables["tas"][:,:,:],-1.0e30)
nc.close()

# read tos.nc
nc = netCDF4.Dataset(sys.argv[2], "r")
print >> sys.stderr, nc.variables.keys()
lats2 = nc.variables["lat"][:]
lons2 = nc.variables["lon"][:]
tos = numpy.ma.filled(nc.variables["tos"][:,:,:],-1.0e30)
y0 = int(nc.variables["time"][:][0]/10000)
nc.close()

# read sic.nc
nc = netCDF4.Dataset(sys.argv[3], "r")
print >> sys.stderr, nc.variables.keys()
lats3 = nc.variables["lat"][:]
lons3 = nc.variables["lon"][:]
sic = numpy.ma.filled(nc.variables["sic"][:,:,:],-1.0e30)
nc.close()

# read sftof.nc
nc = netCDF4.Dataset(sys.argv[4], "r")
print >> sys.stderr, nc.variables.keys()
lats4 = nc.variables["lat"][:]
lons4 = nc.variables["lon"][:]
sftof = numpy.ma.filled(nc.variables["sftof"][:,:],-1.0e30)
nc.close()

# read CRUTEM land data as mask
nc = netCDF4.Dataset(sys.argv[5], "r")
print >> sys.stderr, nc.variables.keys()
lats5 = nc.variables["lat"][:]
lons5 = nc.variables["lon"][:]
cvglnd = numpy.ma.filled(nc.variables["temperature_anomaly"][:,:],-1.0e30)
nc.close()

# read HadSST ocean data as mask
nc = netCDF4.Dataset(sys.argv[6], "r")
print >> sys.stderr, nc.variables.keys()
lats6 = nc.variables["lat"][:]
lons6 = nc.variables["lon"][:]
cvgsst = numpy.ma.filled(nc.variables["sst"][:,:],-1.0e30)
nc.close()

#nc = NetCDF.NetCDFFile(sys.argv[6], "r")
#print >> sys.stderr, nc.variables.keys()
#lats6 = nc.variables["lat"].getValue()
#lons6 = nc.variables["lon"].getValue()
#cvgmsk = nc.variables["temperature_anomaly"].getValue()
#nc.close()


print >> sys.stderr, tas.shape
print >> sys.stderr, tos.shape
print >> sys.stderr, sftof.shape

tas[tas<-500] = -1.0e30
tas[tas> 500] = -1.0e30
tos[tos<-500] = -1.0e30
tos[tos> 500] = -1.0e30

# dates
dates = (numpy.arange(tas.shape[0])+0.5)/12.0 + y0
print >> sys.stderr, dates

# force missing cells to be open water/land and scale if stored as percentage
sic[sic<  0.0] = 0.0
sic[sic>100.0] = 0.0
if numpy.max(sic)>90.0: sic = 0.01*sic

sftof[sftof<  0.0] = 0.0
sftof[sftof>100.0] = 0.0
if numpy.max(sftof)>90.0: sftof = 0.01*sftof

print >> sys.stderr, "sftof ", numpy.min(sftof), numpy.max(sftof), numpy.mean(sftof)

# print tos mask
s = ""
for i in range(tos.shape[1]-1,0,-tos.shape[1]/25):
  for j in range(0,tos.shape[2],tos.shape[2]/50):
    s += "#" if 100 < tos[-1,i,j] < 500 else "."
  s += "\n"
print >> sys.stderr, s, "\n"
# print cvg mask
s = ""
for i in range(cvglnd.shape[1]-1,0,-cvglnd.shape[1]/25):
  for j in range(0,cvglnd.shape[2],cvglnd.shape[2]/50):
    s += "#" if -500 < cvglnd[-1,i,j] < 500 else "."
  s += "\n"
print >> sys.stderr, s, "\n"
# print cvg mask
s = ""
for i in range(cvgsst.shape[1]-1,0,-cvgsst.shape[1]/25):
  for j in range(0,cvgsst.shape[2],cvgsst.shape[2]/50):
    s += "#" if -500 < cvgsst[-1,i,j] < 500 else "."
  s += "\n"
print >> sys.stderr, s, "\n"


# set baseline period
mask = numpy.logical_and( dates > 1961, dates < 1991 )

# convert tas to anomalies
tas[tas<-500] = numpy.nan
base = tas[mask,:,:]
for m in range(12):
  norm = numpy.nanmean(base[m::12,:,:],axis=0)
  tas[m::12,:,:] = tas[m::12,:,:] - norm
tas[numpy.isnan(tas)] = -1.0e30

# convert tos to anomalies
tos[tos<-500] = numpy.nan
base = tos[mask,:,:]
for m in range(12):
  norm = numpy.nanmean(base[m::12,:,:],axis=0)
  tos[m::12,:,:] = tos[m::12,:,:] - norm
tos[numpy.isnan(tos)] = -1.0e30
# eliminate ice cells from tos
tos[sic>0.05] = -1.0e30

print >> sys.stderr, norm
print >> sys.stderr, tos[-1,:,:]
print >> sys.stderr, tos.dtype

# trim tas to land cover
taslnd = tas.copy()
for m in range(tas.shape[0]):
  taslnd[m,sftof>0.99] = -1.0e30

# calculate area weights
w = numpy.zeros_like(sftof)
a = areas(sftof.shape[0])
for i in range(w.shape[0]):
  for j in range(w.shape[1]):
    w[i,j] = a[i]
print >> sys.stderr, w


# downscale
tash = downscale(tas,w)
tosh = downscale(tos,w)
tashlnd = downscale(taslnd,w)

# coarse grid land mask
sftofh = numpy.zeros([36,72], numpy.float32)
for i in range(sftofh.shape[0]):
  for j in range(sftofh.shape[1]):
    sftofh[i,j] = numpy.mean( sftof[5*i:5*i+5,5*j:5*j+5]*w[5*i:5*i+5,5*j:5*j+5] ) / numpy.mean( w[5*i:5*i+5,5*j:5*j+5] )
sftofh[ numpy.logical_and(sftofh>0.75,sftofh<1.0) ] = 0.75

# print tosh mask
print >> sys.stderr, "DOWNSCALED"
s = ""
for i in range(tash.shape[1]-1,0,-tash.shape[1]/25):
  for j in range(0,tash.shape[2],tash.shape[2]/50):
    s += "#" if -500 < tash[-1,i,j] < 500 else "."
  s += "\n"
print >> sys.stderr, s, "\n"
s = ""
for i in range(tosh.shape[1]-1,0,-tosh.shape[1]/25):
  for j in range(0,tosh.shape[2],tosh.shape[2]/50):
    s += "#" if -500 < tosh[-1,i,j] < 500 else "."
  s += "\n"
print >> sys.stderr, s, "\n"
s = ""
for i in range(tashlnd.shape[1]-1,0,-tashlnd.shape[1]/25):
  for j in range(0,tashlnd.shape[2],tashlnd.shape[2]/50):
    s += "#" if -500 < tashlnd[-1,i,j] < 500 else "."
  s += "\n"
print >> sys.stderr, s, "\n"

print >> sys.stderr, "BLEND"

# blend
tsha = numpy.zeros([tash.shape[0],36,72], numpy.float32)
tshb = numpy.zeros([tash.shape[0],36,72], numpy.float32)
for m in range(tash.shape[0]):
  for i in range(tosh.shape[1]):
    for j in range(tosh.shape[2]):
      # basic masking
      if cvglnd[m,i,j] > -500 or cvgsst[m,i,j] > -500:
        tsha[m,i,j] = tash[m,i,j]
      else:
        tsha[m,i,j] = -1.0e30
      # had4 masking
      havelnd = cvglnd[m,i,j] > -500 and tashlnd[m,i,j] > -500
      havesst = cvgsst[m,i,j] > -500 and tosh[m,i,j] > -500
      if havelnd and havesst:
        tshb[m,i,j] = (1.0-sftofh[i,j])*tashlnd[m,i,j]+(sftofh[i,j])*tosh[m,i,j]
      elif havelnd:
        tshb[m,i,j] = tashlnd[m,i,j]
      elif havesst:
        tshb[m,i,j] = tosh[m,i,j]
      else:
        tshb[m,i,j] = -1.0e30

# print land mask
print >> sys.stderr, "sftofh"
s = ""
for i in range(sftofh.shape[0]-1,0,-sftofh.shape[0]/25):
  for j in range(0,sftofh.shape[1],sftofh.shape[1]/50):
    s += "#" if sftofh[i,j] < 0.5 else "."
  s += "\n"
print >> sys.stderr, s, "\n"
# print cvg mask
print >> sys.stderr, "tash"
s = ""
for i in range(tash.shape[1]-1,0,-tash.shape[1]/25):
  for j in range(0,tash.shape[2],tash.shape[2]/50):
    s += "#" if -500 < tash[-1,i,j] < 500 else "."
  s += "\n"
print >> sys.stderr, s, "\n"
# print cvg mask
print >> sys.stderr, "tosh"
s = ""
for i in range(tosh.shape[1]-1,0,-tosh.shape[1]/25):
  for j in range(0,tosh.shape[2],tosh.shape[2]/50):
    s += "#" if -500 < tosh[-1,i,j] < 500 else "."
  s += "\n"
print >> sys.stderr, s, "\n"
# print cvg mask
print >> sys.stderr, "tsha"
s = ""
for i in range(tsha.shape[1]-1,0,-tsha.shape[1]/25):
  for j in range(0,tsha.shape[2],tsha.shape[2]/50):
    s += "#" if -500 < tsha[-1,i,j] < 500 else "."
  s += "\n"
print >> sys.stderr, s, "\n"

# calculate area weights
w = numpy.zeros_like(sftofh)
a = areas(sftofh.shape[0])
for i in range(w.shape[0]):
  for j in range(w.shape[1]):
    w[i,j] = a[i]
print >> sys.stderr, w

# calculate temperatures
for m in range(tsha.shape[0]):
  wa = w.copy()
  wb = w.copy()
  # zero weight for missing cells
  wa[ tsha[m,:,:] < -500 ] = 0.0
  wb[ tshb[m,:,:] < -500 ] = 0.0
  # mean of hemispheric means: air
  san = numpy.sum( wa[0:18,:] )
  tan = numpy.sum( wa[0:18,:] * tsha[m,0:18,:] ) / san
  sas = numpy.sum( wa[18:36,:] )
  tas = numpy.sum( wa[18:36,:] * tsha[m,18:36,:] ) / sas
  ta = 0.5*(tan+tas)
  # mean of hemispheric means: blend
  sbn = numpy.sum( wb[0:18,:] )
  tbn = numpy.sum( wb[0:18,:] * tshb[m,0:18,:] ) / sbn
  sbs = numpy.sum( wb[18:36,:] )
  tbs = numpy.sum( wb[18:36,:] * tshb[m,18:36,:] ) / sbs
  tb = 0.5*(tbn+tbs)
  print dates[m], ta, tb, tb-ta
#  sc = numpy.sum( wb[0:36,:] )
#  tc = numpy.sum( wb[0:36,:] * tshb[m,0:36,:] ) / sc
#  print dates[m], ta, tb, tc-ta, tb-ta, tbn, tbs, sbn, sbs

