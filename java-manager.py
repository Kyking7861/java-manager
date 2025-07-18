import os
import sys
import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import json
import threading
import subprocess
import winreg

CONFIG_FILE = 'java_versions.json'

# 检查管理员权限
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 读取已保存的 Java 版本
def load_versions():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# 保存 Java 版本
def save_versions(versions):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(versions, f, ensure_ascii=False, indent=2)

# 查询系统环境变量
def get_sys_env(var):
    try:
        result = subprocess.run(['reg', 'query', r'HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment', '/v', var],
                               capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            for line in lines:
                if var in line:
                    return line.split(var)[-1].strip().split(None, 1)[-1]
        return None
    except Exception:
        return None

# 设置 .jar 文件关联到当前 JDK/JRE 的 javaw.exe
def set_jarfile_association(javaw_path):
    # 统一为反斜杠
    javaw_path = os.path.normpath(javaw_path).replace('/', '\\')
    value = f'"{javaw_path}" -jar "%1" %*'
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'jarfile\shell\open\command', 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, '', 0, winreg.REG_SZ, value)
        winreg.CloseKey(key)
        return True, ''
    except Exception as e:
        return False, str(e)

# 设置 JAVA_HOME，并确保 Path 包含 %JAVA_HOME%\\bin（双反斜杠），并同步 .jar 关联
def set_java_home_logic(jdk_path, jre_path, callback=None):
    def worker():
        java_home_val = get_sys_env('JAVA_HOME')
        path_val = get_sys_env('Path')
        need_set_path = False
        path_token = '%JAVA_HOME%\\bin'
        if path_val:
            if path_token.lower() not in path_val.lower():
                need_set_path = True
        else:
            need_set_path = True
        os.system(f'setx JAVA_HOME "{jdk_path}" /M')
        if need_set_path:
            os.system(f'setx Path "%Path%;{path_token}" /M')
            msg = f'已切换 JAVA_HOME 到:\n{jdk_path}\n\n已自动将 %JAVA_HOME%\\bin 添加到 Path。'
        else:
            msg = f'已切换 JAVA_HOME 到:\n{jdk_path}\n\nPath 已包含 %JAVA_HOME%\\bin，无需重复添加。'
        javaw_path = ''
        if jre_path and os.path.exists(os.path.join(jre_path, 'bin', 'javaw.exe')):
            javaw_path = os.path.join(jre_path, 'bin', 'javaw.exe')
        elif os.path.exists(os.path.join(jdk_path, 'bin', 'javaw.exe')):
            javaw_path = os.path.join(jdk_path, 'bin', 'javaw.exe')
        else:
            msg += '\n\n[警告] 未找到 javaw.exe，.jar 文件关联未修改。'
            if callback:
                callback(msg)
            return
        ok, err = set_jarfile_association(javaw_path)
        if ok:
            msg += f'\n\n已同步 .jar 文件关联到 {javaw_path}。'
        else:
            msg += f'\n\n[警告] .jar 文件关联修改失败：{err}'
        if callback:
            callback(msg)
    threading.Thread(target=worker, daemon=True).start()

# 主界面类
class JavaManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Java 环境管理器')
        self.versions = load_versions()
        self.create_widgets()
        self.refresh_listbox()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        self.listbox = tk.Listbox(self.root, width=70, height=10)
        self.listbox.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
        self.add_btn = ttk.Button(self.root, text='添加 Java 版本', command=self.add_version)
        self.add_btn.grid(row=1, column=0, padx=10, pady=5)
        self.del_btn = ttk.Button(self.root, text='删除选中版本', command=self.delete_version)
        self.del_btn.grid(row=1, column=1, padx=10, pady=5)
        self.switch_btn = ttk.Button(self.root, text='切换到选中版本', command=self.switch_version)
        self.switch_btn.grid(row=1, column=2, padx=10, pady=5)
        self.path_label = ttk.Label(self.root, text='Path 应包含 %JAVA_HOME%\\bin，程序会自动检测和追加', foreground='blue')
        self.path_label.grid(row=2, column=0, columnspan=3, pady=10)

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for v in self.versions:
            jre_info = f"，jre: {v['jre_path']}" if v.get('jre_path') else ''
            self.listbox.insert(tk.END, f"{v['version']}  ——  jdk: {v['jdk_path']}{jre_info}")

    def add_version(self):
        jdk_path = filedialog.askdirectory(title='选择 JDK 目录')
        if not jdk_path:
            return
        version = simpledialog.askstring('输入版本号', '请输入 Java 版本号（如 jdk8、jdk11）：')
        if not version:
            return
        has_jre = messagebox.askyesno('JRE 目录', '该 JDK 是否有单独的 jre 目录？')
        jre_path = ''
        if has_jre:
            jre_path = filedialog.askdirectory(title='选择 JRE 目录')
            if not jre_path:
                messagebox.showwarning('未选择', '未选择 JRE 目录，已取消添加。')
                return
        for v in self.versions:
            if v['jdk_path'] == jdk_path and v.get('jre_path', '') == jre_path:
                messagebox.showwarning('已存在', '该目录已添加过！')
                return
        self.versions.append({'version': version, 'jdk_path': jdk_path, 'jre_path': jre_path})
        save_versions(self.versions)
        self.refresh_listbox()

    def delete_version(self):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning('未选择', '请先选择要删除的版本！')
            return
        del self.versions[idx[0]]
        save_versions(self.versions)
        self.refresh_listbox()

    def switch_version(self):
        if not is_admin():
            messagebox.showerror('权限不足', '请以管理员身份运行此程序！')
            return
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning('未选择', '请先选择要切换的版本！')
            return
        v = self.versions[idx[0]]
        jdk_path = v['jdk_path']
        jre_path = v.get('jre_path', '')
        self.switch_btn.config(state='disabled')
        self.switch_btn.update()
        def on_finish(msg):
            self.switch_btn.config(state='normal')
            messagebox.showinfo('结果', msg)
        set_java_home_logic(jdk_path, jre_path, on_finish)

if __name__ == '__main__':
    root = tk.Tk()
    app = JavaManagerApp(root)
    root.mainloop()
