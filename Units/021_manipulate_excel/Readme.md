### Readme
> Author: Pengyi
> Date:15 Nov 2021

##### 安装环境
> python3
> xlwings
> xlwt
> PDFplumber
> numpy
> xlrd
> xlwt

##### 命名原则
> 只包含一页的PDF，excel会遵循 output + “PDF原名” + pagenumber1 +xls的格式。
> 包含多页的PDF，会自动将多页拆分为单独的excel文件，遵循同样命名原则，通过名称中“pagenumber X”可以判断出是哪一页的内容。

##### 适用PDF
> PDF中的表格为20行，表格为20行（包含养老、失业、工商、生育、医疗、大病、社保小计、住房公积金、补充公积金、公积金小计、残保金、企业年金、滞纳金、代收工资、年终奖、小计、服务费、税费、合计、服务费合计共20行），可以正确转换为excel。
> PDF中的表格不为20行（例如多一行报销等），或者表格中为20行但不按照以上顺序排列的，则生成的Excel文件中数字会出现错行，需要后续手动修正。

##### 备注
> 暂时无法识别PDF中表格上的文字内容，需要手续手动填写。

##### 使用说明
> PDFToXls.py 可将一页或多页PDF逐页识别，并将每一页PDF转换为具有一个sheet的xls文件。
> PDFplumber目前只能提取table里的内容

> excelToExcel1.3 可批量将excel中表格内容转换位置 excel文件A中C5的内容 复制粘贴到 excel文件B中D6的内容

> mergeTest 可批量合并n个excel中的同一行，存入同一个文件内