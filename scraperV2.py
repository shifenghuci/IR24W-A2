import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pickle

def update_Scraped(url,resp)->None:
# update and save the change to pickle file
   with open('scraped.pickle', 'wb') as f:
      scrapped_url = pickle.load(f)
      #update dictionary
      scrapped_url[url] = resp
      #save to data.pickle
      pickle.dump(scrapped_url, f)

def within_allowedDomain(url:str)-> True|False:
  allowed_domains = {"ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"}
  return urlparse(url).netloc in allowed_domains

def repeatedUrlPattern(url)-> True|False:
  parsed =urlparse(url)
  path_tokens = parsed.path.split("/")
  return len(set(path_tokens)) == len(path_tokens)

def scraper(url, resp)->list:
    update_Scraped(url,resp)
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp)-> list:
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    if resp.status != 200: return []
    soup = BeautifulSoup(resp.raw_response)
    extracted_urls = (tag['href'] for tag in soup.find_all('a'))
    links = []
    for extracted_url in extracted_urls:
        if extracted_url is not None and urlparse(extracted_url).scheme is None: #if not empty but not absolute url
            # excluding mailto and tel
            if extracted_url.startswith('#'):
              continue
            elif extracted_url.startswith('//'): #lacking scheme
              links.append(f'{urlparse(url).scheme}{extracted_url}')
            elif extracted_url.startswith('/'): # convert relative url to absolute url
              links.append(f'{url}{extracted_url}')
    return links

def is_valid(url)-> True|False:
    # Decide whether to crawl this url or not. 
    try:
        parsed = urlparse(url)
        # Case 1: Invalid Scheme
        if parsed.scheme not in set(["http", "https"]):
            return False
        #Case 2: out of domain
        if not within_allowedDomain(url):
           return False
        #Case 3: crawler trap - repeated url pattern
        if repeatedUrlPattern(url):
           return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
    except TypeError:
        print ("TypeError for ", parsed)
        raise