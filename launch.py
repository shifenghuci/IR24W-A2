from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler
import shelve
import pickle

def main(config_file, restart):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart)
    crawler.start()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    print(args.restart)
    if args.restart:
        print(f'Restarting')
        with shelve.open('stats/scraped_urls') as urls:
            print('RESETING record of scraped_urls')
            urls.clear()
        with shelve.open('stats/word_freq') as word_freq:
            print("RESETTING WORD FREQUENCY")
            word_freq.clear()
        with open('stats/longest_page.txt', 'w') as t:
            print("RESETTING LONGEST PAGE")
            #pickle.dump((None,0),t)
            t.write("None\n")
            t.write("0")
        with open('stats/ics_domain.txt', 'w') as u:
            u.write("")
    else:
        print(f'Resume crawling process')

    main(args.config_file, args.restart)
