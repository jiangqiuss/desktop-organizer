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
    ],
    "社交聊天": [
        "微信", "wechat", "qq", "钉钉", "dingtalk", "飞书", "feishu", "slack",
        "discord", "telegram", "whatsapp", "line", "teams", "会议", "meeting",
        "classin", "腾讯会议", "zoom", "skype",
    ],
    "影音娱乐": [
        "网易云", "qq音乐", "spotify", "music", "音乐", "bilibili", "b站",
        "哔哩哔哩", "爱奇艺", "优酷", "腾讯视频", "youtube", "抖音", "快手",
        "potplayer", "vlc", "播放器", "player", "录屏", "obs", "直播",
        "wallpaper", "壁纸",
    ],
    "工具软件": [
        "todesk", "向日葵", "anydesk", "远程", "remote", "火绒", "杀毒",
        "安全", "antivirus", "bandizip", "7zip", "winrar", "压缩", "解压",
        "图吧", "gpu-z", "cpu-z", "鲁大师", "驱动", "driver", "nvidia",
        "legion", "zone", "工具箱", "toolbox", "snipaste", "截图", "screenshot",
        "everything", "listary", "搜索", "teracopy", "复制",
    ],
    "专业软件": [
        "ansys", "autocad", "solidworks", "catia", "ug", "nx", "proe",
        "creo", "matlab", "simulink", "labview", "comsol", "fluent",
        "abaqus", "adams", "multisim", "proteus", "keil", "iar",
        "嘉立创", "立创", "eda", "altium", "ad", "pads", "cadence",
        "photoshop", "illustrator", "premiere", "after effects", "ae",
        "figma", "sketch", "blender", "maya", "3dmax", "c4d",
    ],
    "网络工具": [
        "clash", "v2ray", "trojan", "shadowsocks", "ssr", "vpn",
        "代理", "proxy", "迷雾通", "lantern", "蓝灯",
    ],
    "办公软件": [
        "wps", "office", "word", "excel", "powerpoint", "outlook",
        "onenote", "notion", "语雀", "飞书文档", "腾讯文档",
        "foxmail", "邮件", "mail", "foxit", "pdf", "福昕",
    ],
    "开发工具": [
        "visual studio", "vscode", "idea", "pycharm", "webstorm",
        "android studio", "xcode", "git", "github", "终端", "terminal",
        "powershell", "cmd", "docker", "postman", "navicat", "dbeaver",
    ],
}

JUNK_EXTENSIONS = [".tmp", ".cache"]
JUNK_PATTERNS = ["desktop.ini", "thumbs.db"]


def get_shortcut_category(name: str) -> str:
    """根据快捷方式名字关键词返回细分分类"""
    name_lower = name.lower()
    for category, keywords in SHORTCUT_CATEGORIES.items():
        for kw in keywords:
            if kw.lower() in name_lower:
                return f"快捷方式-{category}"
    return "快捷方式-其他"


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


def scan_directory(path: Path) -> list[dict]:
    """扫描目录，返回文件信息列表"""
    files = []
    for item in path.iterdir():
        if item.is_file():
            files.append({
                "path": item,
                "name": item.name,
                "ext": item.suffix,
                "size": item.stat().st_size,
                "modified": datetime.fromtimestamp(item.stat().st_mtime),
                "type": get_file_type(item.suffix, item.stem),
            })
    return files


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
