import os, sys, time
import xlrd, xlwt
from xlutils.copy import copy as xl_copy

class XlsDB:
    data_offset = 4  # offset from service information
    monitor_column, link_column, shop_name_column, product_name_column = [i for i in range(data_offset)]
    def __init__(self, db_filename='products.xls'):
        self.today = time.strftime('%d.%m.%Y')

        if not os.path.isfile(db_filename):
            self.db_filename = 'products.xls'
        else:
            self.db_filename = db_filename

        try:
            self.read_stream = xlrd.open_workbook(self.db_filename)
        except FileNotFoundError:
            self.read_stream = None

    '''
    def dump_db(self, category='all'):
        try:
            products_db = xlrd.open_workbook(self.db_filename)
            sheet = products_db.sheet_by_index(0)
            print(products_db.sheet_names())
            for col_i in range(sheet.ncols):
                col = sheet.col_values(col_i)
                print(col)

            #for cell in col:
             #   print(cell)
        except FileNotFoundError:
            print('File not exist. Need add information about product')
    '''

    def add_info(self, category, shop, product, price, product_link, date=None):
        if not date:
            date = self.today

        try:
            products_db = xl_copy(self.read_stream)
            sheet = self.read_stream.sheet_by_name(category)
        except Exception:
            if sys.exc_info()[0] is AttributeError: # File not exist
                products_db = xlwt.Workbook()
            else: # List in file not exist xlrd.biffh.XLRDError
                products_db = xl_copy(self.read_stream)

            products_db_sheet = products_db.add_sheet(category)
            products_db_sheet.write(0, self.monitor_column, 'Monitor')
            products_db_sheet.write(0, self.link_column, 'Link')
            products_db_sheet.write(0, self.shop_name_column, 'Shop')
            products_db_sheet.write(0, self.product_name_column, 'Product')
            products_db.save(self.db_filename)
            self.read_stream = xlrd.open_workbook(self.db_filename)
            sheet = self.read_stream.sheet_by_name(category)

        sheet_write = products_db.get_sheet(category)

        product_row = self.find_product_row(sheet, shop, product)
        product_col_date = self.get_date_column(sheet, date)

        if product_col_date < 0:
            product_col_date = sheet.ncols  # cells start with 0

        if product_row < 0: # product row not found
            product_row = sheet.nrows
            sheet_write.write(product_row, self.monitor_column, 1)
            sheet_write.write(product_row, self.link_column, product_link)
            sheet_write.write(product_row, self.shop_name_column, shop)
            sheet_write.write(product_row, self.product_name_column, product)

        sheet_write.write(0, product_col_date, date)
        sheet_write.write(product_row, product_col_date, price)
        products_db.save(self.db_filename)
        self.refresh_book()

    def get_date_column(self, sheet, date):
        if sheet.row_slice(0)[-1].value.strip() != date:
            return -1

        return len(sheet.row_slice(0))-1

    def find_product_row(self, sheet, shop, product):
        for row in range(1, sheet.nrows):
            if sheet.row_slice(row)[self.product_name_column].value == product and \
                            sheet.row_slice(row)[self.shop_name_column].value == shop:
                return row

        return -1

    def get_categories(self):
        try:
            return self.read_stream.sheet_names()
        except AttributeError:
            return []

    def refresh_book(self):
        self.read_stream = xlrd.open_workbook(self.db_filename)

#db = XlsDB()
#db.add_info('Vcardss', 'shop4', 'product3', 'price10')