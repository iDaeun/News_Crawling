# 모든 사이트 크롤링
import argparse
import logging
import ssl
from config import TargetConfig
import urllib.request
from bs4 import BeautifulSoup
import html5lib
from datetime import datetime
from urllib.parse import urlparse
import pymysql
import uuid
import re
from dateutil.parser import parse
from urllib.error import URLError, HTTPError

# 실행 : python3 main2.py --tg CRAWLIMG_ALL_WEBSITES

def getTime(bl_time):
    if bl_time.get("content"):
        # bl_getTime = bl_time["content"]
        # bl_parsed = parse(bl_getTime)
        # bl_d = bl_parsed.date().strftime('%Y-%m-%d')
        # bl_t = bl_parsed.time().strftime('%H:%M:%S')
        
        # bl_published_time = bl_d + " " + bl_t
        bl_published_time = bl_time["content"]
        print("발행 시간 : " + bl_published_time)

        return bl_published_time

def openurl(url):
    # http형식

    try:
        # 403 방지
        headers = {'User-Agent':'Chrome/66.0.3359.181'}
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req)

    except HTTPError as e:
        err = e.read()
        code = e.getcode()

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

                    # DB사용
                    conn = pymysql.connect(host=TargetConfig.DB_HOST, user=TargetConfig.DB_USER, password=TargetConfig.DB_PW, db=TargetConfig.DB_NAME, charset='utf8')
                    curs = conn.cursor()

                    sql = 'SELECT mediacode FROM newsListRequested WHERE idx = 9'
                    curs.execute(sql)
                    cateList = curs.fetchall()
                    
                    # 1. 미디어코드 [mediacode] 
                    for cate in cateList:
                        print("-- newsList에서 하나씩 가져오기 : " + cate[0])
                        bl_mediacode = cate[0]

                        # -- 데이터 추출 -- 
                        # 미디어 코드 대입, iframe으로 되어있음
                        addUrl = TargetConfig.IFRAME + cate[0] + '.html'
                        print("-- IFRAME 주소 만들기 : " + addUrl)
                        soup1 = openurl(addUrl)

                        # 모든 기사제목 가져옴
                        for bl in soup1.find_all('a', target="_blank"):
                            
                            # 2. 판 제목 [stand_title] 
                            bl_title = bl.get_text().strip()
                            
                            # 이미지, 기사요약 --> 걸러내기 1
                            if len(bl_title) > 0 and len(bl_title) <= 50:

                                print(len(bl_title))
                                print("판 제목 : " + bl_title)

                                # 3. 링크 [link]
                                if bl.get('href') or bl.get('ref'):
                                    bl_link = bl.get('href') or bl.get('ref')
                                    print("링크 : " + bl_link)
                                    
                                    soup3 = openurl(bl_link)

                                    # 4. 기사 제목 [article_title]
                                    # 포토 뉴스 --> 걸러내기 2
                                    if soup3.find("meta", property="og:title"):

                                        at = soup3.find("meta", property="og:title")
                                        article_title = at["content"]
                                        print("기사 제목 : " + article_title)

                                        # 5. 발행 시간 [published_time]
                                        # 포토 뉴스 --> 걸러내기 3
                                        if soup3.find("meta", property="article:published_time") or soup3.find("meta", property="article:published") or soup3.find("meta", itemprop="datePublished"):

                                            if soup3.find("meta", property="article:published_time"):
                                                bl_time = soup3.find("meta", property="article:published_time")
                                                bl_published_time = getTime(bl_time)
                                            
                                            elif soup3.find("meta", property="article:published"):
                                                bl_time = soup3.find("meta", property="article:published")
                                                bl_published_time = getTime(bl_time)

                                            elif soup3.find("meta", itemprop="datePublished"):
                                                bl_time = soup3.find("meta", itemprop="datePublished")
                                                bl_published_time = getTime(bl_time)

                                            # 6. 카테고리 [category] 
                                            if soup3.find("meta", property="article:section"):
                                                section = soup3.find("meta", property="article:section")

                                                if section.get("content"):
                                                    category = section["content"]
                                                    print("분류 : " + category)
                                                else:
                                                    category = "none"
                                                    print("분류 : " + category)

                                            else:
                                                category = "none"
                                                print("분류 : " + category)
                                                
                                            # 7. 기사 아이디 [article_id]
                                            if soup3.find("meta", property="dable:item_id") or soup3.find("meta", name_="articleid"):
                                                dable = soup3.find("meta", property="dable:item_id") or soup3.find("meta", name_="articleid")
                                                if dable.get("content"):
                                                    article_id = dable["content"]
                                                    print("기사 아이디 : " + article_id)
                                                else:
                                                    parts = bl_link.split('/')
                                                    article_id = parts[len(parts)-1]
                                                    print("기사 아이디 : " + article_id)
                                                        
                                            else:
                                                parts = bl_link.split('/')
                                                article_id = parts[len(parts)-1]
                                                print("기사 아이디 : " + article_id)
                                    
                                        else:
                                            bl_published_time = "none2"
                                            print("발행 시간 : " + bl_published_time)

                                            category = "none2"
                                            print("분류 : " + category)

                                            article_id = "none2"
                                            print("기사 아이디 : " + article_id)

                                print("--------------------")

                                            # --- test ---
                                            # print(len(bl_title))
                                            # print("기사 아이디 : " + article_id)
                                            # print("판 제목 : " + bl_title)
                                            # print("기사 제목 : " + article_title)
                                            # print("발행 시간 : " + bl_published_time)
                                            # print("링크 : " + bl_link)
                                            # print("분류 : " + category)

                                            # DB 데이터삽입
                                            # sql = 'INSERT INTO crawlingDB (stand_title, article_title, link, crawling_time, published_time, mediacode, category, article_id) VALUES (%s, %s, %s, now(), %s, %s, %s, %s) ON DUPLICATE KEY UPDATE stand_title = %s'
                                            # data = (bl_title, article_title, bl_link, bl_published_time, bl_mediacode, category, article_id, bl_title)
                                            # curs.execute(sql, data)
                                            # conn.commit()
                                                    
                                            

                                                # # interval 1분으로 돌려보기
                                                # sql = 'DELETE FROM crawlingDB WHERE crawling_time <= DATE_SUB(now(), INTERVAL 1 MINUTE)'
                                                # result = curs.execute(sql)
                                                # if result > 0:
                                                #     print("@@@@@@ deleted @@@@@@@")
                                                # conn.commit()
                    
                    curs.close()

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
