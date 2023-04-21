#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Time    : 2023/4/12 16:49
# @AUthor  : yimoru 
# @FileName: chatBot2.py
# @software: PyCharm 
# @desc    : 特征字典 + NB

from Agri_KG_QA.QA_.entityExtractor2 import EntityExtractor
from Agri_KG_QA.QA_.Paser_Answer import QuestionPaser, AnswerSearcher


class ChatBotGraph2:
    def __init__(self):
        self.classifier = EntityExtractor()  # 分类2：特征词+NB
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        answer = '您好，我是智能助理，希望可以帮到您。如果没答上来，祝您身体棒棒！'
        res_classify = self.classifier.extractor(sent)
        print(f'res_classify: {res_classify}')
        if not res_classify:
            return answer

        res_sql = self.parser.parser_main(res_classify)
        print(f'res_sql:{res_sql}')

        final_answers = self.searcher.search_main(res_sql)
        print(f'final_answers: {final_answers}')

        if not final_answers:
            return answer
        else:
            return final_answers


if __name__ == '__main__':
    handler = ChatBotGraph()
    # question = '伦敦市的气候？'
    # question = '日照市适合种植什么？'
    # question = '豆腐乳的营养成分？'
    question = '茄子的基本信息？'
    # question = '植物'

    data = handler.chat_main(question)
    print(data)