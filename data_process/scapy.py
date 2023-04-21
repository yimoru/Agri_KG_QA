#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# @Time    : 2023/3/30 20:50
# @Author  : yimoru
# @FileName: scapy.py
# @software: PyCharm
# @Desc    :

import scrapy


class CnblogSpider(scrapy.Spider):
    name = 'test'
    allowed_domains = ['www.openssl.org']
    start_urls = ['https://www.openssl.org/news/vulnerabilities.html']

    def parse(self, response):
        name = response.xpath('//div[@id="content"]//dl/dt/a/@name').extract()
        fix = response.xpath('//div[@id="content"]//dl/dd/ul/li/text()').extract()
        url = response.xpath('//div[@id="content"]//dl/dd/ul/li/a/@href').extract()
        for item in zip(name, fix, url):
            yield {
                '名称': item[0],
                'fix': item[1],
                'url': item[2]
            }
            print(item)
