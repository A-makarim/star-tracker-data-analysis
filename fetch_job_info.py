import requests
import json
from config import API_KEY

JOB_ID = '14931481'

def get_job_info(job_id):
    print(f"Fetching info for job {job_id}...")
    
    # Get tags
    response = requests.get(f'http://nova.astrometry.net/api/jobs/{job_id}/tags')
    print("Tags:", response.json())
    
    # Get machine tags
    response = requests.get(f'http://nova.astrometry.net/api/jobs/{job_id}/machine_tags')
    print("Machine Tags:", response.json())
    
    # Get objects in field
    response = requests.get(f'http://nova.astrometry.net/api/jobs/{job_id}/objects_in_field')
    print("Objects in field:", response.json())
    
    # Get calibration
    response = requests.get(f'http://nova.astrometry.net/api/jobs/{job_id}/calibration')
    print("Calibration:", response.json())

if __name__ == "__main__":
    get_job_info(JOB_ID)
