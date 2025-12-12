mkdir fail
\rm mean.nc tmp.nc
mv diff_rcp*_bcc-csm1-1-m_r1i1p1.nc fail
mv diff_rcp*_BNU-ESM_r1i1p1.nc fail
mv diff_rcp*_CMCC-CESM_r1i1p1.nc fail
mv diff_rcp*_CSIRO-Mk3-6-0_*.nc fail
cdo ensmean diff_rcp*.nc mean.nc
cdo selyear,1980/2020 mean.nc tmp.nc
python ncNxN.py tmp.nc tas > tmp.dat
python maptrendNxN.py tmp.dat 1985 2015 179 > tmp.trend
python plotmapNxN.py tmp.trend 0 0 -0.1 0.1
\rm mean.nc tmp.nc

