setenv root /data/cmip5/files
if ( $#argv == 0 ) then
  printf '%s\n' $root/historical/OImon/sic/*/* > /tmp/files
else
  printf '%s\n' $root/historical/OImon/sic/*/* | grep "$argv[1]" > /tmp/files
endif

setenv SKIP_SAME_TIME 1
setenv REMAP_EXTRAPOLATE on

@ n = 0

foreach rcp ( rcp85 )
  foreach name (`cat /tmp/files`)
    set ens = $name:t
    set mdl = $name:h:t
    set fam = ( $mdl:s/-/ / ); set fam = $fam[1]
    echo $mdl $ens $fam

    set sic0 = "`printf '%s\n' $root/historical/OImon/sic/$mdl/$ens/sic_OImon_${mdl}_historical_${ens}_*.nc | grep -v 2006`"
    set tos0 = "`printf '%s\n' $root/historical/Omon/tos/$mdl/$ens/tos_Omon_${mdl}_historical_${ens}_*.nc | grep -v 2006`"
    set tas0 = "`printf '%s\n' $root/historical/Amon/tas/$mdl/$ens/tas_Amon_${mdl}_historical_${ens}_*.nc | grep -v 2006`"

    set sic1 = "`printf '%s\n' $root/$rcp/OImon/sic/$mdl/$ens/sic_OImon_${mdl}_${rcp}_${ens}_*.nc`"
    set tos1 = "`printf '%s\n' $root/$rcp/Omon/tos/$mdl/$ens/tos_Omon_${mdl}_${rcp}_${ens}_*.nc`"
    set tas1 = "`printf '%s\n' $root/$rcp/Amon/tas/$mdl/$ens/tas_Amon_${mdl}_${rcp}_${ens}_*.nc`"

    set sftof = "`printf '%s\n' $root/historical/fx/sftof/$mdl/$ens/sftof_*.nc $root/historical/fx/sftof/$mdl/*/sftof_*.nc $root/historical/fx/sftof/$fam*/*/sftof_*.nc $root/historical/fx/sftof/*/*/sftof_*.nc | head -1 `"
    set t = `cdo info $sftof |& awk '/^ *1 *:/{print int(100*($11-$9))}'`
    if ( $t < 90 ) set sftof = "`printf '%s\n' $root/historical/fx/sftof/$mdl/*/sftof_*.nc $root/historical/fx/sftof/$fam*/*/sftof_*.nc $root/historical/fx/sftof/*/*/sftof_*.nc | head -1 `"
    set t = `cdo info $sftof |& awk '/^ *1 *:/{print int(100*($11-$9))}'`
    if ( $t < 90 ) set sftof = "`printf '%s\n' $root/historical/fx/sftof/*/*/sftof_*.nc | head -1 `"

    if ( "$sic0" != "" && "$tos0" != "" && "$tas0" != "" && "$sic1" != "" && "$tos1" != "" && "$tas1" != "" ) then
      \rm m*.nc s*.nc t*.nc
      cdo -a mergetime $sic0 sic0.nc
      cdo -a mergetime $tos0 tos0.nc
      cdo -a mergetime $tas0 tas0.nc
      cdo selyear,1861/2005 sic0.nc sic0y.nc
      cdo selyear,1861/2005 tos0.nc tos0y.nc
      cdo selyear,1861/2005 tas0.nc tas0y.nc
      cdo -a mergetime $sic1 sic1.nc
      cdo -a mergetime $tos1 tos1.nc
      cdo -a mergetime $tas1 tas1.nc
      cdo selyear,2005/2099 sic1.nc sic1y.nc
      cdo selyear,2005/2099 tos1.nc tos1y.nc
      cdo selyear,2005/2099 tas1.nc tas1y.nc
      cdo mergetime sic0y.nc sic1y.nc sic.nc
      cdo mergetime tos0y.nc tos1y.nc tos.nc
      cdo mergetime tas0y.nc tas1y.nc tas.nc
      set n1 = `cdo nmon sic.nc`
      set n2 = `cdo nmon tos.nc`
      set n3 = `cdo nmon tas.nc`
      if ( $n1 == 2868 && $n2 == 2868 && $n3 == 2868 ) then
        mkdir -p $rcp/$mdl/$ens/
        cdo remapdis,grid1x1.cdo tas.nc $rcp/$mdl/$ens/tas.nc
        cdo remapdis,grid1x1.cdo tos.nc $rcp/$mdl/$ens/tos.nc
        cdo remapdis,grid1x1.cdo sic.nc $rcp/$mdl/$ens/sic.nc
        cdo remapbil,grid1x1.cdo $sftof $rcp/$mdl/$ens/$sftof:t
        echo "RUN: " $mdl $ens
        @ n = $n + 1
      endif
    endif
  end
end

echo "Number of models: $n"

