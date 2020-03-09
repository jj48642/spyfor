
use "https://stats.idre.ucla.edu/stat/stata/examples/greene/TBL5-1.DTA", clear
python: import spyfor

python: output_path = "E:\\test_tables\\test_table.xlsx"
python: output = spyfor.workbook.tableWorkBook(output_path)

qui reg y1 x1
python: output.capture_regression_information()
qui reg y1 x1 x2
python: output.capture_regression_information()
python: output.compile_worksheet()
qui reg y2 x1 x3
python: output.capture_regression_information()
qui reg y2 x1 x2 x3
python: 
output.capture_regression_information()
output.compile_worksheet()
output.print_workbook()

