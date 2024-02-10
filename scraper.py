import re
from urllib.parse import urlparse
from lxml import etree
from bs4 import BeautifulSoup
from tokenizer import yieldToken

word_freq = dict()
allowed_domain = {".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"}

def scraper(url, resp):
    global word_freq
    links = list(extract_next_links(url, resp))
    update_word_frequencies(resp,word_freq)
    # print(f"List of hyperlinks extracted from {url}:{links}")
    accepted_link = [link for link in links if is_valid(link)]
    #print(f'Accepted link from {url}: {accepted_link}')
    return accepted_link

#takes in urls, if it is relative convert to absolute url
def convert_to_absolute(url, href) -> str:
    parsed_url = urlparse(url)
    if href[0:2] == "//":
        #if url missing scheme
        return parsed_url.scheme + ":" + href
    elif href[0] == "/":
        # if relative url
        return url + href
    elif href[0] == "#":
        return url
    else:
        # if absolute url
        return href

#no validation will be performed here, all validation perform in is_valid
def extract_next_links(url, resp):
    soup = BeautifulSoup(resp.raw_response.content,'html.parser')
    for tag in soup.find_all('a'):
        href = tag.get('href')
        # Convert relative to absolute
        yield(convert_to_absolute(url,href))


        """ # yield links that has valid schemes and within the allowed domain, and exclude fragment link
        if urlparse(href).scheme in ['http', 'https'] and is_url_allowed(href, allowed_domain):
            clean_url = urlunparse(urlparse(href)._replace(fragment= "")) #remove the fragment part
            yield(clean_url) """


    # legacy code that assume relative url 
    """ soup = BeautifulSoup(url, 'html.parser')
    links = []
    for element in soup.find_all('a'):
        links.append(convert_to_absolute(url, element['href']))
    global counter++
    return links """

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            # if it is not a valid scheme
            print(f"Rejected {url} due to scheme error")
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            # if is document
            print(f'Rejected {url} due to document error')
            return False
        if not is_url_allowed(url, allowed_domain):
            # if out of domain
            print(f"Rejected {url} due to out of domain error")
            return False
        else:
            return True
    except TypeError:
        print ("TypeError for ", parsed)
        raise

#Given a url with set of allowed domain, determined if the url is within the domain
def is_url_allowed(url, allowed_domain:set) -> True | False:
  allowed_domain = {".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"}
  parsed = urlparse(url)
  domain = parsed.netloc
  domain = domain.replace("www", "") if domain else None # strip www if domain is not empty
  return domain in allowed_domain

  #Given a soup object adn a dictionary about word frequencies, update the word frequencies by word token found in the soup
def update_word_frequencies(resp, freq_dict)-> None:
  soup = BeautifulSoup(resp.raw_response.content,'html.parser')
  tokens = list(yieldToken(soup.get_text()))
  for token in tokens:
        freq_dict[token] = freq_dict.get(token, 0) + 1 # if new to dict, assign 1, if not, increment