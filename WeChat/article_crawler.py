# -*- coding: utf-8 -*-
import requests
import time
import json
import os


class Account:
    def __init__(self, cookie, token):
        self.cookie = cookie
        self.headers = {"Cookie": cookie, "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"}
        self.url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
        self.token = token

    def set_folder(self, name):
        path = './data/' + name
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)
            print('--- new folder ---')
            print('--- OK ---')
        else:
            print('--- There is this folder! ---')

        return path

    def get_account_article(self, fakeid):
        # 目标url
        # url = "https://mp.weixin.qq.com/cgi-bin/appmsg"

        # 使用Cookie，跳过登陆操作
        # headers = {
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
        # }
        # headers["Cookie"] = cookie

        """
        需要提交的data
        以下个别字段是否一定需要还未验证。
        注意修改yourtoken,number
        number表示从第number页开始爬取，为5的倍数，从0开始。如0、5、10……
        token可以使用Chrome自带的工具进行获取
        fakeid是公众号独一无二的一个id，等同于后面的__biz
        """
        data = {
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1",
            "action": "list_ex",
            "begin": 0,
            "count": "5",
            "query": "",
            "type": "9",
        }

        data["token"] = self.token
        data["fakeid"] = fakeid

        # 使用get方法进行提交
        while True:
            content_json = requests.get(self.url, headers=self.headers, params=data).json()
            print(content_json)

            if content_json['base_resp']['ret'] == 200013:
                print("frequencey control, stop")
                time.sleep(3600)
                continue
            else:
                break
        # 返回了一个json，里面是每一页的数据
        article_title_url_list = []
        for item in content_json["app_msg_list"]:
            # 提取每页文章的标题及对应的url
            # print(item["title"], "url: " + item["link"])
            article_title_url_list.append((item["title"], item["create_time"], item["link"]))

        return article_title_url_list


if __name__ == "__main__":
    cookie = "pgv_pvi=3739753472; RK=0Ng4KuhTdX; ptcz=092303e3373a68a6c85c15292695328f68b97738d83bb0d57f8948d57ec5f6f3; pgv_pvid=5571772145; tvfe_boss_uuid=e32a7e32f8e35929; iip=0; o_cookie=939799295; pac_uid=1_939799295; pt_sms_phone=182******75; fqm_pvqid=ba03b22c-5643-462f-96f8-0ec5cbbc2c41; pgv_info=ssid=s8632757567; ua_id=umXv63HyzDFR9EHdAAAAAEn9CiXenXuIMZfFRjhqFNE=; wxuin=45409256155066; mm_lang=zh_CN; cert=el2b3vTdauSxDU6fui3HOySVNnTyC20D; sig=h01118a9af737ea31475942c780b2f26e0e1edf1b28de5ef7a9acb32a76cd089490870e64fbf38989e5; ptui_loginuin=939799295; uin=o0939799295; skey=@LKlcYXTav; master_key=ic7UgWCv/WQ7x4CKOou/hzezXVauWsrb6KOyJmFmCeQ=; media_ticket=64b9a4415e2331feab8361e1317f6832d5e53cf6; media_ticket_id=3926331098; rewardsn=; wxtokenkey=777; uuid=fa55505f8b8391b9c48c896d86bd8bb6; rand_info=CAESIDAmBaF/Mx+2kKL13jXCHg4aljJ+u07hHD8iBeXasduS; slave_bizuin=3926331098; data_bizuin=3926331098; bizuin=3926331098; data_ticket=GWrpawiJk9S5APQTf/mQhuqbO+cqEmt6NrGK3ymFBhErnAodPfM8eFPtWS11BrwG; slave_sid=M0Y1WW9tRW5rMlJnRW01YzdsczFPMzJnWk95UFdoWm9ZUTlBRG1nTmc5Q1k4TWNmWV9DWWxxOEoyOVA4X3BEeWJPcENZQ3B0VDVOR2lubUpkbWdvdV9zbmxLWTNsT1h5OW1rYVV4VmhJUFU3NWk2Rlo1VGRodGRWeHVLY29tSTlGMnJHMkZUOU1XcWVnT0VM; slave_user=gh_bbbcfc544bad; xid=8decd58548f120eb158290ece4cf5336"
    token = 536339570
    account = Account(cookie, token)
    folder = account.set_folder("洞见")
    article_title_url_list = account.get_account_article("MjM5MDc0NTY2OA==")
    print(article_title_url_list)
