import os
import json
import configparser

from .colors import THEMES, DEFAULT_THEME
from .logos import get_logo, list_logos

CONFIG_DIRS = [
    os.path.expanduser("~/.config/commiefetch"),
    os.path.join(os.path.dirname(__file__), "..", "..", "configs"),
    "/etc/commiefetch",
]

CONFIG_FILES = [
    "config.toml",
    "config.json",
    "config.ini",
    "commiefetch.toml",
    "commiefetch.json",
]


def find_config():
    for config_dir in CONFIG_DIRS:
        if os.path.isdir(config_dir):
            for fname in CONFIG_FILES:
                path = os.path.join(config_dir, fname)
                if os.path.exists(path):
                    return path
    return None


def parse_json_config(data):
    if isinstance(data, str):
        data = json.loads(data)
    cfg = {}
    cfg["logo"] = data.get("logo", "ussr")
    cfg["theme"] = data.get("theme", DEFAULT_THEME)
    cfg["modules"] = data.get("modules", None)
    cfg["separator"] = data.get("separator", " -> ")
    cfg["color_separator"] = data.get("color_separator", True)
    cfg["bold_labels"] = data.get("bold_labels", True)
    cfg["show_colors"] = data.get("show_colors", True)
    cfg["padding"] = data.get("padding", 2)
    cfg["title"] = data.get("title", None)
    return cfg


def parse_toml(data):
    import re
    cfg = {}
    current_section = None
    for line in data.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'^\[(\w+)\]$', line)
        if m:
            current_section = m.group(1)
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip()
            if val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
            elif val.startswith("[") and val.endswith("]"):
                val = [x.strip().strip('"\'') for x in val[1:-1].split(",") if x.strip()]
            else:
                val = val.strip('"\'')
            if current_section:
                if current_section not in cfg:
                    cfg[current_section] = {}
                cfg[current_section][key] = val
            else:
                cfg[key] = val
    return cfg


def parse_ini_config(path):
    parser = configparser.ConfigParser()
    parser.read(path)
    cfg = {}
    cfg["logo"] = parser.get("commiefetch", "logo", fallback="ascii_hammer")
    cfg["theme"] = parser.get("commiefetch", "theme", fallback=DEFAULT_THEME)
    mods_raw = parser.get("commiefetch", "modules", fallback=None)
    if mods_raw:
        cfg["modules"] = [m.strip() for m in mods_raw.split(",")]
    else:
        cfg["modules"] = None
    cfg["separator"] = parser.get("commiefetch", "separator", fallback=" -> ")
    cfg["color_separator"] = parser.getboolean(
        "commiefetch", "color_separator", fallback=True
    )
    cfg["bold_labels"] = parser.getboolean(
        "commiefetch", "bold_labels", fallback=True
    )
    cfg["show_colors"] = parser.getboolean(
        "commiefetch", "show_colors", fallback=True
    )
    cfg["padding"] = parser.getint("commiefetch", "padding", fallback=2)
    cfg["title"] = parser.get("commiefetch", "title", fallback=None)
    return cfg


def load_config(path=None):
    defaults = {
        "logo": "ascii_hammer",
        "theme": DEFAULT_THEME,
        "modules": DEFAULT_MODULES[:],
        "separator": " -> ",
        "color_separator": True,
        "bold_labels": True,
        "show_colors": True,
        "padding": 2,
        "title": None,
    }
    if path:
        config_path = path
    else:
        config_path = find_config()
    if not config_path:
        return defaults
    try:
        with open(config_path) as f:
            raw = f.read()
        ext = os.path.splitext(config_path)[1].lower()
        if ext == ".json":
            parsed = parse_json_config(raw)
        elif ext == ".toml":
            toml_data = parse_toml(raw)
            if toml_data:
                parsed = {}
                parsed["logo"] = toml_data.get("logo", defaults["logo"])
                parsed["theme"] = toml_data.get(
                    "theme", defaults["theme"]
                )
                main_section = toml_data.get("commiefetch", {})
                if main_section:
                    parsed["logo"] = main_section.get(
                        "logo", parsed["logo"]
                    )
                    parsed["theme"] = main_section.get(
                        "theme", parsed["theme"]
                    )
                    parsed["modules"] = main_section.get(
                        "modules", parsed.get("modules")
                    )
                    parsed["separator"] = main_section.get(
                        "separator", defaults["separator"]
                    )
                else:
                    parsed["modules"] = toml_data.get(
                        "modules", parsed.get("modules")
                    )
                    parsed["separator"] = toml_data.get(
                        "separator", defaults["separator"]
                    )
                parsed["bold_labels"] = toml_data.get(
                    "bold_labels", defaults["bold_labels"]
                )
                parsed["show_colors"] = toml_data.get(
                    "show_colors", defaults["show_colors"]
                )
                parsed["padding"] = toml_data.get(
                    "padding", defaults["padding"]
                )
            else:
                parsed = defaults
        elif ext == ".ini":
            parsed = parse_ini_config(config_path)
        else:
            parsed = defaults
        for k, v in defaults.items():
            if k not in parsed or parsed[k] is None:
                parsed[k] = v
        return parsed
    except Exception:
        return defaults


def write_example_config(path):
    config = {
        "logo": "ussr",
        "theme": "soviet",
        "separator": " -> ",
        "color_separator": True,
        "bold_labels": True,
        "show_colors": True,
        "padding": 2,
        "title": None,
        "modules": [
            "title", "os", "host", "kernel", "uptime",
            "packages", "shell", "de", "wm", "terminal",
            "cpu", "gpu", "memory", "disk", "battery",
        ],
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
    return path


DEFAULT_MODULES = [
    "title", "os", "host", "kernel", "uptime", "packages",
    "shell", "de", "terminal", "cpu", "gpu", "memory",
    "disk", "locale",
]


MODULE_LABELS = {
    "title": "",
    "os": "OS",
    "host": "Host",
    "kernel": "Kernel",
    "uptime": "Uptime",
    "packages": "Packages",
    "shell": "Shell",
    "de": "DE",
    "wm": "WM",
    "terminal": "Terminal",
    "cpu": "CPU",
    "gpu": "GPU",
    "memory": "Memory",
    "disk": "Disk",
    "disks": "Disks",
    "swap": "Swap",
    "battery": "Battery",
    "processes": "Processes",
    "local_ip": "Local IP",
    "public_ip": "Public IP",
    "resolution": "Resolution",
    "locale": "Locale",
    "cpu_temp": "CPU Temp",
    "user_at_host": "",
}
