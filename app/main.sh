#! /bin/bash
#
# Run script for flywheel/infant_recon-all Gear.
#
# Authorship:  Niall Bourke
#
##############################################################################
# Define directory names and containers

subject=$1
session="${2// /_}" # replace spaces with underscores
input_age=$3
num_threads=$4
base_filename=${subject}_${session}

echo "file base name: $base_filename"
echo "input age: $input_age"


FLYWHEEL_BASE=/flywheel/v0
INPUT_DIR=$FLYWHEEL_BASE/input/
OUTPUT_DIR=$FLYWHEEL_BASE/output
WORKDIR=$FLYWHEEL_BASE/work
CONFIG_FILE=$FLYWHEEL_BASE/config.json
CONTAINER='[flywheel/infant_recon-all]'

export FREESURFER_HOME=/usr/local/freesurfer/8.1.0
export SUBJECTS_DIR=$WORKDIR  # or wherever you want outputs
source $FREESURFER_HOME/SetUpFreeSurfer.sh

# Force correct Perl environment for Flywheel
export PATH=$FREESURFER_HOME/mni/bin:$PATH
export PERL5LIB=$FREESURFER_HOME/mni/share/perl5


echo "============================="
# echo "permissions"
# ls -ltra /flywheel/v0/

mkdir $FLYWHEEL_BASE/work
chmod 777 $FLYWHEEL_BASE/work

##############################################################################
# Handle INPUT file

# Find input file In input directory with the extension
input_file=`find $INPUT_DIR -iname '*.nii' -o -iname '*.nii.gz'`

# Check that input file exists
if [[ -e $input_file ]]; then
  echo "${CONTAINER}  Input file found: ${input_file}"

    # Determine the type of the input file
  if [[ "$input_file" == *.nii ]]; then
    type=".nii"
  elif [[ "$input_file" == *.nii.gz ]]; then
    type=".nii.gz"
  fi
  
else
  echo "${CONTAINER}: No inputs were found within input directory $INPUT_DIR"
  exit 1
fi

##############################################################################
# Set initial exit status
exit_status=0

# Read config file for options
config_newborn=$(jq -r '.config.newborn' $CONFIG_FILE)
if [[ $config_newborn == 'true' ]]; then
  age='--newborn'
else
  age="--age $input_age"
fi

# Run infant_recon_all with options
if [[ -e $input_file ]]; then
  echo "Running infant_recon_all on $input_file"
  /usr/local/freesurfer/8.1.0/bin/infant_recon_all -s $base_filename -i $input_file $age
  exit_status=$?
fi

# Organize output files
zip -r $OUTPUT_DIR/$base_filename.zip $WORKDIR/$base_filename
mri_convert --out_orientation RAS $WORKDIR/$base_filename/mri/norm.mgz ${OUTPUT_DIR}/${base_filename}_desc-norm.nii.gz
cp $WORKDIR/$base_filename/mri/aseg.nii.gz $OUTPUT_DIR/${base_filename}_desc-aseg_dseg.nii.gz

# Step 4: Extract cortical thickness measures
# Set SUBJECTS_DIR to the work directory
export SUBJECTS_DIR=$WORKDIR
aparcstats2table --subjects $base_filename --hemi lh --meas thickness --parc=aparc --tablefile=$WORKDIR/aparc_lh.csv
aparcstats2table --subjects $base_filename --hemi rh --meas thickness --parc=aparc --tablefile=$WORKDIR/aparc_rh.csv

# Step 5: Extract area measures
aparcstats2table --subjects $base_filename --hemi lh --meas area --parc=aparc --tablefile=$WORKDIR/aparc_area_lh.csv
aparcstats2table --subjects $base_filename --hemi rh --meas area --parc=aparc --tablefile=$WORKDIR/aparc_area_rh.csv

# Step 6: Extract volume measures
aparcstats2table --subjects $base_filename --hemi lh --meas volume --parc=aparc --tablefile=$WORKDIR/aparc_volume_lh.csv
aparcstats2table --subjects $base_filename --hemi rh --meas volume --parc=aparc --tablefile=$WORKDIR/aparc_volume_rh.csv

# Handle Exit status
if [[ $exit_status == 0 ]]; then
  echo -e "${CONTAINER} Success!"
  exit 0
else
  echo "${CONTAINER}  Something went wrong! infant_recon-all exited non-zero!"
  exit 1
fi
