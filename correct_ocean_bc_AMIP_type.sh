#!/bin/bash

###################################################################################################
# procedure to generate the corrected SST/SICs for AGCM simulations #
###################################################################################################

# Problem: SSTs have to be corrected in a way that the monthly means are retained after doing a linear interpolation in time (as done by ECHAM).
# simplification: each month is assumed to have 30 days (should not be relevant for practical purpose.)

# Correct SST/SIC for AGCM simulations
# ----------------------------------------------
#
# After Taylor et al for the transient simulations. To close the system of linear equations, we have to add to addional constraints, which are as follows: 
# Constraint 1: The corrected temperature of month -1 (i.e. the month prior to the initialization of the transient run) is known. It is concatenated to beginning of the observations and considered as SST/SIC(0) by the python script.
# Constraint 2: Furthermore we assume that the corrected temperature of the last year equals that of the next-to-last year. This is a bit quick-and-dirty. However, since we do not use the last year anyway, and - as described in Taylor et al.
#               the effect on the previous values diminishes by a factor of 6 each month, the effect should be without practical relevance for our purpose (T(n) only changes the last value used by a factor of (1/6)^12).

set -ex

# do it

varname_sst=sst
varname_sic=sic

fyear=SOMETHING
lyear=SOMETHING
lyear_clim=$(( ${fyear} + 29 ))

reallist="SOMETHING"   # list of realizations to loop over them

outdir=SOMETHING
PATH=${PATH}:SOMETHING     # replace SOMETHING by the full path where to find correct_ocean_bc.py

tmp_pref=SOMETHING      # some place to put temporary directories
tmp=$(mktemp -p ${tmp_pref} -d tmp.correct_ocean_bc.XXX)

cd ${tmp}

for var in ${varname_sst} ${varname_sic}; do

   outfile_init=PaleoSST_SIC_1000-1849_RXXX.nc     # Outfile 

   for real in ${reallist}; do

      infile_trans=SOMETHING                              # your infile, all timesteps merged into one file
      outfile_trans=${outdir}/PALAEO-RA_T63_real${real}_${var}_${fyear}-${lyear}.nc    # replace SOMETHING by yyyy-YYYY where yyyy is the first year and YYYY the last year of the reconstruction.
   
      cdo setyear,$(( ${fyear} - 1 )) -selmon,12 ${outfile_init} tmp.init.lyear.nc
      cdo mergetime tmp.init.lyear.nc ${infile_trans} tmp.transient.nc
      correct_ocean_bc.py -c f_prescr_l_const -i tmp.transient.nc -o ${outfile_trans}

   done #reallist   
done #var

rm -rf ${tmp}

exit 0
