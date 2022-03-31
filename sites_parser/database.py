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

        if not sheet_read.cell(product_row, self.product_name_column).value or \
                sheet_read.cell(product_row, self.product_name_column).value == 'Error':
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

    def set_monitor_in_row(self, category, row):
        if category not in self.get_categories():
            return -1

        if type(row) is not int:
            return -2

        products_db = xl_copy(self.read_stream)
        read_sheet = self.read_stream.sheet_by_name(category)
        write_sheet = products_db.get_sheet(category)

        if row < 1 or row > read_sheet.nrows:
            return -4
        
        mon_value = read_sheet.row(row)[0].value
        if not mon_value:
            return -5
        
        if mon_value == '0':
            write_sheet.write(row, self.monitor_column, '1')
        else:
            write_sheet.write(row, self.monitor_column, '0')
        
        products_db.save(self.db_filename)
        self.refresh_book()

        return 0

    def delete_row(self, category, row):
        if category not in self.get_categories():
            return -1

        if type(row) is not int:
            return -2

        products_db = xl_copy(self.read_stream)
        read_sheet = self.read_stream.sheet_by_name(category)
        write_sheet = products_db.get_sheet(category)

        if row < 1 or row >= read_sheet.nrows:
            return -3

        for col_i in range(read_sheet.ncols):
            write_sheet.write(row, col_i, '')

        products_db.save(self.db_filename)
        self.refresh_book()

        return 0

    def sheet_compress(self, category):
        if category not in self.get_categories():
            return -1

        products_db = xl_copy(self.read_stream)
        read_sheet = self.read_stream.sheet_by_name(category)
        write_sheet = products_db.get_sheet(category)
        stack_rows = []

        for row_i in range(1, read_sheet.nrows):
            if read_sheet.row(row_i)[0].value:
                stack_rows.append(row_i)

        cur_row = 1
        for row_i in stack_rows:
            if cur_row != row_i:
                for col_i, value in enumerate(read_sheet.row(row_i)):
                    write_sheet.write(cur_row, col_i, value.value)
                    write_sheet.write(row_i, col_i, '') # delete old row

            cur_row += 1

        products_db.save(self.db_filename)
        self.refresh_book()

        return 0

    def get_monitor_links_from_category(self, category):
        if category not in self.get_categories():
            return -1

        try:
            read_sheet = self.read_stream.sheet_by_name(category)
        except AttributeError:
            return -2

        for row in range(1, read_sheet.nrows):#read_sheet.col_values(self.link_column)[1:]:
            if read_sheet.cell(row, self.monitor_column).value == '1':
                yield { 
                    'link': read_sheet.cell(row, self.link_column).value,
                    'site': read_sheet.cell(row, self.shop_site_column).value,
                    'row': row
                }

    def get_products_names_from_category(self, category):
        if not self.read_stream or category not in self.get_categories():
            return []

        read_sheet = self.read_stream.sheet_by_name(category)
        return read_sheet.col_values(self.product_name_column)[1:]

    def get_dates_from_category(self, category):
        if not self.read_stream or category not in self.get_categories():
            return []

        read_sheet = self.read_stream.sheet_by_name(category)
        return read_sheet.row_values(0)[self.data_offset:]

    def get_date_column(self, category, date):
        if category.row_slice(0)[-1].value.strip() != date:
            return -1

        return len(category.row_slice(0))-1

    def get_product_prices(self, category, product_name):
        if not self.read_stream or category not in self.get_categories():
            return []

        read_sheet = self.read_stream.sheet_by_name(category)
        
        row = self.find_product_row(category, product_name)
        if row < 1: # 0 row contain dates
            return []

        return read_sheet.row_values(row)[self.data_offset:]

    def get_categories(self):
        try:
            return self.read_stream.sheet_names()
        except AttributeError:
            return []

    def get_row_info_slice(self, category, row_index):
        if category not in self.get_categories():
            return None

        read_sheet = self.read_stream.sheet_by_name(category)

        if row_index < 1 or row_index >= read_sheet.nrows:
            return None

        return tuple([elem.value for elem in read_sheet.row_slice(row_index)[:self.data_offset]])

    def get_category_nrows(self, category):
        if category not in self.get_categories():
            return -1

        read_sheet = self.read_stream.sheet_by_name(category)
        return read_sheet.nrows

    def find_product_row(self, category, product_name):
        if not self.read_stream:
            return -1

        category = self.read_stream.sheet_by_name(category)

        for row in range(1, category.nrows):
            if category.row_slice(row)[self.product_name_column].value == product_name:
                return row

        return -1

    def remove_category(self, category):
        if self.read_stream:
            try:
                new_workbook = xl_copy(self.read_stream)
                categories = []

                for category in new_workbook._Workbook__worksheets:
                    if category != category.name:
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

