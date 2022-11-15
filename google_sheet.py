from gspread_formatting import *
import gspread
from df2gspread import df2gspread as d2g
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from gspread_dataframe import set_with_dataframe
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import numpy as np
from pprint import pprint

from requests import delete
from eland_scrap import *
from legal_scrap import *


class Sheet_upload:
    def __init__(self):

        self.sheet1 = None
        self.sheet2 = None
        self.col1 = ["ลำดับ","ชื่อเรื่อง","ชื่อผู้ถือกรรมสิทธิ/ผู้ขอ","ประเภท","วันที่ลงนามในประกาศ","วันที่ครบประกาศ","สำนักงาน","ประกาศ"]
        self.col2 = ["ลำดับที่การขาย", "หมายเลขคดี","ประเภททรัพย์","ไร่", "งาน","ตร.วา","ราคาประเมิน", "ตำบล", "อำเภอ","จังหวัด", "เลขที่โฉนด","โจทก์"]

    def setup(self):
        credentials = service_account.Credentials.from_service_account_file('C:\\eland\\keys.json')
        scoped_credentials = credentials.with_scopes(
            ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']
        )

        gc = gspread.Client(auth=scoped_credentials)
        gc.session = AuthorizedSession(scoped_credentials)

        spreadsheet_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXX'

        sh = gc.open_by_key(spreadsheet_key)
        self.sheet1 = sh.get_worksheet(0)
        self.sheet2 = sh.get_worksheet(1)
        return
    
    def upload(self, df1, df2):
        self.sheet1.clear()
        self.sheet2.clear()
        set_with_dataframe(self.sheet1, df1)
        set_with_dataframe(self.sheet2, df2)
        self.check_box('I', self.sheet1, 2)
        self.check_box('M', self.sheet2, 2)
        return
    
    def check_update_sheet1(self, df_new):
        str_row = self.next_available_row(self.sheet1)
        values = self.sheet1.get_all_values()
        df_old = pd.DataFrame(values)
        df_old.columns = df_old.iloc[0]
        df_old.drop(df_old.index[0], inplace=True)    
        df_old = df_old[self.col1]
        df_check = self.check_data_update(df_old, df_new)
        end_row = str_row + int(len(df_check.values.tolist()))
        print(str_row, end_row)
        self.sheet1.update(f'{str_row}:{end_row}', df_check.values.tolist())
        self.check_box('I', self.sheet1, str_row)
        self.fill_color_wh(2, str_row-1, self.sheet1)
        self.fill_color(str_row, end_row-1, self.sheet1)
        return
    
    def check_update_sheet2(self, df_new):
        str_row = self.next_available_row(self.sheet2)
        values = self.sheet2.get_all_values()
        df_old = pd.DataFrame(values)
        df_old.columns = df_old.iloc[0]
        df_old.drop(df_old.index[0], inplace=True)    
        # print(df_old)
        df_old = df_old[self.col2]

        df_check = self.check_data_update(df_old, df_new)
        end_row = str_row + int(len(df_check.values.tolist()))
        self.sheet2.update(f'{str_row}:{end_row}', df_check.values.tolist())
        self.check_box('M', self.sheet2, str_row)
        self.fill_color_wh(2, str_row-1, self.sheet2)
        self.fill_color(str_row, end_row-1, self.sheet2)
        return


    def next_available_row(self, worksheet): # gat last rows number
        str_list = list(filter(None, worksheet.col_values(1)))

        return int(len(str_list)+1)


    def check_box(self, cols_name, worksheet, str_row): # create checkbox
        validation_rule = DataValidationRule(
            BooleanCondition('BOOLEAN', []), 
            showCustomUi = True
        )

        worksheet.update_acell(f"{cols_name}1", 'verified') # N1
        next_row = self.next_available_row(worksheet)

        set_data_validation_for_cell_range(worksheet, f'{cols_name}{str_row}:{cols_name}{next_row-1}', validation_rule)
        return
    
    def check_data_update(self, df_old, df_new):
        df = df_new.merge(df_old, how = 'outer' ,indicator=True).loc[lambda x : x['_merge']=='left_only']
        return df.drop('_merge',1)
    

    def fill_color(self, str_row, end_row, worksheet):

        fmt = cellFormat(
            backgroundColor=color(1, 0.9, 0.9))

        format_cell_range(worksheet, f'{str_row}:{end_row}', fmt)

    
    def fill_color_wh(self, str_row, end_row, worksheet):

        fmt = cellFormat(
            backgroundColor=color(1, 1, 1))

        format_cell_range(worksheet, f'{str_row}:{end_row}', fmt)
    
    def delete_row(self,worksheet, st, en):
        self.setup()
        worksheet.delete_rows(st,en)

    
    def RUN(self):
        df1 = Eland().run()
        df2 = Legal().RUN()
        self.setup()
        # self.upload(df1, df2) #frist time
        self.check_update_sheet1(df_new = df1)
        self.check_update_sheet2(df_new = df2)
        self.next_available_row(self.sheet2)
        print('success!!')
        return



Sheet_upload().RUN()
