# 네이버에서 mediacode를 가져오기 위한 크롤링 파일 (각 언론사마다의 pcode)
import logging
import ssl
from urllib.request import urlopen
from bs4 import BeautifulSoup
import html5lib
import re
import pymysql
from config import TargetConfig

def main():
    print("~~~~~ start ~~~~~")

    newsstand = 'https://www.naver.com/'

    context = ssl._create_unverified_context()
    html = urlopen(newsstand, context=context)
    source = html.read()
    html.close()

    mediacode = []

    try:
        soup = BeautifulSoup(source, "html5lib")
        script = soup.find_all('script')
        myScript = script[len(script)-1]

        # DB저장
        conn = pymysql.connect(host=TargetConfig.DB_HOST, user=TargetConfig.DB_USER, password=TargetConfig.DB_PW, db=TargetConfig.DB_NAME, charset='utf8')
        curs = conn.cursor()

        # 언론사명 추출 1
        pressCategory = re.search(r'"ct1":(.*)', myScript.get_text())
        myCate = pressCategory.group(1)

        # pcode 추출
        pid = re.search(r'headlineList : (.*)', myScript.get_text()) 
        pgrp = pid.group(1).split('"')

        for r in range(3,len(pgrp)-5,+2):          
            # 언론사명 추출 2
            c1 = re.search(r'"pid":"' + pgrp[r] + '","name":"(.*?)"', myCate)
            c2 = c1.group().split('"')
            # print(" - key값   : "+pgrp[r])
            # print(" - value값 : "+c2[7])
            # print("~~~~~~~~~~~")

            sql = 'INSERT INTO newsList (mediacode, news_name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE mediacode = %s'
            data = (pgrp[r], c2[7], pgrp[r])
            curs.execute(sql, data)
            conn.commit()

    except:
        logging.error("main error(2)")

if __name__ == '__main__':
    try:
        main()
    except:
        logging.error("main error(1)")
