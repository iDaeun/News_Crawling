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
import requests
import json
from time import sleep
import logging
import media

# 실행 : python3 main2.py --tg CRAWLIMG_ALL_WEBSITES

# url -> 기사 아이디 추출
def getId(bl_link):
    parts = bl_link.split('/')
    article_id = parts[len(parts)-1]

    if len(article_id) > 100:
        split = article_id[0:100]
        return split

    return article_id

# 시간 추출
def parseTime(bl_getTime):

    try:
        bl_parsed = parse(bl_getTime)
        bl_d = bl_parsed.date().strftime('%Y-%m-%d')
        bl_t = bl_parsed.time().strftime('%H:%M:%S')
        bl_published_time = bl_d + " " + bl_t

        return bl_published_time
    
    except:
        return None

def getTime(bl_time):
    if bl_time.get("content"):
        bl_published_time = parseTime(bl_time["content"])

        return bl_published_time
    
    else:
        return None

# url 열기
def openurl(url):
    
    # https형식
    if url[4] == 's':
        try:
            print("들어옴??? -- https")
            context = ssl._create_unverified_context()
            html = urllib.request.urlopen(url, context=context)
            source = html.read()
            html.close()
        except HTTPError as e:
            err = e.read()
            code = e.getcode()
            print("HTTP ERROR >>>> " + code)
            
            # 504 방지
            if code == 504:
                print("refresh URL")
                attempts = True
                while attempts:
                    try: 
                        context = ssl._create_unverified_context()
                        html = urllib.request.urlopen(url, context=context)
                        source = html.read()
                        html.close()
                        attempts = False
                    except:
                        logging.info("504 error")

    else:
    # http형식
        try:
            print("들어옴??? -- http")
            # 403 방지
            headers = {'User-Agent':'Chrome/66.0.3359.181'}
            source = requests.get(url, headers=headers).content

        except HTTPError as e:
            err = e.read()
            code = e.getcode()
            print(code)

    return BeautifulSoup(source, "html5lib")

# DB입력
def insert(conn, curs, bl_title, article_title, bl_link, bl_published_time, bl_mediacode, category, article_id):

    sql = 'INSERT INTO R_MEDIA_CHANNEL (CH_STAND_NAME, CH_ARTICLE_NAME, CH_LINK, CRAWLING_DT, PUBLISHED_DT, MEDIA_CHANNEL_CD, MEDIA_CATEGORY, CH_ARTICLE_ID) VALUES (%s, %s, %s, now(), %s, %s, %s, %s) ON DUPLICATE KEY UPDATE CH_STAND_NAME = %s'
    data = (bl_title, article_title, bl_link, bl_published_time, bl_mediacode, category, article_id, bl_title)
    curs.execute(sql, data)
    print("@@ 데이터 입력 @@")
    conn.commit()
    sleep(1)

# ** main **
def main(args, logger):

    print("-- crawling start --")
    context = ssl._create_unverified_context()

    for target in args.tg:
        if target == 'CRAWLIMG_ALL_WEBSITES':
            try:
                loop = True
                while loop == True: 

                    # DB사용
                    conn = pymysql.connect(host=TargetConfig.DB_HOST, user=TargetConfig.DB_USER, password=TargetConfig.DB_PW, db=TargetConfig.DB_NAME, charset='utf8')
                    curs = conn.cursor()

                    sql = 'SELECT MEDIA_CHANNEL_CD FROM R_MEDIA_CHANNEL_CODE' 
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

                            # ---- 필터링 (1) ----
                            
                            # 이미지, 기사요약 --> 걸러내기 1
                            if len(bl_title) > 0 and len(bl_title) <= 50:

                                print(len(bl_title))
                                print("판 제목 : " + bl_title)

                                # 3. 링크 [link]
                                if bl.get('href') or bl.get('ref'):
                                    bl_link = bl.get('href') or bl.get('ref')
                                    print("링크 : " + bl_link)
                                    
                                    soup3 = openurl(bl_link)

                                    # ---- 필터링 (2) ----

                                    # 4. 기사 제목 [article_title]
                                    # 포토 뉴스 --> 걸러내기 2
                                    if soup3.find("meta", property="og:title"):

                                        at = soup3.find("meta", property="og:title")
                                        article_title = at["content"]
                                        print("기사 제목 : " + article_title)

                                        # ---- 필터링 (3) ----

                                        # 5. 발행 시간 [published_time]
                                        # 포토 뉴스 --> 걸러내기 3
                                        if soup3.find("meta", property="article:published_time") or soup3.find("meta", property="article:published") or soup3.find("meta", itemprop="datePublished"):

                                            if soup3.find("meta", property="article:published_time"):
                                                bl_time = soup3.find("meta", property="article:published_time")
                                                bl_published_time = media.segye(soup3) if bl_mediacode == '022' else getTime(bl_time)
                                            
                                            elif soup3.find("meta", property="article:published"):
                                                bl_time = soup3.find("meta", property="article:published")
                                                bl_published_time = getTime(bl_time)

                                            elif soup3.find("meta", itemprop="datePublished"):
                                                bl_time = soup3.find("meta", itemprop="datePublished")
                                                bl_published_time = getTime(bl_time)

                                            # 6. 카테고리 [category]
                                            if bl_mediacode == '052' and soup3.find("meta", property="article:section2"):
                                                section = soup3.find("meta", property="article:section2")
                                                category = section["content"]
                                            
                                            elif bl_mediacode == '214' and soup3.find("meta", id="section"):
                                                section = soup3.find("meta", id="section")
                                                category = section["content"]

                                            elif soup3.find("meta", property="article:section"):
                                                section = soup3.find("meta", property="article:section")
                                                category = section["content"] if section.get("content") else "none"

                                            # 아이뉴스
                                            elif bl_mediacode == '031':
                                                category = media.inews(soup3)
                                            
                                            else:
                                                category = "none"
                                                
                                            # 7. 기사 아이디 [article_id]
                                            if soup3.find("meta", property="dable:item_id") or soup3.find("meta", name_="articleid"):
                                                dable = soup3.find("meta", property="dable:item_id") or soup3.find("meta", name_="articleid")
                                                
                                                article_id = dable["content"] if dable.get("content") else getId(bl_link)

                                            else:
                                                article_id = getId(bl_link)

                                            print("발행 시간 : ", str(bl_published_time))
                                            print("분류 : " + category)
                                            print("기사 아이디 : " + article_id)

                                            # DB 데이터삽입
                                            insert(conn, curs, bl_title, article_title, bl_link, bl_published_time, bl_mediacode, category, article_id)
                                            
                                        else:

                                            db = False

                                            # KBS
                                            if bl_mediacode == '056':
                                                if media.kbs(soup3) is not None:
                                                    bl_published_time = media.kbs(soup3)[0]
                                                    category = media.kbs(soup3)[1]
                                                    db = True
                                            
                                            # 디지털데일리
                                            if bl_mediacode == '138':
                                                bl_published_time = media.ddaily(soup3)[0]
                                                category = media.ddaily(soup3)[1]
                                                db = True

                                            # 디지털타임스
                                            if bl_mediacode == '029':
                                                bl_published_time = media.dtimes(soup3)[0]
                                                category = media.dtimes(soup3)[1]
                                                db = True
                                            
                                            # 문화일보
                                            if bl_mediacode == '021':
                                                bl_published_time = media.munhwa(soup3)[0]
                                                category = media.munhwa(soup3)[1]
                                                db = True
                                            
                                            # 한국일보
                                            if bl_mediacode == '038':
                                                bl_published_time = media.hkilbo(soup3)[0]
                                                category = media.hkilbo(soup3)[1]
                                                db = True
                                            
                                            # 채널A
                                            if bl_mediacode == '903':
                                                bl_published_time = media.channelA(soup3)[0]
                                                category = media.channelA(soup3)[1]
                                                db = True

                                            # 노컷뉴스
                                            if bl_mediacode == '079':
                                                bl_published_time = media.nocut(soup3)[0]
                                                category = media.nocut(soup3)[1]
                                                article_id = media.nocut(soup3)[2]
                                                db = True

                                            if db == True:
                                                article_id = getId(bl_link)

                                                print("발행 시간 : ", str(bl_published_time))
                                                print("분류 : " + category)
                                                print("기사 아이디 : " + article_id)

                                                # DB 데이터삽입
                                                insert(conn, curs, bl_title, article_title, bl_link, bl_published_time, bl_mediacode, category, article_id)

                                print("--------------------")

                print("- - - - - - - 10초 스톱")
                sleep(10)
                print("- - - - - - - - - 시작")

                # interval 1분으로 돌려보기
                sql = 'DELETE FROM R_MEDIA_CHANNEL WHERE CRAWLING_DT <= DATE_SUB(now(), INTERVAL 1 MINUTE)'
                result = curs.execute(sql)
                if result > 0:
                    print("@@@@@@ deleted @@@@@@@")
                conn.commit()

                curs.close()
                    
            except Exception as inst:
                logger.error("main error(2): " + str(inst))


if __name__ == '__main__':

    # logger
    logger = logging.getLogger("log")
    logger.setLevel(logging.INFO)
    handler= logging.StreamHandler()
    
    formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s:%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("server start!")

    # parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--tg', nargs='+', help='crawling start')
    args = parser.parse_args()

    try:
        main(args, logger)
    except:
        logger.error("main error(1)")
