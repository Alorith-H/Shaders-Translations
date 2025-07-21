import customtkinter as ctk
from tkinter import filedialog
import threading
import queue
import json
import os
from foo import DocProcessing

# 主题选项列表
THEMES = ["dark", "light", "system"]
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except:
        pass

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, log_callback):
        super().__init__(master, width=180, corner_radius=0)
        self.log_callback = log_callback
        self.pack_propagate(False)

        self.label = ctk.CTkLabel(self, text="主菜单", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=(20, 10))

        self.btn_select = ctk.CTkButton(self, text="选择光影包", command=master.start_translation_thread)
        self.btn_select.pack(fill="x", padx=20, pady=10)

        self.btn_clear_log = ctk.CTkButton(self, text="清空日志", command=master.clear_log)
        self.btn_clear_log.pack(fill="x", padx=20, pady=10)

        self.btn_about = ctk.CTkButton(self, text="关于", command=self.show_about)
        self.btn_about.pack(fill="x", padx=20, pady=10)

        # 主题切换按钮固定底部
        self.btn_theme = ctk.CTkButton(self, text="切换主题", command=master.cycle_theme)
        self.btn_theme.pack(side="bottom", fill="x", padx=20, pady=20)

    def show_about(self):
        self.log_callback("此程序由 ChatGPT 助手制作，支持Minecraft光影包翻译。")

class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("光影翻译器")
        self.geometry("800x500")
        self.minsize(700, 400)

        self.log_queue = queue.Queue()

        self.sidebar = Sidebar(self, self.log)
        self.sidebar.pack(side="left", fill="y")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        self.log_box = ctk.CTkTextbox(self.main_frame, width=600, height=400, font=ctk.CTkFont(size=14))
        self.log_box.pack(expand=True, fill="both")

        self.btn_translate = ctk.CTkButton(self.main_frame, text="开始翻译", command=self.start_translation_thread)
        self.btn_translate.pack(pady=10)

        self.after(100, self.update_log_from_queue)

        # 读取并应用保存的主题配置
        config = load_config()
        saved_theme = config.get("theme", "system")
        if saved_theme not in THEMES:
            saved_theme = "system"
        ctk.set_appearance_mode(saved_theme)
        self.theme_index = THEMES.index(saved_theme)

    def log(self, message: str):
        self.log_queue.put(message)

    def update_log_from_queue(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
        self.after(100, self.update_log_from_queue)

    def clear_log(self):
        self.log_box.delete("0.0", "end")
        self.log("日志已清空。")

    def start_translation_thread(self):
        threading.Thread(target=self.translation_task, daemon=True).start()

    def translation_task(self):
        file_path = filedialog.askopenfilename(title="选择光影包ZIP文件", filetypes=[("ZIP 文件", "*.zip")])
        if file_path:
            self.log(f"选择文件：{file_path}")
            DocProcessing.Move_func(file_path, log=self.log)
            self.log("🎉 翻译完成！")

    def cycle_theme(self):
        self.theme_index = (self.theme_index + 1) % len(THEMES)
        new_theme = THEMES[self.theme_index]
        ctk.set_appearance_mode(new_theme)
        self.log(f"🌈 主题已切换到：{new_theme}")

        # 保存配置
        config = load_config()
        config["theme"] = new_theme
        save_config(config)

if __name__ == "__main__":
    # 你可以改这里的默认主题
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = TranslatorApp()
    app.mainloop()
