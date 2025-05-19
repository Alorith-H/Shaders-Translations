# coding=utf-8

#Shutil函数实现文件复制操作
import shutil
#os函数
import os
#压缩包处理
import zipfile
#本地翻译
import re
from deep_translator import GoogleTranslator


#判断文件是否存在
def check_file_path(path):
    if not os.path.exists(path):
        print("找不到文件 " + path)
        return 0
    return 1


def Move_func(path):
    #文件路径处理
    path = path.replace('\\','/')
    path = path.replace('"','')
    #path = os.path.join(path)
    print(path)
    if check_file_path(path):
        #获取光影文件名
        Shaders_name = path.split("\\")[-1].replace('"', "")
        print(Shaders_name)
        # 定义源文件和目标文件的路径
        src_path = path
        dst_path = "./Temp/"
        # 使用shutil模块复制文件
        print("*复制光影包文件到程序目录")
        shutil.copy(src_path, dst_path)
        print("Hello :", path)
        Unzip_func(path,Shaders_name)
    else:
        pass


def Unzip_func(path,Shaders_name):
    with zipfile.ZipFile(path, 'r') as zip_ref:
        #解压文件到指定目录
        zip_ref.extractall('./Temp/Zip')
        print("*ZIP文件解压完成,读取文件内容")
        File_read_func()


def File_read_func():
    path = "./Temp/Zip/shaders/lang/en_US.lang"

    with open(path, 'r', encoding="utf-8") as file:
        lines = file.readlines()
        print(f"共读取 {len(lines)} 行")

    translated_lines = Translation_func(lines)

    # 将译文写回原文件
    with open(path, 'w', encoding="utf-8") as file:
        file.write('\n'.join(translated_lines))

    print("翻译完成并已写回原文件。")

def Translation_func(lines):
    translated_lines = []

    for line in lines:
        line = line.replace('搂', '§')  # 修复乱码为§

        if '=' in line:
            key, value = line.split('=', 1)
            original_value = value.strip()

            # 提取 §x 控制符（如 §a）
            color_codes = re.findall(r'§.', original_value)
            text_only = re.sub(r'§.', '', original_value)

            try:
                translated_text = GoogleTranslator(source='en', target='zh-CN').translate(text_only)

                # 简单合并所有颜色码（可改为高级保留原位）
                rebuilt_text = ''.join(color_codes) + translated_text
                translated_line = f"{key.strip()}={rebuilt_text}"
                print(f"原文: {original_value} → 译文: {rebuilt_text}")
                translated_lines.append(translated_line)

            except Exception as e:
                print(f"翻译出错：{e}")
                translated_lines.append(line)
        else:
            translated_lines.append(line)

    return translated_lines