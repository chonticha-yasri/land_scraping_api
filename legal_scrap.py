import encodings
from bs4 import BeautifulSoup
import pandas as pd
from regex import L
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import random
import re
from selenium.webdriver.common.by import By
from lxml import etree

class Legal():

    def __init__(self):
        self.BASE_URL = 'http://asset.led.go.th/newbid-old/'
        self.data = []
        self.driver = None
        self.df = None


    def parse_tr(self, td):
        return {
            "ลำดับที่การขาย": td[0].text.strip(),
            "หมายเลขคดี": td[1].text.strip(),
            "ประเภททรัพย์": td[2].text.strip(),
            "ไร่": td[3].text.strip(),
            "งาน": td[4].text.strip(),
            "ตร.วา": td[5].text.strip(),
            "ราคาประเมิน": td[6].text.strip(),
            "ตำบล": td[7].text.strip(),
            "อำเภอ": td[8].text.strip(),
            "จังหวัด": td[9].text.strip(),
            "เลขที่โฉนด" : None,
            "โจทก์" : None
        }


    def setup(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-notifications")
        options.add_argument('--disable-gpu')
        options.add_argument('--enable-webgl')
        self.driver = webdriver.Chrome("./chromedriver.exe", options=options)
        time.sleep(random.uniform(1,3))
        return self.driver

         
    def request(self, URL):
        self.driver = self.setup()
        self.driver.get(URL)

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1.5,2))
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        self.driver.quit()
        return soup

    def _get_numpage(self, soup):
        dom = etree.HTML(str(soup))
        return int(dom.xpath('/html/body/table[3]/tbody/tr/td[1]/table[2]/tbody/tr/td[2]/div/text()[2]')[0].strip().split('/')[-1])
    
    def main_page(self, numpage):

        URL = f'http://asset.led.go.th/newbid-old/asset_search_province.asp?search_asset_type_id=&search_tumbol=&search_ampur=&search_province=%BA%D8%C3%D5%C3%D1%C1%C2%EC&search_sub_province=&search_price_begin=&search_price_end=&search_bid_date=&page={numpage}'
        soup = self.request(URL)
        print(URL)
        
        table = soup.findAll('table')[6]
        n = 3
        for tr in table.findAll('tr')[2:]:
            data = self.parse_tr(tr.findAll('td'))
            print(data['หมายเลขคดี'])
            try:
                data = self._sub_page(URL, data['หมายเลขคดี'], data)
            except:
                pass
            # print(data)
            n+=1
            self.data.append(data)
        self.df = pd.DataFrame(self.data)
        return self.df

    
    def _sub_page(self, URL, text_search, data):
        self.driver = self.setup()
        self.driver.get(URL)
        window_before = self.driver.window_handles[0]
        self.driver.find_element_by_xpath(f"//*[contains(text(), '{text_search}')]").click() 
        window_after = self.driver.window_handles[1]
        time.sleep(random.uniform(3,6))
        self.driver.switch_to.window(window_after)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        try:
            data['เลขที่โฉนด'] = soup.find(text = re.compile('.*โฉนดเลขที่.*')).findNext('font').get_text(strip=True) #เลขที่โฉนด
        except:
            data['เลขที่โฉนด'] = soup.find(text = re.compile('.*เลขที่.*')).findNext('font').get_text(strip=True) #เลขที่โฉนด
        
        data['โจทก์'] = soup.find(text = re.compile('.*โจทก์.*')).find_previous('font').get_text(strip=True) #โจทก์

        self.driver.switch_to.window(window_before)

        return data

    

    def RUN(self):
        self.driver = self.setup()
        soup = self.request("http://asset.led.go.th/newbid-old/asset_search_province.asp?search_asset_type_id=&search_tumbol=&search_ampur=&search_province=%BA%D8%C3%D5%C3%D1%C1%C2%EC&search_sub_province=&search_price_begin=&search_price_end=&search_bid_date=&page=1")
        num_page = self._get_numpage(soup)
        # num_page = 1
        print(num_page)
        for n in range(num_page):
            print('page :  ', n+1)
            self.main_page(n+1)
        # self.df.to_csv('test.csv', index = False, encoding= 'utf-8-sig')
        self.df.drop_duplicates(inplace=True)
        self.df = self.df.dropna()
        return self.df




# Legal().RUN()



