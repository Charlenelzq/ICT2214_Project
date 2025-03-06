# FusionInclusion (LFI and File Upload Vulnerability Exploit)

## Overview
This project combines **Local File Inclusion (LFI) and File Upload Vulnerabilities** to exploit web applications effectively. The script automates the testing process, making it easier to identify vulnerabilities.

## Features
✅ Automated LFI detection using common traversal patterns.  
✅ File Upload scanning to locate vulnerable directories.  
✅ Bypass techniques using encoding, PHP wrappers, and log poisoning.  
✅ Session handling for authenticated web applications.  
✅ Brute-force LFI attempts across various directories.  
✅ Command execution via LFI to escalate access.  
✅ Multi-threaded scanning for faster exploitation.  
✅ Customizable payloads to evade WAFs and security filters.

## Getting Started
Before running the script, follow these steps:

1. **Modify the Cookie**:
   - Ensure you update the cookie in the script to match your session.

2. **Choose Your Target**:
   - Determine whether you are testing on **DVWA (Damn Vulnerable Web Application)** or our own hosted website:  
     `http://ict2214p1b2.mooo.com/`
   - Comment/uncomment the necessary sections in the provided script based on the target.

## Login Credentials
- if using our website, you may use any ONE of the credentials listed

| Target | Username | Password |
|--------|----------|----------|
| **DVWA** | `admin` | `password` |
| **Our Website** | `pohchuan` | `password1` |
|  | `jake` | `password2` |
|  | `charlene` | `password3` |
|  | `samantha` | `password4` |
|  | `ethan` | `password5` |

## Wordlist Selection
Within the project folder, we have provided both **short** and **long** wordlists. Choose the appropriate one based on your testing needs and update the script accordingly.

## Running the Script

To run the script, simply type:
```sh
python main.py
```

The script will prompt indicators for success and failure: (depending on which website you are targeting)
For our website:
- If prompted for success, just leave it empty. (press enter)
- If prompted for failure, enter: File not found.

For DVWA:
- If prompted for success, just leave it empty. (press enter)
- If prompted for failure, just leave it empty. (press enter)

## Viewing Results
After executing the script, the results will be saved in `vuln_report.txt`. To view the output, simply run:
```sh
cat vuln_report.txt
```

## Notes
- Ensure that the necessary dependencies are installed before running the script.


