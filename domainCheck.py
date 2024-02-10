from urllib.parse import urlparse

#Given a url with set of allowed domain, determined if the url is within the domain
def is_url_allowed(url, allowed_domain:set) -> True | False:
  parsed = urlparse(url)
  domain = parsed.netloc
  domain.replace("www.", "") if not domain else None # strip www if domain is not empty
  return domain in allowed_domain


