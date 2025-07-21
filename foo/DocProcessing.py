# DocProcessing.py（精简示例）
import os
import shutil
import zipfile
import json
import re
from deep_translator import GoogleTranslator

CACHE_FILE = "./translation_cache.json"
Shaders_name_ = ''

def Move_func(path, log=print):
    global Shaders_name_
    path = path.replace('\\','/').replace('"','')
    log(f"📄 读取路径: {path}")

    if not os.path.exists(path):
        log(f"❌ 文件不存在: {path}")
        return

    Shaders_name = os.path.basename(path)[:-4]
    Shaders_name_ = Shaders_name
    log(f"📦 文件名: {Shaders_name}")

    dst = "./Temp/"
    os.makedirs(dst, exist_ok=True)
    shutil.copy(path, dst)
    log("✅ 复制文件完成")

    Unzip_func(path, Shaders_name, log)

def Unzip_func(path, Shaders_name, log=print):
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall('./Temp/Zip')
        log("🗜️ 解压完成")
    File_read_func(Shaders_name, log)

def File_read_func(Shaders_name, log=print):
    lang_path = "./Temp/Zip/shaders/lang/en_US.lang"
    if not os.path.exists(lang_path):
        log("❌ 找不到语言文件")
        return

    with open(lang_path, 'r', encoding="utf-8") as f:
        lines = f.readlines()
    log(f"📖 读取 {len(lines)} 行")

    translated = Translation_func(lines, log)

    with open(lang_path, 'w', encoding="utf-8") as f:
        f.write('\n'.join(translated))
    log("✅ 写回翻译文件完成")

    zip_folder('./Temp/Zip', f'./Temp/{Shaders_name}_zh.zip', log)

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except:
        pass

def Translation_func(lines, log=print):
    translated_lines = []
    cache = load_cache()
    translator = GoogleTranslator(source='en', target='zh-CN')
    total = len(lines)
    count = 0

    for idx, line in enumerate(lines):
        line = line.replace('搂', '§')
        if '=' in line:
            key, value = line.split('=', 1)
            value = value.strip()

            color_positions = []
            text_only = ''
            i = 0
            while i < len(value):
                if value[i] == '§' and i + 1 < len(value):
                    color_positions.append((len(text_only), value[i:i+2]))
                    i += 2
                else:
                    text_only += value[i]
                    i += 1

            if text_only in cache:
                translated_text = cache[text_only]
            else:
                try:
                    translated_text = translator.translate(text_only)
                    if translated_text is None:
                        raise ValueError("翻译返回 None")
                    cache[text_only] = translated_text
                    save_cache(cache)
                except Exception as e:
                    log(f"❌ 翻译第 {idx+1} 行失败: {e}")
                    translated_lines.append(line)
                    continue

            try:
                text_list = list(translated_text)
                offset = 0
                for pos, code in color_positions:
                    insert_pos = min(pos + offset, len(text_list))
                    text_list.insert(insert_pos, code)
                    offset += len(code)
                rebuilt = ''.join(text_list)
            except:
                rebuilt = translated_text

            translated_lines.append(f"{key.strip()}={rebuilt}")
            count += 1
            log(f"✅ 已翻译 {count}/{total} 行: {text_only} → {rebuilt}")
        else:
            translated_lines.append(line)

    return translated_lines

def zip_folder(folder_path, zip_path, log=print):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                full = os.path.join(root, file)
                arcname = os.path.relpath(full, folder_path)
                zipf.write(full, arcname)
    log(f"✅ 已压缩为: {zip_path}")
