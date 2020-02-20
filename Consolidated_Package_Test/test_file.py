import copy
import re
import pandas as pd
from sfi import Matrix as mat
from sfi import Scalar as sca
import xlsxwriter as xl


class PrintRegressions:
    def __init__(self, reg_obj, print_workbook, sheet_title, sheet_sub_title, df_appendix=None, display_control=False,
                 display_se=False):
        self.worksheet = print_workbook.add_worksheet(name=sheet_title)
        self.format_dict = {'font_name': 'Times New Roman', 'align': 'left', 'font_size': 12}
        self.workbook = print_workbook
        self.reg_obj = reg_obj
        self.reg_count = len(self.reg_obj.res)
        self.title = sheet_title
        self.sub_title = sheet_sub_title
        self.sheet_width = (self.reg_count * 3) + 1
        self.x = 1
        self.y = 1
        self.df_appendix = df_appendix
        self.display_order, self.display_names = self.process_appendix(df_appendix)

        self.display_control = display_control
        self.display_se = display_se
        if self.display_se:
            self.spacer = 4
        else:
            self.spacer = 3
        # = appendix

        self.print_titles()
        self.print_header_row()
        self.print_parameters()

        self.print_other_info()
        self.worksheet.set_column(self.x + 1, self.x + 1, options={'hidden': True})

    # processes the appendix into dictionaries that aid in the printing process
    def process_appendix(self, df_appendix):
        """Convert Dataframe Appendix into lookup dictionaries"""
        display_list = self.reg_obj.variables_of_interest + self.reg_obj.controls
        df_parameters = pd.DataFrame(data=display_list, columns=['Variable'])

        # If the code is passed an appendix for ordering then the display order is determined
        # by the appendix order.  If there is no appendix provided then the code just uses
        # the order in which they are stored in memory.
        if df_appendix is not None:
            df_parameters['merge_var'] = df_parameters['Variable'].str.lower()
            df_appendix['merge_var'] = df_appendix['Variable_Name'].str.lower()
            df_mapping = df_parameters.merge(df_appendix, how='left', left_on='merge_var', right_on='merge_var')
            df_placement = df_mapping.sort_values(by=['Order']).reset_index()
            df_placement['id'] = df_placement.index
        else:
            df_placement = df_parameters
            df_placement['id'] = df_placement.index
            df_mapping = df_parameters
            df_mapping['Display_Name'] = df_mapping['Variable']

        df_placement = df_placement[['Variable', 'id']]
        dict_placement = df_placement.set_index('Variable').T.to_dict('list')

        df_name = df_mapping[['Variable', 'Display_Name']]
        dict_display = df_name.set_index('Variable').T.to_dict('list')

        return dict_placement, dict_display

    def print_titles(self):
        """Print Titles onto the Workbook"""
        title_format = self.workbook.add_format({'bold': True, "align": 'center', 'font_name': 'Times New Roman',
                                                 'font_size': 20})
        sub_title_format = self.workbook.add_format({'bold': True, "align": 'center', 'font_name': 'Times New Roman',
                                                     'font_size': 12})
        self.worksheet.merge_range(self.y, self.x, self.y, self.x + self.sheet_width, self.title, title_format)
        self.y += 1
        self.worksheet.merge_range(self.y, self.x, self.y, self.x + self.sheet_width, self.sub_title, sub_title_format)
        self.y += 2

    def print_header_row(self):
        """Prints the header row on the workbook"""
        header_dict = copy.deepcopy(self.format_dict)
        header_dict.update({'bottom': True, 'top': True, "align": 'center'})
        header_fromat = self.workbook.add_format(header_dict)

        self.worksheet.write(self.y, self.x, "Parameters", header_fromat)
        self.worksheet.set_column(self.x, self.x, 30)
        self.worksheet.write(self.y, self.x + 1, "Coding_Name", header_fromat)
        self.worksheet.set_column(self.x + 1, self.x + 1, 30)

        for i in range(0, self.reg_count):
            self.worksheet.write(self.y, self.x + 2 + (i * self.spacer), "(" + str(i + 1) + ")", header_fromat)
            sig_column = self.x + 3 + (i * self.spacer)
            self.worksheet.write(self.y, sig_column, "", header_fromat)
            self.worksheet.set_column(sig_column, sig_column, 5)
            if self.display_se:
                self.worksheet.write(self.y, self.x + 4 + (i * self.spacer), "", header_fromat)
                spacer_column = self.x + 5 + (i * self.spacer)
            else:
                spacer_column = self.x + 4 + (i * self.spacer)
            self.worksheet.write(self.y, spacer_column, "", header_fromat)
            self.worksheet.set_column(spacer_column, spacer_column, 1)
        self.y += 1

    def print_parameters(self):
        """Print Parameter names along with coefficients onto the workbook"""
        param_dict = copy.deepcopy(self.format_dict)
        param_dict.update({'num_format': '#,##0.000', 'align': 'right'})
        param_format = self.workbook.add_format(param_dict)
        display_format = self.workbook.add_format(self.format_dict)
        # prints the labels for the table
        for param in self.display_order:
            y_loc = self.display_order[param][0] + self.y
            # In the case where the paramter does not exists in the appendix the code just writes the
            # coding name in the cell to ensure that it does not error out
            try:
                self.worksheet.write(y_loc, self.x, self.display_names[param][0], display_format)
            except TypeError:
                self.worksheet.write(y_loc, self.x, param, display_format)
            self.worksheet.write(y_loc, self.x + 1, param, display_format)
        # prints coefficients
        paramx = self.x + 2
        for res in self.reg_obj.res:
            dict_pvalues = res.pvalues.to_dict()
            dict_se = res.std_errors
            for param in res.params.iteritems():
                try:
                    paramy = self.y + self.display_order[param[0]][0]
                except KeyError:
                    continue

                self.worksheet.write(paramy, paramx, param[1], param_format)
                print(param[0])
                p_value = dict_pvalues[param[0]]
                if p_value < .01:
                    stars = "***"
                elif p_value < .05:
                    stars = "**"
                elif p_value < .1:
                    stars = "*"
                else:
                    stars = ""
                self.worksheet.write(paramy, paramx + 1, stars, display_format)
                if self.display_se:
                    self.worksheet.write(paramy, paramx + 2, dict_se[param[0]], param_format)
                # for parameter in res.
            paramx += self.spacer

        if self.display_control is False:
            for control in self.reg_obj.controls:
                control_row = self.display_order[control][0] + self.y
                self.worksheet.set_row(control_row, control_row, options={'hidden': True})

        self.y += len(self.display_names) + 1

    def print_other_info(self):
        """Prints regression information such as fixed effects, samples size etc. onto the workbook"""
        label_format = self.workbook.add_format(self.format_dict)

        other_dict = copy.deepcopy(self.format_dict)
        other_dict.update({'align': 'right'})
        other_format = self.workbook.add_format(other_dict)
        effects_list = []

        # Creates a list of unique fixed effects for formatting purposes
        for res in self.reg_obj.res:
            effects_list.append(res.included_effects)

        df_effects = pd.DataFrame(effects_list)
        df_effects = pd.melt(df_effects)
        df_effects = df_effects.groupby('value', as_index=False).count()
        df_effects['id'] = df_effects.index
        df_effects = df_effects[['value', 'id']]
        effects = df_effects.set_index('value').T.to_dict('list')

        # printing the Fixed effects indicator variables
        self.worksheet.write(self.y, self.x, "Fixed Effects", label_format)
        self.y += 1
        for item in effects:
            text = item
            if 'cik' in text.lower():
                text = "Firm"
            elif 'time' in text.lower():
                text = "Year"
            elif 'sic' in text.lower():
                text = 'SIC'
            self.worksheet.write(self.y + effects[item][0], self.x, text, label_format)
        effectx = self.x + 2
        for res in self.reg_obj.res:
            res_effects = res.included_effects
            for item in effects:
                if item in res_effects:
                    print_text = "Included"
                else:
                    print_text = "Not Included"
                self.worksheet.write(self.y + effects[item][0], effectx, print_text, other_format)
            effectx += self.spacer
        self.y += len(effects) + 1

        # Printing Descriptive Information

        obs_form_dict = copy.deepcopy(self.format_dict)
        obs_form_dict.update({'num_format': '#,##0', 'align': 'right'})
        obs_format = self.workbook.add_format(obs_form_dict)

        fit_form_dict = copy.deepcopy(self.format_dict)
        fit_form_dict.update({'num_format': '#,##0.000', 'align': 'right'})
        fit_format = self.workbook.add_format(fit_form_dict)

        self.worksheet.write(self.y, self.x, "Number of Observations", label_format)
        self.worksheet.write(self.y + 1, self.x, "Number of Clusters", label_format)
        self.worksheet.write(self.y + 3, self.x, "R-Square", label_format)
        desx = self.x + 2
        for res in self.reg_obj.res:
            self.worksheet.write(self.y, desx, res.nobs, obs_format)
            self.worksheet.write(self.y + 1, desx, res.entity_info['total'], obs_format)
            self.worksheet.write(self.y + 3, desx, res.rsquared_between, fit_format)
            desx += self.spacer


class RegObject:
    def __init__(self, res_list, interest, controls):
        self.res = res_list
        self.variables_of_interest = list(dict.fromkeys([x.lower() for x in interest]))

        # This avoids errors in the formatter to make sure that there is no overlap of variables of
        # interest and control variables
        self.controls = []
        for item in list(dict.fromkeys([x.lower() for x in controls])):
            if item not in self.variables_of_interest:
                self.controls.append(item)

        # creating a unique list of all parameters used in all of the specifications that are grouped together in case
        # they are not specified as interest or control variables.  I will treat all variables not specified as a
        # variable of interest as a control variable for presentation purposes.
        for output in self.res:
            for var in output.param_names:
                if var not in self.variables_of_interest and var not in self.controls and "." not in var and var != "_cons":
                    self.controls.append(var)

    def print_res(self, file_dir):
        with open(file_dir, 'w') as f:
            for item in self.res:
                f.write(str(item))


class res_obj:
    def __init__(self):
        table_matrix = mat.get("r(table)")
        rows = mat.getRowNames("r(table)")

        self.param_names = mat.getColNames("r(table)")

        coefficient_row = rows.index("b")
        self.params = pd.Series(table_matrix[coefficient_row], index=self.param_names)

        p_value_row = rows.index("pvalue")
        self.pvalues = pd.Series(table_matrix[p_value_row], index=self.param_names)

        std_row = rows.index("se")
        self.std_errors = pd.Series(table_matrix[std_row], index=self.param_names)

        self.nobs = sca.getValue("e(N)")
        self.entity_info = pd.Series([sca.getValue("e(N_clust)")], index=['total'])
        self.rsquared_between = sca.getValue("e(r2)")
        if self.rsquared_between is None:
            self.rsquared_between = sca.getValue("e(r2_p)")

        time_binary = False
        entity_binary = False
        sic_binary = False
        for param in self.param_names:
            if re.search("\D{4}\.*year*", param.lower()):
                time_binary = True

            if re.search("\D{2,12}\.*cik*", param.lower()):
                entity_binary = True
            if re.search("\D{2,12}\.*sic*", param.lower()):
                sic_binary = True

        self.included_effects = []
        if time_binary:
            self.included_effects.append('time')
        if entity_binary:
            self.included_effects.append('cik')
        if sic_binary:
            self.included_effects.append('sic')


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


