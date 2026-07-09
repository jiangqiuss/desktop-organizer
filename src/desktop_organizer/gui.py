"""桌面文件自动整理工具 - 图形界面版"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime
import shutil


# 文件类型配置
FILE_TYPES = {
    "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".tiff"],
    "文档": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".csv", ".rtf"],
    "视频": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
    "音乐": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
    "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "安装包": [".exe", ".msi", ".dmg", ".deb", ".rpm"],
    "代码": [".py", ".js", ".ts", ".java", ".c", ".cpp", ".go", ".rs", ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".sh", ".bat"],
    "快捷方式": [".lnk", ".url"],
}

JUNK_EXTENSIONS = {".tmp", ".bak", ".old", ".cache"}
JUNK_NAMES = {"desktop.ini", "thumbs.db"}


def get_file_type(ext):
    ext = ext.lower()
    for type_name, extensions in FILE_TYPES.items():
        if ext in extensions:
            return type_name
    return "其他"


def resolve_dest(dest):
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    counter = 1
    while dest.exists():
        dest = dest.parent / f"{stem}_{counter}{suffix}"
        counter += 1
    return dest


class DesktopOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("桌面文件整理工具")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # 设置样式
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=4)

        # 目录选择
        frame_dir = ttk.LabelFrame(root, text="选择目录", padding=10)
        frame_dir.pack(fill="x", padx=10, pady=5)

        self.dir_var = tk.StringVar(value=str(Path.home() / "Desktop"))
        ttk.Entry(frame_dir, textvariable=self.dir_var, width=50).pack(side="left", padx=(0, 5))
        ttk.Button(frame_dir, text="浏览...", command=self.browse_dir).pack(side="left")

        # 整理模式
        frame_mode = ttk.LabelFrame(root, text="整理模式", padding=10)
        frame_mode.pack(fill="x", padx=10, pady=5)

        self.mode_var = tk.StringVar(value="type")
        ttk.Radiobutton(frame_mode, text="按类型整理（图片/文档/视频/...）", variable=self.mode_var, value="type").pack(anchor="w")
        ttk.Radiobutton(frame_mode, text="按日期整理（年-月）", variable=self.mode_var, value="date").pack(anchor="w")

        # 选项
        frame_opt = ttk.LabelFrame(root, text="选项", padding=10)
        frame_opt.pack(fill="x", padx=10, pady=5)

        self.clean_var = tk.BooleanVar()
        ttk.Checkbutton(frame_opt, text="同时清理垃圾文件（.tmp, .bak, .old 等）", variable=self.clean_var).pack(anchor="w")

        self.dry_run_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_opt, text="先预览再执行（推荐）", variable=self.dry_run_var).pack(anchor="w")

        # 按钮
        frame_btn = ttk.Frame(root, padding=10)
        frame_btn.pack(fill="x")

        self.scan_btn = ttk.Button(frame_btn, text="扫描预览", command=self.scan)
        self.scan_btn.pack(side="left", padx=5)

        self.exec_btn = ttk.Button(frame_btn, text="执行整理", command=self.execute, state="disabled")
        self.exec_btn.pack(side="left", padx=5)

        # 结果显示
        frame_result = ttk.LabelFrame(root, text="预览 / 结果", padding=10)
        frame_result.pack(fill="both", expand=True, padx=10, pady=5)

        self.result_text = tk.Text(frame_result, height=12, width=70, state="disabled", font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(frame_result, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        self.result_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.files = []

    def browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.dir_var.get())
        if d:
            self.dir_var.set(d)

    def log(self, msg):
        self.result_text.configure(state="normal")
        self.result_text.insert("end", msg + "\n")
        self.result_text.see("end")
        self.result_text.configure(state="disabled")

    def clear_log(self):
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.configure(state="disabled")

    def scan(self):
        source = Path(self.dir_var.get())
        if not source.exists():
            messagebox.showerror("错误", f"目录不存在：{source}")
            return

        self.clear_log()
        self.files = []

        # 扫描文件
        self.log(f"扫描目录: {source}")
        for item in source.iterdir():
            if item.is_file():
                self.files.append({
                    "path": item,
                    "name": item.name,
                    "ext": item.suffix,
                    "size": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime),
                    "type": get_file_type(item.suffix),
                })

        self.log(f"找到 {len(self.files)} 个文件\n")

        # 垃圾文件预览
        if self.clean_var.get():
            junk = [f for f in self.files if f["ext"].lower() in JUNK_EXTENSIONS or f["name"].lower() in JUNK_NAMES]
            if junk:
                self.log("=== 将清理的垃圾文件 ===")
                for j in junk:
                    self.log(f"  删除: {j['name']}")
                self.log("")
            else:
                self.log("没有垃圾文件\n")

        # 整理预览
        mode = self.mode_var.get()
        mode_name = "类型" if mode == "type" else "日期"
        self.log(f"=== 按{mode_name}整理预览 ===")

        non_junk = [f for f in self.files if f["ext"].lower() not in JUNK_EXTENSIONS and f["name"].lower() not in JUNK_NAMES]
        for f in non_junk:
            if mode == "type":
                target = f["type"]
            else:
                target = f["modified"].strftime("%Y-%m")
            self.log(f"  {f['name']} → {target}/")

        self.log(f"\n共 {len(non_junk)} 个文件将被移动")
        self.exec_btn.configure(state="normal")

    def execute(self):
        source = Path(self.dir_var.get())
        if not source.exists():
            messagebox.showerror("错误", f"目录不存在：{source}")
            return

        self.clear_log()
        self.log("正在整理...\n")

        moved = 0
        cleaned = 0
        mode = self.mode_var.get()

        # 清理垃圾
        if self.clean_var.get():
            for item in source.iterdir():
                if item.is_file():
                    if item.suffix.lower() in JUNK_EXTENSIONS or item.name.lower() in JUNK_NAMES:
                        item.unlink()
                        self.log(f"  已删除: {item.name}")
                        cleaned += 1

        # 整理文件
        for item in source.iterdir():
            if item.is_file():
                if mode == "type":
                    target = get_file_type(item.suffix)
                else:
                    target = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m")

                dest_dir = source / target
                dest_dir.mkdir(exist_ok=True)
                dest = resolve_dest(dest_dir / item.name)
                shutil.move(str(item), str(dest))
                self.log(f"  {item.name} → {target}/")
                moved += 1

        self.log(f"\n完成！移动了 {moved} 个文件")
        if cleaned:
            self.log(f"清理了 {cleaned} 个垃圾文件")

        messagebox.showinfo("完成", f"整理完成！\n移动了 {moved} 个文件")
        self.exec_btn.configure(state="disabled")


def main():
    root = tk.Tk()
    app = DesktopOrganizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
