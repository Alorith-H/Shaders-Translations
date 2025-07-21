import customtkinter as ctk
from tkinter import filedialog
import threading
import queue
import json
import os
from foo import DocProcessing  # 你的翻译处理模块

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

        self.btn_output_dir = ctk.CTkButton(self, text="选择输出目录", command=master.select_output_directory)
        self.btn_output_dir.pack(fill="x", padx=20, pady=10)

        self.btn_clear_log = ctk.CTkButton(self, text="清空日志", command=master.clear_log)
        self.btn_clear_log.pack(fill="x", padx=20, pady=10)

        self.btn_about = ctk.CTkButton(self, text="关于", command=self.show_about)
        self.btn_about.pack(fill="x", padx=20, pady=10)

        self.btn_theme = ctk.CTkButton(self, text="切换主题", command=master.cycle_theme)
        self.btn_theme.pack(side="bottom", fill="x", padx=20, pady=20)

    def show_about(self):
        self.log_callback("By Alorith. 支持Minecraft光影包翻译。")

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

        self.log_box = ctk.CTkTextbox(self.main_frame, font=ctk.CTkFont(size=14))
        self.log_box.pack(side="top", expand=True, fill="both", pady=(0,10))

        bottom_frame = ctk.CTkFrame(self.main_frame)
        bottom_frame.pack(side="bottom", fill="x")

        self.input_var = ctk.StringVar()
        self.entry = ctk.CTkEntry(bottom_frame, textvariable=self.input_var, placeholder_text="请输入光影包路径或留空选择文件")
        self.entry.pack(side="left", expand=True, fill="x", padx=(0, 10))

        self.btn_translate = ctk.CTkButton(bottom_frame, text="开始翻译", width=100, command=self.on_button_click)
        self.btn_translate.pack(side="right")

        self.after(100, self.update_log_from_queue)

        self.input_var.trace_add("write", self.on_input_change)

        # 新增状态，等待用户输入翻译器选择
        self.waiting_for_translator_choice = False
        self.selected_file_path = None
        self.selected_translator = "google"

        config = load_config()
        saved_theme = config.get("theme", "dark")
        if saved_theme not in THEMES:
            saved_theme = "dark"
        ctk.set_appearance_mode(saved_theme)
        self.theme_index = THEMES.index(saved_theme)

        self.output_dir = config.get("output_dir", "./Temp")
        self.log(f"当前输出目录: {self.output_dir}")

    def on_input_change(self, *args):
        text = self.input_var.get().strip()
        if text:
            self.btn_translate.configure(text="发送")
        else:
            self.btn_translate.configure(text="开始翻译")

    def on_button_click(self):
        text = self.input_var.get().strip()
        if self.waiting_for_translator_choice:
            if text == "1":
                self.selected_translator = "google"
            else:
                self.log("输入无效，请输入有效数字对应翻译器。")
                return

            self.log(f"已选择翻译器：{self.selected_translator}，开始翻译...")
            self.waiting_for_translator_choice = False
            self.input_var.set("")
            self.start_translation_thread(file_path=self.selected_file_path, translator_type=self.selected_translator)
        else:
            if text:
                if os.path.exists(text):
                    self.start_translation_thread(file_path=text)
                else:
                    self.log("输入路径无效，请选择有效文件。")
            else:
                self.start_translation_thread()

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

    def select_output_directory(self):
        selected_dir = filedialog.askdirectory(title="选择输出目录")
        if selected_dir:
            self.output_dir = selected_dir
            self.log(f"输出目录已设置为：{self.output_dir}")

            config = load_config()
            config["output_dir"] = self.output_dir
            save_config(config)

    def start_translation_thread(self, file_path=None, translator_type=None):
        if translator_type is not None:
            self.btn_translate.configure(state="disabled")
            threading.Thread(target=self.translation_task, args=(file_path, translator_type), daemon=True).start()
        else:
            if not file_path:
                file_path = filedialog.askopenfilename(title="选择光影包ZIP文件", filetypes=[("ZIP 文件", "*.zip")])
            if file_path:
                self.selected_file_path = file_path
                self.log(f"选择文件：{file_path}")
                self.log("请选择翻译器:")
                self.log("1. Google翻译")
                self.log("请输入对应数字后，点击发送开始翻译。")
                self.waiting_for_translator_choice = True
            else:
                self.log("未选择文件，操作取消。")

    def translation_task(self, file_path=None, translator_type="google"):
        if file_path:
            try:
                DocProcessing.Move_func(file_path, output_dir=self.output_dir, log=self.log, translator_type=translator_type)
                self.log("🎉 翻译完成！")
            except Exception as e:
                self.log(f"❌ 翻译失败: {e}")
        else:
            self.log("未选择文件，操作取消。")

        self.after(0, lambda: self.btn_translate.configure(state="normal"))

    def cycle_theme(self):
        self.theme_index = (self.theme_index + 1) % len(THEMES)
        new_theme = THEMES[self.theme_index]
        ctk.set_appearance_mode(new_theme)
        self.log(f"🌈 主题已切换到：{new_theme}")

        config = load_config()
        config["theme"] = new_theme
        save_config(config)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = TranslatorApp()
    app.mainloop()
