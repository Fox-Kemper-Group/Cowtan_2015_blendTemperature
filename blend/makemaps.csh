\rm maps/*.png

foreach name (diff_rcp*.nc)
echo $name

# scale = 10000 for -a dates / 10 for C/decade
\rm diff_0.nc diff_3.nc diff_9.nc
cdo remapbil,r180x90 -selyear,1985/2014 $name diff_0.nc
cdo selmon,3 diff_0.nc diff_3.nc
cdo selmon,9 diff_0.nc diff_9.nc

python ncNxN.py diff_0.nc tas > diff.dat
python maptrendNxN.py diff.dat 1985 2015 179 > diff.trend
python plotmapNxN.py diff.trend 0 0 -0.25 0.25
mv diff.trend.png maps/$name:r.png

python ncNxN.py diff_3.nc tas > diff.dat
python maptrendNxN.py diff.dat 1985 2015 14 > diff.trend
python plotmapNxN.py diff.trend 0 0 -0.25 0.25
mv diff.trend.png maps/$name:r_3.png

python ncNxN.py diff_9.nc tas > diff.dat
python maptrendNxN.py diff.dat 1985 2015 14 > diff.trend
python plotmapNxN.py diff.trend 0 0 -0.25 0.25
mv diff.trend.png maps/$name:r_9.png

end

\rm diff_0.nc diff_3.nc diff_9.nc
\rm diff.dat diff.trend

