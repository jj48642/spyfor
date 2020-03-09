import re

import pandas as pd
import numpy as np
from sfi import Matrix as mat
from sfi import Scalar as sca


class corr:
    def __init__(self):
        pass

    @staticmethod
    def unpivot_stata_output(self, data_matrix, column_names, new_column_name):
        column_names = np.asarray(self.rows)
        df_return = pd.DataFrame(self.corr_matrix, columns=self.rows)
        df_return['col_names'] = column_names
        df_return = pd.melt(df_return, id_vars=['col_names'])
        df_return.rename({'value': new_column_name}, inplace=True)
        return df_return

    def unpivot_correlation(self):
        df_coefficients = self.unpivot_stata_output(self.corr_matrix, self.rows, 'coefficient')
        df_pvalues = self.unpivot_stata_output(self.pvalue_matrix, self.rows, 'p_value')

        df_return = df_coefficients.merge(df_pvalues, how='Left', left_on=['col_names', 'variable'], right_on=['col_names', 'variable'])

        return df_return


class spearman_obj(corr):
    def __init__(self):
        """Captures the output of the "spearman" command in Stata"""
        self.corr_matrix = mat.get("r(Rho)")
        self.pvalue_matrix = mat.get("r(P)")
        self.rows = mat.getRowNames("r(Rho)")

        self.df_values = self.unpivot_correlation()


class pearson_obj(corr):
    def __init__(self):
        """Captures the output of the "pwcorr <variables>, sig" command in Stata"""
        self.corr_matrix = mat.get("r(C)")
        try:
            self.pvalue_matrix = mat.get("r(sig)")
        except:
            print("Need to use pwcorr <variable>,sig for pvalues to be generated.  All P-Values set to 1")
            self.pvalue_matrix = 1
        self.df_values = self.unpivot_correlation()

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





