#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-07-20 16:29:02
# Project: maotouying
import pymongo
from pyspider.libs.base_handler import *


class Handler(BaseHandler):
    crawl_config = {
    }
    client = pymongo.MongoClient('localhost')
    db = client['trip']

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('https://www.tripadvisor.cn/Attractions-g186338-Activities-London_England.html#ATTRACTION_SORT_WRAPPER', callback=self.index_page)
        
    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('.listing_title > a').items():
            self.crawl(each.attr.href, callback=self.detail_page)
        next = response.doc('.pagination > .taLnk').attr.href
        self.crawl(next, callback=self.index_page)
        
    @config(priority=2)
    def detail_page(self, response):
        name = response.doc('.heading_title').text()
        type_jindian = response.doc('.attraction_details a').text()
        iphone = response.doc('.headerBL .phone > span').text()
        return {
            "name": name,
            "type_jindian": type_jindian,
            "iphone": iphone
        }

    def on_result(self, result):
        if result:
            self.save_to_mongo(result)
    
    def save_to_mongo(self, result):
        if self.db['london'].insert(result):
            print('saved to mongo', result)