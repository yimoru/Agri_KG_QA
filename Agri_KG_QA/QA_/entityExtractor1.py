#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Time    : 2023/4/12 16:35
# @AUthor  : yimoru
# @FileName: entityExtractor1.py
# @software: PyCharm
# @desc    :


import os
import ahocorasick


class QuestionClassifier:
    def __init__(self):
        cur_dir = os.path.abspath('.')  # 获得当前工作目录      (django run)
        # cur_dir = os.path.abspath(os.path.join(os.getcwd(), '../../'))  # 获得当前工作目录的上两级目录  (local run)
        # print(cur_dir)
        # cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        # 特征值路径
        self.city_path = os.path.join(cur_dir, 'dict/city.txt')
        self.food_path = os.path.join(cur_dir, 'dict/food.txt')
        self.plant_path = os.path.join(cur_dir, 'dict/plant.txt')

        # 加载特征值
        self.city_wds = [i.strip() for i in open(self.city_path, encoding='utf8') if i.strip()]
        self.food_wds = [i.strip() for i in open(self.food_path, encoding='utf8') if i.strip()]
        self.plant_wds = [i.strip() for i in open(self.plant_path, encoding='utf8') if i.strip()]
        self.region_words = set(self.city_wds + self.food_wds + self.plant_wds)

        # 构造领域actree
        self.region_tree = self.build_actree(list(self.region_words))
        # 构造词典
        self.wdtype_dict = self.build_wdtype_dict()
        # 问句疑问词
        self.city_qwds = ['气候', '天气']
        self.food_qwds = ['营养元素', '营养成分']
        self.cityplant_qwds = ['适合种植', '适合种', '可以种植', '可以种', '应该种', '适合种']
        self.plant_qwds = ['详细信息', '简介', '基本信息', '知识']

        print('model init finished ......')
        return

    # 构造词对应类型
    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.city_wds:
                wd_dict[wd].append('city')
                wd_dict[wd].append('city2plant')
            if wd in self.food_wds:
                wd_dict[wd].append('food')
            if wd in self.plant_wds:
                wd_dict[wd].append('plant2detail')

        return wd_dict

    # 构造actree，加速过滤
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()  # 创建自动机
        for index, word in enumerate(wordlist):  # 构造trie树
            actree.add_word(word, (index, word))
        actree.make_automaton()  #
        return actree

    # 问句过滤
    def check_question(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        # print(f"stop_wds:{stop_wds}")
        # print(f"final_wds:{final_wds}")
        final_dict = {i: self.wdtype_dict.get(i) for i in final_wds}
        # print(final_dict)

        return final_dict

    # 基于特征词进行分类
    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False

    # 分类主函数
    def classify(self, question):
        data = {}
        question_dict = self.check_question(question)
        print(question_dict)
        if not question_dict:
            return {}
        data['args'] = question_dict
        # 收集问句当中所涉及到的实体类型
        types = []
        for type_ in question_dict.values():
            types += type_
        question_type = 'others'

        question_types = []

        # city
        if self.check_words(self.city_qwds, question) and ('city' in types):
            question_type = 'city'
            question_types.append(question_type)

        # plant
        if self.check_words(self.food_qwds, question) and ('food' in types):
            question_type = 'food'
            question_types.append(question_type)

        # city2plant
        if self.check_words(self.cityplant_qwds, question) and ('city2plant' in types):
            question_type = 'city2plant'
            question_types.append(question_type)

        # plant2detail
        if self.check_words(self.plant_qwds, question) and ('plant2detail' in types):
            question_type = 'plant2detail'
            question_types.append(question_type)

        # 将多个分类结果进行合并处理，组装成一个字典
        data['question_types'] = question_types
        return data
