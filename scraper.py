import re
import shelve
import lxml.html
from urllib.parse import urlparse
from typing import Generator
import requests
from utils.response import Response

# TODO: Implement near and exact duplication
#       implement checksum(), simHash(), calculateSimilarity()
#       use hammingDistance for calculateSimilarity()


# TODO: Implement multi-threading
#       Reimplement Frontier.py
#       Reimplement Worker.py
#       No changes in scraper.py

# TODO: Determine any extra mechanism for data collection

def get_words(resp: Response) -> Generator[str, None, None]:
    """
    return words (as defined as sequence of alphanumeric string, including apstrophies) from the html string
    """
    html_string = resp.raw_response.content
    doc = lxml.html.fromstring(html_string)
    pattern = r"\w+'?\w*"  # find any alphanumeric sequence, including apostrophe
    for body in doc.xpath("//body"):  # search only in the body section
        body_text = body.text_content
        yield from re.findall(pattern, body_text)  # yield from all found word


def update_word_dict(resp: Response) -> None:
    """
    update a shelves file about word frequencies
    """
    stop_words = {}
    with open('stopWords.txt', 'r') as f:
        stop_words = {word.strip() for word in f.readlines()}

    with shelve.open('stats/word_dict') as word_dict:
        for word in get_words(resp):
            if word not in stop_words:
                word_dict[word] = word_dict.get(word, 0) + 1


def read_robot(url: str) -> list[str] or None:
    """
     Given an url, try to access the robots.txt
     return links of sitemap found on robots.txt
    """
    url = url.removesuffix('/')
    robot = requests.get(f'{url}/robots.txt')
    if robot.url == url or robot.status_code == 404:
        return None  # robots.txt does not exist, has been redirected
    sitemap_urls = []
    if robot.status_code == 200:
        print(f'{url} has a robots.txt file')
        for line in robot.text.split('\n'):
            if line.startswith('Disallow:'):
                with shelve.open('disallowed_urls') as d:
                    try:
                        link = f'{url}{line.split()[1]}'
                        print(f'Adding disallowed_urls: {link}')
                        d[url] = d.get(url, frozenset()).union({link})
                    except IndexError:
                        continue
            elif line.startswith('Allow:'):
                with shelve.open('allowed_urls') as d:
                    try:
                        link = f'{url}{line.split()[1]}'
                        print(f'Adding allowed_urls: {link}')
                        d[url] = d.get(url, frozenset()).union({link})
                    except IndexError:
                        continue
            elif line.startswith('Sitemap:'):
                try:
                    sitemap_url = f'{url}{line.split()[1]}'
                    print(f'Sitemap found: {sitemap_url}')
                    sitemap_urls.append(sitemap_url)
                except IndexError:
                    continue
    return sitemap_urls


def scraper(url: str, resp: Response) -> list[str]:
    # redirection is handled automatically by requests.get
    update_word_dict(resp)
    sitemap_urls = []
    if urlparse(url).path in {'/', ''}:  # only attempt robots.txt for homepage
        sitemap_urls = read_robot(url)  # attempt to read robots.txt
    if sitemap_urls:  # if sitemap found
        links = []
        for url in sitemap_urls:  # extract link from each sitemap
            links.extend(list(extract_next_links(url)))
        return links
    else:  # sitemap not found, scraped from url instead
        links = extract_next_links(url, resp)
        return [link for link in links if is_valid(link)]


def extract_next_links(url: str, resp: Response = None) -> Generator[str, None, None]:
    """
    yield links extracted from the url, ensure that link yielded is absolute url
    if not given a resp object, use request.get() to get html file
    """
    if resp:
        hrefs = lxml.html.fromstring(resp.raw_response.content).xpath("//a/@href")
    else:
        hrefs = lxml.html.fromstring(requests.get(url).text).xpath("//a/@href")

    for link in hrefs:
        if link.rstrip("/") == url or link == url:
            continue  # skip self reference
        elif link.startswith('#'):
            continue  # skip fragment
        elif link.startswith('tel:') or link.startswith('mailto:'):
            continue  # skip tel: or mailto:
        elif link.startswith('//'):
            yield f'https:{link}'  # attach scheme
        elif link.startswith('/'):
            yield f'{url.rstrip("/")}{link}'  # remove ending / to avoid wrong concatenation
        else:
            yield link


def within_domains(url: str) -> True | False:
    """
    determined if the url is within the given set of domains
    """
    hostname = urlparse(url).netloc
    p = r'.*(.ics.uci.edu/|.cs.uci.edu/|.stat.uci.edu/|.informatics.uci.edu/).*'  # regular expression for matching
    # domain name
    return re.match(p, url)


def is_sus_trap(url: str) -> True | False:
    # sus sus sus sus amongus sus amongus sus amongus
    # ^sorry, I can't give up the chance to bring this meme up
    """determine if the url is a potential trap"""
    DEPTH_THRESHOLD = 3  # Based on observation of past crawl and randomly clicking website on domain,
    # path do not exceed three layer (mostly two)
    path_token = urlparse(url).path.split('/')
    path_depth = len(path_token)
    calendar_words = {'events', 'schedule', 'news', 'page', 'appointments', 'date'}
    if path_depth > DEPTH_THRESHOLD:
        return True
    elif any((token in calendar_words) for token in path_token):
        return True
    else:
        return False


def is_allowed(url: str) -> True | False:
    parsed = urlparse(url)
    domain_url = f'{parsed.scheme}://{parsed.netloc}'
    with shelve.open('disallowed_urls') as d:
        if domain_url in set(d.keys()):  # check if in set of disallowed url
            print('Record found, checking if is disallowed')
            print(d.get(domain_url))
            if any(url.startswith(x) for x in d.get(domain_url)):
                with shelve.open('allowed_urls') as a:
                    return any(url.startswith(x) for x in a.get(domain_url, frozenset()))
        else:
            return True


def is_valid(url: str) -> True | False:
    # return True for url we want to crawl, False for url we don't want to crawl
    parsed = urlparse(url)
    try:
        if parsed.scheme not in {'http', 'https'}:
            return False
        elif re.match(
                r".*\.(css|js|bmp|gif|jpe?g|ico"
                + r"|png|tiff?|mid|mp2|mp3|mp4"
                + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                + r"|epub|dll|cnf|tgz|sha1"
                + r"|thmx|mso|arff|rtf|jar|csv"
                + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ics)$", parsed.path.lower()):  # added ics for calendar
            return False
        elif not is_allowed(url):
            return False
        elif not within_domains(url):
            return False
        elif is_sus_trap(url):
            return False
    except TypeError:
        print("TypeError for ", parsed)
        raise


if __name__ == '__main__':
    read_robot("https://www.stat.uci.edu")
    d = "https://www.stat.uci.edu/wp-admin/k"
    a = "https://www.stat.uci.edu/wp-admin/loser"
    print(is_allowed(d))
    print(is_allowed(a))
