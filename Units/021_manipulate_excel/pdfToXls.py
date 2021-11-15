#encoding:utf-8  

# -*- coding: utf-8 -*-
"""
请确保你在运行这个代码的时候，已经安装了pdfplumber库
如果没有安装，请在[附件-命令提示符]下输入：
pip install pdfplumber
pip install xlwt
"""

import pdfplumber
import xlwt
import os

def chagePDFtoExcel(filePath,excelFileName):
    #path = input("请输入PDF文件位置：")    
#    path = "成都航天微电09三次+机电工程（派遣2 武汉）09（机电工程）09+上海神软09&（成都）09+ 海鹰机电（天津）（异地）09_Part5.PDF"  # 导入PDF路径
    pdf = pdfplumber.open(filePath)
    print('开始读取数据')
    for page in pdf.pages:
        # 获取当前页面的全部文本信息，包括表格中的文字
#        text = page.extract_text(x_tolerance=1, y_tolerance=1)
#        print('text is',text)
        strPagenumber = str(page.page_number)
        print('the page number is ', page.page_number)
        for table in page.extract_tables():
            print(table)
            workbook = xlwt.Workbook()  #定义workbook
            sheet = workbook.add_sheet('Sheet1')  #添加sheet
            i = 0 # Excel起始位置
            for row in table:            
                print(row)
                for j in range(len(row)):
                    sheet.write(i, j, row[j])
                i += 1
            print('---------- 分割线 ----------')
            sheet.write(0,9, excelFileName+'pagenumber'+strPagenumber)

#输出excel路径            
            path_file1 = r'/Users/zhanpengyi/Desktop/excel/PDFoutputs'
            filepath3 = os.path.join(path_file1,excelFileName+'.pagenumber'+strPagenumber+'.xls')
            workbook.save(filepath3)
    pdf.close()
#    workbook.save('PDFresult.xls')
    print('\n')
    print('写入excel成功')
    print('保存位置：')
    print('PDFresult.xls')
    print('\n')
#    input('PDF取读完毕，按任意键退出')

#输入excel路径
path_file1 = r'/Users/zhanpengyi/Desktop/excel/PDFinputs'
file_list = os.listdir(path_file1)
for i in file_list:
  if i.startswith('~$'):
    continue
  print('the file name is ',i)
  if i.endswith('pdf'):
    filepath1 = os.path.join(path_file1,i)      
    chagePDFtoExcel(filepath1,i)

'''
    # 保存文件为一整个Excel表
    path_file1 = r'/Users/zhanpengyi/Desktop/excel/PDFinputs'
    filepath3 = os.path.join(path_file1,excelFileName+'.xls')
    workbook.save(filepath3)
'''
