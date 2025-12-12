# Calculate blended temperatures using HadCRUT4 method
# Usage:
#  python ncblendhadcrut.py tas.nc tos.nc sic.nc sftof.nc CRU.nc SST.nc > blend.temp
#
#  see README for more details


import sys
import math

import netCDF4
import numpy
import scipy.stats


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


def mask_string(data, time_index=-1, threshold_low=-500, threshold_high=500):
  """Render a coarse mask for debugging coverage, matching the original prints."""

  array = data if data.ndim == 2 else data[time_index]
  rows, cols = array.shape
  step_i = max(1, rows // 25)
  step_j = max(1, cols // 50)
  s = ""
  for i in range(rows - 1, 0, -step_i):
    for j in range(0, cols, step_j):
      s += "#" if threshold_low < array[i, j] < threshold_high else "."
    s += "\n"
  return s


# MAIN PROGRAM

# read tas.nc
nc = netCDF4.Dataset(sys.argv[1], "r")
print(nc.variables.keys(), file=sys.stderr)
lats1 = nc.variables["lat"][:]
lons1 = nc.variables["lon"][:]
tas = nc.variables["tas"][:]
nc.close()

# read tos.nc
nc = netCDF4.Dataset(sys.argv[2], "r")
print(nc.variables.keys(), file=sys.stderr)
lats2 = nc.variables["lat"][:]
lons2 = nc.variables["lon"][:]
tos = nc.variables["tos"][:]
y0 = int(nc.variables["time"][:][0] / 10000)
nc.close()

# read sic.nc
nc = netCDF4.Dataset(sys.argv[3], "r")
print(nc.variables.keys(), file=sys.stderr)
lats3 = nc.variables["lat"][:]
lons3 = nc.variables["lon"][:]
sic = nc.variables["sic"][:]
nc.close()

# read sftof.nc
nc = netCDF4.Dataset(sys.argv[4], "r")
print(nc.variables.keys(), file=sys.stderr)
lats4 = nc.variables["lat"][:]
lons4 = nc.variables["lon"][:]
sftof = nc.variables["sftof"][:]
nc.close()

# read CRUTEM land data as mask
nc = netCDF4.Dataset(sys.argv[5], "r")
print(nc.variables.keys(), file=sys.stderr)
lats5 = nc.variables["lat"][:]
lons5 = nc.variables["lon"][:]
cvglnd = nc.variables["temperature_anomaly"][:]
nc.close()

# read HadSST ocean data as mask
nc = netCDF4.Dataset(sys.argv[6], "r")
print(nc.variables.keys(), file=sys.stderr)
lats6 = nc.variables["lat"][:]
lons6 = nc.variables["lon"][:]
cvgsst = nc.variables["sst"][:]
nc.close()

#nc = NetCDF.NetCDFFile(sys.argv[6], "r")
#print >> sys.stderr, nc.variables.keys()
#lats6 = nc.variables["lat"].getValue()
#lons6 = nc.variables["lon"].getValue()
#cvgmsk = nc.variables["temperature_anomaly"].getValue()
#nc.close()


print(tas.shape, file=sys.stderr)
print(tos.shape, file=sys.stderr)
print(sftof.shape, file=sys.stderr)

tas[tas<-500] = -1.0e30
tas[tas> 500] = -1.0e30
tos[tos<-500] = -1.0e30
tos[tos> 500] = -1.0e30

# dates
dates = (numpy.arange(tas.shape[0]) + 0.5) / 12.0 + y0
print(dates, file=sys.stderr)

# force missing cells to be open water/land and scale if stored as percentage
sic[sic<  0.0] = 0.0
sic[sic>100.0] = 0.0
if numpy.max(sic)>90.0: sic = 0.01*sic

sftof[sftof<  0.0] = 0.0
sftof[sftof>100.0] = 0.0
if numpy.max(sftof)>90.0: sftof = 0.01*sftof

print("sftof ", numpy.min(sftof), numpy.max(sftof), numpy.mean(sftof), file=sys.stderr)

# print tos mask
print(mask_string(tos, threshold_low=100), "\n", file=sys.stderr)
# print coverage masks
print(mask_string(cvglnd), "\n", file=sys.stderr)
print(mask_string(cvgsst), "\n", file=sys.stderr)


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

print(norm, file=sys.stderr)
print(tos[-1, :, :], file=sys.stderr)
print(tos.dtype, file=sys.stderr)

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
print(w, file=sys.stderr)


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
print("DOWNSCALED", file=sys.stderr)
print(mask_string(tash), "\n", file=sys.stderr)
print(mask_string(tosh), "\n", file=sys.stderr)
print(mask_string(tashlnd), "\n", file=sys.stderr)

print("BLEND", file=sys.stderr)

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
print("sftofh", file=sys.stderr)
print(mask_string(sftofh, time_index=0, threshold_high=0.5), "\n", file=sys.stderr)
# print cvg masks
print("tash", file=sys.stderr)
print(mask_string(tash), "\n", file=sys.stderr)
print("tosh", file=sys.stderr)
print(mask_string(tosh), "\n", file=sys.stderr)
print("tsha", file=sys.stderr)
print(mask_string(tsha), "\n", file=sys.stderr)

# calculate area weights
w = numpy.zeros_like(sftofh)
a = areas(sftofh.shape[0])
for i in range(w.shape[0]):
  for j in range(w.shape[1]):
    w[i,j] = a[i]
print(w, file=sys.stderr)

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
  print(dates[m], ta, tb, tb-ta)
#  sc = numpy.sum( wb[0:36,:] )
#  tc = numpy.sum( wb[0:36,:] * tshb[m,0:36,:] ) / sc
#  print dates[m], ta, tb, tc-ta, tb-ta, tbn, tbs, sbn, sbs

