from urllib.parse import urlparse

def is_url_allowed(url, allowed_domain:set) -> True | False:
  parsed = urlparse(url)
  domain = parsed.netloc
  domain.replace("www.", "") if not domain else None # strip www if domain is not empty
  return domain in allowed_domain


