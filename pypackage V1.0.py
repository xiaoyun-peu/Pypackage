import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, scrolledtext
import subprocess
import threading
import json
import sys

def install_package(package_name, index_url=None):
    extra_args = ["-i", index_url] if index_url else []
    try:
        # 使用subprocess在后台执行pip install命令
        subprocess.run([sys.executable, "-m", "pip", "install", package_name] + extra_args, check=True)
        update_output("成功安装: " + package_name + "\n")
    except Exception as e:
        update_output(f"安装错误: {str(e)}\n")

def check_and_update_packages(index_url=None):
    extra_args = ["-i", index_url] if index_url else []
    outdated_packages = []
    try:
        # 使用pip list --outdated命令获取过时的包
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"] + extra_args,
            check=True,
            stdout=subprocess.PIPE,
            text=True
        )
        outdated_packages = json.loads(result.stdout)
        if outdated_packages:
            packages_info = "\n".join([f"{pkg['name']} (当前版本: {pkg['version']}, 最新版本: {pkg['latest_version']})" for pkg in outdated_packages])
            update_output(f"检测到以下包需要更新：\n{packages_info}\n")
            if messagebox.askyesno("更新", "是否要更新这些包？"):
                update_packages(outdated_packages, index_url)
        else:
            messagebox.showinfo("检查更新", "没有需要更新的包。")
    except Exception as e:
        update_output(f"检查更新时出错：{str(e)}\n")

def update_packages(outdated_packages, index_url=None):
    extra_args = ["-i", index_url] if index_url else []
    for pkg in outdated_packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", pkg['name']] + extra_args, check=True)
            update_output(f"更新成功: {pkg['name']}\n")
        except subprocess.CalledProcessError as e:
            update_output(f"更新错误: {e.stderr.decode()}\n")

def check_and_update_pip(index_url=None):
    extra_args = ["-i", index_url] if index_url else []
    try:
        # 使用pip install --upgrade pip命令更新pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"] + extra_args, check=True)
        messagebox.showinfo("更新", "pip 更新成功！或pip已是最新版本")
        update_output("pip 更新成功！\n")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("错误", f"更新 pip 时出错：\n{e.stderr.decode()}")
        update_output(f"更新 pip 时出错：\n{e.stderr.decode()}\n")

def on_install_button_click():
    package_name = entry.get().strip()
    index_url = index_entry.get().strip()
    if package_name:
        threading.Thread(target=install_package, args=(package_name, index_url), daemon=True).start()
    else:
        messagebox.showwarning("警告", "请输入库名称！")

def on_check_updates_button_click():
    index_url = index_entry.get().strip()
    threading.Thread(target=check_and_update_packages, args=(index_url,), daemon=True).start()

def on_check_pip_updates_button_click():
    index_url = index_entry.get().strip()
    threading.Thread(target=check_and_update_pip, args=(index_url,), daemon=True).start()

def update_output(message):
    text_output.config(state='normal')
    text_output.insert(tk.END, message)
    text_output.see(tk.END)
    text_output.config(state='disabled')

# 创建UI界面
root = tk.Tk()
root.title("Pypackage")
root.minsize(600, 400)

# 创建样式
style = ttk.Style()
style.theme_use("default")

# 定义样式
style.configure("TButton", font=("Helvetica", 12), padding=10)
style.configure("TEntry", font=("Helvetica", 10), padding=5)

# 创建库名称输入框的标签
package_name_label = ttk.Label(root, text="库名称:")
package_name_label.pack(pady=5)

# 创建库名称输入框
entry = ttk.Entry(root)
entry.pack(pady=5)

# 创建索引服务器输入框的标签
index_entry_label = ttk.Label(root, text="自定义PyPI索引服务器 (可选):")
index_entry_label.pack(pady=5)

# 创建索引服务器输入框
index_entry = ttk.Entry(root)
index_entry.pack(pady=5)

# 创建安装按钮
install_button = ttk.Button(root, text="安装库（需要等待）", command=on_install_button_click)
install_button.pack(pady=10)

# 创建检测库更新按钮
check_updates_button = ttk.Button(root, text="检测库更新（需要等待）", command=on_check_updates_button_click)
check_updates_button.pack(pady=10)

# 创建检测pip更新按钮
check_pip_updates_button = ttk.Button(root, text="检测pip更新（需要等待）", command=on_check_pip_updates_button_click)
check_pip_updates_button.pack(pady=10)

# 创建滚动文本框
scrollbar = ttk.Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_output = tk.Text(root, state='disabled', yscrollcommand=scrollbar.set)
text_output.pack(pady=10, fill=tk.BOTH, expand=True)

scrollbar.config(command=text_output.yview)

root.mainloop()