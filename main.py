import argparse
import logging
import ssl
from config import TargetConfig
from urllib.request import urlopen
from bs4 import BeautifulSoup
import html5lib
from datetime import datetime
from urllib.parse import urlparse
import pymysql
import uuid
import re

# 실행 : python3 main.py --tg BLOTER_REALTIME_SEARCH_KEYWORD

def main(args):

    print("-- crawling start --")
    context = ssl._create_unverified_context()

    for target in args.tg:
        if target == 'BLOTER_REALTIME_SEARCH_KEYWORD':
            try:
                #loop = True
                #while loop == True: 
                    url = TargetConfig.MAIN
                    html = urlopen(url, context=context)
                    source = html.read()
                    html.close()
                    soup = BeautifulSoup(source, "html5lib")

                    # DB저장
                    conn = pymysql.connect(host=TargetConfig.DB_HOST, user=TargetConfig.DB_USER, password=TargetConfig.DB_PW, db=TargetConfig.DB_NAME, charset='utf8')
                    curs = conn.cursor()

                    id = str(uuid.uuid4())

                    # 미디어 코드 (var pcode = 000)
                    test = soup.find_all('script')
                    match = re.search(r'var pcode = (.*);', test[len(test)-1].get_text())
                    # print(match)
                    # print(match.group(0).split("'")[1])
                    mediacode = match.group(0).split("'")[1]

                    # -- 데이터 추출 -- 
                    # iframe으로 되어있기 때문에 url1 열기
                    url1 = TargetConfig.IFRAME
                    html1 = urlopen(url1, context=context)
                    source1 = html1.read()
                    html1.close()
                    soup1 = BeautifulSoup(source1, "html5lib")

                    # (1)(2)(3) 기사 id, title, link
                    for links in soup1.find_all("div", {'class':["bl_topnews_txt", "ns_bl_subnews_title"]}): # - top news + sub news
                        for l in links.find_all("a"):
                            #print("title: " + l.get_text())
                            #print("link: " + l.get('href'))
                            title = l.get_text()
                            link = l.get('href')
                            #print(link)

                            # (4) 해당 기사 발행일 : 해당 기사 링크에 들어가서 확인해야함
                            html2 = urlopen(link, context=context)
                            source2 = html2.read()
                            html2.close()
                            soup2 = BeautifulSoup(source2, "html5lib")

                            time = soup2.find(class_="publish") or soup2.find(class_="date")
                            published_time = time.get_text()
                            # print(time.get_text())

                            parts = urlparse(link)
                            news_id = parts.path.split('/')[2]
                            #print("news_id: " + parts.path.split('/')[2])
             
                            sql = 'INSERT INTO crawlingDB (id, news_id, title, link, crawling_time, published_time, mediacode) VALUES (%s, %s, %s, %s, now(), %s, %s) ON DUPLICATE KEY UPDATE title = %s'
                            data = (id, news_id, title, link, published_time, mediacode, title)
                            curs.execute(sql, data)
                            conn.commit()

                            # interval 5분으로 돌려보기
                            # sql = 'DELETE FROM crawlingDB WHERE crawling_time <= DATE_SUB(now(), INTERVAL 5 MINUTE)'
                            # curs.execute(sql)
                            # conn.commit()
                        
                    # sleep(30)

            except:
                logging.error("main error(2)")


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
        logging.error("main error(1)")
