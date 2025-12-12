set root = $PWD/../..
set rcp = rcp85

if ( $#argv == 0 ) then
  printf '%s\n' $root/$rcp/*/* > files
else
  printf '%s\n' $root/$rcp/*/* | grep "$argv[1]" > files
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

  python ncblendmask.py xxx $tas $tos $sic $sftof > ${rcp}_${mdl}_${ens}.temp
  #mv diff.nc diff_${rcp}_${mdl}_${ens}.nc
  \rm diff.nc
  echo "RUN: " $mdl $ens `cdo nmon diff_${rcp}_${mdl}_${ens}.nc`
  @ n = $n + 1
end

echo "Number of models: $n"
