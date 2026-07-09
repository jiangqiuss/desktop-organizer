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
}

# 快捷方式扩展名
SHORTCUT_EXTENSIONS = {".lnk", ".url", ".appref-ms"}

# 快捷方式细分规则
SHORTCUT_CATEGORIES = {
    "游戏": [
        "steam", "epic", "wegame", "游戏", "game", "英雄联盟", "lol", "王者", "原神",
        "明日方舟", "鹰角", "启动器", "launcher", "minecraft", "我的世界", "暴雪",
        "blizzard", "origin", "ubisoft", "育碧", "方舟", "终末地", "genshin",
        "valorant", "csgo", "dota", "pubg", "吃鸡", "永劫", "逆水寒", "剑网",
        "三国杀", "炉石", "守望", "暗黑", "星际", "魔兽", "堡垒之夜", "fortnite",
        "roblox", "糖豆人", "among us", "apex", "彩虹六号", "刺客信条", "看门狗",
        "gta", "荒野大镖客", "赛博朋克", "艾尔登法环", "黑神话", "只狼",
        "植物大战僵尸", "愤怒的小鸟", "开心消消乐", "4399",
    ],
    "社交聊天": [
        "微信", "wechat", "qq", "钉钉", "dingtalk", "飞书", "feishu", "slack",
        "discord", "telegram", "whatsapp", "line", "teams", "会议", "meeting",
        "classin", "腾讯会议", "zoom", "skype", "企业微信", "陌陌", "探探",
        "soul", "脉脉", "领英", "linkedin", "twitter", "微博", "weibo",
        "贴吧", "知乎", "小红书",
    ],
    "影音娱乐": [
        "网易云", "qq音乐", "spotify", "music", "音乐", "bilibili", "b站",
        "哔哩哔哩", "爱奇艺", "优酷", "腾讯视频", "youtube", "抖音", "快手",
        "potplayer", "vlc", "播放器", "player", "录屏", "obs", "直播",
        "wallpaper", "壁纸", "酷狗", "酷我", "咪咕", "千千", "foobar",
        "暴风", "射手", "字幕", "剪映", "pr", "达芬奇", "resolve",
        "喜马拉雅", "蜻蜓fm", "懒人听书", "猫耳", "荔枝",
    ],
    "工具软件": [
        "todesk", "向日葵", "anydesk", "远程", "remote", "火绒", "杀毒",
        "安全", "antivirus", "bandizip", "7zip", "winrar", "压缩", "解压",
        "图吧", "gpu-z", "cpu-z", "鲁大师", "驱动", "driver", "nvidia",
        "legion", "zone", "工具箱", "toolbox", "snipaste", "截图", "screenshot",
        "everything", "listary", "搜索", "teracopy", "复制", "ccleaner",
        "清理", "注册表", "分区", "diskgenius", "ghost", "备份", "还原",
        "ultraiso", "rufus", "ventoy", "pe", "装机", "360", "腾讯电脑管家",
        "2345", "猎豹", "搜狗输入法", "百度输入法", "讯飞输入法",
        "wgesture", "quicker", "utools", "powertoys", "seer", "quicklook",
    ],
    "专业软件": [
        "ansys", "autocad", "solidworks", "catia", "ug", "nx", "proe",
        "creo", "matlab", "simulink", "labview", "comsol", "fluent",
        "abaqus", "adams", "multisim", "proteus", "keil", "iar",
        "嘉立创", "立创", "eda", "altium", "ad", "pads", "cadence",
        "photoshop", "illustrator", "premiere", "after effects", "ae",
        "figma", "sketch", "blender", "maya", "3dmax", "c4d",
        "revit", "天正", "pkpm", "广联达", "斯维尔", "鲁班",
        "spss", "stata", "sas", "r语言", "origin", "graphpad",
        "mathtype", "latex", "overleaf", "wind", "同花顺", "东方财富",
    ],
    "网络工具": [
        "clash", "v2ray", "trojan", "shadowsocks", "ssr", "vpn",
        "代理", "proxy", "迷雾通", "lantern", "蓝灯", "加速器",
        "wireguard", "openvpn", "tailscale", "zerotier",
        "firefox", "chrome", "edge", "opera", "brave", "vivaldi", "浏览器", "browser",
        "idm", "aria2", "motrix", "迅雷", "thunder", "qbittorrent", "bt",
    ],
    "办公软件": [
        "wps", "office", "word", "excel", "powerpoint", "outlook",
        "onenote", "notion", "语雀", "飞书文档", "腾讯文档",
        "foxmail", "邮件", "mail", "foxit", "pdf", "福昕",
        "有道", "翻译", "translate", "百度网盘", "阿里云盘", "onedrive",
        "dropbox", "坚果云", "天翼", "城通", "蓝奏",
        "扫描", "ocr", "白描", "汉王",
    ],
    "开发工具": [
        "visual studio", "vscode", "vs code", "idea", "pycharm", "webstorm",
        "android studio", "xcode", "git", "github", "终端", "terminal",
        "powershell", "cmd", "docker", "postman", "navicat", "dbeaver",
        "sublime", "notepad++", "vim", "emacs", "cursor", "windsurf",
        "anaconda", "jupyter", "colab", "redis", "mongo", "mysql",
        "vmware", "virtualbox", "hyper-v", "wsl",
    ],
}

JUNK_EXTENSIONS = {".tmp", ".cache"}
JUNK_NAMES = {"desktop.ini", "thumbs.db"}


def get_shortcut_category(name):
    """根据快捷方式名字关键词返回细分分类"""
    name_lower = name.lower().strip()
    for category, keywords in SHORTCUT_CATEGORIES.items():
        for kw in keywords:
            if kw.strip().lower() in name_lower:
                return category
    return "其他"


def get_file_type(ext, name=""):
    ext = ext.lower()
    if ext in SHORTCUT_EXTENSIONS:
        return get_shortcut_category(name)
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
        ttk.Checkbutton(frame_opt, text="同时清理垃圾文件（.tmp, .cache 等）", variable=self.clean_var).pack(anchor="w")

        self.recursive_var = tk.BooleanVar()
        ttk.Checkbutton(frame_opt, text="扫描子文件夹，重新分类放错位置的文件", variable=self.recursive_var).pack(anchor="w")

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
        recursive = self.recursive_var.get()

        # 扫描文件
        mode_text = "递归扫描" if recursive else "扫描"
        self.log(f"{mode_text}目录: {source}")

        if recursive:
            # 递归扫描，跳过已分类的文件夹
            all_categories = set(FILE_TYPES.keys()) | set(SHORTCUT_CATEGORIES.keys()) | {"其他"}
            for item in source.rglob("*"):
                if item.is_file():
                    rel = item.relative_to(source)
                    parts = rel.parts
                    # 跳过已在分类文件夹内的文件
                    if len(parts) > 1 and parts[0] in all_categories:
                        continue
                    self.files.append({
                        "path": item,
                        "name": item.name,
                        "ext": item.suffix,
                        "size": item.stat().st_size,
                        "modified": datetime.fromtimestamp(item.stat().st_mtime),
                        "type": get_file_type(item.suffix, item.stem),
                        "in_subdir": item.parent != source,
                    })
        else:
            for item in source.iterdir():
                if item.is_file():
                    self.files.append({
                        "path": item,
                        "name": item.name,
                        "ext": item.suffix,
                        "size": item.stat().st_size,
                        "modified": datetime.fromtimestamp(item.stat().st_mtime),
                        "type": get_file_type(item.suffix, item.stem),
                        "in_subdir": False,
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
            subdir_tag = " [子目录]" if f.get("in_subdir") else ""
            self.log(f"  {f['name']}{subdir_tag} → {target}/")

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
        recursive = self.recursive_var.get()

        # 收集要处理的文件
        files_to_process = []
        all_categories = set(FILE_TYPES.keys()) | set(SHORTCUT_CATEGORIES.keys()) | {"其他"}

        if recursive:
            for item in source.rglob("*"):
                if item.is_file():
                    rel = item.relative_to(source)
                    parts = rel.parts
                    if len(parts) > 1 and parts[0] in all_categories:
                        continue
                    files_to_process.append(item)
        else:
            for item in source.iterdir():
                if item.is_file():
                    files_to_process.append(item)

        # 清理垃圾
        if self.clean_var.get():
            for item in files_to_process[:]:
                if item.suffix.lower() in JUNK_EXTENSIONS or item.name.lower() in JUNK_NAMES:
                    item.unlink()
                    self.log(f"  已删除: {item.name}")
                    cleaned += 1
                    files_to_process.remove(item)

        # 整理文件
        for item in files_to_process:
            if mode == "type":
                target = get_file_type(item.suffix, item.stem)
            else:
                target = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m")

            dest_dir = source / target
            dest_dir.mkdir(exist_ok=True)
            dest = resolve_dest(dest_dir / item.name)
            shutil.move(str(item), str(dest))
            self.log(f"  {item.name} → {target}/")
            moved += 1

        # 清理空文件夹
        empty_removed = 0
        if recursive:
            for d in sorted(source.rglob("*"), reverse=True):
                if d.is_dir() and not any(d.iterdir()):
                    try:
                        d.rmdir()
                        empty_removed += 1
                    except:
                        pass

        self.log(f"\n完成！移动了 {moved} 个文件")
        if cleaned:
            self.log(f"清理了 {cleaned} 个垃圾文件")
        if empty_removed:
            self.log(f"清理了 {empty_removed} 个空文件夹")

        messagebox.showinfo("完成", f"整理完成！\n移动了 {moved} 个文件")
        self.exec_btn.configure(state="disabled")


def main():
    root = tk.Tk()
    app = DesktopOrganizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
