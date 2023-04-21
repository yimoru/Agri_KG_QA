#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Time    : 2023/4/12 16:35
# @AUthor  : yimoru
# @FileName: entityExtractor1.py
# @software: PyCharm
# @desc    :


import os
import ahocorasick
from sklearn.externals import joblib
import jieba
import numpy as np


class EntityExtractor:
    def __init__(self):
        cur_dir = os.path.abspath('.')  # 获得当前工作目录      (django run)
        # cur_dir = os.path.abspath(os.path.join(os.getcwd(), '../../'))  # 获得当前工作目录的上两级目录   (local run)
        # cur_dir = '/'.join(os.path.abspath(".").split('\\')[:-1])
        # print(cur_dir)
        data_dir = cur_dir + '/dict/'
        # 路径
        self.stopwords_path = os.path.join(cur_dir, 'dict/stop_words.utf8')
        self.word2vec_path = os.path.join(cur_dir, 'dict/merge_sgns_bigram_char300.txt')
        # self.same_words_path = os.path.join(cur_dir, 'DATA/同义词林.txt')
        self.stopwords = [w.strip() for w in open(self.stopwords_path, 'r', encoding='utf8') if w.strip()]

        # 意图分类模型文件
        self.tfidf_path = os.path.join(cur_dir, 'model/tfidf_model.m')
        self.nb_path = os.path.join(cur_dir, 'model/intent_reg_model.m')  # 朴素贝叶斯模型
        self.tfidf_model = joblib.load(self.tfidf_path)
        self.nb_model = joblib.load(self.nb_path)

        self.city_path = data_dir + 'city.txt'
        self.plant_path = data_dir + 'plant.txt'
        self.food_path = data_dir + 'food.txt'

        self.city_entities = [w.strip() for w in open(self.city_path, encoding='utf8') if w.strip()]
        self.plant_entities = [w.strip() for w in open(self.plant_path, encoding='utf8') if w.strip()]
        self.food_entities = [w.strip() for w in open(self.food_path, encoding='utf8') if w.strip()]

        self.region_words = list(set(self.city_entities+self.plant_entities+self.food_entities))

        # 构造领域actree
        self.city_tree = self.build_actree(list(set(self.city_entities)))
        self.plant_tree = self.build_actree(list(set(self.plant_entities)))
        self.food_tree = self.build_actree(list(set(self.food_entities)))

        self.city_qwds = ['气候', '天气']
        self.food_qwds = ['营养元素', '营养成分']
        self.cityplant_qwds = ['适合种植', '适合种', '可以种植', '可以种', '应该种', '适合种']
        self.plant_qwds = ['详细信息', '简介', '基本信息', '知识']

    def build_actree(self, wordlist):
        """
        构造actree，加速过滤
        :param wordlist:
        :return:
        """
        actree = ahocorasick.Automaton()
        # 向树中添加单词
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    def check(self, type, word):
        stop_wds = []
        # key = ['city', 'food', 'plant', 'city_plant']
        # print(f'word:{word}')
        for wd1 in word:
            for wd2 in word:
                if wd1 in wd2 and wd1 != wd2:
                    # print(f'{wd1}')
                    stop_wds.append(wd1)
        final_wds = [i for i in word if i not in stop_wds]
        # print(f"stop_wds:{final_wds}")
        # print(f"final_wds:{final_wds}")
        # for i in final_wds:
        #     self.final_dict[i] = [type]
        for i in final_wds:
            if i not in self.final_dict:
                self.final_dict[i] = [type]
            else:
                self.final_dict[i].append(type)

        # self.final_dict = {i: type for i in final_wds}
        # print(f'final_dict{self.final_dict}')
        return self.final_dict

    def entity_reg(self, question):
        """
        模式匹配, 得到匹配的词和类型。如疾病，疾病别名，并发症，症状
        :param question:str
        :return:
        """
        result = {}
        # q_type = []
        self.final_dict = {}

        for i in self.city_tree.iter(question):
            word = i[1][1]
            if "city" not in result:
                result["city"] = [word]
            else:
                result["city"].append(word)
        if 'city' in result.keys():
            # q_type.append('city')
            q_type = 'city'
            self.check(q_type, result["city"])

        for i in self.food_tree.iter(question):
            word = i[1][1]
            if "food" not in result:
                result["food"] = [word]
            else:
                result["food"].append(word)
        # print(result['food'])
        if 'food' in result.keys():
            # q_type.append('food')
            q_type = 'food'
            self.check(q_type, result['food'])

        for i in self.plant_tree.iter(question):
            wd = i[1][1]
            if "plant" not in result:
                result["plant"] = [wd]
            else:
                result["plant"].append(wd)
        if 'plant' in result.keys():
            # q_type.append('plant')
            q_type = 'plant2detail'
            self.check(q_type, result['plant'])

        for i in self.city_tree.iter(question):
            wd = i[1][1]
            # data = self.check('city', wd)
            if "city2plant" not in result:
                result["city2plant"] = [wd]
            else:
                result["city2plant"].append(wd)
        if 'city2plant' in result.keys():
            # q_type.append('city_plant')
            q_type = 'city2plant'
            self.check(q_type, result['city2plant'])

        return self.final_dict

    def find_sim_words(self, question):
        """
        当全匹配失败时，就采用相似度计算来找相似的词
        :param question:
        :return:相似度最高的实体
        """
        import re
        import string
        from gensim.models import KeyedVectors

        jieba.load_userdict(self.city_path)    # 加载自定义词库
        # 加载预训练好的词向量
        self.model = KeyedVectors.load_word2vec_format(self.word2vec_path, binary=False)

        # re.sub    替换字符串中的匹配项
        # re.escape 去除转义字符
        # string.punctuation      #所有的标点字符   '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        sentence = re.sub("[{}]", re.escape(string.punctuation), question)
        sentence = re.sub("[，。‘’；：？、！【】]", " ", sentence)
        sentence = sentence.strip()     # 去除首尾指定字符，默认为空格或换行符
        print(f'sentence: {sentence}')

        words = [w.strip() for w in jieba.cut(sentence) if w.strip() not in self.stopwords and len(w.strip()) >= 2]

        alist = []

        for word in words:
            temp = [self.city_entities, self.food_entities, self.plant_entities, self.complication_entities]
            for i in range(len(temp)):
                flag = ''
                if i == 0:
                    flag = "city"
                elif i == 1:
                    flag = "food"
                elif i == 2:
                    flag = "plant2detail"
                elif i == 3:
                    flag = "city_plant"
                scores = self.simCal(word, temp[i], flag)
                alist.extend(scores)
        temp1 = sorted(alist, key=lambda k: k[1], reverse=True)
        if temp1:
            self.result[temp1[0][2]] = [temp1[0][0]]

    def editDistanceDP(self, s1, s2):
        """
        采用DP方法计算编辑距离
        :param s1:要比较的字符串1
        :param s2:要比较的字符串2
        :return:solution[m][n] 数据类型为int 返回数据越小，相似度越大
        """
        m = len(s1)
        n = len(s2)
        solution = [[0 for j in range(n + 1)] for i in range(m + 1)]
        for i in range(len(s2) + 1):
            solution[0][i] = i
        for i in range(len(s1) + 1):
            solution[i][0] = i

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    solution[i][j] = solution[i - 1][j - 1]
                else:
                    solution[i][j] = 1 + min(solution[i][j - 1], min(solution[i - 1][j],
                                                                     solution[i - 1][j - 1]))
        return solution[m][n]

    def simCal(self, word, entities, flag):
        """
        计算词语和字典中的词的相似度
        相同字符的个数/min(|A|,|B|)   +  余弦相似度
        :param word: str
        :param entities:List
        :return:
        """
        a = len(word)
        scores = []
        for entity in entities:
            sim_num = 0
            b = len(entity)
            c = len(set(entity+word))
            temp = []
            for w in word:
                if w in entity:
                    sim_num += 1
            if sim_num != 0:
                score1 = sim_num / c  # overlap score
                temp.append(score1)
            try:
                score2 = self.model.similarity(word, entity)  # 余弦相似度分数
                temp.append(score2)
            except:
                pass
            score3 = 1 - self.editDistanceDP(word, entity) / (a + b)  # 编辑距离分数
            if score3:
                temp.append(score3)

            score = sum(temp) / len(temp)
            if score >= 0.7:
                scores.append((entity, score, flag))

        scores.sort(key=lambda k: k[1], reverse=True)   # 按照score进行从大到小排序
        return scores

    def check_words(self, wds, sent):
        """
        基于特征词分类
        :param wds:
        :param sent:
        :return:
        """
        for wd in wds:
            if wd in sent:
                return True
        return False

    def tfidf_features(self, text, vectorizer):
        """
        提取问题的TF-IDF特征
        :param text:
        :param vectorizer:
        :return:
        """
        jieba.load_userdict(self.city_path)
        words = [w.strip() for w in jieba.cut(text) if w.strip() and w.strip() not in self.stopwords]
        sents = [' '.join(words)]

        tfidf = vectorizer.transform(sents).toarray()
        return tfidf

    def other_features(self, text):
        """
        提取问题的关键词特征
        :param text:
        :return:
        """
        features = [0] * 4
        for d in self.cityplant_qwds:
            if d in text:
                features[0] += 1

        for s in self.city_qwds:
            if s in text:
                features[1] += 1

        for c in self.food_qwds:
            if c in text:
                features[2] += 1

        for c in self.plant_qwds:
            if c in text:
                features[3] += 1

        m = max(features)
        n = min(features)
        normed_features = []
        if m == n:
            normed_features = features
        else:
            for i in features:
                j = (i - n) / (m - n)
                normed_features.append(j)

        return np.array(normed_features)

    def model_predict(self, x, model):
        """
        预测意图
        :param x:
        :param model:
        :return:
        """
        question_types = []
        # print(question_types)
        pred = model.predict(x)
        # print(pred[0])
        if pred[0] == 0:
            # question_type = 'city_plant'
            # if question_type not in question_types:
            question_types.append('city2plant')
        elif pred[0] == 1:
            # question_type = 'city'
            # if question_type not in question_types:
            question_types.append('city')
        elif pred[0] == 2:
            # question_type = 'food'
            # if question_type not in question_types:
            question_types.append('food')
        elif pred[0] == 3:
            # question_type = 'plant'
            # if question_type not in question_types:
            question_types.append('plant2detail')
        # print(question_types)
        # return pred
        return question_types

    # 实体抽取主函数
    def extractor(self, question):
        data = {}
        self.entity_reg(question)
        if not self.final_dict:
            self.find_sim_words(question)
        data['args'] = self.final_dict

        types = []  # 实体类型
        for v in self.final_dict.keys():
            types.append(v)

        question_types = []  # 查询意图

        # 意图预测
        tfidf_feature = self.tfidf_features(question, self.tfidf_model)

        predicted = self.model_predict(tfidf_feature, self.nb_model)
        # print(predicted)
        question_types.append(predicted[0])

        #
        if self.check_words(self.city_qwds, question) and ('city' in types):
            if self.check_words(self.cityplant_qwds, question) and ('city2plant' in types):
                question_type = "city2plant"
            else:
                question_type = "city"
            if question_type not in question_types:
                question_types.append(question_type)

        if self.check_words(self.plant_qwds, question) and ('plant2detail' in types):
            question_type = "plant2detail"
            if question_type not in question_types:
                question_types.append(question_type)
        #
        if self.check_words(self.food_qwds, question) and ('food' in types):
            question_type = "food"
            if question_type not in question_types:
                question_types.append(question_type)

        data["question_types"] = question_types

        return data

