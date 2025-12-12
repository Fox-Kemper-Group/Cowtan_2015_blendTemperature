# Calculate blended temperatures using general methods
# Usage:
#  python ncblendmask.py <mode> tas.nc tos.nc sic.nc sftof.nc [Had4.nc] > blend.temp
#  <mode> is one of xxx, mxx, xax, max, xxf, mxf, xaf, maf
#  see README for more details


import math
import sys

import netCDF4
import numpy
import scipy.stats


# cell areas, used for calculating area weighted averages
def areas(grid):
  area = grid * [0.0]
  for i in range(grid):
    area[i] = ( ( math.sin(math.radians(180.0 * (i + 1) / grid - 90.0)) -
                  math.sin(math.radians(180.0 * (i    ) / grid - 90.0)) ) /
                math.sin(math.radians(180.0 / grid)) )
  return area


def mask_string(data, palette=None, time_index=-1, threshold_low=-500, threshold_high=500):
  """Render a coarse mask for debugging coverage prints."""

  array = data if data.ndim == 2 else data[time_index]
  rows, cols = array.shape
  step_i = max(1, rows // 25)
  step_j = max(1, cols // 50)
  s = ""

  if palette:
    max_val = numpy.max(array)
    if max_val == 0:
      max_val = 1.0
  for i in range(rows - 1, 0, -step_i):
    for j in range(0, cols, step_j):
      if palette:
        idx = int((len(palette) - 1) * array[i, j] / max_val)
        idx = max(0, min(len(palette) - 1, idx))
        s += palette[idx]
      else:
        s += "#" if threshold_low < array[i, j] < threshold_high else "."
    s += "\n"
  return s


# MAIN PROGRAM

# m = mask
# a = blend anomalies
# f = fix ice
# (use x for none)
options = sys.argv[1]

# read tas.nc
nc = netCDF4.Dataset(sys.argv[2], "r")
print(nc.variables.keys(), file=sys.stderr)
lats1 = nc.variables["lat"][:]
lons1 = nc.variables["lon"][:]
tas = numpy.ma.filled(nc.variables["tas"][:, :, :], -1.0e30)
nc.close()

# read tos.nc
nc = netCDF4.Dataset(sys.argv[3], "r")
print(nc.variables.keys(), file=sys.stderr)
lats2 = nc.variables["lat"][:]
lons2 = nc.variables["lon"][:]
tos = numpy.ma.filled(nc.variables["tos"][:, :, :], -1.0e30)
y0 = int(nc.variables["time"][:][0] / 10000)
nc.close()

# read sic.nc
nc = netCDF4.Dataset(sys.argv[4], "r")
print(nc.variables.keys(), file=sys.stderr)
lats3 = nc.variables["lat"][:]
lons3 = nc.variables["lon"][:]
sic = numpy.ma.filled(nc.variables["sic"][:, :, :], -1.0e30)
nc.close()

# read sftof.nc
nc = netCDF4.Dataset(sys.argv[5], "r")
print(nc.variables.keys(), file=sys.stderr)
lats4 = nc.variables["lat"][:]
lons4 = nc.variables["lon"][:]
sftof = numpy.ma.filled(nc.variables["sftof"][:, :], -1.0e30)
nc.close()

if 'm' in options:
  # read HadCRUT4 data as mask
  nc = netCDF4.Dataset(sys.argv[6], "r")
  print(nc.variables.keys(), file=sys.stderr)
  lats5 = nc.variables["lat"][:]
  lons5 = nc.variables["lon"][:]
  cvgmsk = numpy.ma.filled(nc.variables["temperature_anomaly"][:, :, :], -1.0e30)
  nc.close()


print(tas.shape, file=sys.stderr)
print(tos.shape, file=sys.stderr)
print(sftof.shape, file=sys.stderr)
print(sic.shape, file=sys.stderr)

sic = sic[0:tas.shape[0],:,:]
print(sic.shape, file=sys.stderr)


# dates
dates = (numpy.arange(tas.shape[0]) + 0.5) / 12.0 + y0
print(dates, file=sys.stderr)

# force missing cells to be open water/land and scale if stored as percentage
sic[sic <  0.0] = 0.0
sic[sic >100.0] = 0.0
if numpy.max(sic) > 90.0:
  sic = 0.01 * sic

sftof[sftof <  0.0] = 0.0
sftof[sftof >100.0] = 0.0
if numpy.max(sftof) > 90.0:
  sftof = 0.01 * sftof

print("sic ", numpy.min(sic), numpy.max(sic), numpy.mean(sic), file=sys.stderr)
print("sftof ", numpy.min(sftof), numpy.max(sftof), numpy.mean(sftof), file=sys.stderr)

# optional fixed ice mode
if 'f' in options:
  # mask all cells with any ice post 1961
  for m0 in range(0, len(dates), 12):
    if dates[m0] > 1961:
      break
  print(m0, dates[m0], file=sys.stderr)
  for i in range(sic.shape[1]):
    for j in range(sic.shape[2]):
      for m in range(12):
        cmax = sic[m0 + m::12, i, j].max()
        if cmax > 0.01:
          sic[m::12, i, j] = 1.0

# combine land/ice masks
for m in range(sic.shape[0]):
  sic[m, :, :] = (1.0 - sic[m, :, :]) * sftof

# print mask
print(mask_string(sic, palette=".123456789#"), "\n", file=sys.stderr)
# print tos mask
print(mask_string(tos, threshold_low=100, threshold_high=500), "\n", file=sys.stderr)
# print cvg mask
if 'm' in options:
  print(mask_string(cvgmsk, threshold_low=-100, threshold_high=100), "\n", file=sys.stderr)

# deal with missing tos through sic
for m in range(sic.shape[0]):
  sic[m, tos[m, :, :] < -500.0] = 0.0
  sic[m, tos[m, :, :] > 500.0] = 0.0

# baseline and blend in the desired order
if 'a' in options:

  # prepare missing
  for m in range(sic.shape[0]):
    tos[m, tos[m, :, :] < -500.0] = numpy.nan
    tos[m, tos[m, :, :] > 500.0] = numpy.nan

  # baseline
  mask = numpy.logical_and( dates > 1961, dates < 1991 )
  base = tas[mask, :, :]
  for m in range(12):
    norm = numpy.mean(base[m::12, :, :], axis=0)
    tas[m::12, :, :] = tas[m::12, :, :] - norm
  base = tos[mask, :, :]
  for m in range(12):
    norm = numpy.nanmean(base[m::12, :, :], axis=0)
    tos[m::12, :, :] = tos[m::12, :, :] - norm
  # blend
  for m in range(sic.shape[0]):
    tos[m, :, :] = tas[m, :, :] * (1.0 - sic[m, :, :]) + tos[m, :, :] * (sic[m, :, :])

else:

  # blend
  for m in range(sic.shape[0]):
    tos[m, :, :] = tas[m, :, :] * (1.0 - sic[m, :, :]) + tos[m, :, :] * (sic[m, :, :])
  # baseline
  mask = numpy.logical_and( dates > 1961, dates < 1991 )
  base = tas[mask, :, :]
  for m in range(12):
    norm = numpy.mean(base[m::12, :, :], axis=0)
    tas[m::12, :, :] = tas[m::12, :, :] - norm
  base = tos[mask, :, :]
  for m in range(12):
    norm = numpy.mean(base[m::12, :, :], axis=0)
    tos[m::12, :, :] = tos[m::12, :, :] - norm

print(sic.dtype, tos.dtype, file=sys.stderr)

# deal with any remaining nans
for m in range(sic.shape[0]):
  msk = numpy.isnan(tos[m, :, :])
  tos[m, msk] = tas[m, msk]

# calculate area weights
w = numpy.zeros_like(sftof)
a = areas(sftof.shape[0])
for i in range(w.shape[0]):
  for j in range(w.shape[1]):
    w[i, j] = a[i]
print(w, file=sys.stderr)

# calculate temperatures
for m in range(tas.shape[0]):
  wm = w.copy()
  if 'm' in options:
    wm[cvgmsk[m, :, :] < -100] = 0.0
  s = numpy.sum(wm)
  ta = numpy.sum(wm * tas[m, :, :]) / s
  tb = numpy.sum(wm * tos[m, :, :]) / s
  print(dates[m], ta, tb, tb - ta)

# calculate difference map series (force in place)
for m in range(tos.shape[0]):
  t = tos[m, :, :] - tas[m, :, :]
  if 'm' in options:
    t[cvgmsk[m, :, :] < -100] = 0.0
  tos[m, :, :] = t

# output difference map series
nc1 = netCDF4.Dataset(sys.argv[2], "r")
nc2 = netCDF4.Dataset("diff.nc", "w")
nc2.createDimension("time", tas.shape[0])
nc2.createDimension("lat", tas.shape[1])
nc2.createDimension("lon", tas.shape[2])
nc2.createVariable("time", "f8", ("time",))
nc2.createVariable("lat", "f8", ("lat",))
nc2.createVariable("lon", "f8", ("lon",))
nc2.createVariable("tas", "f4", ("time", "lat", "lon"))

for v in ["time", "lat", "lon"]:
  var_in = nc1.variables[v]
  var_out = nc2.variables[v]
  var_out[:] = var_in[:]
  for attr in var_in.ncattrs():
    setattr(var_out, attr, getattr(var_in, attr))

nc2.variables["tas"][:] = tos
nc2.close()
nc1.close()

