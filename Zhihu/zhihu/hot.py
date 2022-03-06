#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from datetime import datetime

from .common import *
from .base import BaseZhihu


class Hot(BaseZhihu):
    """答案类，请使用``ZhihuClient.hot``方法构造对象."""

    @class_common_init(re_hot_page_url)
    def __init__(self, url=Hot_page_URL, session=None):
        """创建话题类实例.

        :param url: 热榜主页url
        :return: Hot
        """
        self.url = url
        self._session = session

    @property
    @check_soup('_questions')
    def questions(self):
        """获取热榜下的所有问题（按时间降序排列）

        :return: 热榜下所有问题，返回生成器
        :rtype: Question.Iterable
        """
        from .question import Question
        import json
        print(self.soup.prettify())
        js_initialData = json.loads(self.soup.find('script', id='js-initialData').get_text())
        hotList = js_initialData["initialState"]["topstory"]["hotList"]

        # print(json.dumps(hotList, indent=5))

        for que in hotList:
            title = que['target']['titleArea']['text']
            url = que['target']['link']['url']
            answer_num = que['feedSpecific']['answerCount']
            yield Question(url, title, answer_num=answer_num, session=self._session)
