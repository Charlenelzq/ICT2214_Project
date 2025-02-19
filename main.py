#!/usr/bin/env python3

from argparse import ArgumentParser
from sys import exit
import requests
from bs4 import BeautifulSoup
import urllib.parse
import crawler


COOKIE = {
    'PHPSESSID': 'ks3ah94pfi21cdhe2ck77b6h6g',
    'security': 'medium'
}




"""
Get command line arguments for the script 
"""
def getArgs():
    parser = ArgumentParser()
    parser.add_argument("url",
                        help="Target URL")
    parser.add_argument("wordlist",
                        help="Wordlist")
    parser.add_argument(
        "-p", "--payload",
        type=str,
        choices=['rev', 'webshell'],
        required=True,
        help="Specify the payload type, Web Shell or Reverse Shell"
    )
    parser.add_argument("-ip",
                         help="IP of listening host (rev shell)", 
                         default=None)
    parser.add_argument("-rport", 
                        help="Listening port (rev shell)", 
                        type=int, 
                        default=0)
    args = parser.parse_args()

    if args.payload == 'rev':
        if args.ip is None or args.rport == 0:
            exit("Please specify the IP and port for Reverse Shell")
    return args



def main():
    # Main function
    arguments = getArgs()
    found_urls = crawler.main_crawl(arguments.url, arguments.wordlist, COOKIE)
    print("Crawling complete.")
    




if __name__ == "__main__":
    main()