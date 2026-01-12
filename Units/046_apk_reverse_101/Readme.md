## Requisite

1. APK
2. Jadx-GUI
[https://github.com/skylot/jadx]

3. Frida
4. Simulator without rooted environment

## Step
1.  Locate the onclick() function in APK
![[Pasted image 20251208115841.png]]
2. learn the code logic
```
table

一乙二十丁厂七卜人入 八九几儿了力乃刀又三
于干亏士工土才寸下大 丈与万上小口巾山千乞
川亿个勺久凡及夕丸么 广亡门义之尸弓己已子  //Ascii(5)=53,  Table[53]=义
卫也女飞刃习叉马乡丰 王井开夫天无元专云扎  //Ascii(8)=56,  Table[56]=弓
艺木五支厅不太犬区历 尤友匹车巨牙屯比互切
瓦止少日中冈贝内水见 午牛手毛气升长仁什片
仆化仇币仍仅斤爪反介 父从今凶分乏公仓月氏
勿欠风丹匀乌凤勾文六 方火为斗忆订计户认心
尺引丑巴孔队办以允予 劝双书幻玉刊示末未击
打巧正扑扒功扔去甘世 古节本术可丙左厉右石
布龙平灭轧东卡北占业 旧帅归且旦目叶甲申叮
电号田由史只央兄叼叫 另叨叹四生失禾丘付仗
代仙们仪白仔他斥瓜乎 丛令用甩印乐
```

3. Rewrite the script to read the logo file.
```
import os
import sys

def getCodesFromPic(filename='logo.png'):
    """
    从特定的 PNG 图片中读取隐藏的码表和加密字符串
    """
    if not os.path.exists(filename):
        print(f"错误: 找不到文件 {filename}")
        sys.exit(1)

    try:
        # 使用 'rb' (二进制模式) 读取图片
        with open(filename, 'rb') as f:
            v0 = f.read()
        
        # 检查文件大小是否足够，防止切片越界
        if len(v0) < 91265 + 18:
            print("错误: 图片文件过小，不是目标 CTF 文件。")
            return None, None

        # 提取码表 (Table)
        # 注意：读取出来的 v0 是 bytes 类型，切片后也是 bytes
        # 需要将其解码为字符串以便后续进行 find 操作
        # 在原题中，隐藏部分被设计为合法的 utf-8 字符，所以可以 decode
        table_bytes = v0[89473 : 89473 + 768]
        code_bytes = v0[91265 : 91265 + 18]

        try:
            table = table_bytes.decode('utf-8')
            pwdCode = code_bytes.decode('utf-8')
            return table, pwdCode
        except UnicodeDecodeError:
            print("错误: 指定位置的数据不是有效的 UTF-8 文本。")
            return None, None

    except Exception as e:
        print(f"发生未知错误: {e}")
        return None, None

def aliCodeToBytes(codeTable, strCmd):
    """
    解密逻辑：查表还原
    """
    pwd = ''
    try:
        for char in strCmd:
            # 在 codeTable 中找到 char 的索引位置
            index = codeTable.find(char)
            
            if index == -1:
                print(f"警告: 字符 '{char}' 不在码表中！")
                pwd += '?'
            else:
                # 索引值即为原始字符的 ASCII 码
                pwd += chr(index)
    except Exception as e:
        print(f"解密过程出错: {e}")
    
    return pwd

if __name__ == "__main__":
    print("--- 开始运行解密脚本 ---")
    
    # 1. 获取隐藏数据
    table, pwdCode = getCodesFromPic('logo.png')
    
    if table and pwdCode:
        print(f"成功提取码表长度: {len(table)}")
        print(f"成功提取密文: {pwdCode}")
        
        # 2. 执行解密
        decoded_pwd = aliCodeToBytes(table, pwdCode)
        
        print("\n---------------------------")
        print(f"解密结果 (Flag): {decoded_pwd}")
        print("---------------------------")
    else:
        print("提取失败，请确保目录下存在正确的 'logo.png' 文件。")

```
