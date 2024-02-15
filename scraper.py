import re
import shelve
import lxml.html
from urllib.parse import urlparse
from typing import Generator
import requests
from utils.response import Response

# TODO: Implement robots.txt check and usage of sitemap
#       10. Try visiting https://www.example.com/robots.txt
#       10.1 If fail to visit, proceed onto normal scrawling
#       10.2 If exists, parse and construct set of disallow urls, disallowed_urls,append(f'{url}{disallow_relative}'
#       10.3 Look for sitemap, if exists, parse it and directly return href extracted from the sitemap
#       10.3.1 This is to assume that the sitemap contain valid link that is not a trap

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


def scraper(url: str, resp: Response) -> list[str]:
    # redirection is handled automatically by requests.get
    update_word_dict(resp)
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url: str, resp: Response) -> Generator[str, None, None]:
    """
    yield links extracted from the url, ensure that link yielded is absolute url
    """
    hrefs = lxml.html.fromstring(resp.raw_response.content).xpath("//a/@href")
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
        elif not within_domains(url):
            return False
        elif is_sus_trap(url):
            return False
    except TypeError:
        print("TypeError for ", parsed)
        raise


if __name__ == '__main__':
    def foo(resp) -> list[str]:
        """
        return words (as defined as sequence of alphanumeric string, including apstrophies) from the html string
        """
        html_string = resp.text
        tree = lxml.html.fromstring(html_string)
        pattern = r"\w+'?\w*"  # find any alphanumeric sequence, including apostrophe
        text = tree.text_content()
        return [word for word in re.findall(pattern, text)]


    print(foo(requests.get("https://ics.uci.edu/2024/02/14/13-teams-recognized-at-irvinehacks-2024/")))
