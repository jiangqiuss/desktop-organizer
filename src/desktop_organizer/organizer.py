"""
桌面文件自动整理工具
功能：按类型、按日期分文件夹，清理垃圾文件
"""
import shutil
from datetime import datetime
from pathlib import Path

# 配置：文件类型 → 文件夹名
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

# 快捷方式细分规则：关键词 → 分类名
# 按优先级排列，第一个匹配的生效
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

JUNK_EXTENSIONS = [".tmp", ".cache"]
JUNK_PATTERNS = ["desktop.ini", "thumbs.db"]


def get_shortcut_category(name: str) -> str:
    """根据快捷方式名字关键词返回细分分类"""
    name_lower = name.lower().strip()
    for category, keywords in SHORTCUT_CATEGORIES.items():
        for kw in keywords:
            if kw.strip().lower() in name_lower:
                return category
    return "其他"


def get_file_type(ext: str, name: str = "") -> str:
    """根据扩展名返回文件类型，快捷方式会进一步细分"""
    ext = ext.lower()
    if ext in SHORTCUT_EXTENSIONS:
        return get_shortcut_category(name)
    for type_name, extensions in FILE_TYPES.items():
        if ext in extensions:
            return type_name
    return "其他"


def resolve_dest(dest: Path) -> Path:
    """处理重名文件，返回不冲突的目标路径"""
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    counter = 1
    while dest.exists():
        dest = dest.parent / f"{stem}_{counter}{suffix}"
        counter += 1
    return dest


def scan_directory(path: Path, recursive: bool = False) -> list[dict]:
    """扫描目录，返回文件信息列表"""
    files = []
    if recursive:
        for item in path.rglob("*"):
            if item.is_file() and not _is_inside_category_dir(item, path):
                files.append({
                    "path": item,
                    "name": item.name,
                    "ext": item.suffix,
                    "size": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime),
                    "type": get_file_type(item.suffix, item.stem),
                    "in_subdir": item.parent != path,
                })
    else:
        for item in path.iterdir():
            if item.is_file():
                files.append({
                    "path": item,
                    "name": item.name,
                    "ext": item.suffix,
                    "size": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime),
                    "type": get_file_type(item.suffix, item.stem),
                    "in_subdir": False,
                })
    return files


def _is_inside_category_dir(file_path: Path, root: Path) -> bool:
    """检查文件是否已经在分类文件夹内（避免重复整理）"""
    # 获取所有已知的分类文件夹名
    all_categories = set()
    for type_name in FILE_TYPES:
        all_categories.add(type_name)
    all_categories.add("其他")
    for cat in SHORTCUT_CATEGORIES:
        all_categories.add(cat)
    all_categories.add("其他")

    # 检查文件的父目录是否是分类文件夹
    rel = file_path.relative_to(root)
    parts = rel.parts
    if len(parts) > 1 and parts[0] in all_categories:
        return True
    return False


def organize_by_type(files: list[dict], target_dir: Path) -> int:
    """按类型整理文件"""
    moved = 0
    for f in files:
        type_dir = target_dir / f["type"]
        type_dir.mkdir(exist_ok=True)
        dest = resolve_dest(type_dir / f["name"])
        shutil.move(str(f["path"]), str(dest))
        moved += 1
    return moved


def organize_by_date(files: list[dict], target_dir: Path) -> int:
    """按日期整理文件（年-月）"""
    moved = 0
    for f in files:
        date_dir = target_dir / f["modified"].strftime("%Y-%m")
        date_dir.mkdir(exist_ok=True)
        dest = resolve_dest(date_dir / f["name"])
        shutil.move(str(f["path"]), str(dest))
        moved += 1
    return moved


def clean_junk(path: Path) -> list[str]:
    """清理垃圾文件"""
    cleaned = []
    for item in path.iterdir():
        if item.is_file():
            if item.suffix.lower() in JUNK_EXTENSIONS:
                cleaned.append(item.name)
                item.unlink()
            elif item.name.lower() in [p.lower() for p in JUNK_PATTERNS]:
                cleaned.append(item.name)
                item.unlink()
    return cleaned


def clean_empty_dirs(path: Path) -> int:
    """清理空文件夹（从深到浅）"""
    removed = 0
    for d in sorted(path.rglob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
            removed += 1
    return removed
