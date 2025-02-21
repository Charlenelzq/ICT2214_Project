#!/usr/bin/env python3

import requests
import http.client
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup  # Import BeautifulSoup
import threading
import queue


NUM_THREADS = 5
LFI_PARAMETERS_FILE = "wordlists/lfi-parameters.txt"
lock = threading.Lock()
# Create a set to store found URLs
processed_url = set()
found_urls_queue = queue.Queue()
uploadable_urls = set()


def check_directory(url, directory, COOKIE):
    full_url = f"{url}{directory}"
    new_url = None

    if "logout" in full_url:
        return
    try:
        response = requests.get(full_url, allow_redirects=True, cookies=COOKIE)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            anchor_tags = soup.find_all('a', recursive=True)
            for tag in anchor_tags:
                href = tag.get('href')
                print(href)
                if not urlparse(href).scheme and not href.startswith('#'):
                    if href.startswith('/'):
                        new_url = (href)
                    elif href.startswith('../'):
                        count = href.count('../')
                        tmp = directory.split('/')[:-(count+1)]
                        href = '/'.join(tmp) + href[count*3:]
                        new_url = href
                    else:
                        if href.startswith('./'):
                            new_url = directory + href[1:]
                        else:
                            if href.startswith('?'):
                                new_url = "/".join(directory.split("?")[:-1]) + href
                            else:
                                new_url = "/".join(directory.split("/")[:-2]) + href
                          
                        
            # Check if the page contains a file upload capability
            file_upload_form = soup.find_all('input', {'type': 'file'})
            
            
            if new_url and new_url not in processed_url:
                with lock:
                    processed_url.add(new_url)
                    found_urls_queue.put(new_url)
            if file_upload_form:
                with lock:
                    uploadable_urls.add(full_url)

    except requests.exceptions.RequestException:
        pass


def clean_found_urls(base_url, processed_url):
    cleaned_urls = set()
    for url in processed_url:
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
    for directory in directories:
        full_url = f"{url}{directory}"
        try:
            response = requests.get(full_url, allow_redirects=True, cookies=COOKIE)
            if response.status_code == 200:
                found_urls_queue.put(directory)
                processed_url.add(directory)
        except requests.exceptions.RequestException:
            pass

    while not found_urls_queue.empty():        
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            while not found_urls_queue.empty():
                directory = found_urls_queue.get()
                executor.submit(check_directory, url, directory, COOKIE)
            executor.shutdown(wait=True)
        
    # # Process newly found URLs
    # while not found_urls_queue.empty():
    #     directory = found_urls_queue.get()
    #     check_directory(url, directory, COOKIE)

    # # Output the results (optional)
    # print("\n[+] Found Pages:")
    # for page in processed_url:
    #     print(f"URL: {page}")
    # print(f"\n[+] Found {len(processed_url)} pages")
    return processed_url, uploadable_urls

    
   