from bs4 import BeautifulSoup
import re
import main2
import json

# -- 언론사별 개별 코드 --
# 056 KBS
# 분류 : var _TRK_CP = '^뉴스^사회';
# 날짜 : <span class="txt-info"> <em class="date">입력 2019.12.13 (08:27)</em>
def kbs(soup3):
    # ---- 필터링 ----
    if soup3.find("em", class_="date"):
        date1 = soup3.find("em", class_="date").get_text()
        date2 = date1.split(" ")[1] 
        date3 = re.findall('\(([^)]+)', date1.split(" ")[2])
        date4 = date2 + " " + date3[0] + ":00"
        
        for text in soup3.find_all('script'):
            if re.search(r'var _TRK_CP = (.*);', text.get_text()):
                match = re.search(r'var _TRK_CP = (.*);', text.get_text())
                cate2 = match.group(0).split("'")[1]
                cate3 = cate2.split("^")[2]
                if len(cate3) == 0:
                    cate3 = cate2.split("^")[1]
        
        li = [date4, cate3]

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
    date3 = main2.parseTime(date2)

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

    cate1 = soup3.find("a", class_="d14b_2F5").get_text()
    cate2 = cate1.split("[")[1].split(']')[0]

    return [date2, cate2]

# 031 아이뉴스24
# 분류 : inews-www-hover active
def inews(soup3):

    cate1 = soup3.find("a", {'class':["inews-www-hover active", "inews-www-hover  active"]})
    cate2 = cate1.get_text().strip()

    return cate2

# 038 한국일보
def hkilbo(soup3):

    # 1) 연예뉴스 <meta name="hk:nw_press" content="스타한국" />
        # 분류 : <meta name="hk:nw_class" content="음악" />
        # 날짜 : <meta name="hk:nw_newsoutdt" content="20191213131148" />
    #print(soup3)
    for metas in soup3.find_all('meta'):
        if 'name' in metas.attrs and metas.attrs['name'] == 'hk:nw_press':
            if metas.attrs['content'] == '스타한국':
                cate = '연예'
            # 2) 포토갤러리
            else:
                return ['--', '포토갤러리']
            
            for metas in soup3.find_all('meta'):
                if 'name' in metas.attrs and metas.attrs['name'] == 'hk:nw_newsoutdt':
                    date1 = metas.attrs['content']
                    date2 = date1[0:4] + "-" + date1[4:6] + "-" + date1[6:8] + " " + date1[8:10] + ":" + date1[10:12] + ":" + date1[12:]

                    return [date2, cate]

# 022 세계일보
def segye(bl_time):
    bl_parsed = bl_time["content"]
    parts1 = bl_parsed.split('T')
    yr = parts1[0]
    parts2 = parts1[1].split('+')
    time = parts2[0]

    return yr + " " + time

# 903 채널에이
# 날짜: <span class="date"><span>[채널A]</span> 2019-12-16 13:23</span>
# 분류: 
def channelA(soup3):
    date1 = soup3.find("span", class_="date").get_text()
    date2 = date1.split(']')[1] + ":00"

    return [date2, 'none']

# 079 노컷뉴스
def nocut(soup3):
    for metas in soup3.find_all('meta'):
        if 'name' in metas.attrs and metas.attrs['name'] == 'article:section':
            cate = metas.attrs['content']
        if 'name' in metas.attrs and metas.attrs['name'] == 'article:published_time':
            date1 = metas.attrs['content']
            date2 = main2.parseTime(date1)
        if 'name' in metas.attrs and metas.attrs['name'] == "dable:item_id":
            id = metas.attrs['content']
        
    return [date2, cate, id]