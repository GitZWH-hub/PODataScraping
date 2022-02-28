"""
@written on 2022/2/23
"""
import argparse
from tqdm import tqdm
from rank_ import get_daily_rank
from article_crawler import Account
from ArticleInfo import ArticleInfo
import hashlib
import datetime
import json


parser = argparse.ArgumentParser(description='args')

# params in crawler_url
parser.add_argument('--url_file', type=str, default='./crawler_url/exist_url_new.txt')

# params in wechat account rank(rank_.py)
parser.add_argument('--start', type=str, default='2022-2-23')
parser.add_argument('--end', type=str, default='2022-2-23')
parser.add_argument('--rank_name', type=str, default='文化')
parser.add_argument('--rank_name_group', type=str, default='生活')

# params in articles of wechat account(article_crawler.py)
# parser.add_argument('--cookie', type=str, default='pgv_pvi=3739753472; RK=0Ng4KuhTdX; ptcz=092303e3373a68a6c85c15292695328f68b97738d83bb0d57f8948d57ec5f6f3; pgv_pvid=5571772145; tvfe_boss_uuid=e32a7e32f8e35929; iip=0; o_cookie=939799295; pac_uid=1_939799295; pt_sms_phone=182******75; fqm_pvqid=ba03b22c-5643-462f-96f8-0ec5cbbc2c41; pgv_info=ssid=s8632757567; ua_id=umXv63HyzDFR9EHdAAAAAEn9CiXenXuIMZfFRjhqFNE=; wxuin=45409256155066; mm_lang=zh_CN; cert=el2b3vTdauSxDU6fui3HOySVNnTyC20D; sig=h01118a9af737ea31475942c780b2f26e0e1edf1b28de5ef7a9acb32a76cd089490870e64fbf38989e5; ptui_loginuin=939799295; uin=o0939799295; skey=@LKlcYXTav; master_key=ic7UgWCv/WQ7x4CKOou/hzezXVauWsrb6KOyJmFmCeQ=; media_ticket=64b9a4415e2331feab8361e1317f6832d5e53cf6; media_ticket_id=3926331098; rewardsn=; wxtokenkey=777; uuid=fa55505f8b8391b9c48c896d86bd8bb6; rand_info=CAESIDAmBaF/Mx+2kKL13jXCHg4aljJ+u07hHD8iBeXasduS; slave_bizuin=3926331098; data_bizuin=3926331098; bizuin=3926331098; data_ticket=GWrpawiJk9S5APQTf/mQhuqbO+cqEmt6NrGK3ymFBhErnAodPfM8eFPtWS11BrwG; slave_sid=M0Y1WW9tRW5rMlJnRW01YzdsczFPMzJnWk95UFdoWm9ZUTlBRG1nTmc5Q1k4TWNmWV9DWWxxOEoyOVA4X3BEeWJPcENZQ3B0VDVOR2lubUpkbWdvdV9zbmxLWTNsT1h5OW1rYVV4VmhJUFU3NWk2Rlo1VGRodGRWeHVLY29tSTlGMnJHMkZUOU1XcWVnT0VM; slave_user=gh_bbbcfc544bad; xid=8decd58548f120eb158290ece4cf5336')
# parser.add_argument('--token', type=int, default=536339570)
parser.add_argument('--cookie', type=str, default='appmsglist_action_3926331098=card; pgv_pvi=3739753472; RK=0Ng4KuhTdX; ptcz=092303e3373a68a6c85c15292695328f68b97738d83bb0d57f8948d57ec5f6f3; pgv_pvid=5571772145; tvfe_boss_uuid=e32a7e32f8e35929; iip=0; o_cookie=939799295; pac_uid=1_939799295; pt_sms_phone=182******75; fqm_pvqid=ba03b22c-5643-462f-96f8-0ec5cbbc2c41; ua_id=umXv63HyzDFR9EHdAAAAAEn9CiXenXuIMZfFRjhqFNE=; wxuin=45409256155066; mm_lang=zh_CN; ptui_loginuin=939799295; pgv_info=ssid=s6813234265; uuid=9acdb035b5bf54d2028c8f7fbe604cea; rand_info=CAESIFVShO3MCLSu/OIGX5OB9sfmTehGLFYivXAXlwhzxPlA; slave_bizuin=3926331098; data_bizuin=3926331098; bizuin=3926331098; data_ticket=MULW8wk65kVn/MI7CdBhGTzWuHpNv0ugsUBBNLOPk2VFL5epvUD2285Bm4WtK5XU; slave_sid=RG5NV1BVR0loTlNwQzg1emRyaHNEb1ZPVldfVEdlTEdkRUhzYWlxdlJEZDRZd0w0dVV6b0Z5VTg1SDFEekJFUG90SlN4RkFUckZsUmlWZXdWT1hpUW9jNVE2NUdianBxOTFVY01xdDMxSGU4TGptcEpsRmRhMjludjhrNmVFZGo2NXNpT21JWk9RekF1Tzg2; slave_user=gh_bbbcfc544bad; xid=b868fe6130bcb7bb7412141bc03fe9fa')
parser.add_argument('--token', type=int, default=532556409)


args = parser.parse_args()

with open(args.url_file, 'r', encoding='utf8') as f:
    url_set = set([url_md5.strip() for url_md5 in f.readlines()])
new_url_set = set()

account_biz_info_list = get_daily_rank(args.end, args.start, args.rank_name, args.rank_name_group)
account = Account(args.cookie, args.token)
articleInfo = ArticleInfo()


for name, biz_info in tqdm(account_biz_info_list):
    print(name, biz_info)
    folder = account.set_folder(name)
    article_title_urls_list = account.get_account_article(biz_info)
    for title, create_time, url in article_title_urls_list:
        # print(title, url)
        url_md5hash = hashlib.md5(url.encode('utf-8'))
        url_md5 = url_md5hash.hexdigest()
        if url_md5 in url_set:
            print('current url exists')
            continue
        print(title, url)
        url_set.add(url_md5)
        new_url_set.add(url_md5)

        title = title.strip('\n')
        title = title.replace('/', '')
        title = title.replace('\\', '')
        if len(title) > 50:
            title = title[:50]
        file = folder + '/' + title + '.json'
        time_value = str(datetime.datetime.fromtimestamp(create_time))
        article_content = articleInfo.get_text(url)
        article_dict = {'create_time': time_value, 'url': url, 'text': '\n'.join(article_content)}
        with open(file, 'w', encoding='utf8') as f:
            # f.write(time_value)
            # f.write('\n')
            # f.write(url)
            # f.write('\n')
            # for text in article_content:
            #     f.write(text)
            #     f.write('\n')
            json.dump(article_dict, f)

with open(args.url_file, 'a+', encoding='utf8') as f:
    for url in new_url_set:
        f.write(url)
        f.write('\n')
