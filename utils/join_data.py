import flywheel
import json
import pandas as pd
from datetime import datetime
import re
import os
import shutil
import logging


log = logging.getLogger(__name__)

#  Module to identify the correct template use for the subject VBM analysis based on age at scan
#  Need to get subject identifiers from inside running container in order to find the correct template from the SDK


def housekeeping(demographics):

    acq = demographics['acquisition'].values[0]
    sub = demographics['subject'].values[0]
    # -------------------  Concatenate the data  -------------------  #

    # Start with cortical thickness data
    filePath = '/flywheel/v0/work/aparc_lh.csv'
    lh_thickness = pd.read_csv(filePath, sep='\t', engine='python')

    filePath = '/flywheel/v0/work/aparc_rh.csv'
    rh_thickness = pd.read_csv(filePath, sep='\t', engine='python')

    # smush the data together
    frames = [demographics, lh_thickness, rh_thickness]
    df = pd.concat(frames, axis=1)
    out_name = f"{acq}_thickness.csv"
    outdir = ('/flywheel/v0/output/' + out_name)
    df.to_csv(outdir)

    lh_area_filePath = '/flywheel/v0/work/aparc_area_lh.csv'
    rh_area_filePath = '/flywheel/v0/work/aparc_area_rh.csv'

    lh_area = pd.read_csv(lh_area_filePath, sep='\t', engine='python')
    rh_area = pd.read_csv(rh_area_filePath, sep='\t', engine='python')

    # smush the data together
    frames = [demographics, lh_area, rh_area]
    df = pd.concat(frames, axis=1)
    out_name = f"{acq}_area.csv"
    outdir = ('/flywheel/v0/output/' + out_name)
    df.to_csv(outdir)

    # volume data
    filePath = '/flywheel/v0/work/synthseg.vol.csv'
    with open(filePath) as csv_file:
        vol_data = pd.read_csv(csv_file, index_col=None, header=0) 
        vol_data = vol_data.drop('subject', axis=1)
    
    # smush the data together
    frames = [demographics, vol_data]
    df = pd.concat(frames, axis=1)
    out_name = f"{acq}_volume.csv"
    outdir = ('/flywheel/v0/output/' + out_name)
    df.to_csv(outdir)

    # SynthSeg QC data
    filePath = '/flywheel/v0/work/synthseg.qc.csv'
    with open(filePath) as csv_file:
        qc_data = pd.read_csv(csv_file, index_col=None, header=0) 
        qc_data = qc_data.drop('subject', axis=1)

    # smush the data together
    frames = [demographics, qc_data]
    df = pd.concat(frames, axis=1)
    out_name = f"{acq}_qc.csv"
    outdir = ('/flywheel/v0/output/' + out_name)
    df.to_csv(outdir)
    

    # Segmentation output
    synthSR_path = '/flywheel/v0/work/synthSR.nii.gz'
    aseg_path = '/flywheel/v0/work/aparc+aseg.nii.gz'

    # New file name with label
    SR_output = f"/flywheel/v0/output/{acq}_synthSR.nii.gz"
    aseg_output = f"/flywheel/v0/output/{acq}_aparc+aseg.nii.gz"

    shutil.copy(synthSR_path, SR_output)
    shutil.copy(aseg_path, aseg_output)

    # # -------------------  Generate QC image  -------------------  #


    # Run the render script to generate the QC image 

    # # Construct the command to run your bash script with variables as arguments
    # qc_command = f"/flywheel/v0/utils/render.sh '{subject_label}' '{session_label}' '{cleaned_string}' '{infant}'"

    # # Execute the bash script
    # subprocess.run(qc_command, shell=True)

