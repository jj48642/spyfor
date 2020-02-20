
import importlib.util as test
# This object is created to carry along the variables of interest for display purposes

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
        params = []
        for output in self.res:
            for var in output.params:
                print("Variable: ", var)
                if var not in self.variables_of_interest and var not in self.controls:
                    self.controls.append(var)

    def print_res(self, file_dir):
        with open(file_dir, 'w') as f:
            for item in self.res:
                f.write(str(item))



