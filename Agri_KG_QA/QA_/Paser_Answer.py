#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/3/15 10:53
# @Author  : yimoru
# @FileName: QA_.py
# @Software: PyCharm


from py2neo import Graph, Node, Relationship
from django.shortcuts import render

class QuestionPaser:
    # 构建实体节点
    def build_entitydict(self, args):
        entity_dict = {}
        for arg, types in args.items():
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [arg]
                else:
                    entity_dict[type].append(arg)
        return entity_dict

    # 解析主函数
    def parser_main(self, res_classify):
        args = res_classify['args']
        entity_dict = self.build_entitydict(args)
        question_types = res_classify['question_types']
        sqls = []
        for question_type in question_types:
            sql_ = {'question_type': question_type}
            sql = []
            if question_type == 'city':
                sql = self.sql_transfer(question_type, entity_dict.get('city'))
            elif question_type == 'food':
                sql = self.sql_transfer(question_type, entity_dict.get('food'))
            elif question_type == 'city2plant':
                sql = self.sql_transfer(question_type, entity_dict.get('city2plant'))
            elif question_type == 'plant2detail':
                sql = self.sql_transfer(question_type, entity_dict.get('plant2detail'))

            if sql:
                sql_['sql'] = sql

                sqls.append(sql_)

        return sqls

    # 针对不同的问题，分开进行处理

    def sql_transfer(self, question_type, entities):
        if not entities:
            return []

        # 查询语句
        sql = []
        # 查询城市气候
        if question_type == 'city':
            sql = ["MATCH (m:city)-[relation:气候]->(n:weather) where m.city = '{0}'" \
                   " return n.weather, m.city".format(i) for i in entities]
        # 查询food营养成分
        elif question_type == 'food':
            sql = ["MATCH (m:food)-[r:营养元素]->(n:nutrition) where m.food = '{0}' " \
                   "return n.nutrition, m.food".format(i) for i in entities]
        # 查询city2plant营养成分
        elif question_type == 'city2plant':
            sql = ["MATCH (m:city)-[*2]->(n) where m.city = '{0}'" \
                   " return n.plant, m.city".format(i) for i
                   in entities]
        # 查询plant2detail
        elif question_type == 'plant2detail':
            sql = ["MATCH (m:plant)-[relation:简介]->(n:detail) where m.plant = '{0}'" \
                   " return n.detail, m.plant".format(i) for i in entities]

        return sql


class AnswerSearcher:
    def __init__(self):
        self.g = Graph(
            host="127.0.0.1",
            http_port=7474,
            user="neo4j",
            password="123456")
        self.num_limit = 20

    '''执行cypher查询，并返回相应结果'''

    def search_main(self, sqls):
        final_answers = {}
        for sql_ in sqls:
            question_type = sql_['question_type']
            queries = sql_['sql']
            answers = []
            for query in queries:
                ress = self.g.run(query).data()
                answers += ress
                # print(f'answers{answers}')
            final_answer = self.answer_prettify(question_type, answers)
            # print(f'final_answer{final_answer}')
            if final_answer:
                final_answers = dict(final_answer, **final_answers)
        return final_answers

    '''根据对应的qustion_type，调用相应的回复模板'''

    def answer_prettify(self, question_type, answers):
        final_answer = {'answer': [], 'list': []}
        # final_answer['answer'] = ''.join(final_answer['answer'])
        # print(f'final_a{final_answer}')
        # print(f'answers:{answers}')
        if not answers:
            return ''
        if question_type == 'city':
            desc = [i['m.city'] for i in answers]
            subject = answers[0]['n.weather']
            final_answer['answer'] = subject.split('asdfghjk')
            final_answer['list'].append({'entity1': list(set(desc)), 'rel': '气候类型', 'entity2': subject,
                                         'entity1_type': 'city', 'entity2_type': 'weather'})

        elif question_type == 'food':
            desc = [i['m.food'] for i in answers]
            import re
            subject = re.split('，|、', answers[0]['n.nutrition'])
            final_answer['answer'] = subject
            # subject = answers[0]['n.nutrition'].split('、')
            for i in range(len(subject)):
                final_answer['list'].append({'entity1': list(set(desc))[0], 'rel': '营养成分', 'entity2': subject[i],
                                         'entity1_type': 'food', 'entity2_type': 'nutrition'})

        elif question_type == 'city2plant':
            desc = [i['m.city'] for i in answers]
            # print(f'desc:{desc}')
            subject = []
            for i in range(len(answers)):
                sub = answers[i]['n.plant']
                subject.append(answers[i]['n.plant'])
                # print(f'subject{subject}')
                # final_answer['answer'] = '{1}适合种植的植物包括：{0}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
                final_answer['answer'] = subject
                final_answer['list'].append({'entity1': list(set(desc))[0], 'rel': '适合种植', 'entity2': sub,
                                             'entity1_type': 'city', 'entity2_type': 'plant'})
                if i > 10:
                    break
            final_answer['answer'] = subject
        elif question_type == 'plant2detail':
            desc = [i['m.plant'] for i in answers]
            subject = answers[0]['n.detail']
            final_answer['answer'] = subject.split('asdfghjk')
            final_answer['list'].append({'entity1': list(set(desc)), 'rel': '基本知识', 'entity2': subject,
                                         'entity1_type': 'plant', 'entity2_type': 'detail'})
        return final_answer




