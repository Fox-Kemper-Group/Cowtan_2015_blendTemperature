mkdir plot
\rm plot/*.temp
foreach name (rcp*.temp)
python annualize.py < $name > plot/$name
end
find plot -size 0 -delete
\rm plot/rcp*_BNU-ESM_r1i1p1.temp
\rm plot/rcp*_CMCC-CESM_r1i1p1.temp
\rm plot/rcp*_bcc-csm1-1-m_r1i1p1.temp
python plotbias.py plot/rcp*.temp
python means.py plot/rcp*.temp > mean.temp
