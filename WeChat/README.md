### 微信公众号

+ 任务描述：
    1. 获取热门微信公众号
    2. 增量式文档爬取（文档内容、文档时间、文档标签、文档url）

+ 概要过程：
    1. [newrank](https://www.newrank.cn/public/info/list.html?period=day&type=data)新榜网站获取公众号当日排名。
    2. 获取到的公众号的字段提供更难过个人微信订阅号获取文章列表
    3. 根据文章url获取文章内容
    4. 增量：存储已爬取文章url(md5码)，爬取前判断文章url是否存在在文本文件，存在、跳过，否则爬取。

+ 结果：
    1. 文章内容存储：data/"公众号name"/"文章".json
    2. Json文件格式：  
    {  
        &emsp; "create_name": "创建时间",  
        &emsp; "url": "文章链接",  
        &emsp; "text": "内容"  
    }