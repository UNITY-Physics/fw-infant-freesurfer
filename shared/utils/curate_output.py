import flywheel
import json
import pandas as pd
from datetime import datetime
import re
import os
import shutil
from dateutil import parser
import logging


log = logging.getLogger(__name__)


#  Module to identify the correct template use for the subject VBM analysis based on age at scan
#  Need to get subject identifiers from inside running container in order to find the correct template from the SDK
def find_gear_version(analyses, filename):
    for asys in analyses:
        for file in asys.files:
            if file.name == filename:
                if 'gambas' in asys.label:
                    return asys.label.split(' ')[0]
                elif 'mrr' in asys.label:
                    return f"{file.gear_info.name}/{file.gear_info.version}"
    return None
def get_age(session, dicom_header):
    
    # -------------------  Get the subject age & matching template  -------------------  #
    # uploaded demographics the most reliable, after that try to get from dicom header
    # get the T2w axi dicom acquisition from the session
    # Should contain the DOB in the dicom header
    # Some projects may have DOB removed, but may have age at scan in the subject container

    age_source, age = None, None

    # Check if age is in custom session info
    # if session.info.get('age_at_scan_months', None) != None and str(session.info.get('age_at_scan_months')) != "0":
    #     age_source = 'custom_info'
    #     age =  session.info.get('age_at_scan_months')
    # else:
    try:
        log.info(f"PatientAge: {dicom_header.info.get('PatientAge')}")
        # Check for PatientAge in the DICOM header
        if dicom_header.info.get('PatientAge', None) is not None:
            age = re.sub('\D', '', dicom_header.info.get('PatientAge'))
            log.info(f"No custom demographic age uploaded in session info! Trying PatientAge from dicom...")
            age_raw = dicom_header.info['PatientAge']

            # Parse age and convert to months
            unit = age_raw[-1].upper()  # Extract the unit (D = Days, W = Weeks, M = Months, Y = Years)
            log.info(f"PatientAge raw value: {age_raw}, unit: {unit}")
            try:
                numeric_age = re.findall(r'\d+', age_raw)
                #numeric_age = int(re.sub('\D', '', age_raw))  # Remove non-numeric characterq 
                
                age_source = 'dicom_age'
                if numeric_age and unit == 'D':  # Days to months
                    
                    age = int(numeric_age[0]) // 30
                
                elif numeric_age and unit == 'W':  # Weeks to months
                    
                    age = int(numeric_age[0]) // 4
                    
                elif numeric_age and unit == 'M':  # Already in months
                    
                    age = int(numeric_age[0])
                
                elif numeric_age and unit == 'Y':  # Years to months
                    
                    age = int(numeric_age[0]) * 12
                
                else:
                    log.warning("Unknown unit for PatientAge. Setting age to None.")
                    age_source, age = None, None

            except TypeError as te:
                log.exception(f"Caught a TypeError: {te}")
                age_source, age = None, None
            except Exception as e:
                log.exception(f"Error parsing dates from dicom: {e}")
                age_source, age = None, None

            
            
            

            log.info(f"PatientAge from dicom: {age_raw} -> {age} months")

        
        if age is None or str(age) == "0":
            # If PatientAge is unavailable or invalid, fallback to PatientBirthDate and SeriesDate
            dob = dicom_header.info.get('PatientBirthDate', None)
            series_date = dicom_header.info.get('SeriesDate', None)
            if dob != None and series_date != None:
                log.info("Trying DOB from dicom...")    
                log.warning("WARNING: This may be inaccurate if false DOB was entered at time of scanning!")
                # Calculate age at scan
                # Calculate the difference in months
                
                series_dt = parser.parse(series_date)
                dob_dt = parser.parse(dob)
                age_days = (series_dt - dob_dt).days

                # Convert days to months
                age = age_days // 30
                age_source = 'dicom_DOB'

                
        
                # Adjust if the day in series_dt is earlier than the day in dob_dt
                if age_days < 0:
                    log.error(f"Series date {series_date} is before {dob_dt}. Setting age to None.")
                    age_source, age = None, None

            else:
                log.warning("No valid birthdate or series date found in dicom header. Setting age to None.")
                age_source, age = None, None
    except ValueError as ve:
        log.exception(f"Caught a ValueError: {ve}")
        age_source, age = None, None
    except TypeError as te:
        log.exception(f"Caught a TypeError: {te}")
        age_source, age = None, None
    except Exception as e:
        log.exception(f"Error parsing dates from dicom: {e}")
        age_source, age = None, None

    try:
        age = float(age)
        if age <= 0 or age > 1200:
            log.warning(f"Age out of expected bounds: {age}")
            age_source, age = None, None
            
    except ValueError as ve:
        log.exception(f"Caught a ValueError: {ve}")
        age_source, age = None, None
    except TypeError as te:
        log.exception(f"Caught a TypeError: {te}")
        age_source, age = None, None
    except Exception as e:
        log.exception(f"Age not found or not a valid number: {age}". format(e))
        age_source, age = None, None

    log.info(f"{age}, {age_source}")
    return age, age_source

def demo(context):

    # Initialize variables
    data = []
    sex = 'NA'
    
    # Read config.json file
    p = open('/flywheel/v0/config.json')
    config = json.loads(p.read())

    # Read API key in config file
    api_key = (config['inputs']['api-key']['key'])
    fw = flywheel.Client(api_key=api_key)
    
    # Get the input file id
    input_container = context.client.get_analysis(context.destination["id"])

    # Get the subject id from the session id
    # & extract the subject container
    subject_id = input_container.parents['subject']
    subject_container = context.client.get(subject_id)
    subject = subject_container.reload()
    log.info(f"Subject label: {subject.label}")
    subject_label = subject.label

    # Get the session id from the input file id
    # & extract the session container
    session_id = input_container.parents['session']
    session_container = context.client.get(session_id)
    session = session_container.reload()
    session_info = session.info
    session_label = session.label
    log.info(f"Session label: {session.label}")
    
    # -------------------  Get Acquisition label -------------------  #

    # Specify the directory you want to list files from
    directory_path = '/flywheel/v0/input/input'
    gear_v = 'NA'
    # List all files in the specified directory
    for filename in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, filename)):
            filename_without_extension = filename.split('.')[0]
            no_white_spaces = filename_without_extension.replace(" ", "")
            # no_white_spaces = filename.replace(" ", "")
            acquisition_cleaned = re.sub(r'[^a-zA-Z0-9]', '_', no_white_spaces)
            acquisition_cleaned = acquisition_cleaned.rstrip('_') # remove trailing underscore
             # default value for gear version
            #look for the file and the mrr/gambas version associated with it

            gear_v = find_gear_version(session.analyses, filename)

            if not gear_v:
                for acq in session.acquisitions():
                    acq = acq.reload()
                    gear_v = find_gear_version(acq.analyses, filename)
                    if gear_v:
                        break
                    
    # -------------------  Get the subject age & matching template  -------------------  #

    # get the T2w axi dicom acquisition from the session
    # Should contain the DOB in the dicom header
    # Some projects may have DOB removed, but may have age at scan in the subject container

    sex,age,age_source, scannerSoftwareVersion = None,None,None, "NA"

    if any(age not in [None, 0, "0"] for age in [session.info.get('childTimepointAge_months',None), session.info.get('age_at_scan_months',None)]):
        age_source = 'custom_info'
        age =  session.info.get('childTimepointAge_months')
    else:
        acqs = [acq for acq in session.acquisitions() if ('T2' in acq.label or 'T1' in acq.label) and 'Segmentation' not in acq.label and 'Align' not in acq.label]
        if acqs:
            acq = acqs[0]
        # for acq in session.acquisitions():
            log.info(f"ACQUISITION USED: {acq.label}")
            acq = acq.reload()
            # if 'T2' in acq.label and 'AXI' in acq.label and 'Segmentation' not in acq.label and 'Align' not in acq.label: 
            for file_obj in acq.files: # get the files in the acquisition
                # Screen file object information & download the desired file
                if file_obj['type'] == 'dicom':
                    
                    dicom_header = fw._fw.get_acquisition_file_info(acq.id, file_obj.name)
                    age, age_source = get_age(session, dicom_header)
                    scannerSoftwareVersion = dicom_header.info.get('SoftwareVersions', "NA")

                    try:
                        sex = session_info.get("childBiologicalSex", session_info.get("sex_at_birth", dicom_header.info.get("PatientSex","NA")))
                    except:
                        continue

    
    # assign values to lists. 
    data = [{'subject': subject_label, 'session': session_label, 'age': age, 'age_source': age_source, 'sex': sex, 'acquisition': acquisition_cleaned, "input_gear_v": gear_v, "scanner_software_v": scannerSoftwareVersion }]  
    # Creates DataFrame.  
    demo = pd.DataFrame(data)

    log.info(f"Demographics:  {subject_label} {session_label} {age} {sex}")

    return demo
