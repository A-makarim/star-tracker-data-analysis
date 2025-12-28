import requests
import json
import time
import os
import rawpy
import imageio.v3 as imageio
import numpy as np
from config import API_KEY

class AstrometrySolver:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://nova.astrometry.net/api"
        self.session = None

    def login(self):
        print("Logging in to Astrometry.net...")
        response = requests.post(f"{self.base_url}/login", data={'request-json': json.dumps({"apikey": self.api_key})})
        result = response.json()
        if result.get('status') == 'success':
            self.session = result.get('session')
            print(f"Login successful. Session: {self.session}")
        else:
            raise Exception(f"Login failed: {result}")

    def upload_image(self, file_path):
        if not self.session:
            self.login()
        
        print(f"Uploading {file_path}...")
        with open(file_path, 'rb') as f:
            # The API expects multipart/form-data
            # request-json contains session and other options
            json_data = {"session": self.session, "allow_commercial_use": "d", "allow_modifications": "d", "publicly_visible": "y"}
            
            files = {'file': f}
            data = {'request-json': json.dumps(json_data)}
            
            response = requests.post(f"{self.base_url}/upload", files=files, data=data)
            
        result = response.json()
        if result.get('status') == 'success':
            sub_id = result.get('subid')
            print(f"Upload successful. Submission ID: {sub_id}")
            return sub_id
        else:
            raise Exception(f"Upload failed: {result}")

    def wait_for_submission(self, sub_id):
        print(f"Waiting for submission {sub_id} to process...")
        while True:
            response = requests.get(f"{self.base_url}/submissions/{sub_id}")
            result = response.json()
            
            if result.get('processing_finished'):
                job_ids = result.get('jobs', [])
                if job_ids and job_ids[0] is not None:
                    print(f"Submission processed. Job IDs: {job_ids}")
                    return job_ids
                else:
                    # Sometimes processing finishes but no jobs are created if it failed immediately
                    print("Submission finished but no jobs found (likely failed).")
                    print(f"Full response: {json.dumps(result, indent=2)}")
                    return []
            
            time.sleep(2)

    def wait_for_job(self, job_id):
        print(f"Waiting for job {job_id} to finish...")
        while True:
            response = requests.get(f"{self.base_url}/jobs/{job_id}")
            result = response.json()
            
            status = result.get('status')
            if status == 'success':
                print(f"Job {job_id} succeeded!")
                return True
            elif status == 'failure':
                print(f"Job {job_id} failed.")
                return False
            
            time.sleep(2)

    def get_job_info(self, job_id):
        # Get calibration info
        response = requests.get(f"{self.base_url}/jobs/{job_id}/calibration")
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_annotations(self, job_id):
        # Get annotations (constellations, stars, etc.)
        response = requests.get(f"{self.base_url}/jobs/{job_id}/annotations")
        if response.status_code == 200:
            return response.json()
        return None

def convert_raw_to_jpg(raw_path, output_path):
    print(f"Converting {raw_path} to {output_path} for upload...")
    with rawpy.imread(raw_path) as raw:
        rgb = raw.postprocess()
        # Resize if too large to save bandwidth/time? 
        # For now, let's just save as is, maybe with some compression
        imageio.imwrite(output_path, rgb, quality=85)

def main():
    if API_KEY == 'YOUR_API_KEY_HERE':
        print("Please set your API_KEY in config.py first!")
        return

    solver = AstrometrySolver(API_KEY)
    
    # 1. Process Original Image (Converted to JPG)
    raw_image = 'IMG_1085.CR2'
    jpg_image = 'IMG_1085_converted.jpg'
    
    if not os.path.exists(jpg_image):
        convert_raw_to_jpg(raw_image, jpg_image)
    
    # 2. Process Refined Image
    refined_image = 'refined_image.png'
    if not os.path.exists(refined_image):
        print(f"{refined_image} not found. Please run refined_star_detection.py first.")
        return

    images_to_solve = [jpg_image, refined_image]
    
    for img_path in images_to_solve:
        print(f"\n--- Solving {img_path} ---")
        try:
            sub_id = solver.upload_image(img_path)
            job_ids = solver.wait_for_submission(sub_id)
            
            if not job_ids:
                print("No jobs generated.")
                continue
                
            # Just track the first job
            job_id = job_ids[0]
            success = solver.wait_for_job(job_id)
            
            if success:
                calib = solver.get_job_info(job_id)
                print(f"Calibration Data for {img_path}:")
                print(json.dumps(calib, indent=2))
                
                # You can also fetch annotations
                # annotations = solver.get_annotations(job_id)
                # print(json.dumps(annotations, indent=2))
                
                # Save calibration to file
                base_name = os.path.splitext(img_path)[0]
                with open(f'{base_name}_calibration.json', 'w') as f:
                    json.dump(calib, f, indent=2)
                print(f"Saved calibration to {base_name}_calibration.json")
                
        except Exception as e:
            print(f"An error occurred processing {img_path}: {e}")

if __name__ == "__main__":
    main()
