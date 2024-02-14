import re
import shelve
import lxml.html
from urllib.parse import urlparse
from typing import Generator
from utils.response import Response


def get_words(resp: Response) -> list[str]:
    """
    return words (as defined as sequence of alphanumeric string, including apstrophies) from the html string
    """
    html_string = resp.raw_response.content
    tree = lxml.html.fromstring(html_string)
    pattern = r"\w+'?\w*"  # find any alphanumeric sequence, including apostrophe
    text = tree.text_content()
    return [word for word in re.findall(pattern, text)]


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
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False

    except TypeError:
        print("TypeError for ", parsed)
        raise


if __name__ == '__main__':
    print()