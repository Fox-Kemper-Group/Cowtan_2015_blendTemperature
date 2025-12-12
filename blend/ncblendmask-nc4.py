# Calculate blended temperatures using general methods
# Usage:
#  python ncblendmask.py <mode> tas.nc tos.nc sic.nc sftof.nc [Had4.nc] > blend.temp
#  <mode> is one of xxx, mxx, xax, max, xxf, mxf, xaf, maf
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


# MAIN PROGRAM

# m = mask
# a = blend anomalies
# f = fix ice
# (use x for none)
options = sys.argv[1]

# read tas.nc
nc = netCDF4.Dataset(sys.argv[2], "r")
print >> sys.stderr, nc.variables.keys()
lats1 = nc.variables["lat"][:]
lons1 = nc.variables["lon"][:]
tas = numpy.ma.filled(nc.variables["tas"][:,:,:],-1.0e30)
nc.close()

# read tos.nc
nc = netCDF4.Dataset(sys.argv[3], "r")
print >> sys.stderr, nc.variables.keys()
lats2 = nc.variables["lat"][:]
lons2 = nc.variables["lon"][:]
tos = numpy.ma.filled(nc.variables["tos"][:,:,:],-1.0e30)
y0 = int(nc.variables["time"][:][0]/10000)
nc.close()

# read sic.nc
nc = netCDF4.Dataset(sys.argv[4], "r")
print >> sys.stderr, nc.variables.keys()
lats3 = nc.variables["lat"][:]
lons3 = nc.variables["lon"][:]
sic = numpy.ma.filled(nc.variables["sic"][:,:,:],-1.0e30)
nc.close()

# read sftof.nc
nc = netCDF4.Dataset(sys.argv[5], "r")
print >> sys.stderr, nc.variables.keys()
lats4 = nc.variables["lat"][:]
lons4 = nc.variables["lon"][:]
sftof = numpy.ma.filled(nc.variables["sftof"][:,:],-1.0e30)
nc.close()

if 'm' in options:
  # read HadCRUT4 data as mask
  nc = netCDF4.Dataset(sys.argv[6], "r")
  print >> sys.stderr, nc.variables.keys()
  lats5 = nc.variables["lat"][:]
  lons5 = nc.variables["lon"][:]
  cvgmsk = numpy.ma.filled(nc.variables["temperature_anomaly"][:,:,:],-1.0e30)
  nc.close()


print >> sys.stderr, tas.shape
print >> sys.stderr, tos.shape
print >> sys.stderr, sftof.shape
print >> sys.stderr, sic.shape

sic = sic[0:tas.shape[0],:,:]
print >> sys.stderr, sic.shape


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

print >> sys.stderr, "sic ", numpy.min(sic), numpy.max(sic), numpy.mean(sic)
print >> sys.stderr, "sftof ", numpy.min(sftof), numpy.max(sftof), numpy.mean(sftof)

# optional fixed ice mode
if 'f' in options:
  # mask all cells with any ice post 1961
  for m0 in range(0,len(dates),12):
    if dates[m0] > 1961: break
  print >> sys.stderr, m0, dates[m0]
  for i in range(sic.shape[1]):
    for j in range(sic.shape[2]):
      for m in range(12):
        cmax = sic[m0+m::12,i,j].max()
        if cmax > 0.01:
          sic[m::12,i,j] = 1.0

# combine land/ice masks
for m in range(sic.shape[0]):
  sic[m,:,:] = (1.0-sic[m,:,:])*sftof

# print mask
s = ""
sicmax = numpy.max(sic)
for i in range(sic.shape[1]-1,0,-sic.shape[1]/25):
  for j in range(0,sic.shape[2],sic.shape[2]/50):
    s += ".123456789#"[int(10*sic[-1,i,j]/sicmax)]
  s += "\n"
print >> sys.stderr, s, "\n"
# print tos mask
s = ""
for i in range(tos.shape[1]-1,0,-tos.shape[1]/25):
  for j in range(0,tos.shape[2],tos.shape[2]/50):
    s += "#" if 100 < tos[-1,i,j] < 500 else "."
  s += "\n"
print >> sys.stderr, s, "\n"
# print cvg mask
if 'm' in options:
  s = ""
  for i in range(cvgmsk.shape[1]-1,0,-cvgmsk.shape[1]/25):
    for j in range(0,cvgmsk.shape[2],cvgmsk.shape[2]/50):
      s += "#" if -100 < cvgmsk[-1,i,j] < 100 else "."
    s += "\n"
  print >> sys.stderr, s, "\n"

# deal with missing tos through sic
for m in range(sic.shape[0]):
  sic[m,tos[m,:,:]<-500.0] = 0.0
  sic[m,tos[m,:,:]> 500.0] = 0.0

# baseline and blend in the desired order
if 'a' in options:

  # prepare missing
  for m in range(sic.shape[0]):
    tos[m,tos[m,:,:]<-500.0] = numpy.nan
    tos[m,tos[m,:,:]> 500.0] = numpy.nan

  # baseline
  mask = numpy.logical_and( dates > 1961, dates < 1991 )
  base = tas[mask,:,:]
  for m in range(12):
    norm = numpy.mean(base[m::12,:,:],axis=0)
    tas[m::12,:,:] = tas[m::12,:,:] - norm
  base = tos[mask,:,:]
  for m in range(12):
    norm = numpy.nanmean(base[m::12,:,:],axis=0)
    tos[m::12,:,:] = tos[m::12,:,:] - norm
  # blend
  for m in range(sic.shape[0]):
    tos[m,:,:] = tas[m,:,:]*(1.0-sic[m,:,:])+tos[m,:,:]*(sic[m,:,:])

else:

  # blend
  for m in range(sic.shape[0]):
    tos[m,:,:] = tas[m,:,:]*(1.0-sic[m,:,:])+tos[m,:,:]*(sic[m,:,:])
  # baseline
  mask = numpy.logical_and( dates > 1961, dates < 1991 )
  base = tas[mask,:,:]
  for m in range(12):
    norm = numpy.mean(base[m::12,:,:],axis=0)
    tas[m::12,:,:] = tas[m::12,:,:] - norm
  base = tos[mask,:,:]
  for m in range(12):
    norm = numpy.mean(base[m::12,:,:],axis=0)
    tos[m::12,:,:] = tos[m::12,:,:] - norm

print >> sys.stderr, sic.dtype, tos.dtype

# deal with any remaining nans
for m in range(sic.shape[0]):
  msk = numpy.isnan(tos[m,:,:])
  tos[m,msk] = tas[m,msk]

# calculate area weights
w = numpy.zeros_like(sftof)
a = areas(sftof.shape[0])
for i in range(w.shape[0]):
  for j in range(w.shape[1]):
    w[i,j] = a[i]
print >> sys.stderr, w

# calculate temperatures
for m in range(tas.shape[0]):
  wm = w.copy()
  if 'm' in options: wm[ cvgmsk[m,:,:] < -100 ] = 0.0 
  s = numpy.sum( wm )
  ta = numpy.sum( wm * tas[m,:,:] ) / s
  tb = numpy.sum( wm * tos[m,:,:] ) / s
  print dates[m], ta, tb, tb-ta

# calculate difference map series (force in place)
for m in range(tos.shape[0]):
  t = tos[m,:,:] - tas[m,:,:]
  if 'm' in options: t[ cvgmsk[m,:,:] < -100 ] = 0.0
  tos[m,:,:] = t

