#!/usr/bin/env python3
import requests
import cloudscraper
import tls_client
from fake_useragent import UserAgent
import httpx
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import mechanize
import asyncio
import aiohttp
import pycurl
from io import BytesIO
from urllib.request import Request, urlopen
import http.client
from urllib.parse import urlparse
import os  # For environment variables
import time  # For timing
import random  # For generating random four-digit numbers
import json  # For handling JSON content
from pathlib import Path  # For handling file paths
import re  # For sanitizing URLs
from bs4 import BeautifulSoup  # For formatting HTML content

def get_random_user_agent():
    """
    Generates a random User-Agent string.
    """
    try:
        ua = UserAgent(os='linux', browsers=['firefox'])
        return ua.random
    except Exception as e:
        print(f"[Error] Failed to initialize UserAgent: {e}")
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
               "AppleWebKit/537.36 (KHTML, like Gecko) " \
               "Chrome/103.0.0.0 Safari/537.36"

def sanitize_url(url):
    """
    Sanitizes the URL to create a valid filename by removing or replacing
    characters that are invalid in filenames.
    """
    # Remove the scheme (http:// or https://)
    sanitized = re.sub(r'^https?:\/\/', '', url)
    # Replace non-alphanumeric characters with underscores
    sanitized = re.sub(r'[^A-Za-z0-9]', '_', sanitized)
    # Truncate to a reasonable length to avoid overly long filenames
    return sanitized[:50]

def save_result(method_name, url, content):
    """
    Saves the scraping result to an HTML or JSON file inside the 'data' folder.
    The filename follows the pattern: (method)_(sanitizedURL)_(random4digits).(html/json)
    """
    # Ensure the 'data' directory exists
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)

    # Generate a random four-digit number
    rand_num = random.randint(1000, 9999)

    # Sanitize the URL for filename
    sanitized_url = sanitize_url(url)

    # Determine file extension and format content based on content type
    if is_json(content):
        file_ext = 'json'
        try:
            json_content = json.loads(content)
            data_to_save = json.dumps(json_content, indent=4)
        except json.JSONDecodeError:
            print("[Warning] Content is not valid JSON. Saving as raw HTML.")
            file_ext = 'html'
            data_to_save = content
    else:
        file_ext = 'html'
        # Prettify HTML content using BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        data_to_save = soup.prettify()

    # Create the filename
    filename = f"{method_name}_{sanitized_url}_{rand_num}.{file_ext}"
    file_path = data_dir / filename

    # Write the content to the file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data_to_save)
        print(f"Result saved to {file_path}\n")
    except Exception as e:
        print(f"Failed to save result: {e}\n")

def is_json(content):
    """
    Checks if the given content is in JSON format.
    """
    try:
        json.loads(content)
        return True
    except ValueError:
        return False

def try_requests(url, headers, full_output=False):
    """
    Attempts to scrape the URL using the requests library.
    Returns a tuple (status, content).
    """
    try:
        response = requests.get(url, headers=headers)
        print("Requests:")
        print(f"Status Code: {response.status_code}")
        if response.status_code != 403:
            content = response.text
            if full_output:
                print(f"Content:\n{content}\n")
            else:
                lines = content.splitlines()
                first_5_lines = '\n'.join(lines[:5])
                print(f"Content (First 5 Lines):\n{first_5_lines}\n")
            return (response.status_code == 200, content)
        else:
            print("Response content not displayed due to status code 403.\n")
            return (False, None)
    except Exception as e:
        print(f"Requests failed: {e}\n")
        return (False, None)

def try_cloudscraper(url, headers, full_output=False):
    """
    Attempts to scrape the URL using cloudscraper to bypass Cloudflare.
    Returns a tuple (status, content).
    """
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, headers=headers)
        print("Cloudscraper:")
        print(f"Status Code: {response.status_code}")
        if response.status_code != 403:
            content = response.text
            if full_output:
                print(f"Content:\n{content}\n")
            else:
                lines = content.splitlines()
                first_5_lines = '\n'.join(lines[:5])
                print(f"Content (First 5 Lines):\n{first_5_lines}\n")
            return (response.status_code == 200, content)
        else:
            print("Response content not displayed due to status code 403.\n")
            return (False, None)
    except Exception as e:
        print(f"Cloudscraper failed: {e}\n")
        return (False, None)

def try_requests_session(url, headers, full_output=False):
    """
    Attempts to scrape the URL using requests.Session.
    Returns a tuple (status, content).
    """
    try:
        session = requests.Session()
        response = session.get(url, headers=headers)
        print("Requests.Session:")
        print(f"Status Code: {response.status_code}")
        if response.status_code != 403:
            content = response.text
            if full_output:
                print(f"Content:\n{content}\n")
            else:
                lines = content.splitlines()
                first_5_lines = '\n'.join(lines[:5])
                print(f"Content (First 5 Lines):\n{first_5_lines}\n")
            return (response.status_code == 200, content)
        else:
            print("Response content not displayed due to status code 403.\n")
            return (False, None)
    except Exception as e:
        print(f"Requests.Session failed: {e}\n")
        return (False, None)

def try_tls_client(url, headers, full_output=False):
    """
    Attempts to scrape the URL using tls_client with a specific client identifier.
    Returns a tuple (status, content).
    """
    try:
        session = tls_client.Session(client_identifier='chrome_103')
        response = session.get(url, headers=headers)
        print("tls_client:")
        print(f"Status Code: {response.status_code}")
        if response.status_code != 403:
            content = response.text
            if full_output:
                print(f"Content:\n{content}\n")
            else:
                lines = content.splitlines()
                first_5_lines = '\n'.join(lines[:5])
                print(f"Content (First 5 Lines):\n{first_5_lines}\n")
            return (response.status_code == 200, content)
        else:
            print("Response content not displayed due to status code 403.\n")
            return (False, None)
    except Exception as e:
        print(f"tls_client failed: {e}\n")
        return (False, None)

def try_httpx(url, headers, full_output=False):
    """
    Attempts to scrape the URL using the httpx library.
    Returns a tuple (status, content).
    """
    try:
        response = httpx.get(url, headers=headers)
        print("httpx:")
        print(f"Status Code: {response.status_code}")
        if response.status_code != 403:
            content = response.text
            if full_output:
                print(f"Content:\n{content}\n")
            else:
                lines = content.splitlines()
                first_5_lines = '\n'.join(lines[:5])
                print(f"Content (First 5 Lines):\n{first_5_lines}\n")
            return (response.status_code == 200, content)
        else:
            print("Response content not displayed due to status code 403.\n")
            return (False, None)
    except Exception as e:
        print(f"httpx failed: {e}\n")
        return (False, None)

def try_urllib3(url, headers, full_output=False):
    """
    Attempts to scrape the URL using urllib3 library.
    Returns a tuple (status, content).
    """
    try:
        http = urllib3.PoolManager()
        response = http.request('GET', url, headers=headers)
        print("urllib3:")
        print(f"Status Code: {response.status}")
        if response.status != 403:
            content = response.data.decode('utf-8', errors='ignore')
            if full_output:
                print(f"Content:\n{content}\n")
            else:
                lines = content.splitlines()
                first_5_lines = '\n'.join(lines[:5])
                print(f"Content (First 5 Lines):\n{first_5_lines}\n")
            return (response.status == 200, content)
        else:
            print("Response content not displayed due to status code 403.\n")
            return (False, None)
    except Exception as e:
        print(f"urllib3 failed: {e}\n")
        return (False, None)

def try_selenium(url, headers, full_output=False):
    """
    Attempts to scrape the URL using Selenium with a headless Chrome browser.
    Returns a tuple (status, content).
    """
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument(f'user-agent={headers["User-Agent"]}')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        print("Selenium:")
        # Selenium doesn't provide HTTP status codes, assuming success if no exception
        status_code = 200
        print(f"Status Code: {status_code}")
        content = driver.page_source
        if full_output:
            print(f"Content:\n{content}\n")
        else:
            lines = content.splitlines()
            first_5_lines = '\n'.join(lines[:5])
            print(f"Content (First 5 Lines):\n{first_5_lines}\n")
        driver.quit()
        return (True, content)
    except Exception as e:
        print(f"Selenium failed: {e}\n")
        return (False, None)

def try_mechanize(url, headers, full_output=False):
    """
    Attempts to scrape the URL using mechanize, simulating a browser.
    Returns a tuple (status, content).
    """
    try:
        br = mechanize.Browser()
        br.addheaders = [(key, value) for key, value in headers.items()]
        br.set_handle_robots(False)
        response = br.open(url)
        print("Mechanize:")
        status_code = response.code
        print(f"Status Code: {status_code}")
        if status_code != 403:
            content = response.read().decode('utf-8', errors='ignore')
            if full_output:
                print(f"Content:\n{content}\n")
            else:
                lines = content.splitlines()
                first_5_lines = '\n'.join(lines[:5])
                print(f"Content (First 5 Lines):\n{first_5_lines}\n")
            return (status_code == 200, content)
        else:
            print("Response content not displayed due to status code 403.\n")
            return (False, None)
    except Exception as e:
        print(f"Mechanize failed: {e}\n")
        return (False, None)

def try_pycurl(url, headers, full_output=False):
    """
    Attempts to scrape the URL using pycurl.
    Returns a tuple (status, content).
    """
    try:
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        header_list = [f"{key}: {value}" for key, value in headers.items()]
        c.setopt(c.HTTPHEADER, header_list)
        c.perform()
        status_code = c.getinfo(pycurl.RESPONSE_CODE)
        print("pycurl:")
        print(f"Status Code: {status_code}")
        if status_code != 403:
            content = buffer.getvalue().decode('utf-8', errors='ignore')
            if full_output:
                print(f"Content:\n{content}\n")
            else:
                lines = content.splitlines()
                first_5_lines = '\n'.join(lines[:5])
                print(f"Content (First 5 Lines):\n{first_5_lines}\n")
            c.close()
            return (status_code == 200, content)
        else:
            print("Response content not displayed due to status code 403.\n")
            c.close()
            return (False, None)
    except Exception as e:
        print(f"pycurl failed: {e}\n")
        return (False, None)

async def try_aiohttp(url, headers, full_output=False):
    """
    Attempts to scrape the URL using aiohttp for asynchronous requests.
    Returns a tuple (status, content).
    """
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=60) as response:
                status_code = response.status
                print("aiohttp:")
                print(f"Status Code: {status_code}")
                if status_code != 403:
                    content = await response.text()
                    if full_output:
                        print(f"Content:\n{content}\n")
                    else:
                        lines = content.splitlines()
                        first_5_lines = '\n'.join(lines[:5])
                        print(f"Content (First 5 Lines):\n{first_5_lines}\n")
                    return (status_code == 200, content)
                else:
                    print("Response content not displayed due to status code 403.\n")
                    return (False, None)
    except Exception as e:
        print(f"aiohttp failed: {e}\n")
        return (False, None)

def display_menu():
    """
    Displays the scraping methods menu and returns the user's choice.
    """
    menu = """
What method would you like to scrape your request URL with?
1. Requests
2. Cloudscraper
3. Requests.Session
4. tls_client
5. httpx
6. urllib3
7. Selenium
8. Mechanize
9. pycurl
10. aiohttp
11. All
"""
    print(menu)
    while True:
        try:
            choice = int(input("Enter the number corresponding to your choice: "))
            if 1 <= choice <= 11:
                return choice
            else:
                print("Please enter a number between 1 and 11.\n")
        except ValueError:
            print("Invalid input. Please enter a valid number.\n")

def main():
    """
    Main function that orchestrates the scraping attempts based on user selection.
    """
    url = input("Enter the URL to scrape (A VPN is highly recommended if you don't want to get your IP address banned): ")

    # Generate a random User-Agent
    user_agent = get_random_user_agent()
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # Display the menu and get user choice
    choice = display_menu()

    # Mapping of choices to method names and functions
    methods = {
        1: ("Requests", try_requests),
        2: ("Cloudscraper", try_cloudscraper),
        3: ("Requests.Session", try_requests_session),
        4: ("tls_client", try_tls_client),
        5: ("httpx", try_httpx),
        6: ("urllib3", try_urllib3),
        7: ("Selenium", try_selenium),
        8: ("Mechanize", try_mechanize),
        9: ("pycurl", try_pycurl),
        10: ("aiohttp", try_aiohttp),
    }

    results = {}

    if 1 <= choice <= 10:
        # Single Method Execution
        method_name, method_func = methods[choice]
        print(f"\n--- {method_name} Method ---")
        start_time = time.perf_counter()  # Start timing
        if method_name == "aiohttp":
            status, content = asyncio.run(method_func(url, headers, full_output=True))
        elif method_name == "Selenium":
            status, content = method_func(url, headers, full_output=True)
        else:
            status, content = method_func(url, headers, full_output=True)
        end_time = time.perf_counter()  # End timing
        if status:
            duration = end_time - start_time
            print(f"Time taken: {duration:.2f} seconds\n")
            results[method_name] = {"Status": "Success", "Time": duration}

            # Prompt user to save the result
            while True:
                save_choice = input("Would you like to save the result? (y/n): ").strip().lower()
                if save_choice in ['y', 'n']:
                    break
                else:
                    print("Please enter 'y' for yes or 'n' for no.")
            if save_choice == 'y':
                save_result(method_name, url, content)
        else:
            results[method_name] = {"Status": "Failed", "Time": None}

    elif choice == 11:
        # All Methods Execution
        print("\n--- All Methods ---\n")
        # List of tuples containing method names and their corresponding functions
        all_methods = [
            ("Requests", try_requests),
            ("Cloudscraper", try_cloudscraper),
            ("Requests.Session", try_requests_session),
            ("tls_client", try_tls_client),
            ("httpx", try_httpx),
            ("urllib3", try_urllib3),
            ("Selenium", try_selenium),
            ("Mechanize", try_mechanize),
            ("pycurl", try_pycurl),
            ("aiohttp", try_aiohttp),
        ]

        for method_name, method_func in all_methods:
            print(f"--- {method_name} Method ---")
            start_time = time.perf_counter()  # Start timing
            if method_name == "aiohttp":
                status, _ = asyncio.run(method_func(url, headers, full_output=False))
            elif method_name == "Selenium":
                status, _ = method_func(url, headers, full_output=False)
            else:
                status, _ = method_func(url, headers, full_output=False)
            end_time = time.perf_counter()  # End timing
            if status:
                duration = end_time - start_time
                print(f"Time taken: {duration:.2f} seconds\n")
                results[method_name] = {"Status": "Success", "Time": duration}
            else:
                results[method_name] = {"Status": "Failed", "Time": None}

    # Print the summary
    print("\n===== Summary of Scraping Methods =====")
    for method, info in results.items():
        status = info["Status"]
        time_taken = info["Time"]
        if status == "Success" and time_taken is not None:
            print(f"{method}: {status} (Time taken: {time_taken:.2f} seconds)")
        else:
            print(f"{method}: {status}")
    print("=======================================\n")

if __name__ == "__main__":
    main()
