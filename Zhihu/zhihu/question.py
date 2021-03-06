#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
from datetime import datetime

import requests

from .common import *
from .base import BaseZhihu


class Question(BaseZhihu):
    """问题类，请使用``ZhihuClient.question``方法构造对象."""

    @class_common_init(re_question_url, trailing_slash=False)
    def __init__(self, url, title=None, followers_num=None,
                 answer_num=None, creation_time=None, author=None,
                 session=None):
        """创建问题类实例.

        :param str url: 问题url. 现在支持两种 url

            1. https://www.zhihu.com/question/qid
            2. https://www.zhihu.com/question/qid?sort=created

            区别在于,使用第一种,调用 ``question.answers`` 的时候会按投票排序返回答案;
            使用第二种, 会按时间排序返回答案, 后提交的答案先返回
        
        :param str title: 问题标题，可选,
        :param int followers_num: 问题关注人数，可选
        :param int answer_num: 问题答案数，可选
        :param datetime.datetime creation_time: 问题创建时间，可选
        :param Author author: 提问者，可选
        :return: 问题对象
        :rtype: Question
        """
        self._session = session
        self._url = url
        self._title = title
        self._answer_num = answer_num
        self._followers_num = followers_num
        self._id = int(re.match(r'.*/(\d+)', self.url).group(1))
        self._author = author
        self._creation_time = creation_time
        self._logs = None
        self._deleted = None

    def _gen_soup(self, content):
        self.soup = BeautifulSoup(content)
        self._js_initialData = json.loads(self.soup.find("script", id="js-initialData").text)

    @property
    def url(self):
        # always return url like https://www.zhihu.com/question/1234/
        url = re.match(re_question_url_std, self._url).group()
        return url if url.endswith('/') else url + '/'

    @property
    def id(self):
        """获取问题id（网址最后的部分）.

        :return: 问题id
        :rtype: int
        """
        return self._id

    # @property
    # @check_soup('_qid')
    # def qid(self):
    #     """获取问题内部id（用不到就忽视吧）
    #
    #     :return: 问题内部id
    #     :rtype: int
    #     """
    #     return int(self.soup.find(
    #         'div', id='zh-question-detail')['data-resourceid'])

    # @property
    # @check_soup('_xsrf')
    # def xsrf(self):
    #     """获取知乎的反xsrf参数（用不到就忽视吧~）
    #
    #     :return: xsrf参数
    #     :rtype: str
    #     """
    #     return 'xsrf'
    #     # return self.soup.find('input', attrs={'name': '_xsrf'})['value']

    @property
    @check_soup('_html')
    def html(self):
        """获取页面源码.

        :return: 页面源码
        :rtype: str
        """
        return self.soup.prettify()

    @property
    @check_soup('_title')
    def title(self):  # modified
        """获取问题标题.

        :return: 问题标题
        :rtype: str
        """
        return self.soup.find('h1', class_='QuestionHeader-title').text.replace('\n', '')

    @property
    @check_soup('_details')
    def details(self):  # modified
        """获取问题详细描述，目前实现方法只是直接获取文本，效果不满意……等更新.

        :return: 问题详细描述
        :rtype: str
        """
        details = self.soup.find('div', class_='QuestionRichText')
        if details is None:  # 可能不存在介绍信息
            return ''
        return details.text

    @property
    @check_soup('_answer_num')
    def answer_num(self):  # modified
        """获取问题答案数量.

        :return: 问题答案数量
        :rtype: int
        """
        # print(self.soup.prettify())
        answer_num_block = self.soup.find('h4', class_='List-headerText')
        # 当0人回答或1回答时，都会找不到 answer_num_block，
        # 通过找答案的赞同数block来判断到底有没有答案。
        if answer_num_block is None:
            if self.soup.find('span', class_='count') is not None:
                return 1
            else:
                return 0
        return extract_number_from_string(answer_num_block.span.text)

    @property
    @check_soup('_follower_num')
    def follower_num(self):  # modified
        """获取问题关注人数.

        :return: 问题关注人数
        :rtype: int
        """
        follower_num_block = self.soup.find('div', class_='QuestionFollowStatus')
        # 无人关注时 找不到对应block，直接返回0 （感谢知乎用户 段晓晨 提出此问题）
        if follower_num_block is None or follower_num_block.strong is None:
            return 0
        return extract_number_from_string(follower_num_block.strong.text)

    @property
    @check_soup('_topics')
    def topics(self):
        """获取问题所属话题.

        :return: 问题所属话题
        :rtype: Topic.Iterable
        """
        from .topic import Topic
        for topic in self.soup.find_all('div', class_='Tag QuestionTopic'):
            yield Topic('https:' + topic.a['href'], session=self._session)

    @property
    def followers(self):
        """获取关注此问题的用户

        :return: 关注此问题的用户
        :rtype: Author.Iterable
        :问题: 要注意若执行过程中另外有人关注，可能造成重复获取到某些用户
        """
        self._make_soup()
        followers_url = self.url + 'followers'
        for x in common_follower(followers_url, self.xsrf, self._session):
            yield x

    @property
    def answers(self):
        """获取问题的所有答案.

        :return: 问题的所有答案，返回生成器
        :rtype: Answer.Iterable
        """
        from .author import Author
        from .answer import Answer

        self._make_soup()

        # TODO: 统一逻辑. 完全可以都用 _parse_answer_html 的逻辑替换
        if False and self._url.endswith('sort=created'):
            pass
            # pager = self.soup.find('div', class_='zm-invite-pager')
            # if pager is None:
            #     max_page = 1
            # else:
            #     max_page = int(pager.find_all('span')[-2].a.text)
            #
            # for page in range(1, max_page + 1):
            #     if page == 1:
            #         soup = self.soup
            #     else:
            #         url = self._url + '&page=%d' % page
            #         soup = BeautifulSoup(self._session.get(url).content)
            #     error_answers = soup.find_all('div', id='answer-status')
            #     for each in error_answers:
            #         each['class'] = 'zm-editable-content'
            #     answers_wrap = soup.find('div', id='zh-question-answer-wrap')
            #     # 正式处理
            #     authors = answers_wrap.find_all(
            #         'div', class_='zm-item-answer-author-info')
            #     urls = answers_wrap.find_all('a', class_='answer-date-link')
            #     up_num = answers_wrap.find_all('div',
            #                                    class_='zm-item-vote-info')
            #     contents = answers_wrap.find_all(
            #         'div', class_='zm-editable-content')
            #     assert len(authors) == len(urls) == len(up_num) == len(
            #         contents)
            #     for author, url, up_num, content in \
            #             zip(authors, urls, up_num, contents):
            #         a_url, name, motto, photo = parser_author_from_tag(author)
            #         author_obj = Author(a_url, name, motto, photo_url=photo,
            #                             session=self._session)
            #         url = Zhihu_URL + url['href']
            #         up_num = int(up_num['data-votecount'])
            #         content = answer_content_process(content)
            #         yield Answer(url, self, author_obj, up_num, content,
            #                      session=self._session)
        else:
            pagesize = 10
            new_header = dict(Default_Header)
            new_header['Referer'] = self.url
            params = {"url_token": self.id,
                      'pagesize': pagesize,
                      'offset': 0}
            data = {  # '_xsrf': self.xsrf,
                'method': 'next',
                'params': ''}
            for i in range(0, (self.answer_num - 1) // pagesize + 1):
                if False and i == 1:
                    pass
                # 修正各种建议修改的回答……
                # print(self.soup.prettify())
                # error_answers = self.soup.find_all('div',
                #                                    id='answer-status')
                # for each in error_answers:
                #     each['class'] = 'zm-editable-content'
                # answers_wrap = self.soup.find_all('div',
                #                                   class_='ContentItem AnswerItem')
                # 正式处理
                # authors = self.soup.find_all(
                #     'div', class_='AuthorInfo-content')
                # urls = self.soup.find_all('div', class_='ContentItem-time')
                # up_num = self.soup.find_all('div',
                #                             class_='ContentItem-actions')
                # contents = self.soup.find_all(
                #     'span', class_='RichText ztext CopyrightRichText-richText css-hnrfcf')
                # assert len(authors) == len(urls) == len(up_num) == len(
                #     contents)
                # for author, url, up_num, content in \
                #         zip(authors, urls, up_num, contents):
                #     a_url, name, motto = parser_author_from_tag2(
                #         author)
                #     author_obj = Author(a_url, name, motto,
                #                         session=self._session)
                #     url = 'https:' + url.a['href']
                #     up_num = extract_number_from_string(up_num.span.button['aria-label'])
                #     content = answer_content_process(content)
                #     yield Answer(url, self, author_obj, up_num, content,
                #                  session=self._session)
                else:
                    params['offset'] = i * pagesize
                    data['params'] = json.dumps(params)
                    r = self._session.post(Question_Get_More_Answer_URL,
                                           data=data,
                                           headers=new_header)
                    answer_list = r.json()['msg']
                    for answer_html in answer_list:
                        yield self._parse_answer_html(answer_html)

    @property
    def top_answer(self):
        """获取排名第一的答案.

        :return: 排名第一的答案
        :rtype: Answer
        """
        for a in self.answers:
            return a

    def top_i_answer(self, i):
        """获取排名某一位的答案.

        :param int i: 要获取的答案的排名
        :return: 答案对象，能直接获取的属性参见answers方法
        :rtype: Answer
        """
        for j, a in enumerate(self.answers):
            if j == i - 1:
                return a

    def top_i_answers(self, i):
        """获取排名在前几位的答案.

        :param int i: 获取前几个
        :return: 答案对象，返回生成器
        :rtype: Answer.Iterable
        """
        for j, a in enumerate(self.answers):
            if j <= i - 1:
                yield a
            else:
                return

    @property
    @check_soup('_author')
    def author(self):
        """获取问题的提问者.
        
        :return: 提问者
        :rtype: Author or zhihu.ANONYMOUS
        """
        from .author import Author, ANONYMOUS

        logs = self._query_logs()
        author_a = logs[-1].find_all('div')[0].a
        if author_a.text == '匿名用户':
            return ANONYMOUS
        else:
            url = Zhihu_URL + author_a['href']
            return Author(url, name=author_a.text, session=self._session)

    @property
    @check_soup('_creation_time')
    def creation_time(self):
        """
        :return: 问题创建时间
        :rtype: datetime.datetime
        """
        # log_url = self.url + 'log'
        # resp = self._session.get(log_url)
        # log_soup = BeautifulSoup(resp.content)
        # print(log_soup.prettify())

        logs = self._query_logs()
        time_string = logs[-1].find('div', class_='zm-item-meta').time[
            'datetime']
        return datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")

    @property
    @check_soup('_last_edit_time')
    def last_edit_time(self):
        """
        :return: 问题最后编辑时间
        :rtype: datetime.datetime
        """
        data = {'_xsrf': self.xsrf, 'offset': '1'}
        res = self._session.post(self.url + 'log', data=data)
        _, content = res.json()['msg']
        soup = BeautifulSoup(content)
        time_string = soup.find_all('time')[0]['datetime']
        return datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")

    def _query_logs(self):
        if self._logs is None:
            gotten_feed_num = 20
            start = '0'
            offset = 0
            api_url = self.url + 'log'
            logs = None
            while gotten_feed_num == 20:
                data = {'offset': offset, 'start': start}
                res = self._session.post(api_url, data=data)
                gotten_feed_num, content = res.json()['msg']
                offset += gotten_feed_num
                soup = BeautifulSoup(content)
                logs = soup.find_all('div', class_='zm-item')
                start = logs[-1]['id'][8:] if len(logs) > 0 else '0'
                time.sleep(0.2)  # prevent from posting too quickly

            # res = self._session.get(api_url)
            # new_session = requests.Session()
            # new_session.headers.update(Default_Header)
            # new_session.headers.update({'cookie':'__snaker__id=cohg9BCpWdF8VI0n; SESSIONID=JhjrrD7zxTjPdiJGQiK2YBJXWPeyAgkBA16kjAM4HaP; osd=V14RBEhZ0iViOiu3SVtX-2nlITFcefMFRR8Llml88gRCHQ6XaDDXOQI_KrZOwFiY2BIJ5XR5PmEuvWrrBWcy4MI=; JOID=U1oVBk1d1iFgPy-zTVlS_23hIzRYffcHQBsPkmt59gBGHwuTbDTVPAY7LrRLxFyc2hcN4XB7O2UquWjuAWM24sc=; _zap=f2a03de3-7c1c-44cc-b622-7752709ddc31; d_c0="AFCe_NQIgxSPTurs92gqYUyfNyflQldleJY=|1645170960"; _9755xjdesxxd_=32; YD00517437729195:WM_TID=WY/IXZDKj2pEFVVFQAJuvgZtVHLtxvme; q_c1=211decf789a6415cba4618941cdd390f|1645423165000|1645423165000; __snaker__id=LkxKKW92jVFv26Nv; __utmv=51854390.100-1|2=registration_date=20180815=1^3=entry_date=20180815=1; _xsrf=4b703ecb-ecdd-4ca5-8d98-ac8aaf412f87; YD00517437729195:WM_NI=yCVqYvtiH019rFiqWOtrek64AQUoXsoHDhkFTAft69vf+JeYHPm/l/bVDs4rwsV0hNHz3KQVX8FTO4EgXJbEFXiAWCRCrz+E1WfQhEzec9xqeHHIEHi1+F3ex+fclzFiRlU=; YD00517437729195:WM_NIKE=9ca17ae2e6ffcda170e2e6ee8fe65e81ab8ab2e580928a8ba6d55f978b8b85f57ebcea998cd94994bca294b62af0fea7c3b92abb9d9a92dc7eb8b788d1b433b29aa792d645b8aeab8cb540838f9b90db79ad988c89ea4e989faa95b533b6bae5abe8538c90a3d0ef25a28a8c94b77ab5ad9ad1eb468ca6fdacd45e9ce88ab5ce4087b998abe14f8688a7a2d649929dbe9baa4ff389aab2eb4fbabbaddafb7ba79888aac844abefe5a7b26fbcf5aa84ef7286b79e8dd837e2a3; l_n_c=1; n_c=1; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1645937730,1645937763,1645937997,1645938116; SESSIONID=aBgk2YgWmqofBmen8hDm6rB3IFmfG4Q4E1GEg7VLEll; JOID=VF0UB0ha_gAJkJMgA1h42AJKmaUQOLhiZafJQ1EyjGtq1ftGaQLuGWmWlCEBot7gFJMm-oAmZdVxeJOiY9K9qVE=; osd=Wl8UB09U_AAJl50iA1h_1gBKmaIeOrhiYqnLQ1E1gmlq1fxIawLuHmeUlCEGrNzgFJQo-IAmYttzeJOlbdC9qVY=; tst=h; __utmb=51854390.0.10.1645950807; __utmc=51854390; __utma=51854390.846679434.1645533003.1645533003.1645950807.2; __utmz=51854390.1645950807.2.2.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/question/518532038; NOT_UNREGISTER_WAITING=1; gdxidpyhxdE=ECZtfWNkRehdgkky2tNQkvo69O\DAeXfhZ76LwvtAJB6p9W5G0T1CoqZYHyiPTf8X9Wrrw72z2h5rhHtzgd\A4QdvaTYJjAS0s9XexMdTrsN2NVQ/RZGBLuTtyT\Ad3QnZUZ\XRJyxJ2934AxJBf\sYTG+XPK6xUyrdQ/sx2hcuP0mhZ:1645952947631; l_cap_id="OWRlYzE5MWUzN2E0NGIzNThjYTg0MGFlMzA4NWZjMWE=|1645952062|e6a59064f9419b3b9f4d97fb3e83e8a8729adf26"; r_cap_id="MGM0ZTI5NDVlYTcwNGI3Njg2YjNmNjliYjg4YjgxMzk=|1645952062|f58dc3b2185e31647310884355f232aba060aaf4"; cap_id="MDVhNmQ3MTA3OGM3NDkwM2I2ZmM4Y2E0ZjNiZWExZDA=|1645952062|5f6c986018ae9c9b653640e1161d3ad349dd332e"; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1645952061; captcha_session_v2="2|1:0|10:1645952192|18:captcha_session_v2|88:M1RkNmNkaktpaG5pWThtQmI0c0tQMTEvUUU3V0w3MDl4VFk4S3ZSVEZVMzBEWGFDZUlrQ2h1dTBNNndCbllqbA==|7848deb912d70bda6c8a9a069c3760193c6a2adcff191b6ae75561ff315ec55a"; captcha_ticket_v2="2|1:0|10:1645952201|17:captcha_ticket_v2|704:eyJ2YWxpZGF0ZSI6IkNOMzFfblBnUUUwSGZ0MEl2Q3N4V0JlVWEwTEpMUEdLVHpxQlFBVDZzU0tHNWJRTUVKbmgwcjI5eUpPS3FGT0t4VnhuRFhUZ1lxOV9Wa3pxcnFyUGk3RTAxamtwcXNKd1dLQS1FeXZlOGtxTVE2TDl1bzZwcEhhUC45VDJIUVkwei1fNElTb0VjNFVCYzUycVI1QVVNbGNBUFVGWmxLN2tZLi02cm45eTRVRS10bzR5V1lNQnhMdmRzRVFwd00wUUQxYXl1TVJYRlA1X3I0eDVCd0l0WmZxQkw1bWRablg5aTZhLm93bHJYcl9Oc1NuUVN2MkxKQVNmU3BsU0ZFZEtTV0FVRnlOcHpEVXRxZXE4bjduVG5TT0hFMG84NU4xblppSnFYVS1JQlpqUjVjcFdmNG85eFlna3BBWHNNaTZCXzBTcWM2MW5BcDhTTWlDLXdTWGNqc3JyaXVMVTduXzRKY0I0UVd5ZHNKbU1FYnkuVlBYVnhzS2trSjlhYndKS1l5ay5LWVpBR1hBQklZMi5lY2FOdDQ5S0RTQWk3NDBNS2RWV0JZOEM2ZG9iY2xTZXM3UWNiMHlmVF9DbTUyeXRMY2ExZXN2Y181TDFxQi5pclN4cE95V0s3LTJUZDByb1RQVEkyWGRpUzloSTRLXy05TVVveGk3RERiUTVOLUxqMyJ9|cb732a340d375d79d7726e065d48b5c0dcf738ba74e20dd4c966e760854afa1c"; z_c0="2|1:0|10:1645952202|4:z_c0|92:Mi4xZlp1YkN3QUFBQUFBVUo3ODFBaURGQ1lBQUFCZ0FsVk55WW9JWXdBOExtM3BkUDBVcm5ac1pCaDFVam0xa3VFWGNn|bad1718276e7a7f5f2b36c736901a6f7f147d1ab7121634ad6fd55f9840e5663"; KLBRSID=fb3eda1aa35a9ed9f88f346a7a3ebe83|1645952201|1645937731'})
            # res2 = new_session.get(api_url)
            # print(res.text)
            # logs = None
            self._logs = logs

        return self._logs

    # noinspection PyAttributeOutsideInit
    def refresh(self):
        """刷新 Question object 的属性. 
        例如回答数增加了, 先调用 ``refresh()`` 
        再访问 answer_num 属性, 可获得更新后的答案数量.
        
        :return: None
        """
        super().refresh()
        self._html = None
        self._title = None
        self._details = None
        self._answer_num = None
        self._follower_num = None
        self._topics = None
        self._last_edit_time = None
        self._logs = None

    @property
    @check_soup('_deleted')
    def deleted(self):
        """问题是否被删除, 被删除了返回 True, 未被删除返回 False
        :return: True or False
        """
        return self._deleted

    def _parse_answer_html(self, answer_html):
        from .author import Author
        from .answer import Answer
        soup = BeautifulSoup(answer_html)
        # 修正各种建议修改的回答……
        error_answers = soup.find_all('div', id='answer-status')

        for each in error_answers:
            each['class'] = 'zm-editable-content'

        answer_url = self.url + 'answer/' + soup.div['data-atoken']
        author = soup.find('div', class_='zm-item-answer-author-info')
        upvote_num = int(soup.find(
            'div', class_='zm-item-vote-info')['data-votecount'])
        content = soup.find('div', class_='zm-editable-content')
        content = answer_content_process(content)
        a_url, name, motto, photo = parser_author_from_tag(author)
        author = Author(a_url, name, motto, photo_url=photo,
                        session=self._session)
        return Answer(answer_url, self, author, upvote_num, content,
                      session=self._session)
