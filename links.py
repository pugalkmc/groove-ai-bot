import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

visited_urls = set()
file_name = 'visited_urls.txt'

def is_valid_url(url, domain):
    parsed = urlparse(url)
    return parsed.scheme in ('http', 'https') and domain in parsed.netloc

def get_all_links(url, domain):
    links = set()
    try:
        response = requests.get(url)
        # print(response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup.find_all('a'))
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(url, href)
            if is_valid_url(full_url, domain):
                links.add(full_url)
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return links


def create_file(links):

    # Write the links to the file
    with open(file_name, 'w') as f:
        for link in links:
            f.write(link + '\n')

    print(f"Links written to '{file_name}' successfully.")

from collections import deque

def crawl(url, domain, limit=50):
    q = deque([])
    q.append(url)
    visited = set()
    while len(visited) <= limit:
        current = q.popleft()
        visited.add(current)
        links = get_all_links(current, domain)
        for link in links:
            if link not in visited:
                q.append(link)
    
    create_file(visited)

def read_urls_from_file():
    urls = []
    with open(file_name, 'r') as file:
        for line in file:
            urls.append(line.strip())  # Strip removes leading and trailing whitespaces including the newline character
    return urls

# Example usage:

# print(read_urls_from_file())
# crawl("https://docs.kommunitas.net", "kommunitas.net")
