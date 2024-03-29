import scrapy
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy.http import TextResponse
from grpdiscount.items import GrpItem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import xlwt
class SearchSpider(scrapy.Spider):
    name = "proptiger"
    page =1
    allowed_domains = ['www.proptiger.com']
    start_urls = ['https://www.proptiger.com/noida/property-sale?page=1']

    def __init__(self, filename=None):
        # wire us up to selenium
        
        self.driver = webdriver.Firefox()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        self.driver.close()


    def add_in_sheet(self,item):
        workbook = xlwt.Workbook()
        #workbook.save('grpdiscount.xls')
        sheet = workbook.add_sheet('Sheet_1')
        sheet.write(0,0,'Project Url')
        sheet.write(0,1,item['project_url'])
        sheet.write(1,0,'Name')
        sheet.write(1,1,item['property_name'])
        sheet.write(2,0,'Address')
        sheet.write(2,1,item['address'])
        sheet.write(3,0,'Status')
        sheet.write(3,1,item['status'])
        sheet.write(4,0,'Email')
        sheet.write(4,1,"")
        sheet.write(5,0,'Phone')
        sheet.write(5,1,"")
        sheet.write(7,0,'price_per_sqft')
        sheet.write(7,1,item['price_per_sqft'])
        sheet.write(8,0,'Total Project Area')
        sheet.write(8,1,item['total_area'])
        sheet.write(9,0,'Launch Date')
        sheet.write(9,1,item['launch_date'])
        sheet.write(10,0,'Possession Date')
        sheet.write(10,1,item['possession_date'])
        sheet.write(11,0,'Type')
        col = 1
        for bhk in item['property_bhk']:
            sheet.write(11,col,bhk)
            col+=1
        sheet.write(12,0,'Bedrooms')
        col = 1
        for bedroom in item['bedroom']:
            sheet.write(12,col,bedroom)
            col+=1

        sheet.write(13,0,'Bathrooms')
        col = 1
        for bath in item['bathroom']:
            sheet.write(13,col,bath)
            col+=1
        
        sheet.write(14,0,'Area Sq. Ft.')
        prop = item['property_size']
        for i in range(len(prop)):
            sheet.write(14,i+1,prop[i])

        sheet.write(6,0,'Area-range')
        sheet.write(6,1,item['area_range'])

        sheet.write(15, 0,'Price')
        prop = item['property_price']
        for i in range(len(prop)):
            sheet.write(15,i+1,prop[i])

        sheet.write(16,0,'Carpet Area')
        sheet.write(16,1,'')
        sheet.write(17,0,'Facing')
        sheet.write(17,1,'')
        sheet.write(18,0,'Description')
        sheet.write(18,1,'Description of Project')
        sheet.write(19,1,item['description'])
        sheet.write(20,0,'Speciality')
        sheet.write(20,1,item['speciality'])
        sheet.write(21,0,'About Builder')
        sheet.write(21,1,"")
        sheet.write(22,0,'Certifications')
        sheet.write(22,1,'')
        sheet.write(23,0,'unit')
        sheet.write(23,1,item['total_apartment'])
        sheet.write(24,0,'Videos')
        col = 1
        temp = item['photos']
        if temp:
            for video in temp:
                if 'youtube' in video:
                    sheet.write(24,col,video)
                    col += 1
        sheet.write(25,0,'Amenities')
        sheet.write(25,1,item['amenities'])
        sheet.write(26,0,'Main Image')
        sheet.write(26,1,item['main_image'])
        sheet.write(27,0,'galary Image')
        col =1
        temp = item['photos']
        for image in temp:
            if not 'youtube' in image:
                sheet.write(27,col,image)
                col+=1
        workbook.save(item['property_name']+'.xlsx')

    def parse_property(self, response):
        item = GrpItem()
        # Load the current page into Selenium
        self.driver.get(response.url)

        try:
            WebDriverWait(self.driver, 40).until(EC.presence_of_element_located((By.XPATH, '//*[@id="overview"]/div/div[1]/h2')))
        except TimeoutException:
            print "Time out"
            return

        # Sync scrapy and selenium so they agree on the page we're looking at then let scrapy take over
        resp = TextResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8');
        item['property_name'] = ""
        temp = format(resp.xpath('//*[@id="views"]/div/div/div[2]/div/div[2]/div/div[1]/div/div/div[1]/div/h1/span/text()').extract())
        item['property_name'] = temp[3:-2]
    
        item['project_url'] =format(resp.url)

        main_address = format(resp.xpath('//*[@id="views"]/div/div/div[2]/div/div[2]/div/div[1]/div/div/div[2]/div[1]/span/text()').extract())
        locality = format(resp.xpath('//*[@id="views-"]/div/div/div[2]/div/div[2]/div/div[1]/div/div/div[2]/div[2]/span/text()').extract())
        item['address'] =""
        item['address'] = main_address[3:-2] +  ', ' + locality[3:-2]

        item['builder_name'] = ""
        builder_name = format(resp.xpath('//*[@id="views"]/div/div/div[3]/div/div[6]/div[5]/div/div[1]/div/div/span/text()').extract())
        builder_name = builder_name[3:-2]
        builder_name = builder_name.split()
        if len(builder_name) > 1:
            item['builder_name'] = builder_name[1]

        item['status'] = ""
        item['possession_date'] = ""
        item['area_range'] = ""
        item['total_area'] = ""
        item['total_apartment'] = ""
        item['launch_date'] = ""
        for entity in resp.xpath('//div[@id="overview"]/div/div[2]/div/span'):
            heading = format(entity.xpath('b/text()').extract()).lower()
            if heading[3:-2] == 'status':
                value = format(entity.xpath('text()').extract())
                item['status'] = value[3:-2]
            if heading[3:-2] == 'possession :' or heading[3:-2] == 'completed :':
                value = format(entity.xpath('text()').extract())
                item['possession_date'] = value[3:-2]
            if heading[3:-2] == 'sizes':
                value = format(entity.xpath('text()').extract())
                item['area_range'] = value[3:-2]
            if heading[3:-2] == 'total area':
                value = format(entity.xpath('text()').extract())
                item['total_area'] = value[3:-2]
            if heading[3:-2] == 'total apartments':
                value = format(entity.xpath('text()').extract())
                item['total_apartment'] = value[3:-2]
            if heading[3:-2] == 'launch date':
                value = format(entity.xpath('text()').extract())
                item['launch_date'] = value[3:-2]
        try :
            item['description'] = ""
            desc = self.driver.find_element_by_xpath('//*[@id="overview"]/div/div[3]/div/span[2]')
            try:
                desc.click()
                WebDriverWait(self.driver,8)
                resp = TextResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8');
                description = format(resp.xpath('//*[@id="overview"]/div/div[3]/div/span[@itemprop="description"]/text()').extract())
                item['description'] = description[3:-2]
            except:
                print 'Full description is not available....'
                description = format(resp.xpath('//*[@id="overview"]/div/div[3]/div/span[@itemprop="description"]/text()').extract())
                item['description'] = description[3:-2]
        except:
            try:
                description = format(resp.xpath('//*[@id="overview"]/div/div[3]/div/span[@itemprop="description"]/text()').extract())
                item['description'] = description[3:-2]
            except:
                item['description'] = ""

        main_amenity = resp.xpath('//div[@class="amenitiesContainer"]//div[contains(@class,"amen-cont-info ")]/span[2]/text()')
        if main_amenity:
            main_amenity = format(main_amenity.extract())
            main_amenity = main_amenity.replace("u'",'')
            main_amenity = main_amenity.replace('u"','')
            main_amenity = main_amenity.replace("'",'')
            main_amenity = main_amenity[1:-1]
            main_amenity = main_amenity.replace(',','\n')
        else :
            main_amenity = ""
        secondary_amenity = resp.xpath('//div[@class="amenitiesContainer"]/div/ul//li/text()')
        if secondary_amenity:
            secondary_amenity = format(secondary_amenity.extract())
            secondary_amenity = secondary_amenity.replace("u'",'')
            secondary_amenity = secondary_amenity.replace('u"','')
            secondary_amenity = secondary_amenity.replace("'",'')
            secondary_amenity = secondary_amenity[1:-1]
            secondary_amenity = secondary_amenity.replace(',','\n')
        else :
            secondary_amenity = ""
        item['amenities'] = main_amenity + secondary_amenity

        item['speciality'] = ""
        try:
            for speci in resp.xpath('//div[@class="specificationContainer"]/div[contains(@class,"prop-speci-info")]'):
                heading = format(speci.xpath('div/div/div[contains(@class,"stat-subComm-head-info")]/text()').extract())
                item['speciality'] += heading[3:-2] + '\n'
                for spec in speci.xpath('div/div/div[contains(@class,"spec-item")]'):
                    try :
                        value = format(spec.xpath('text()').extract())
                        value = value[5:-2]
                        value = value.strip()
                    except :
                        value = format(spec.xpath('..text()').extract())
                        value = value[5:-2]
                        value = value.strip()
                        print 'case 1'
                    try :
                        #print 6
                        header = format(spec.xpath('b/text()').extract())
                        item['speciality'] += header[3:-2] + ' : ' + value[5:-2] + '\n'
                    except :
                        item['speciality'] += value[5:-2] + '\n'
                        print "case 2"
        except:
            item['speciality'] = ""
            print "speciality is not working"
        
        item['property_bhk']=[]
        item['property_size'] = []
        for size in resp.xpath('//div[contains(@class,"projAccHeadTextInfo")]'):
            temp = format(size.xpath('div[contains(@class,"projDetaInfo")]/h2/a/text()').extract())
            try :
                temp = temp[3:]
                ind = temp.index(')')
                temp = temp[:ind]
                temp = temp.split('(')
                item['property_bhk'] += [temp[0]]
                item['property_size'] += [temp[1]]
            except :
                print "exe"
                item['property_bhk'] += []
                item['property_size'] += []

        item['property_price'] = []
        item['price_per_sqft'] = ""
        for size in resp.xpath('//div[contains(@class,"projAccBuilDetaInfo")]'):
            price_lac = size.xpath('div/div[contains(@class,"projPricInfo")]/text()').extract()
            price_sqft = size.xpath('div/div[contains(@class,"projPricDetaInfo")]/text()').extract()
            if price_lac and price_sqft:
                try :
                    price_sqft = format(price_sqft)
                    price_lac = format(price_lac)
                    price_lac = price_lac[3:-2]
                    price_sqft = price_sqft[10:-8]
                    item['price_per_sqft'] = price_sqft
                    item['property_price'] += [price_lac + ", (" + price_sqft + ')']
                except :
                    try :
                        item['property_price'] += [price_lac]
                    except:
                        try :
                            item['property_price'] += [price_sqft]
                        except :
                            item['property_price'] += []
            else :
                price = format(size.xpath('a/text()').extract())
                item['property_price'] += [price[3:-2]]

        #//div[contains(@class,"projAccorContInfo")]/div[2]/div[2]/div[1]/span/text()
        item['bedroom']  = []
        item['bathroom']  =[]
        for size in resp.xpath('//div[contains(@class,"projAccorContInfo")]'):
            bedroom = format(size.xpath('div[2]/div[2]/div[1]/span/text()').extract())
            bathroom = format(size.xpath('div[2]/div[2]/div[2]/span/text()').extract())
            try :
                bedroom = bedroom[3:-2]
                bathroom = bathroom[3:-2]
                item['bedroom'] += [bedroom]
                item['bathroom'] += [bathroom]
            except :
                item['bedroom'] += []
                item['bathroom'] += []

        item['photos'] = []
        for image in resp.xpath('//div[@id="projectImages"]//div[@class="pt-thums-img-gallery"]/ul[@class="carouselIndicators"]/li'):
            try:
                img = format(image.xpath('a/div/img/@src').extract())
                img = img[3:-2]
                item['photos'] += [img]
            except :
                item['photos'] += []

        item['main_image'] = item['photos'][0]
        self.add_in_sheet(item)


    def parse(self, response):
        self.driver.get(response.url)

        try:
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH,'//*[@id="views"]/div/div[2]/div[2]/div[3]/div[10]/div/div/div/div/div[2]/div[1]/div[1]/div[1]/div[1]/div/a/span')))
        except TimeoutException:
            print "Time out"
            return

        # Sync scrapy and selenium so they agree on the page we're looking at then let scrapy take over
        resp = TextResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8');

        for href in resp.xpath('//*[@id="views"]/div/div[2]/div[2]/div[3]/div/div/div/div/div/div[2]/div[1]/div[1]/div[1]/div[1]/div/a/@href'):
            url = resp.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_property)


        if self.page == 5 :
            return
            
        self.page += 1
        yield scrapy.Request(url="https://www.proptiger.com/noida/property-sale?page=%d" % self.page,
                      headers={"Referer": "https://www.proptiger.com/noida/property-sale", "X-Requested-With": "XMLHttpRequest"},
                      callback=self.parse, 
                      dont_filter=True)