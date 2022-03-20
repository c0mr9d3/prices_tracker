import os, sys, time
import xlrd, xlwt
from xlutils.copy import copy as xl_copy

class XlsDB:
    data_offset = 4  # offset from service information
    monitor_column, link_column, shop_site_column, product_name_column = [i for i in range(data_offset)]
    def __init__(self, db_filename='products.xls'):
        self.today = time.strftime('%d.%m.%Y')

        if not os.path.isfile(db_filename):
            self.db_filename = 'products.xls'
        else:
            self.db_filename = db_filename

        try:
            self.read_stream = xlrd.open_workbook(self.db_filename)
        except (xlrd.biffh.XLRDError, FileNotFoundError): # xlrd.biffh.XLRDError when filesize 0 bytes
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

    def update_product_info(self, category, product_row, product_name, price, date=None):
        if product_row < 1:
            return -1

        if not date:
            date = self.today

        try:
            products_db = xl_copy(self.read_stream)
        except Exception:
            if sys.exc_info()[0] is AttributeError: # File not exist or filesize 0 bytes
                products_db = xlwt.Workbook()
            else: # Category sheet in file not exist xlrd.biffh.XLRDError
                products_db = xl_copy(self.read_stream)

            self.create_category_skel(category)

        sheet_read = self.read_stream.sheet_by_name(category)
        sheet_write = products_db.get_sheet(category)
        product_col_date = self.get_date_column(sheet_read, date)

        if product_col_date < 0:
            product_col_date = sheet_read.ncols  # cells start with 0

        if not sheet_read.cell(product_row, self.product_name_column).value:
            sheet_write.write(product_row, self.product_name_column, product_name)

        sheet_write.write(0, product_col_date, date)
        sheet_write.write(product_row, product_col_date, price)
        products_db.save(self.db_filename)
        self.refresh_book()
        return 0

    def create_category_skel(self, category):
        try:
            products_db = xl_copy(self.read_stream)
        except AttributeError: # File not exist or filesize 0 bytes
            products_db = xlwt.Workbook()

        products_db_sheet = products_db.add_sheet(category)
        products_db_sheet.write(0, self.monitor_column, 'Monitor')
        products_db_sheet.write(0, self.link_column, 'Link')
        products_db_sheet.write(0, self.shop_site_column, 'Shop')
        products_db_sheet.write(0, self.product_name_column, 'Product')
        products_db.save(self.db_filename)
        self.refresh_book()
        return 0

    def add_link_to_category(self, category, link, shop_site):
        if category not in self.get_categories():
            return -1

        try:
            products_db = xl_copy(self.read_stream)
            read_sheet = self.read_stream.sheet_by_name(category)
            write_sheet = products_db.get_sheet(category)

        except AttributeError: # File not exist or filesize 0 bytes (self.read_stream is None)
            return -1

        if link in read_sheet.col_values(self.link_column):
            return 0

        write_sheet.write(read_sheet.nrows, self.monitor_column, '1')
        write_sheet.write(read_sheet.nrows, self.link_column, link)
        write_sheet.write(read_sheet.nrows, self.shop_site_column, shop_site)
        products_db.save(self.db_filename)
        self.refresh_book()

    def get_monitor_links_from_category(self, category):
        if category not in self.get_categories():
            return -1

        try:
            read_sheet = self.read_stream.sheet_by_name(category)
        except AttributeError:
            return -2

        for row in range(1, read_sheet.nrows):#read_sheet.col_values(self.link_column)[1:]:
            if read_sheet.cell(row, self.monitor_column).value == '1':
                yield { 'link': read_sheet.cell(row, self.link_column).value,
                        'site': read_sheet.cell(row, self.shop_site_column).value,
                        'row': row }

    def get_date_column(self, sheet, date):
        if sheet.row_slice(0)[-1].value.strip() != date:
            return -1

        return len(sheet.row_slice(0))-1

    def find_product_row(self, sheet, shop, product):
        for row in range(1, sheet.nrows):
            if sheet.row_slice(row)[self.product_name_column].value == product and \
                    sheet.row_slice(row)[self.shop_site_column].value == shop:
                return row

        return -1

    def get_categories(self):
        try:
            return self.read_stream.sheet_names()
        except AttributeError:
            return []

    def remove_category(self, category_name):
        if self.read_stream:
            try:
                new_workbook = xl_copy(self.read_stream)
                categories = []

                for category in new_workbook._Workbook__worksheets:
                    if category_name != category.name:
                        categories.append(category)

                if not categories:
                    os.remove(self.db_filename)
                else:
                    new_workbook._Workbook__worksheets = categories
                    new_workbook.save(self.db_filename)
                self.refresh_book()

            except AttributeError: # self.read_stream is None
                return -1

        return 0

    def refresh_book(self):
        try:
            self.read_stream = xlrd.open_workbook(self.db_filename)
        except FileNotFoundError:
            self.read_stream = None
            return -1
        
        return 0

