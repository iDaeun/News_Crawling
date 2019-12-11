# 모든 사이트 크롤링
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
from dateutil.parser import parse

# 실행 : python3 main2.py --tg CRAWLIMG_ALL_WEBSITES

def openurl(url):
    context = ssl._create_unverified_context()
    html = urlopen(url, context=context)
    source = html.read()
    html.close()

    return BeautifulSoup(source, "html5lib")

def main(args):

    print("-- crawling start --")
    context = ssl._create_unverified_context()

    for target in args.tg:
        if target == 'CRAWLIMG_ALL_WEBSITES':
            try:
                # loop = True
                # while loop == True: 
                    soup = openurl(TargetConfig.MAIN)

                    # DB저장
                    conn = pymysql.connect(host=TargetConfig.DB_HOST, user=TargetConfig.DB_USER, password=TargetConfig.DB_PW, db=TargetConfig.DB_NAME, charset='utf8')
                    curs = conn.cursor()

                    # -- 데이터 추출 -- 
                    # iframe으로 되어있음
                    soup1 = openurl(TargetConfig.IFRAME)
                    
                    # 모든 기사제목 가져옴
                    for bl in soup1.find_all('a', target="_blank"):
                        #if len(bl.get_text()) < 1:
                            #print(bl.find_all("img", alt=True))
                            # blo = bl.find_all("img", alt=True)
                            # for blot in blo:
                            #     print(blot["alt"])
                            #     print("------------")
                        #print(bl.find_parent('div'))
                        #print(bl.parent('div'))
                        #print("--------------------")

                        # 1. 아이디 [id]
                        id = str(uuid.uuid4())
                        
                        # 2. 제목 [title]
                        bl_title = bl.get_text().strip()

                        if len(bl_title) > 0:
                            print("제목 : " + bl_title)

                            # 3. 링크 [link]
                            bl_link = bl.get('href')
                            print("링크 : " + bl_link)

                            # 4. duplicate on (sql) 기준으로 잡을 기사 아이디 [news_id]
                            parts = bl_link.split('/')
                            news_id = parts[len(parts)-1]
                            print("아이디 : " + news_id)

                            soup3 = openurl(bl_link)

                            # 5. 발행 시간 [published_time]
                            if soup3.find("meta", property="article:published_time"):

                                bl_time = soup3.find("meta", property="article:published_time")
                                bl_getTime = bl_time["content"]
                                bl_parsed = parse(bl_getTime)
                                bl_d = bl_parsed.date().strftime('%Y-%m-%d')
                                # 만약 시간이 없으면 -> 00:00으로 출력
                                bl_t = bl_parsed.time().strftime('%H:%M:%S')
                                bl_published_time = bl_d + " " + bl_t

                                print("시간 : " + bl_published_time)
                            
                            else:
                                print("시간 : -- none -- ")

                            # 6. 카테고리 [category]
                            # 7. 미디어코드 [mediacode]                            

                            print("--------------------")

                            # # DB 데이터삽입
                            # sql = 'INSERT INTO crawlingDB (id, news_id, title, link, crawling_time, published_time, mediacode) VALUES (%s, %s, %s, %s, now(), %s, %s) ON DUPLICATE KEY UPDATE title = %s'
                            # data = (id, news_id, title, link, published_time, mediacode, title)
                            # curs.execute(sql, data)
                            # conn.commit()

                            # # interval 1분으로 돌려보기
                            # sql = 'DELETE FROM crawlingDB WHERE crawling_time <= DATE_SUB(now(), INTERVAL 1 MINUTE)'
                            # result = curs.execute(sql)
                            # if result > 0:
                            #     print("@@@@@@ deleted @@@@@@@")
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
