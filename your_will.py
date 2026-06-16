#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
你的遗嘱 - 加密解密工具
极简浅色界面，支持数字密钥，AES-256-CBC
"""

import sys
import os
import base64
import hashlib
import secrets
import tkinter as tk
from tkinter import filedialog, messagebox

# 导入美化库
try:
    import ttkbootstrap as tb
    from ttkbootstrap.constants import *
    from ttkbootstrap.scrolled import ScrolledText
    HAS_BOOTSTRAP = True
except ImportError:
    # 如果没有安装 ttkbootstrap 则降级（但会提示）
    import tkinter.ttk as ttk
    from tkinter import scrolledtext as scrolledtext_orig
    HAS_BOOTSTRAP = False
    class ScrolledText(scrolledtext_orig.ScrolledText):
        pass

# 加密核心库
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# ---------- 加密核心函数 ----------
def derive_aes_key(digital_key: str) -> bytes:
    if not digital_key.isdigit():
        raise ValueError("密钥必须为纯数字")
    if len(digital_key) not in (4, 6):
        raise ValueError("密钥长度必须为4位或6位数字")
    return hashlib.sha256(digital_key.encode('utf-8')).digest()

def encrypt_text(plain_text: str, digital_key: str) -> str:
    key = derive_aes_key(digital_key)
    iv = secrets.token_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain_bytes = plain_text.encode('utf-8')
    padded_data = pad(plain_bytes, AES.block_size)
    cipher_bytes = cipher.encrypt(padded_data)
    encrypted_data = iv + cipher_bytes
    return base64.b64encode(encrypted_data).decode('ascii')

def decrypt_text(encrypted_b64: str, digital_key: str) -> str:
    key = derive_aes_key(digital_key)
    try:
        encrypted_data = base64.b64decode(encrypted_b64)
    except Exception:
        raise ValueError("密文格式错误：无效的Base64编码")
    if len(encrypted_data) < 16:
        raise ValueError("密文数据损坏：长度不足")
    iv = encrypted_data[:16]
    cipher_bytes = encrypted_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    try:
        decrypted_padded = cipher.decrypt(cipher_bytes)
        plain_bytes = unpad(decrypted_padded, AES.block_size)
        return plain_bytes.decode('utf-8')
    except Exception as e:
        raise ValueError(f"解密失败，请检查密钥或密文是否完整。")

# ---------- 欢迎弹窗 ----------
def show_welcome(parent):
    """显示启动欢迎弹窗（模态）"""
    welcome = tk.Toplevel(parent)
    welcome.title("欢迎")
    welcome.geometry("500x350")
    welcome.resizable(False, False)
    # 居中显示
    parent.update_idletasks()
    x = (parent.winfo_screenwidth() // 2) - (500 // 2)
    y = (parent.winfo_screenheight() // 2) - (350 // 2)
    welcome.geometry(f"+{x}+{y}")
    welcome.grab_set()  # 模态

    # 主框架
    main_frame = tb.Frame(welcome, padding=30) if HAS_BOOTSTRAP else tk.Frame(welcome, padx=30, pady=30)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # 图标 + 标题
    title_label = tb.Label(
        main_frame, text="🛡️ 欢迎使用", 
        font=("微软雅黑", 20, "bold")
    ) if HAS_BOOTSTRAP else tk.Label(main_frame, text="欢迎使用", font=("微软雅黑", 20, "bold"))
    title_label.pack(pady=(0, 20))

    # 致谢内容
    thanks_text = (
        "本工具由以下项目联合驱动：\n\n"
        "• Python 软件基金会 (PSF)\n"
        "• DeepSeek\n"
        "• 家养荔枝爬行\n"
    )
    thanks_label = tb.Label(
        main_frame, text=thanks_text, 
        font=("微软雅黑", 12), justify="center"
    ) if HAS_BOOTSTRAP else tk.Label(
        main_frame, text=thanks_text, font=("微软雅黑", 12), justify="center"
    )
    thanks_label.pack(pady=10)

    # 开始按钮
    def on_start():
        welcome.destroy()
    start_btn = tb.Button(
        main_frame, bootstyle="success", text="开始使用", 
        command=on_start, width=20, padding=8
    ) if HAS_BOOTSTRAP else tk.Button(
        main_frame, text="开始使用", command=on_start, 
        bg="#28a745", fg="white", font=("微软雅黑", 12, "bold"),
        relief="flat", padx=20, pady=8
    )
    start_btn.pack(pady=20)

    # 绑定回车键
    welcome.bind('<Return>', lambda e: on_start())
    welcome.focus_set()

# ---------- 主界面 ----------
class MainApp:
    def __init__(self, root):
        self.root = root
        root.title("你的遗嘱")
        root.geometry("780x700")
        root.minsize(700, 600)

        # 应用主题（浅色）
        if HAS_BOOTSTRAP:
            self.style = tb.Style(theme="flatly")
            self.style.configure("TLabel", font=("微软雅黑", 10))
            self.style.configure("TButton", font=("微软雅黑", 10, "bold"), padding=6)
            self.style.configure("TEntry", font=("微软雅黑", 10))

        # 主容器
        container = tb.Frame(root, padding=20) if HAS_BOOTSTRAP else tk.Frame(root, padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        # ---- 标题 ----
        title = tb.Label(
            container, text="📜 你的遗嘱", 
            font=("微软雅黑", 22, "bold")
        ) if HAS_BOOTSTRAP else tk.Label(
            container, text="你的遗嘱", font=("微软雅黑", 22, "bold")
        )
        title.pack(pady=(0, 5))
        subtitle = tb.Label(
            container, text="安全加密 / 解密工具 · 支持 4/6 位数字密钥",
            font=("微软雅黑", 10)
        ) if HAS_BOOTSTRAP else tk.Label(
            container, text="安全加密 / 解密工具 · 支持 4/6 位数字密钥",
            font=("微软雅黑", 10)
        )
        subtitle.pack(pady=(0, 15))

        # 分割线
        if HAS_BOOTSTRAP:
            tb.Separator(container, bootstyle="secondary").pack(fill=tk.X, pady=10)
        else:
            tk.Frame(container, height=2, bg="#ccc").pack(fill=tk.X, pady=10)

        # ---- 操作行：模式 + 密钥 ----
        control_frame = tb.Frame(container) if HAS_BOOTSTRAP else tk.Frame(container)
        control_frame.pack(fill=tk.X, pady=10)

        # 模式
        mode_frame = tb.LabelFrame(control_frame, text="操作模式", padding=8) if HAS_BOOTSTRAP else tk.LabelFrame(control_frame, text="操作模式")
        mode_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.mode_var = tk.StringVar(value="encrypt")
        if HAS_BOOTSTRAP:
            tb.Radiobutton(
                mode_frame, bootstyle="primary-outline-toolbutton",
                text="🔒 加密", variable=self.mode_var, value="encrypt"
            ).pack(side=tk.LEFT, padx=10)
            tb.Radiobutton(
                mode_frame, bootstyle="warning-outline-toolbutton",
                text="🔓 解密", variable=self.mode_var, value="decrypt"
            ).pack(side=tk.LEFT, padx=10)
        else:
            tk.Radiobutton(mode_frame, text="加密", variable=self.mode_var, value="encrypt").pack(side=tk.LEFT, padx=10)
            tk.Radiobutton(mode_frame, text="解密", variable=self.mode_var, value="decrypt").pack(side=tk.LEFT, padx=10)

        # 密钥（明文显示）
        key_frame = tb.LabelFrame(control_frame, text="数字密钥", padding=8) if HAS_BOOTSTRAP else tk.LabelFrame(control_frame, text="数字密钥")
        key_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.key_var = tk.StringVar()
        self.key_entry = tb.Entry(
            key_frame, textvariable=self.key_var, width=20,
            font=("Consolas", 12), show=""   # 明文显示
        ) if HAS_BOOTSTRAP else tk.Entry(
            key_frame, textvariable=self.key_var, width=20, font=("Consolas", 12)
        )
        self.key_entry.pack(side=tk.LEFT, padx=5)
        tip = tb.Label(key_frame, text="(4或6位数字)", font=("微软雅黑", 9)) if HAS_BOOTSTRAP else tk.Label(key_frame, text="(4或6位数字)", font=("微软雅黑", 9))
        tip.pack(side=tk.LEFT, padx=5)

        # ---- 输入区域 ----
        input_frame = tb.LabelFrame(container, text="📄 输入内容", padding=10) if HAS_BOOTSTRAP else tk.LabelFrame(container, text="输入内容")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.input_text = ScrolledText(
            input_frame, height=8, wrap=tk.WORD,
            font=("微软雅黑", 10), relief="flat", borderwidth=2
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)

        # 输入工具栏
        input_toolbar = tb.Frame(input_frame) if HAS_BOOTSTRAP else tk.Frame(input_frame)
        input_toolbar.pack(fill=tk.X, pady=(5, 0))
        if HAS_BOOTSTRAP:
            tb.Button(
                input_toolbar, bootstyle="info-outline",
                text="📂 从 txt 导入", command=self.load_file
            ).pack(side=tk.LEFT, padx=5)
            tb.Button(
                input_toolbar, bootstyle="secondary-outline",
                text="🗑️ 清空", command=self.clear_input
            ).pack(side=tk.LEFT, padx=5)
        else:
            tk.Button(input_toolbar, text="从 txt 导入", command=self.load_file).pack(side=tk.LEFT, padx=5)
            tk.Button(input_toolbar, text="清空", command=self.clear_input).pack(side=tk.LEFT, padx=5)

        # ---- 执行按钮 ----
        action_frame = tb.Frame(container) if HAS_BOOTSTRAP else tk.Frame(container)
        action_frame.pack(fill=tk.X, pady=15)
        if HAS_BOOTSTRAP:
            self.run_btn = tb.Button(
                action_frame, bootstyle="success",
                text="🚀 执行加密 / 解密", command=self.run_action,
                width=30, padding=8
            )
        else:
            self.run_btn = tk.Button(
                action_frame, text="执行加密/解密", command=self.run_action,
                bg="#28a745", fg="white", font=("微软雅黑", 11, "bold"),
                relief="flat", padx=20, pady=8
            )
        self.run_btn.pack(pady=5)

        # ---- 结果区域 ----
        result_frame = tb.LabelFrame(container, text="📋 处理结果", padding=10) if HAS_BOOTSTRAP else tk.LabelFrame(container, text="处理结果")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.result_text = ScrolledText(
            result_frame, height=8, wrap=tk.WORD,
            font=("Consolas", 10), relief="flat", borderwidth=2,
            background="#f8f9fa" if not HAS_BOOTSTRAP else None
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # 结果工具栏
        result_toolbar = tb.Frame(result_frame) if HAS_BOOTSTRAP else tk.Frame(result_frame)
        result_toolbar.pack(fill=tk.X, pady=(5, 0))
        if HAS_BOOTSTRAP:
            tb.Button(
                result_toolbar, bootstyle="primary-outline",
                text="💾 保存为 txt", command=self.save_result
            ).pack(side=tk.LEFT, padx=5)
            tb.Button(
                result_toolbar, bootstyle="secondary-outline",
                text="清空结果", command=self.clear_result
            ).pack(side=tk.LEFT, padx=5)
        else:
            tk.Button(result_toolbar, text="保存为 txt", command=self.save_result).pack(side=tk.LEFT, padx=5)
            tk.Button(result_toolbar, text="清空结果", command=self.clear_result).pack(side=tk.LEFT, padx=5)

        # ---- 底部状态栏 + 致谢 ----
        bottom_frame = tb.Frame(container) if HAS_BOOTSTRAP else tk.Frame(container)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_var = tk.StringVar(value="就绪")
        status_label = tb.Label(
            bottom_frame, textvariable=self.status_var,
            font=("微软雅黑", 9), bootstyle="secondary"
        ) if HAS_BOOTSTRAP else tk.Label(
            bottom_frame, textvariable=self.status_var,
            font=("微软雅黑", 9), fg="#555"
        )
        status_label.pack(side=tk.LEFT)

        # 右下角致谢（小字）
        credit = tb.Label(
            bottom_frame, text="由 Python · DeepSeek · 家养荔枝爬行 提供支持",
            font=("微软雅黑", 8), bootstyle="secondary"
        ) if HAS_BOOTSTRAP else tk.Label(
            bottom_frame, text="由 Python · DeepSeek · 家养荔枝爬行 提供支持",
            font=("微软雅黑", 8), fg="#999"
        )
        credit.pack(side=tk.RIGHT)

        # 绑定回车执行
        root.bind('<Return>', lambda e: self.run_action())

    # ---------- 功能方法 ----------
    def load_file(self):
        file_path = filedialog.askopenfilename(title="选择文本文件", filetypes=[("文本文件", "*.txt")])
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(tk.END, content)
            self.status_var.set(f"已导入：{os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("读取失败", f"无法读取文件：{str(e)}")
            self.status_var.set("导入失败")

    def clear_input(self):
        self.input_text.delete(1.0, tk.END)
        self.status_var.set("输入已清空")

    def clear_result(self):
        self.result_text.delete(1.0, tk.END)
        self.status_var.set("结果已清空")

    def run_action(self):
        key = self.key_var.get().strip()
        if not key or not key.isdigit() or len(key) not in (4, 6):
            messagebox.showerror("密钥错误", "请输入4位或6位纯数字密钥！")
            self.status_var.set("密钥格式错误")
            return

        content = self.input_text.get(1.0, tk.END).rstrip('\n')
        if not content:
            messagebox.showerror("输入为空", "请先输入或导入要处理的文本！")
            self.status_var.set("输入文本为空")
            return

        mode = self.mode_var.get()
        try:
            if mode == "encrypt":
                result = encrypt_text(content, key)
                self.status_var.set("加密成功")
            else:
                result = decrypt_text(content, key)
                self.status_var.set("解密成功")
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result)
        except Exception as e:
            messagebox.showerror("操作失败", str(e))
            self.status_var.set("操作失败，请检查密钥或内容")

    def save_result(self):
        content = self.result_text.get(1.0, tk.END).rstrip('\n')
        if not content:
            messagebox.showwarning("内容为空", "结果区域没有内容可保存！")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt")],
            title="保存结果"
        )
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.status_var.set(f"已保存至：{os.path.basename(file_path)}")
            messagebox.showinfo("保存成功", f"文件已保存至：\n{file_path}")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))
            self.status_var.set("保存失败")

# ---------- 启动 ----------
if __name__ == "__main__":
    root = tk.Tk()
    # 先隐藏主窗口（防止先显示）
    root.withdraw()
    # 显示欢迎弹窗
    show_welcome(root)
    # 欢迎弹窗关闭后，显示主窗口
    root.deiconify()
    app = MainApp(root)
    root.mainloop()