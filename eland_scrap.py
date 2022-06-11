import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

class Eland:
    def __init__(self):
        self.BASE_URL = 'http://announce.dol.go.th/'
        self.data = []

    def _request(self, URL):
        r = requests.get(URL)
        print(r.status_code)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup
    

    def parse_tr(self, tr):
        return {
            "ลำดับ": tr[0].text,
            "ชื่อเรื่อง": tr[1].text,
            "ชื่อผู้ถือกรรมสิทธิ/ผู้ขอ": tr[2].text,
            "ประเภท": tr[3].text,
            "วันที่ลงนามในประกาศ": tr[4].text,
            "วันที่ครบประกาศ": tr[5].text,
            "สำนักงาน": tr[6].text,
            "ประกาศ": self.BASE_URL+re.findall('.*href="(.*)" target', str(tr[7]))[0]
        }


    def _table(self):
        p = 1
        condition = True
        while condition:
            soup = self._request(f'http://announce.dol.go.th/index.php?Page={p}&searchprovince=28&searchoffice=&searchtype=ใบแทน&searchtitle=&searchconcerned=&searchdocno=')
            tr = soup.find("table")
            if len(tr.find_all('tr')[1:]) == 0:
                condition = False
            for th in tr.find_all('tr')[1:]:
                self.data.append(self.parse_tr(th.find_all('th')))
            p +=1
        return 

    def run(self):
        self._table()
        df = pd.DataFrame(self.data)      
        return df



# df = Eland().run()

