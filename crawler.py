#!/usr/bin/env python3

import requests
import http.client
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup  # Import BeautifulSoup
import threading


NUM_THREADS = 5
LFI_PARAMETERS_FILE = "wordlists/lfi-parameters.txt"
lock = threading.Lock()
# Create a set to store found URLs
found_urls = set()
uploadable_urls = set()


def check_directory(url, directory, COOKIE):
    full_url = f"{url}{directory}"

    if "logout" in full_url:
        return
    try:
        response = requests.get(full_url, allow_redirects=True, cookies=COOKIE)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            anchor_tags = soup.find_all('a', recursive=True)
            for tag in anchor_tags:
                href = tag.get('href')
                if not urlparse(href).scheme and not href.startswith('#'):
                    if href.startswith('/'):
                        found_urls.add(href)
                    elif href.startswith('../'):
                        count = href.count('../')
                        tmp = directory.split('/')[:-(count+1)]
                        href = '/'.join(tmp) + href[count*3:]
                        found_urls.add(href)
                    else:
                        if href.startswith('./'):
                            found_urls.add(directory + href[1:])
                        else:
                            if href.startswith('?'):
                                found_urls.add("/".join(directory.split("?")[:-1]) + href)
                            else:
                                found_urls.add("/".join(directory.split("/")[:-2]) + href)
                          
                        
            # Check if the page contains a file upload capability
            file_upload_form = soup.find_all('input', {'type': 'file'})
            if file_upload_form:
                with lock:
                    uploadable_urls.add(full_url)

    except requests.exceptions.RequestException:
        pass


def clean_found_urls(base_url, found_urls):
    cleaned_urls = set()
    for url in found_urls:
        if "?" in url:
            tmp = url.split("?")
            tmp1 = tmp[1].split("=")[0]
            cleaned_urls.add(base_url + tmp[0] + "?" + tmp1 + "=")
        else:
            cleaned_urls.add(base_url + url)
    return cleaned_urls


def check_lfi(url_list):
    lfi_targets = set()
    with open(LFI_PARAMETERS_FILE, "r") as file:
        lfi_parameters = [line.strip() for line in file]
    for url in url_list:
        for payload in lfi_parameters:
            if payload in url:
                lfi_targets.add(url)
                print(f"[+] Potential LFI vulnerability found at: {url}")
    return lfi_targets

            
def main_crawl(url, wordlist, COOKIE):
    with open(wordlist, "r") as file:
        directories = [line.strip() for line in file]
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        executor.map(lambda directory: check_directory(url, directory, COOKIE), directories)

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        executor.map(lambda directory: check_directory(url, directory, COOKIE), found_urls)

    # # Output the results (optional)
    # print("\n[+] Found Pages:")
    # for page in found_urls:
    #     print(f"URL: {page}")
    # print(f"\n[+] Found {len(found_urls)} pages")
    return found_urls, uploadable_urls

    
   