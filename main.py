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
                # print("target: " + target)

                url = TargetConfig.BLOTER_REALTIME_SEARCH_KEYWORD
                html = urlopen(url, context=context)
                source = html.read()
                html.close()
                
                soup = BeautifulSoup(source, "html5lib")

                # 신문사 Bloter인지 확인
                panedId = soup.find('div', id="focusPanelCenter")
                # print(panedId)

                # 현재 시간
                now = datetime.now().strftime('%Y-%m-%d %H:%M')
                # print(now)

                # -- 데이터 추출 -- 

                # (1) 신문 발행 시간
                publishedTime = soup.find(class_="fl").em.string
                # print(publishedTime)

                # --- iframe으로 되어있기 때문에 selenium 사용하여 frame으로 바꿔줌
                # driver = webdriver.Chrome('./chromedriver')
                # driver.get(https://newsstand.naver.com/include/page/293.html)
                # driver.switch_to_frame('ifr_arc')
                # page_source = driver.page_source
                # print(page_source)

                url1 = TargetConfig.IFRAME
                html1 = urlopen(url1, context=context)
                source1 = html1.read()
                html1.close()

                soup1 = BeautifulSoup(source1, "html5lib")
                # print(soup1.find('div'))

                # ns_bl_wrap = soup1.find('div', id="ns_bl_wrap")
                # print(ns_bl_wrap)

                # (2)(3)(4) 기사 id, title, link
                # - top news 
                for links in soup1.find_all(class_="bl_topnews_txt"):
                    for link in links.find_all("a"):
                        print(link.get_text())
                        print(link.get('href'))
                        href = link.get('href')
                        parts = urlparse(href)
                        print(parts.path.split('/')[2])
                    

                # - sub news
                for links in soup1.find_all(class_="ns_bl_subnews_title"):
                    for link in links.find_all("a"):
                        print(link.get_text())
                        print(link.get('href'))
                        href = link.get('href')
                        parts = urlparse(href)
                        print(parts.path.split('/')[2])

                # iframe = soup.find('iframe')
                # print(iframe)
                # response = urlopen(iframe.attrs['src'])
                # iframe_soup = BeautifulSoup(response)
                # print(iframe_soup)

                

                

                

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
