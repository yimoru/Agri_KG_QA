#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Time    : 2023/4/21 14:30
# @AUthor  : yimoru 
# @FileName: view_qa.py
# @software: PyCharm 
# @desc    :
from django.http import HttpResponse
from django.shortcuts import render

from Agri_KG_QA.QA_.chatBot import ChatBotGraph1
from Agri_KG_QA.QA_.chatBot2 import ChatBotGraph2


def index(request):
    return render(request, 'question_answering.html')


def qa(request, page_id):
    print(page_id)
    context = {'ctx': ''}
    if request.GET:
        question = request.GET['question']
        print(question)
        if page_id == 1:
            handler = ChatBotGraph1()
        else:
            handler = ChatBotGraph2()
        ret_dict = handler.chat_main(question)

        if len(ret_dict) != 0 and ret_dict != 0:
            return render(request, 'question_answering.html', {'ret': ret_dict})

    return render(request, 'question_answering.html', {'ctx': '暂未找到答案'})
    return render(request, 'question_answering.html', context)
