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

# 실행 : python3 main2.py --tg CRAWLIMG_ALL_WEBSITES

# -- 언론사별 개별 코드 --
# 056 KBS
# 분류 : var _TRK_CP = '^뉴스^사회';
# 날짜 : <span class="txt-info"> <em class="date">입력 2019.12.13 (08:27)</em>
def kbs(soup3):

    # ---- 필터링 ----
    if soup3.find("em", class_="date"):
        date = soup3.find("em", class_="date").get_text()
        
        for text in soup3.find_all('script'):
            if re.search(r'var _TRK_CP = (.*);', text.get_text()):
                match = re.search(r'var _TRK_CP = (.*);', text.get_text())
                cate2 = match.group(0).split("'")[1]
        
        li = [date, cate2]

        return li

# 138 디지털데일리
# 분류 : 없음
# 날짜 : <p class="arvdate">2019.12.13 09:01:31 / 김도현
def ddaily(soup3):

    date = soup3.find("p", class_="arvdate").get_text().split('/')[0]
    return [date, 'none']

# 029 디지털타임스
# 분류 : 없음
# 날짜 : <script type="application/ld+json"> "dateModified": "2019-12-12T14:25:00+08:00"
def dtimes(soup3):

    date1 = soup3.find("script", type="application/ld+json").get_text()
    date2 = (json.loads(date1))["datePublished"]
    date3 = parseTime(date2)

    return [date3, 'none']

# 021 문화일보
# 분류 : <a href=http://www.munhwa.com/news/section_list.html?sec=society&class=0 class=d14b_2F5>[사회]</a>
# 날짜 : <td align="right">게재 일자 : 2019년 12월 13일(金)</td>
def munhwa(soup3):

    tds = soup3.find_all("td", align="right")
    for td in tds:
        if re.search(r'게재 일자 : (.*)', td.get_text()):
            match = re.search(r'게재 일자 : (.*)', td.get_text())
            date2 = match.group(0).split(":")[1]

    cate = soup3.find("a", class_="d14b_2F5").get_text()

    return [date2, cate]

# 031 아이뉴스24
# 분류 : inews-www-hover active
def inews(soup3):

    cate1 = soup3.find("a", {'class':["inews-www-hover active", "inews-www-hover  active"]})
    cate2 = cate1.get_text().strip()

    return cate2

# 038 한국일보
# 분류 :
# 날짜 :
def hkilbo(soup3):

    # 1) 연예뉴스 <meta name="hk:nw_press" content="스타한국" />
        # 분류 : <meta name="hk:nw_class" content="음악" />
        # 날짜 : <meta name="hk:nw_newsoutdt" content="20191213131148" />
    #print(soup3)
    for metas in soup3.find_all('meta'):
        #print(metas.attrs['content'])
        if 'name' in metas.attrs and metas.attrs['name'] == 'hk:nw_press':
            print("comeeeeeeeeeee")
            if metas.attrs['content'] == '스타한국':
                print(metas.attrs['content'])
                cate = '연예'
            # 2) 포토갤러리
            else:
                return ['--', '포토갤러리']
            
            for metas in soup3.find_all('meta'):
                if 'name' in metas.attrs and metas.attrs['name'] == 'hk:nw_newsoutdt':
                    print(metas.attrs['content'])
                    date = metas.attrs['content']

                    return [date, cate]

# ----------------------

# url -> 기사 아이디 추출
def getId(bl_link):
    parts = bl_link.split('/')
    article_id = parts[len(parts)-1]
    print("기사 아이디 : " + article_id)

    return article_id

# 시간 추출
def parseTime(bl_getTime):

    bl_parsed = parse(bl_getTime)
    bl_d = bl_parsed.date().strftime('%Y-%m-%d')
    bl_t = bl_parsed.time().strftime('%H:%M:%S')
    bl_published_time = bl_d + " " + bl_t

    return bl_published_time

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

# url 열기
def openurl(url):
    
    # https형식
    if url[4] == 's':
        context = ssl._create_unverified_context()
        html = urllib.request.urlopen(url, context=context)
        source = html.read()
        html.close()
    
    else:
    # http형식
        try:
            print("들어옴??? -- 0")
            # 403 방지
            headers = {'User-Agent':'Chrome/66.0.3359.181'}
            # req = urllib.request.Request(url, headers=headers)
            # print(req)
            # html = urllib.request.urlopen(req)
            # print(html)
            source = requests.get(url, headers=headers).content

        except HTTPError as e:
            err = e.read()
            code = e.getcode()
            print(code)

        # source = html.read() # html.read().decpde('utf-8') --> 왜 에러?
        # html.close()

    return BeautifulSoup(source, "html5lib")

# ** main **
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

                    sql = 'SELECT mediacode FROM newsListRequested where idx = 45'
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
                                    print("들어옴??? -- 1")

                                    # ---- 필터링 (1) ----

                                    # 4. 기사 제목 [article_title]
                                    # 포토 뉴스 --> 걸러내기 2
                                    if soup3.find("meta", property="og:title"):
                                        print("들어옴??? -- 2")

                                        at = soup3.find("meta", property="og:title")
                                        article_title = at["content"]
                                        print("기사 제목 : " + article_title)

                                        # ---- 필터링 (2) ----

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

                                            # 아이뉴스
                                            elif bl_mediacode == '031':
                                                    category = inews(soup3)
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
                                                    article_id = getId(bl_link)    
                                            else:
                                                article_id = getId(bl_link)
                                    
                                        else:

                                            # KBS
                                            if bl_mediacode == '056':
                                                if not kbs(soup3) is None:
                                                    bl_published_time = kbs(soup3)[0]
                                                    category = kbs(soup3)[1]
                                                    print("발행 시간 : " + bl_published_time)
                                                    print("분류 : " + category)
                                            
                                            # 디지털데일리
                                            if bl_mediacode == '138':
                                                bl_published_time = ddaily(soup3)[0]
                                                category = ddaily(soup3)[1]
                                                print("발행 시간 : " + bl_published_time)
                                                print("분류 : " + category)

                                            # 디지털타임스
                                            if bl_mediacode == '029':
                                                bl_published_time = dtimes(soup3)[0]
                                                category = dtimes(soup3)[1]
                                                print("발행 시간 : " + bl_published_time)
                                                print("분류 : " + category)
                                            
                                            # 문화일보
                                            if bl_mediacode == '021':
                                                bl_published_time = munhwa(soup3)[0]
                                                category = munhwa(soup3)[1]
                                                print("발행 시간 : " + bl_published_time)
                                                print("분류 : " + category)
                                            
                                            # 한국일보
                                            if bl_mediacode == '038':
                                                bl_published_time = hkilbo(soup3)[0]
                                                category = hkilbo(soup3)[1]
                                                print("발행 시간 : " + bl_published_time)
                                                print("분류 : " + category)
                                               
                                            else:

                                                bl_published_time = "none2"
                                                print("발행 시간 : " + bl_published_time)
                                                print("**** 시간 코드 만들어야함 :: " + bl_mediacode)

                                                category = "none2"
                                                print("분류 : " + category)
                                                print("**** 카테고리 코드 만들어야함 :: " + bl_mediacode)

                                            article_id = getId(bl_link)

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
