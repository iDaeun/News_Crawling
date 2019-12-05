import yaml

yaml_file = './resource/application-dev.yml'

# 파일 생성 open("새파일",파일열기모드), r=읽기모드
with open(yaml_file, 'r') as yml:
    cfg = yaml.safe_load(yml) # deserialize하기


class TargetConfig:
    BLOTER_REALTIME_SEARCH_KEYWORD = cfg['URL']['BLOTER_REALTIME_SEARCH_KEYWORD']
    IFRAME = cfg['URL1']['IFRAME']

    DB_HOST = cfg['DB']['HOST']
    DB_USER = cfg['DB']['USER']
    DB_PW = cfg['DB']['PW']
    DB_NAME = cfg['DB']['DB']