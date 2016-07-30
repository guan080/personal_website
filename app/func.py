# # coding: utf-8
# import wikipedia
#
# wikipedia.set_lang('zh')
#
#
# def wiki(kw):
#     try:
#         content = wikipedia.summary(kw)
#     except wikipedia.exceptions.DisambiguationError as e:
#         content = '关键词似乎有多种解释，请选择后重新查询：\n' + \
#                     e.options
#     except wikipedia.exceptions.PageError:
#         content = '关键词似乎不存在记录，请重新查询。'