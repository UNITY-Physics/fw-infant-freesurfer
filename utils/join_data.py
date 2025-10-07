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

    # area data
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
    lh_vol_filePath = '/flywheel/v0/work/aparc_volume_lh.csv'
    rh_vol_filePath = '/flywheel/v0/work/aparc_volume_rh.csv'

    lh_vol = pd.read_csv(lh_vol_filePath, sep='\t', engine='python')
    rh_vol = pd.read_csv(rh_vol_filePath, sep='\t', engine='python')
    # smush the data together
    frames = [demographics, lh_vol, rh_vol]
    df = pd.concat(frames, axis=1)
    out_name = f"{acq}_volume.csv"
    outdir = ('/flywheel/v0/output/' + out_name)
    df.to_csv(outdir)
    

