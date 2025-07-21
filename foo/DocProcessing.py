# coding=utf-8

import os
import shutil
import zipfile
import re
import json
from deep_translator import GoogleTranslator

# -------------------- 全局配置 --------------------

# 翻译缓存文件路径，防止重复翻译
CACHE_FILE = "./translation_cache.json"

# 临时目录，用于解压、缓存中间文件
TEMP_DIR = "./Temp"
ZIP_DIR = os.path.join(TEMP_DIR, "Zip")

# lang 文件在压缩包内的相对路径
LANG_FILE_RELATIVE = os.path.join("shaders", "lang", "en_US.lang")

# 当前处理的光影包名称（用于清理临时文件）
Shaders_name_ = "hello python - global"


# -------------------- 工具函数 --------------------

def check_file_path(path):
    """
    检查指定路径的文件是否存在。
    返回 True 表示存在，False 表示不存在。
    """
    if not os.path.exists(path):
        print("找不到文件:", path)
        return False
    return True


# -------------------- 主入口函数：导入并处理光影包 --------------------

def Move_func(path):
    """
    主入口：复制、解压光影包并启动翻译流程。
    参数 path 为光影 zip 文件路径。
    """
    global Shaders_name_

    # 规范化路径，去除多余引号、反斜杠
    path = path.replace("\\", "/").replace('"', '')
    print("输入路径:", path)

    # 检查文件是否存在
    if not check_file_path(path):
        return

    # 提取光影包名称（去掉 .zip）
    Shaders_name = os.path.basename(path)[:-4]
    Shaders_name_ = Shaders_name
    print("文件名为:", Shaders_name)

    # 将 zip 文件复制到临时目录中
    dst_path = TEMP_DIR
    print("*复制光影包文件到程序目录")
    shutil.copy(path, dst_path)

    print("Hello:", path)
    Unzip_func(path, Shaders_name)


# -------------------- 解压并读取语言文件 --------------------

def Unzip_func(path, Shaders_name):
    """
    解压光影 zip 文件到 ./Temp/Zip 目录，并启动翻译流程。
    """
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(ZIP_DIR)
        print("*ZIP文件解压完成，读取文件内容")
        File_read_func(Shaders_name)


# -------------------- 读取语言文件、翻译、写回 --------------------

def File_read_func(Shaders_name):
    """
    读取解压后的 en_US.lang 文件，执行翻译，并将翻译结果写回。
    同时重新打包为 *_zh.zip。
    """
    lang_path = os.path.join(ZIP_DIR, LANG_FILE_RELATIVE)

    # 检查 lang 文件是否存在
    if not os.path.exists(lang_path):
        print("找不到语言文件:", lang_path)
        return

    # 读取语言文件所有行
    with open(lang_path, 'r', encoding="utf-8") as file:
        lines = file.readlines()
        print(f"共读取 {len(lines)} 行")

    # 翻译文本行
    translated_lines = Translation_func(lines)

    # 写回原文件
    with open(lang_path, 'w', encoding="utf-8") as file:
        file.write('\n'.join(translated_lines))

    print("翻译完成并已写回原文件。")

    # 打包为新的 zip 文件
    zip_output = os.path.join(TEMP_DIR, f"{Shaders_name}_zh.zip")
    zip_folder(ZIP_DIR, zip_output)
    print("文件已压缩")


# -------------------- 翻译逻辑（含缓存、颜色码保留） --------------------

def load_cache():
    """
    加载本地翻译缓存。
    返回格式：{原文: 译文}
    """
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("加载缓存文件失败:", e)
    return {}


def save_cache(cache):
    """
    将翻译缓存保存回本地 JSON 文件。
    """
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("保存缓存文件失败:", e)


def Translation_func(lines):
    """
    执行逐行翻译。
    - 保留 Minecraft 颜色符号（§x）
    - 使用 Google 翻译 + 缓存机制
    """
    translated_lines = []
    translation_cache = load_cache()
    translator = GoogleTranslator(source='en', target='zh-CN')
    total = len(lines)

    for idx, line in enumerate(lines):
        # 修复乱码字符（替换为 §）
        line = line.replace('搂', '§')

        if '=' in line:
            # 拆分为 key=value 格式
            key, value = line.split('=', 1)
            value = value.strip()

            # 记录颜色控制符位置，并去除颜色符号
            color_positions = []  # [(纯文本位置, "§a")]
            text_only = ''
            i = 0
            while i < len(value):
                if value[i] == '§' and i + 1 < len(value):
                    color_positions.append((len(text_only), value[i:i + 2]))
                    i += 2
                else:
                    text_only += value[i]
                    i += 1

            # 查找缓存，或调用 Google 翻译
            if text_only in translation_cache:
                translated_text = translation_cache[text_only]
            else:
                try:
                    translated_text = translator.translate(text_only)
                    if translated_text is None:
                        raise ValueError("翻译返回 None")
                    translation_cache[text_only] = translated_text
                    save_cache(translation_cache)
                except Exception as e:
                    print(f"[{(idx + 1) / total * 100:.1f}%] 翻译出错: {e}")
                    translated_lines.append(line)
                    continue

            # 将颜色控制符插入翻译结果的指定位置
            try:
                text_list = list(translated_text)
                offset = 0
                for pos, code in color_positions:
                    insert_pos = min(pos + offset, len(text_list))
                    text_list.insert(insert_pos, code)
                    offset += len(code)
                rebuilt_text = ''.join(text_list)
            except Exception as e:
                print(f"[{(idx + 1) / total * 100:.1f}%] 颜色码插入出错: {e}")
                rebuilt_text = translated_text

            # 写入结果：key=翻译文本（含颜色码）
            translated_line = f"{key.strip()}={rebuilt_text}"
            translated_lines.append(translated_line)

            print(f"[{(idx + 1) / total * 100:.1f}%] 原文: {text_only} → 译文: {rebuilt_text}")
        else:
            # 非 key=value 格式（注释、空行等）原样保留
            translated_lines.append(line)

    # 最后保存一次缓存
    save_cache(translation_cache)
    return translated_lines


# -------------------- 压缩工具与清理 --------------------

def zip_folder(folder_path, zip_path):
    """
    将指定文件夹压缩为 zip 文件。
    - 保留文件相对路径结构
    - 压缩完成后清理临时文件夹
    """
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, start=folder_path)
                zipf.write(full_path, arcname)
    print(f"文件夹 {folder_path} 已压缩为 {zip_path}")
    clean_temp_folder(folder_path)


def clean_temp_folder(folder_path):
    """
    删除中间解压文件夹和原始 zip 文件（避免重复）。
    """
    try:
        shutil.rmtree(folder_path)
        zip_path = os.path.join(TEMP_DIR, Shaders_name_ + ".zip")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        print(f"临时文件夹 {folder_path} 已删除。")
    except Exception as e:
        print("清理临时文件夹失败:", e)
