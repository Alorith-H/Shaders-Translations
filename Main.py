import customtkinter as ctk
from tkinter import filedialog
import threading
import queue
import time  # 仅用于演示

from foo import DocProcessing  # 确保与你文件名对应

class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("光影翻译器")
        self.geometry("600x400")

        # 日志文本框
        self.log_box = ctk.CTkTextbox(self, width=580, height=300)
        self.log_box.pack(padx=10, pady=10)

        # 按钮
        self.btn = ctk.CTkButton(self, text="选择文件并翻译", command=self.start_translation_thread)
        self.btn.pack(pady=10)

        # 线程安全队列用于日志传递
        self.log_queue = queue.Queue()

        # 启动定时器，更新日志显示
        self.after(100, self.update_log_from_queue)

    def log(self, message: str):
        self.log_queue.put(message)

    def update_log_from_queue(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
        self.after(100, self.update_log_from_queue)

    def start_translation_thread(self):
        threading.Thread(target=self.translation_task, daemon=True).start()

    def translation_task(self):
        file_path = filedialog.askopenfilename(title="选择光影包ZIP文件", filetypes=[("ZIP 文件", "*.zip")])
        if file_path:
            self.log(f"选择文件：{file_path}")
            DocProcessing.Move_func(file_path, log=self.log)
            self.log("🎉 翻译完成！")

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = TranslatorApp()
    app.mainloop()
