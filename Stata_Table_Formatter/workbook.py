import pandas as pd
import xlsxwriter as xl

from .Format_Regression_Output import PrintRegressions as PrintRegressions
from .Reg_Obj import RegObject as RegObject
from .Stata_Reg_Obj import res_obj as res_obj


class tableWorkBook:
    def __init__(self, print_directory, appendix_dir=None):
        if appendix_dir is not None:
            try:
                self.df_appendix = pd.read_csv(filepath_or_buffer=appendix_dir)
            except UnicodeDecodeError:
                try:
                    self.df_appendix = pd.read_csv(filepath_or_buffer=appendix_dir, encoding="ISO-8859-1")
                except:
                    self.df_appendix = None
                    print("Error Loading Appendix.  Proceeding with no Appendix")
        else:
            self.df_appendix = None
            print("No Appendix Loaded")

        self.workbook = xl.Workbook(print_directory)
        self.res_list = []
        self.sheet_counter = 1
        self.printer = None

    def capture_regression_information(self):
        """"Captures regression information from Stata and stores information in Python"""
        self.res_list.append(res_obj())

    def compile_worksheet(self, sheet_title=None, sheet_sub_title=None, display_control=True, display_se=False, interest_variables=[], control_variables=[]):
        """Compiles information from regressions into a worksheet and clears temporary regression storage"""
        if sheet_title is None:
            sheet_title = "Table " + str(self.sheet_counter)
        if sheet_sub_title is None:
            sheet_sub_title = "Insert Table Description Here"
        regression_object = RegObject(self.res_list, interest_variables, control_variables)
        self.printer = PrintRegressions(reg_obj=regression_object, print_workbook=self.workbook, sheet_title=sheet_title,
                         sheet_sub_title=sheet_sub_title, df_appendix=self.df_appendix,
                         display_control=display_control, display_se=display_se)
        # adds 1 to the sheet counter in case the user does not specifiy table names
        self.sheet_counter += 1

        # clears out the results list so that the list of specifications does not keep growing.
        self.res_list = []

    def print_workbook(self):
        """Prints the excel workbook to the specified filename"""
        self.workbook.close()



