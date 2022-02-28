import requests
import json
import subprocess
import os
import csv
from urllib.parse import urlencode
from datetime import datetime
import time
from bs4 import BeautifulSoup
import pickle
# 这个是本地的js文件位置
# os.environ["NODE_PATH"] = "C:/Users/Bran/AppData/Roaming/npm/node_modules/"
os.environ["NODE_PATH"] = "/usr/local/lib/node_modules/"
file = open("id_set.pkl","rb")
id_set = pickle.load(file)
file.close()


def get_sign(url):
    sign = subprocess.getoutput('node sign.js "{}"'.format(url))
    return sign.strip()


def get_user_homepage(user_token):
    base_url = "https://www.toutiao.com/api/pc/list/feed"
    params = {
        "category":"pc_profile_article",
        "token":user_token,
        "max_behot_time":0,
        "aid":24,
        "app_name":"toutiao_web"
    }
    url = "{}?{}".format(base_url, urlencode(params))
    sign = get_sign(url)
    params["_signature"]=sign
    # headers = {
    #     "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
    # }
    headers = {"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}
    cookies = {
        "s_v_web_id" : "verify_kzw24fwg_tRrWeO4u_WzV0_4D9U_9xmF_DbjN8pXWcDSL"
    }
    res = requests.get(url=base_url,
                       params=params,
                       headers=headers)
    data = json.loads(res.text)
    print(data)
    if not data['data']:
        print("获取html失败，请重新检查代码")
        return
    print("获取html成功")
    return data


def get_article_id(data):
    article_ids = []
    for i in data['data']:
        article_ids.append((i['tag'],i['tag_id']))
        id_set.add(i['tag_id'])

    return article_ids


def get_artilce_detail(id,tag):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
    }
    url = "https://m.toutiao.com/i"+str(id)+"/info/"
    res = requests.get(url=url,
                       headers=headers)
    data = json.loads(res.text)
    time = int(data['data']['publish_time'])
    true_time = datetime.fromtimestamp(time)
    title = data['data']['title']
    raw_content = data['data']['content']
    soup = BeautifulSoup(raw_content, 'html.parser')
    content = soup.get_text()

    file_url = data['data']['url']
    header = ['发表时间','标题','内容','标签','来源']
    if tag == '':
        tag = "无明确标签"
    row = {'发表时间':true_time,'标题':title,'内容':content,'标签':tag,'来源':file_url}
    return row
    # with open("文章.csv",'a',newline='',encoding='gb18030') as f:
    #     f_csv = csv.DictWriter(f,header)
        # f_csv.writeheader()
        # f_csv.writerow(row)
    # print("成功保存文件")


def main():
    user_token = "MS4wLjABAAAAjtBwvR3OD0QmhA9w_LoIHcbufaw2GM6-i2fNvseUEL0"
    data = get_user_homepage(user_token)
    article_ids = get_article_id(data)
    rows = []
    for i in article_ids:
        tag = i[0]
        id = i[1]
        if id not in id_set:
            rows.append(get_artilce_detail(id,tag))
            id_set.add(id)
            time.sleep(5)

    # rows即是文章内容

    f = open("id_set.pkl","wb")
    pickle.dump(id_set[:20],f)
    f.close()


if __name__ == '__main__':
    main()