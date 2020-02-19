from sfi import Matrix as mat
from sfi import Scalar as sca
import pandas as pd
import re

class res_obj:
    def __init__(self):
        table_matrix = mat.get("r(table)")
        rows = mat.getRowNames("r(table)")

        param_names = mat.getColNames("r(table)")

        coefficient_row = rows.index("b")
        self.params = pd.Series(table_matrix[coefficient_row], index=param_names)

        p_value_row = rows.index("pvalue")
        self.pvalues = pd.Series(table_matrix[p_value_row], index=param_names)

        std_row = rows.index("se")
        self.std_errors = pd.Series(table_matrix[std_row], index=param_names)

        self.nobs = sca.getValue("e(N)")
        self.entity_info = pd.Series([sca.getValue("e(N_clust)")], index=['total'])
        self.rsquared_between = sca.getValue("e(r2)")
        if self.rsquared_between is None:
            self.rsquared_between = sca.getValue("e(r2_p)")

        time_binary = False
        entity_binary = False
        sic_binary = False
        for param in param_names:
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





