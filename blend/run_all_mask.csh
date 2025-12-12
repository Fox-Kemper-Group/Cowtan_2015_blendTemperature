set root = $PWD/../..
set rcp = rcp85

if ( $#argv == 0 ) then
  printf '%s\n' $root/$rcp/*/* > files
else
  printf '%s\n' $root/$rcp/*/* | grep "$argv[1]" > files
endif

if (! -e Had4.nc) then
  unzip -o HadCRUT.4.3.0.0.median_netcdf.zip
  cdo -a remapnn,grid1x1.cdo -selyear,1861/2014 -selvar,temperature_anomaly HadCRUT.4.3.0.0.median.nc Had4.nc
endif


@ n = 0

foreach name (`cat files`)
  set ens = $name:t
  set mdl = $name:h:t
  set fam = ( $mdl:s/-/ / ); set fam = $fam[1]
  echo $mdl $ens $fam

  set sic = $root/$rcp/$mdl/$ens/sic.nc
  set tos = $root/$rcp/$mdl/$ens/tos.nc
  set tas = $root/$rcp/$mdl/$ens/tas.nc
  set sftof = $root/$rcp/$mdl/$ens/sftof*.nc

  \rm s*.nc t*.nc
  cdo selyear,1861/2014 $sic sic.nc
  cdo selyear,1861/2014 $tos tos.nc
  cdo selyear,1861/2014 $tas tas.nc
  python ncblendmask.py xxx tas.nc tos.nc sic.nc $sftof Had4.nc > ${rcp}_${mdl}_${ens}.temp
  \rm diff.nc
  echo "RUN: " $mdl $ens `cdo nmon diff_${rcp}_${mdl}_${ens}.nc`
  @ n = $n + 1
end

echo "Number of models: $n"
