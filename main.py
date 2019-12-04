import argparse
import logging
import ssl
from config import TargetConfig
from urllib.request import urlopen
from bs4 import BeautifulSoup
import html5lib
from datetime import datetime
from urllib.parse import urlparse

# 실행 : python3 main.py --tg BLOTER_REALTIME_SEARCH_KEYWORD

def main(args):

    print("-- crawling start --")
    context = ssl._create_unverified_context()

    for target in args.tg:
        if target == 'BLOTER_REALTIME_SEARCH_KEYWORD':
            try:
                url = TargetConfig.BLOTER_REALTIME_SEARCH_KEYWORD
                html = urlopen(url, context=context)
                source = html.read()
                html.close()
                soup = BeautifulSoup(source, "html5lib")

                # 현재 시간
                now = datetime.now().strftime('%Y-%m-%d %H:%M')
                print("현재 시간: " + now)

                # -- 데이터 추출 -- 
                # (1) 신문 발행 시간
                panel = soup.find(id="focusPanelCenter")
                publishedTime = panel.find(class_="fl").em.string
                print("신문 발행 시간: " + publishedTime)

                # (2~4)데이터 : iframe으로 되어있기 때문에 url1 열기
                url1 = TargetConfig.IFRAME
                html1 = urlopen(url1, context=context)
                source1 = html1.read()
                html1.close()
                soup1 = BeautifulSoup(source1, "html5lib")

                # (2)(3)(4) 기사 id, title, link
                # - top news + sub news
                for links in soup1.find_all("div", {'class':["bl_topnews_txt", "ns_bl_subnews_title"]}):
                    for link in links.find_all("a"):
                        print("title: " + link.get_text())
                        print("link: " + link.get('href'))
                        href = link.get('href')
                        parts = urlparse(href)
                        print("id: " + parts.path.split('/')[2])
                    

                # - sub news
                # for links in soup1.find_all(class_="ns_bl_subnews_title"):
                #     for link in links.find_all("a"):
                #         print("title: " + link.get_text())
                #         print("link: " + link.get('href'))
                #         href = link.get('href')
                #         parts = urlparse(href)
                #         print("id: " + parts.path.split('/')[2])

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
