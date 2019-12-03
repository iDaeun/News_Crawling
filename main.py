import argparse
import logging
import ssl
from config import TargetConfig
from urllib.request import urlopen
from bs4 import BeautifulSoup
import html5lib


def main(args):

    print("-- crawling start --")
    context = ssl._create_unverified_context()

    for target in args.tg:
        if target == 'BLOTER_REALTIME_SEARCH_KEYWORD':
            try:
                # print("target: " + target)

                url = TargetConfig.BLOTER_REALTIME_SEARCH_KEYWORD
                html = urlopen(url, context=context)
                source = html.read()
                html.close()
                
                soup = BeautifulSoup(source, "html5lib")

                # 신문 발행 시간
                publishedTime = soup.find(class_="fl").em
                print(publishedTime)

            except:
                logging.error("main erorr(2)")


if __name__ == '__main__':

    # start time
    # logger

    # parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--tg', nargs='+', help='crawling start')
    args = parser.parse_args()

    try:
        main(args)
    except:
        logging.error("main erorr(1)")
