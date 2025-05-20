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
#缓存文件读写
import json


#全局变量
Shaders_name_ = 'hello python - global'

# 缓存文件路径，保存翻译过的文本及其译文，防止重复翻译
CACHE_FILE = "./translation_cache.json"

#判断文件是否存在
def check_file_path(path):
    if not os.path.exists(path):
        print("找不到文件 " + path)
        return 0
    return 1


def Move_func(path):
    #全局化文件名
    global Shaders_name_
    #文件路径处理
    path = path.replace('\\','/')
    path = path.replace('"','')
    #path = os.path.join(path)
    print(path)
    if check_file_path(path):
        #获取光影文件名
        Shaders_name = path.split("/")[-1].replace('"', "")[:-4]
        Shaders_name_ = Shaders_name
        print("文件名为：" + Shaders_name)
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
        File_read_func(Shaders_name)


def File_read_func(Shaders_name):
    path = "./Temp/Zip/shaders/lang/en_US.lang"

    with open(path, 'r', encoding="utf-8") as file:
        lines = file.readlines()
        print(f"共读取 {len(lines)} 行")

    translated_lines = Translation_func(lines)

    # 将译文写回原文件
    with open(path, 'w', encoding="utf-8") as file:
        file.write('\n'.join(translated_lines))

    print("翻译完成并已写回原文件。")
    zip_folder('./Temp/Zip', './Temp/' + Shaders_name + '_zh.zip')
    print("文件已压缩")


#单行翻译原始代码
'''
def Translation_func(lines):
    translated_lines = []
    total = len(lines)

    for idx, line in enumerate(lines):
        line = line.replace('搂', '§')  # 修复乱码为§

        if '=' in line:
            key, value = line.split('=', 1)
            original_value = value.strip()

            # 提取 §x 控制符（如 §a）
            color_codes = re.findall(r'§.', original_value)
            text_only = re.sub(r'§.', '', original_value)

            try:
                translated_text = GoogleTranslator(source='en', target='zh-CN').translate(text_only)

                rebuilt_text = ''.join(color_codes) + translated_text
                translated_line = f"{key.strip()}={rebuilt_text}"

                percent = (idx + 1) / total * 100
                print(f"[{percent:.1f}%] 原文: {original_value} → 译文: {rebuilt_text}")

                translated_lines.append(translated_line)
            except Exception as e:
                print(f"[{(idx + 1) / total * 100:.1f}%] 翻译出错：{e}")
                translated_lines.append(line)
        else:
            translated_lines.append(line)

    return translated_lines
'''

#改进后的翻译模块
def load_cache():
    """
    从本地JSON文件加载翻译缓存。
    如果缓存文件不存在或读取失败，返回空字典。
    """
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载缓存文件失败: {e}")
            return {}
    else:
        return {}

def save_cache(cache):
    """
    将翻译缓存字典保存到本地JSON文件。
    使用ensure_ascii=False保证中文不被转义，indent格式化输出。
    """
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存缓存文件失败: {e}")

def Translation_func(lines):
    """
    逐行翻译文本行列表，保留Minecraft格式颜色代码，使用本地缓存优化翻译效率。

    参数:
        lines (list[str]): 文件内容逐行文本列表。

    返回:
        list[str]: 翻译后文本列表。
    """
    translated_lines = []               # 存放翻译结果行
    translation_cache = load_cache()    # 加载本地缓存，格式：{原文: 译文}
    total = len(lines)                  # 总行数
    translated_count = 0                # 已翻译行数计数
    translator = GoogleTranslator(source='en', target='zh-CN')  # 初始化谷歌翻译器

    for idx, line in enumerate(lines):
        # 修复乱码，将错误字符替换成颜色符号 §
        line = line.replace('搂', '§')

        if '=' in line:
            # 拆分为key=value形式
            key, value = line.split('=', 1)
            value = value.strip()

            # 提取颜色代码及其在纯文本中的位置
            color_positions = []  # [(index_in_text, '§x'), ...]
            text_only = ''        # 去除颜色码后的纯文本
            i = 0
            while i < len(value):
                if value[i] == '§' and i + 1 < len(value):
                    # 记录颜色码位置（相对于纯文本的索引）
                    color_positions.append((len(text_only), value[i:i+2]))
                    i += 2
                else:
                    text_only += value[i]
                    i += 1

            # 尝试从缓存中读取翻译结果
            if text_only in translation_cache:
                translated_text = translation_cache[text_only]
            else:
                try:
                    # 调用Google翻译API进行翻译
                    translated_text = translator.translate(text_only)
                    # 防止返回None异常
                    if translated_text is None:
                        raise ValueError("翻译返回了 None")
                    # 缓存新翻译结果
                    translation_cache[text_only] = translated_text
                    # 每翻译一条就保存缓存，避免丢失
                    save_cache(translation_cache)
                except Exception as e:
                    print(f"[{(idx + 1) / total * 100:.1f}%] 翻译出错: {e}")
                    # 出错则保留原行，继续处理下一行
                    translated_lines.append(line)
                    continue

            # 将颜色码重新插入翻译后的文本对应位置
            try:
                text_list = list(translated_text)
                offset = 0
                for pos, code in color_positions:
                    # 计算插入位置，防止越界
                    insert_pos = min(pos + offset, len(text_list))
                    text_list.insert(insert_pos, code)
                    offset += len(code)  # 插入后偏移量增加
                rebuilt_text = ''.join(text_list)
            except Exception as e:
                print(f"[{(idx + 1) / total * 100:.1f}%] 颜色码插入出错: {e}")
                rebuilt_text = translated_text  # 出错则使用纯翻译文本

            # 组合成 key=翻译后的文本行
            translated_line = f"{key.strip()}={rebuilt_text}"
            translated_lines.append(translated_line)

            translated_count += 1
            percent = (translated_count / total) * 100
            print(f"[{percent:.1f}%] 原文: {text_only} → 译文: {rebuilt_text}")
        else:
            # 不含等号的行原样保留（比如空行、注释等）
            translated_lines.append(line)

    # 最终保存缓存（防止未及时保存）
    save_cache(translation_cache)

    return translated_lines


def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # os.walk递归遍历文件夹
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                # arcname保证压缩包里文件相对路径正确
                arcname = os.path.relpath(full_path, start=folder_path)
                zipf.write(full_path, arcname)
    print(f"文件夹 {folder_path} 已压缩为 {zip_path}")
    clean_temp_folder('./Temp/Zip')


def clean_temp_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        os.remove('./Temp/' + Shaders_name_ + '.zip')
        print(f"临时文件夹 {folder_path} 已删除。")
        print(f"临时文件夹 {Shaders_name_} 已删除。")
    except Exception as e:
        print(f"清理临时文件夹失败: {e}")
