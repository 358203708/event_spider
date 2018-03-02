from scrapy import Request
from scrapy.spiders import Spider
from event_spider.items import EventSpiderItem
from scrapy.http import Request, FormRequest
import re
import json
from datetime import datetime
from zhon.hanzi import punctuation


class EventSpider(Spider):
    name = 'event_spider'
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0"
    }
    
    start_urls = 'http://www.eshow365.com/ZhanHui/Ajax/AjaxSearcherV3.aspx'
    __page_num__ = None
    
    #发送请求获取页面总数page_num
    def start_requests(self):
        form_data =    {
            "1":"1",
            "tag":"0",
            "startendtime":"2018/12/31",
            "starttime":"2018/1/1"}
        yield FormRequest(self.start_urls,
                          formdata=form_data,
                          headers=self.headers,
                          callback = self.parse_page_num)

    #发生post请求，请求每个页面
    def parse_page_num(self, response):
        page_num = len(response.xpath('//*[@id="pagestr"]/li[5]/select/option'))
        page_info = None
        
        self.__page_num__ = page_num
        #self.__page_num__ = 10
        for i in range(1, self.__page_num__+1):
            form_data =    {
            "page" : str(i),
            "1":"1",
            "tag":"0",
            "startendtime":"2018/12/31",
            "starttime":"2018/1/1"}
            yield FormRequest(self.start_urls,
                          formdata=form_data,
                          headers=self.headers,
                          callback = self.parse)

    #根据展会场地名称向百度地图api发送post请求，获取场地坐标
    def get_geolocation(self, response):
        #print('get_loc')
        item = response.meta['item']
        
        status = int(response.xpath('//status/text()').extract()[0])
        #print(response.xpath('string(.)'))
        if status == 0 :
            item['site_lat'] = response.xpath('//location/lat/text()').extract()[0]
            item['site_lng'] = response.xpath('//location/lng/text()').extract()[0]
        else:
            item['site_lat'] = []
            item['site_lng'] = []
        
        yield item

        
    #对xpath取出的list进行字符串处理
    def go_split(self, info):
        
        #去除中文标点符号
        punc = "，,！？｡＂＃＄％＆＇()＊＋，－／；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.（）、"
        info = re.sub(r"[%s]+" %punc,"", info)
        #info = re.sub(r"[%s]+" %punctuation,"", info)
        #print(info)

        #拆分字符串
        pattern = '\||\-|\：|\r|\n| '
        result = re.split(pattern, info)       
        
        return [ i.strip() for i in filter(lambda x:x.strip() != '', result)]


    #获取展会信息
    def get_info(self,response):
        #print('get_info')
        item = EventSpiderItem()

        name = response.xpath('//div[5]/div/h1/text()').extract()[0]
        item['name'] = self.go_split(name)[0]

        event_time = response.xpath('//div[5]/div/div[3]/div[2]/p[1]/text()').extract()[0]
        #datetime.strptime("2018/01/12", "%Y/%m/%d").strftime('%Y-%m-%d')
        item['start_time'] = datetime.strptime(self.go_split(event_time)[1],"%Y/%m/%d").strftime('%Y-%m-%d')
        item['end_time'] = datetime.strptime(self.go_split(event_time)[2],"%Y/%m/%d").strftime('%Y-%m-%d')
        #print(item['start_time'])
        #print(item['end_time'])
        
        item['category'] = response.xpath('//div[5]/div/div[3]/div[2]/p[3]/a[1]/text()').extract()[0]

        city = response.xpath('//div[5]/div/div[3]/div[2]/p[4]/text()').extract()[0]
        item['city'] = self.go_split(city)[2]
    
        site_name = response.xpath('//div[5]/div/div[3]/div[2]/p[2]').xpath('string(.)').extract()[0].replace(u'\xa0', u' ')
        #print(site_name)
        item['site_name'] = self.go_split(site_name)[1]

        #根据展会场地名称向百度地图api发送post请求，获取场地坐标
        default_urls = 'http://api.map.baidu.com/geocoder/v2/'

        form_data =    {
            "address" : str(item['site_name']) ,
            "city": str(item['city']),
            "output": "xml",
            "callback": "showLocation",
            "ak": "gavUQ1swaSkE3yCFuvjg5sV4hcfugEaG"}

        #print(form_data)

        request = FormRequest(default_urls,
                          formdata=form_data,
                          callback = self.get_geolocation, 
                          dont_filter=True)

        request.meta['item'] = item
 
        #item['site_location'] = response.xpath('//div[5]/div/div[3]/div[2]/p[2]/text()[2]').extract()[0].replace(u'\xa0', u'')
        
        yield request



    def parse(self, response):
        #print('parse')             
        events = response.xpath('//*[@id="from1"]/div[@class="sslist"]')

        #通过每个展会的link获取每个展会信息
        for event in events:
            link = 'http://www.eshow365.com/' + event.xpath('./p[1]/a/@href').extract()[0] 
            #print(link)
            yield Request(link, callback = self.get_info)



 







