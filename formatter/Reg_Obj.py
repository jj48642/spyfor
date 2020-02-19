
import importlib.util as test
# This object is created to carry along the variables of interest for display purposes

class RegObject:
    def __init__(self, res_list, interest, controls):
        self.res = res_list
        self.variables_of_interest = list(dict.fromkeys([x.lower() for x in interest]))

        # This avoids errors in the formatter to make sure that there is no overlap of variables of
        # interest and control variables
        self.controls = []
        for item in list(dict.fromkeys([x.lower() for x in  controls])):
            if item not in self.variables_of_interest:
                self.controls.append(item)

    def print_res(self, file_dir):
        with open(file_dir, 'w') as f:
            for item in self.res:
                f.write(str(item))



