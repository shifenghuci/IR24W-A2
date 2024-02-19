import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from tokenizer import yieldToken
import shelve
import pickle



def scraper(url, resp):
    if resp.status == 200: #only scraped success page
        with open('stats/ics_domain.txt', 'a') as u:
            if 'ics.uci.edu' in url:
                u.write(f"{url}\n")
        links = extract_next_links(url, resp)
    else:
        links = [] # return empty links for not successful visit page
    #return []
    return [link for link in links if is_valid(link)]

def get_tokenSet(url:str):
  parsedUrlSet = set()
  for t in url.split('/'):
    #print(t)
    if t:
        parsedUrlSet.add(t)
    else:
        continue
  #return frozenset({x for x in url.split('/')} if x else continue)
  return frozenset(parsedUrlSet)

def extract_next_links(url, resp):
    #print(f"scraping this url {url}")
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    '''
    Expected cases & handle:
        1.absolute url: append directly to links
        2.relative url: convert to absolute and append to links
        3.fragment: ignore, don't append
        5.None: ignore, don't append
        6.Non website scheme: ignore, don't append
        7.url lacking scheme: apply scheme and append to links
    '''

    # update dict of scraped urls
    with shelve.open('stats/scraped_urls') as d:
        d[url] = get_tokenSet(url)

    absoluteLinks = []
    hyperlinks = []
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    for hrefs in soup.find_all('a'):
        hyperlinks.append(hrefs.get('href'))

    # updates longest page
    tokens = list(yieldToken(soup.get_text()))
    num_words = len(tokens)
    if (num_words < 200):
        return []
    with open('stats/longest_page.txt', 'r') as longest_page:
        lines = longest_page.readlines()
        #print(f"here is lines: {lines}")
        storedMaxLen = int(lines[1].strip())
        storedStr = lines[0].strip()
        #print(f"this is num_words: {num_words}")

        if storedStr == "None" or num_words > storedMaxLen:
            with open('stats/longest_page.txt', 'w') as t:
                t.write(f"{url}\n")
                t.write(str(num_words))
        #if 'long' in longest_page:
            #if num_words > longest_page["long"][1]:
                #longest_page['url'] = [url,num_words]
                #longest_page['num'] = num_words
        #else:
            #longest_page['long'] = [url,0]
            #longest_page['url'] = url

    # updates frequency of each word from url
    with shelve.open('stats/word_freq') as word_freq:
        for token in tokens:
            word_freq[token] = word_freq.get(token, 0) + 1
 
    # converts links to absolute links if needed and adds to absoluteLinks to be returned
    for link in set(hyperlinks):
        if not link:
            continue #skip None
        if link.startswith('http') or link.startswith('https'):
            #is complete url
            absoluteLinks.append(link)
        if link.startswith('//'):
            #missing scheme
            absoluteLinks.append(f'{urlparse(url).scheme}:{link}') #Give it the same scheme as the original url
        elif link.startswith('/'):
            #is relative
            if url[-1] == '/':
                url = url[:-1] #normalize self-directing page, ie: http://www.ics.uci.edu/ -> http://www.ics.uci.edu
            absolute_url = f'{url}{link}'
            absoluteLinks.append(absolute_url)
        else:
            # The fragment, mailto, tel got ignored
            continue
    return absoluteLinks

def exceedRepeatedThreshold(url)-> True|False:
    #return true indicating if the url's path contain repeated pattern that exceed a certain threshold
    '''
    Definition of threshold
    THRESHOLD = 1 We don't allow there to be recurring path

    THRESHOLD = 2 We allowed once recurrent, but more than that smell fishy
    
    '''
    #print(f"url from repeatedThreshold {url}")
    repeat_THRESHOLD = 1 #if the same token appear more than three time in the path, the url is consider a trap that has infinite pattern
    d = {}
    tokenSet = get_tokenSet(url)
    #print(tokenSet)
    for x in url.split('/'):
        if x != '':
            #if x[-1] == ":":
                #x = x[:-1]
            d[x] = d.get(x,0) + 1
    #for t in d:
        #print(f"here: {t} and {d[t]}")
    #check the record of all seemd tokenSets
    with shelve.open('stats/scraped_urls') as url_dict:
        #for v in url_dict:
            #print(f"k: {v} and values: {url_dict[v]}")
        tokenSets = url_dict.values()
        #print(f"here is tokenSets {tokenSets}")
        #print(f"look at this: {get_tokenSet(url)}")
        #for test in tokenSets:
            #print(f"seen tokensets {test}")
        seemedToken = get_tokenSet(url) in tokenSets
        #print(f"seemedToken: {seemedToken}")
        #print(f'{url} seemed? {seemedToken}')
        return any(value > repeat_THRESHOLD for value in d.values()) or seemedToken

def detectedTrap(url):
    path_token = urlparse(url).path.split('/')
    path_depth = len(path_token)
    DEPTH_THRESHOLD = 6
    calendar_words = {'events', 'schedule', 'news', 'page', 'appointments', 'date'}
    if path_depth > DEPTH_THRESHOLD:
        return True
    elif any((token in calendar_words) for token in path_token):
        return True
    else:
        return False

def is_valid(url):
    #return True or False that determine whether to crawl
    '''
    Expected Cases & handle:
    1. Illegal domain: if netloc not in one of the four allowed domain
    2. Repeated Pattern: fetch path and determine if there are repeated path exceeding certain threshold
    3. Document: use regular expression
    4. .php script: ignore them
    5. query: ignore them
    '''
    try:
        #print(f"checking this url: {url}")
        parsed = urlparse(url)
        #print(parsed)
        if parsed.scheme not in set(["http", "https"]):
            #print("1")
            #print(f'{url} will not be crawl due to <<<<<invalid scheme error>>>>>')
            return False
        elif parsed.netloc not in {"www.ics.uci.edu", "www.cs.uci.edu", "www.informatics.uci.edu", "www.stat.uci.edu"}:
            #print("2")
            #print(f'{url} will not be crawl due to <<<<<illegal domain error>>>>>')
            return False
        #elif '.php' in url or '.html' in url or '.pdf' in url or '.txt' in url:
            #print("3")
            #return False
        elif parsed.query:
            #print("4")
            return False
        elif detectedTrap(url):
            #print("5")
            return False
        elif exceedRepeatedThreshold(url):
            #print("6")
            #print(f'{url} will not be crawl due to <<<<<exceedRepeatedThreshold error>>>>>')
            return False
        #print("7")
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