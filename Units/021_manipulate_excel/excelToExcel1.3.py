#encoding:utf-8  

import xlwings as xw
import os
import numpy as np

'''
path_file1 = r'/Users/zhanpengyi/Desktop/excel'
path_file2 = r'/Users/zhanpengyi/Desktop/excel/output'

file_list = os.listdir(path_file1)
for i in file_list:
  if i.startswith('~$'):
    continue
  changeFormat(i,i_01)
'''


def changeFormat(fileName1,fileName2):
#  filepath1 = os.path.join(path_file,i)
#    filepath1 = r'fileName1.xlsx'

#转换前的excel文件夹路径
    path_file = r'/Users/zhanpengyi/Library/Containers/com.microsoft.Excel/Data/excelTestFolder'
#模板excel所在文件夹路径
#    path_file1= r'/Users/zhanpengyi/Desktop/excel'
#转换后的excel文件夹路径
    path_file2 = r'/Users/zhanpengyi/Desktop/excel/output'
    
    filepath1 = os.path.join(path_file,fileName1)
    app=xw.App(visible=False,add_book=False)
    wb=app.books.open(filepath1)

    sheet_1 = wb.sheets[0]
    
#    filepath2 = os.path.join(path_file1,'小票PDF转Excel.xlsx')
#    wb2 = app.books.open(filepath2)
#    sheet_2 = wb2.sheets[0]

#直接新建不打开文件
    wb2 = app.books.add()
    sheet_2 = wb2.sheets[0]
    
    def writeInNewSheet(a,b): # a 是原excel中的数据编号， b是要写入的excel的表格编号
        tempvalue = sheet_1.range(a).value
        sheet_2.range(b).value = tempvalue
        
    def advanceWriteInNewSheet(a,b,c,d): # a，b 是原excel中一行数据的开头和结尾编号， c，d是要写入的excel的表格编号
        tempvalue = sheet_1.range(a+':'+b).value
        sheet_2.range(c+':'+d).value = tempvalue
#写入文件名
    writeInNewSheet('J1','A6')
    finalArray=[]
    for i in range(2,22):
        strStart = 'D'+str(i);
        strEnd = 'F'+str(i)
#        print('start is ',strStart)
        tempArray = sheet_1.range(strStart +':'+strEnd).value
        finalArray = np.concatenate((finalArray,tempArray),axis=0)
#    print ('Array is', finalArray)

    finalArray= np.append(finalArray,sheet_1.range('C24').value)
    finalArray= np.append(finalArray,sheet_1.range('E24').value)
    finalArray= np.append(finalArray,sheet_1.range('I24').value)
    finalArray= np.append(finalArray,sheet_1.range('C25').value)
    
    sheet_2.range('J6:BU6').value = finalArray
#养老保险
#   writeInNewSheet('D2','J6')
#   writeInNewSheet('E2','K6')
#   writeInNewSheet('F2','L6')
#    advanceWriteInNewSheet('D2','F2','J6','L6')
#    tempvalue = sheet_1.range('D2:F2').value
#    print('tempvalue is ',tempvalue)
#    sheet_2.range('J6:L6').value = tempvalue

#开票人
#    writeInNewSheet('C24','BR6')

#部门
#    writeInNewSheet('E24','BS6')

#开票日期   
#    writeInNewSheet('H24','BT6')
    
#备注   
#    writeInNewSheet('C25','BU6')

    filepath3 = os.path.join(path_file2,'./output'+fileName2)
    print('filepath3 is ',filepath3)
    wb2.save(filepath3)

    print('the xls file saved')
    
    wb.close()
    wb2.close()
    app.quit()
    
if __name__ == "__main__":
#输入excel的文件夹路径 MAC必须放在此路径下
    path_file1 = r'/Users/zhanpengyi/Library/Containers/com.microsoft.Excel/Data/excelTestFolder'
    #path_file2 = r'/Users/zhanpengyi/Desktop/excel/output'

    file_list = os.listdir(path_file1)
    file_list.sort()
    for i in file_list:
      if i.startswith('~$'):
        continue
      print('the file name is ',i)
      if i.endswith('xls'):
         changeFormat(i,i)
    #changeFormat('成都105  09.xlsx','2022.xlsx')
 
