import shutil
import os
import zipfile
import json
from deep_translator import GoogleTranslator, BaiduTranslator

CACHE_FILE = "./translation_cache.json"

def load_cache():
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
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存缓存文件失败: {e}")

def check_file_path(path):
    if not os.path.exists(path):
        print("找不到文件 " + path)
        return False
    return True

def Move_func(path, output_dir="./Temp", log=print, translator_type='google', baidu_config=None):
    path = path.replace('\\', '/').replace('"', '')
    log(f"输入路径: {path}")

    if not check_file_path(path):
        log(f"文件不存在: {path}")
        return

    shader_name = os.path.splitext(os.path.basename(path))[0]
    log(f"光影包名: {shader_name}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        log(f"创建输出目录: {output_dir}")

    dst_path = os.path.join(output_dir, os.path.basename(path))
    shutil.copy(path, dst_path)
    log(f"复制文件到 {dst_path}")

    Unzip_func(dst_path, shader_name, output_dir, log, translator_type, baidu_config)

def Unzip_func(zip_path, shader_name, output_dir, log=print, translator_type='google', baidu_config=None):
    extract_dir = os.path.join(output_dir, "Zip")
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    log(f"解压完成: {extract_dir}")

    File_read_func(shader_name, output_dir, log, translator_type, baidu_config)

def File_read_func(shader_name, output_dir, log=print, translator_type='google', baidu_config=None):
    lang_dir = os.path.join(output_dir, "Zip")
    target_file = None

    for root, dirs, files in os.walk(lang_dir):
        for file in files:
            if file.endswith(".lang"):
                if file == "en_US.lang":
                    target_file = os.path.join(root, file)
                    break
                elif target_file is None:
                    target_file = os.path.join(root, file)
        if target_file and os.path.basename(target_file) == "en_US.lang":
            break

    if not target_file:
        log(f"未找到语言文件（.lang）")
        return

    log(f"找到语言文件: {target_file}")

    with open(target_file, 'r', encoding="utf-8") as f:
        lines = f.readlines()

    log(f"读取语言文件，共 {len(lines)} 行")

    translated_lines = Translation_func(lines, log, translator_type, baidu_config)

    with open(target_file, 'w', encoding="utf-8") as f:
        f.write('\n'.join(translated_lines))
    log("翻译完成，写回语言文件。")

    zip_out_path = os.path.join(output_dir, f"{shader_name}_zh.zip")
    zip_folder(os.path.join(output_dir, "Zip"), zip_out_path, log)

def Translation_func(lines, log=print, translator_type='google', baidu_config=None):
    translated_lines = []
    translation_cache = load_cache()
    total = len(lines)

    if translator_type == 'google':
        translator = GoogleTranslator(source='en', target='zh-CN')
    elif translator_type == 'baidu':
        if not baidu_config or 'app_id' not in baidu_config or 'secret_key' not in baidu_config:
            log("百度翻译配置缺失，使用Google翻译代替。")
            translator = GoogleTranslator(source='en', target='zh-CN')
        else:
            translator = BaiduTranslator(
                appid=baidu_config['app_id'],     # 注意这里是 appid
                appkey=baidu_config['secret_key'], # 注意这里是 appkey
                from_lang='en',
                to_lang='zh'
            )
    else:
        log(f"未知翻译器 {translator_type}，默认使用Google翻译")
        translator = GoogleTranslator(source='en', target='zh-CN')

    for idx, line in enumerate(lines):
        line = line.replace('搂', '§')  # 修复乱码
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

            if text_only in translation_cache:
                translated_text = translation_cache[text_only]
            else:
                try:
                    translated_text = translator.translate(text_only)
                    if translated_text is None:
                        raise ValueError("翻译返回None")
                    translation_cache[text_only] = translated_text
                    save_cache(translation_cache)
                except Exception as e:
                    log(f"[{(idx + 1) / total * 100:.1f}%] 翻译错误: {e}")
                    translated_lines.append(line)
                    continue

            try:
                text_list = list(translated_text)
                offset = 0
                for pos, code in color_positions:
                    insert_pos = min(pos + offset, len(text_list))
                    text_list.insert(insert_pos, code)
                    offset += len(code)
                rebuilt_text = ''.join(text_list)
            except Exception as e:
                log(f"[{(idx + 1) / total * 100:.1f}%] 颜色码插入错误: {e}")
                rebuilt_text = translated_text

            translated_line = f"{key.strip()}={rebuilt_text}"
            translated_lines.append(translated_line)
            log(f"[{(idx + 1) / total * 100:.1f}%] {text_only} → {rebuilt_text}")
        else:
            translated_lines.append(line)

    save_cache(translation_cache)
    return translated_lines

def zip_folder(folder_path, zip_path, log=print):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, start=folder_path)
                zipf.write(full_path, arcname)
    log(f"压缩完成: {zip_path}")
    clean_temp_folder(folder_path, os.path.dirname(zip_path), log)

def clean_temp_folder(folder_path, base_output_dir, log=print):
    try:
        shutil.rmtree(folder_path)
        zip_file = os.path.join(base_output_dir, os.path.basename(base_output_dir) + ".zip")
        if os.path.exists(zip_file):
            os.remove(zip_file)
        log(f"临时文件夹 {folder_path} 和临时文件已删除。")
    except Exception as e:
        log(f"清理临时文件夹失败: {e}")
