#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
import json
import sys
import pickle
import requests
from bs4 import BeautifulSoup

file = open("url_set.pkl","rb")
url_set = pickle.load(file)
file.close()

def url2article(url):

    #获取单条新闻的内容

    res = requests.get(url)
    #print(res.encoding)

    res.encoding = 'utf-8'

    soup = BeautifulSoup(res.text, 'html.parser')

    title = soup.title.text

    article_time = soup.time.text
    article = soup.get_text()
    labels = []
    return [title,article_time,article,labels]
init_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=50&page={}'

headers = {'User-Agent':

            'Mozilla/5.0 (Windows NT 10.0; WOW64) '

            'AppleWebKit/537.36 (KHTML, like Gecko) '

            'Chrome/55.0.2883.87 Safari/537.36'}

page = requests.get(url=init_url.format(1)).json()
def main():
    data = []
#新浪新闻1页50条，可爬取前50页
    for j in range(50):    
        url = page['result']['data'][j]['wapurl']
        if url in url_set:
            continue
        [title,article_time,article,labels] = url2article(url)
        data.append({'create_time':article_time,'url':url,'text':article,'labels':labels})        
        print(url)
        print(article_time)
        print(title)
        print(article)
        url_set.add(url)
        time.sleep(5)
    with open('sinanews.json','w') as fp:
        fp.write(json.dumps(data,indent = 4))
        #print(count)
    f = open("url_set.pkl","wb")
    pickle.dump(url_set[:20],f)
    f.close()
if __name__ == '__main__':
    main()
 


# In[ ]:





# In[ ]:





# In[ ]:




