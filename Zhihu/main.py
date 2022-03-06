from zhihu import ZhihuClient

client = ZhihuClient()

user_id_file = 'user_id_list.txt'
with open(user_id_file, 'r') as f:
    for uid in f:
        url = f'https://www.zhihu.com/people/{uid.strip()}'
        author = client.author(url)
#         print('用户名 %s' % author.name)
#         print('用户id %s' % author.id)
        # print('用户简介 %s' % author.motto)
        # print('用户行业 %s' % author.business)
        # print('用户关注人数 %d' % author.followee_num)
        # print('取用户粉丝数 %d' % author.follower_num)
        # # print('用户得到赞同数 %d' % author.upvote_num)
        # print('用户提问数 %d' % author.question_num)
#         print('用户答题数 %d' % author.answer_num)
#         print('用户答案:')
        for (i, ans) in enumerate(author.answers):
            print(f'    {i}:{ans.question.title}')
            ans.save()

# question = client.question('https://www.zhihu.com/question/36966326')
# print(f'问题:{question.title}, 答案数目:{question.answer_num}')
# for (i, answer) in enumerate(question.answers):
#     print(i + 1, answer.author.name)
# answer.save()

# print('用户专栏文章数 %d，名称分别为：' % author.post_num)
# for column in author.columns:
#     print(column.name)
# print('用户收藏夹数 %d，名称分别为：' % author.collection_num)
# for collection in author.collections:
#     print(collection.name)

#
# que = client.question(url='https://www.zhihu.com/question/518532038')
# print(f'{que.title} answer_num:{que.answer_num} follower_num:{que.follower_num}')
# # print(f'tag ={[t.name for t in que.topics]}')
# print(f'创建时间：{que.creation_time}  最后编辑时间：{que.last_edit_time} 提问者：{que.author.name}')
