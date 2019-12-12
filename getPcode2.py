import pymysql
from config import TargetConfig

# DB저장
conn = pymysql.connect(host=TargetConfig.DB_HOST, user=TargetConfig.DB_USER, password=TargetConfig.DB_PW, db=TargetConfig.DB_NAME, charset='utf8')
curs = conn.cursor()

mediaPcode = ['904','056','214','057','374','055','902','052','032','005','079','421','003','368','020','138','029','009','417','008','021','006','293','011','081','022','277','031','310','422','047','018','030','366','023','990','025','903','296','014','002','028','015','215','038','016']

for pcode in mediaPcode:
    print(pcode)

    sql0 = 'SELECT news_name from newsList WHERE mediacode = %s'
    curs.execute(sql0, pcode)
    news_name = curs.fetchone()

    sql = 'INSERT INTO newsListRequested (mediacode, news_name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE mediacode = %s'
    data = (pcode, news_name, pcode)
    curs.execute(sql, data)
    conn.commit()

    print("-----")


