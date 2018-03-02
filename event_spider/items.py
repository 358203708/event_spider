# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EventSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    category = scrapy.Field()
    name = scrapy.Field()
    #follower = scrapy.Field()
    #event_time = scrapy.Field()
    start_time = scrapy.Field()
    end_time = scrapy.Field()
    city = scrapy.Field()
    site_name = scrapy.Field()
    site_lat = scrapy.Field()
    site_lng = scrapy.Field()
    #site_location = scrapy.Field()

    pass
