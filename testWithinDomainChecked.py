from urllib.parse import urlparse

seed_urls = "https://www.ics.uci.edu,https://www.cs.uci.edu,https://www.informatics.uci.edu,https://www.stat.uci.edu"
allowed_domain = {urlparse(seed_url).netloc.replace("www.", "") for seed_url in seed_urls.split(sep=",")}
print(f'List of allowed domain: {allowed_domain}')

outside_url = "https://www.google.com"
inside_url = "https://ics.uci.edu/2023/11/17/zothacks-2023-highlights-ucis-beginner-hackers/"
empty_url = "this is not url"

def is_url_allowed(url) -> True | False:
  print(url)
  parsed = urlparse(url)
  domain = parsed.netloc
  domain.replace("www.", "") if not domain else None#strip www if domain is not empty
  return domain in allowed_domain
  
  

print(is_url_allowed(outside_url))
print(is_url_allowed(inside_url))
print(is_url_allowed(empty_url))


