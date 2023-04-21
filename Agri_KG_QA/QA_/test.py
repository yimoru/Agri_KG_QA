#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Time    : 2023/4/12 16:40
# @AUthor  : yimoru
# @FileName: chatBot.py
# @software: PyCharm
# @desc    :

from Agri_KG_QA.QA_.entityExtractor1 import QuestionClassifier
from Agri_KG_QA.QA_.entityExtractor2 import EntityExtractor
from Agri_KG_QA.QA_.Paser_Answer import QuestionPaser, AnswerSearcher
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class ChatBotGraph:
    def __init__(self):
        self.classifier1 = QuestionClassifier()     # 分类1：特征词+特征疑问词
        self.classifier2 = EntityExtractor()        # 分类2：特征词+NB
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        answer = '您好，我是智能助理，希望可以帮到您。如果没答上来，祝您身体棒棒！'
        res_classify1 = self.classifier1.classify(sent)
        res_classify2 = self.classifier2.extractor(sent)

        # print(f'res_classify: {res_classify1}')
        # if not res_classify1:
        #     return answer
        #
        # res_sql = self.parser.parser_main(res_classify1)
        # print(f'res_sql:{res_sql}')
        #
        # final_answers = self.searcher.search_main(res_sql)
        # print(f'final_answers: {final_answers}')

        res_classify_list = [res_classify1, res_classify2]
        print(f'res_classify_: {res_classify_list}')
        if not res_classify_list:
            return answer

        res_sqls = []
        for res_classify in res_classify_list:
            res_sql = self.parser.parser_main(res_classify)
            res_sqls.append(res_sql)
            # if len(res_sqls) == 0:
            #     res_sqls.append(res_sql)
            # else:
            #     for i in res_sqls:
            #         if i[0]['sql'] != res_sql[0]['sql']:
            #             res_sqls.append(res_sql)

        print(f'res_sql:{res_sqls}')

        final_answers = []
        for res_sql in res_sqls:
            final_answer = self.searcher.search_main(res_sql)

            final_answers.append(final_answer)
        # print(type(final_answers))
        print(f'final_answers: {final_answers}')

        if not final_answers:
            return answer
        else:
            return final_answers


def question_answering(request):
    context = {'ctx': ''}
    if request.GET:
        question = request.GET['question']

    # question = '豆腐乳的营养成分？'
    # question = request.POST.get['question']
        handler = ChatBotGraph()
        ret_dict = handler.chat_main(question)

        if len(ret_dict) != 0 and ret_dict != 0:
        #     return render(request, 'question_answering.html', context={'ret': ret_dict})
        # #####################################################################################################
            # objects = ret_dict.object.all()
            paginator = Paginator(ret_dict, 1)
            cnt = paginator.count       # page的总数
            num = paginator.num_pages   # 分页后page的数量
            print(cnt, num)
            try:
                pages = paginator.page(num)
            except PageNotAnInteger:
                pages = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
            except EmptyPage:
                pages = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
            # return render(request, 'question_answering.html', {'pages': pages})
            return render(request, 'question_answering.html', {'pages': pages})

    return render(request, 'question_answering.html', {'ctx': '暂未找到答案'})
    return render(request, 'question_answering.html', context)


if __name__ == '__main__':
    handler = ChatBotGraph()
    # question = '伦敦市的气候？'
    # question = '日照市适合种植什么？'
    question = '豆腐乳的营养成分？'
    # question = '茄子的基本信息？'
    # question = '植物'

    data = handler.chat_main(question)
    # print(data)