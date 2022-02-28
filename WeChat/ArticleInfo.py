import re
import requests
from bs4 import BeautifulSoup as bs
from selectolax.parser import HTMLParser
from lxml import etree


class ArticleInfo:
    def __init__(self, proxies={"http":None, "https": None}):
        self.headers = {
            "User-Agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0Chrome/57.0.2987.132 MQQBrowser/6.2 Mobile"
        }
        self.proxies = proxies
        self.too_frequently_text = "你的访问过于频繁，需要从微信打开验证身份，是否需要继续访问当前页面"

    def get_text(self, url):
        s = requests.get(url, headers=self.headers, proxies=self.proxies)

        # text = HTMLParser(s.text).text()
        selector = etree.HTML(s.text)
        # time_text = selector.xpath('//div[@id="js_article" and @class="rich_media"]/div[@class="rich_media_inner"]/em[@id="publish_time"]//text()')
        # print(time_text)
        text = selector.xpath('//div[@id="js_article" and @class="rich_media"]/div[@class="rich_media_inner"]//text()')
        res = []
        zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
        # if (r.test(str)){}
        for t in text:
            t = t.strip()
            if t == '' or not re.search(zh_pattern, t):
                continue
            res.append(t)
        return res


# cookie = "pgv_pvi=3739753472; RK=0Ng4KuhTdX; ptcz=092303e3373a68a6c85c15292695328f68b97738d83bb0d57f8948d57ec5f6f3; pgv_pvid=5571772145; tvfe_boss_uuid=e32a7e32f8e35929; iip=0; o_cookie=939799295; pac_uid=1_939799295; pt_sms_phone=182******75; fqm_pvqid=ba03b22c-5643-462f-96f8-0ec5cbbc2c41; pgv_info=ssid=s8632757567; ua_id=umXv63HyzDFR9EHdAAAAAEn9CiXenXuIMZfFRjhqFNE=; wxuin=45409256155066; mm_lang=zh_CN; xid=887f14b47ee86ed2e0913d75d4809fee; uuid=3a48a219d2ae6f83cb076009a75c8fcd; cert=el2b3vTdauSxDU6fui3HOySVNnTyC20D; sig=h01118a9af737ea31475942c780b2f26e0e1edf1b28de5ef7a9acb32a76cd089490870e64fbf38989e5; ptui_loginuin=939799295; uin=o0939799295; skey=@LKlcYXTav; data_bizuin=3926331098; data_ticket=MOH4uL8ra1u7eKkpb+YzeM86uYsqrH9YWmAci/XqMoN/krYlp5CASTabVRRL1fUk; master_key=ic7UgWCv/WQ7x4CKOou/hzezXVauWsrb6KOyJmFmCeQ=; master_user=gh_bbbcfc544bad; master_sid=ZGhYd0RFU3ZHSVBYcm9iTTB6UDd6U2J6bTRQd043eXVpUHkzb1ZIWVo5OENlX184QnpfdUFVcG53NEM1UWRKQkJyZkg3V2dBa1U3X1lJVHNJaWtreE9oX0xrWHFqaWl3ckhISG1IeTFvaFQ0czVUTEhnNll4WkVZa3VZVGNyU0ltdkkzNUR0dU45SVFCM3dZ; master_ticket=c63f383296b6f58da9c8a84481aae5fa; bizuin=3926331098; media_ticket=64b9a4415e2331feab8361e1317f6832d5e53cf6; media_ticket_id=3926331098; slave_user=gh_bbbcfc544bad; slave_sid=RTV1Nm1aakxRekQ1dGNNQVd6VVRZcVRwaDBwR1loT054NGhGSmtwdXVtWDJhRTE1M2RFb09seW9UbDMxZG5qbEI1d1QwTl9YYzZ1QWZxVmt0QUZBUXFrNWU5Z0NoVDFOVXBJSW9jUm9RQktrN3ZOaHBNWXVlU2YzSzFHVHJoVkhYYXBPd1JLT2xwczFxZlRh"

articleinfo = ArticleInfo()
print(articleinfo.get_text("http://mp.weixin.qq.com/s?__biz=MjM5MDc0NTY2OA==&mid=2651640864&idx=8&sn=0f3562c5cb10c505ea1a8f1452f91142&chksm=bdb8610b8acfe81d53dcfd704eadaf748ae47f288b9e55627448d0a659283b0c88affcd784ae#rd"))
print(articleinfo.get_text("http://mp.weixin.qq.com/s?__biz=MjM5MDc0NTY2OA==&mid=2651641909&idx=1&sn=baac915235cc6fbc2e49e8051b26a75d&chksm=bdb86d1e8acfe40881332510121ba75b84b5633f209a23aae50dd665b69f19112e872aa9e29d#rd"))