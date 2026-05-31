import argparse
import os
import sys
import textwrap
import platform

from . import __version__, __app_name__
from .colors import (
    THEMES, DEFAULT_THEME, apply_theme, colorize, NO_COLOR,
    RESET, BOLD, DIM, ITALIC, BLINK,
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE,
    BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW,
    BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE,
    BG_RED, BG_GREEN, BG_YELLOW, BG_BLUE, BG_MAGENTA, BG_CYAN, BG_WHITE,
)
from .logos import LOGOS, get_logo, list_logos
from .config import (
    load_config, write_example_config, DEFAULT_MODULES, MODULE_LABELS,
    find_config,
)
from .modules import (
    get_user, get_hostname, get_os, get_kernel, get_uptime,
    get_cpu, get_gpu, get_memory, get_swap, get_disk, get_disks,
    get_terminal, get_shell, get_desktop, get_wm, get_packages,
    get_resolution, get_cpu_temp, get_processes, get_local_ip,
    get_public_ip, get_battery, get_locale,
)


def build_arg_parser():
    parser = argparse.ArgumentParser(
        prog=__app_name__,
        description=f"{__app_name__} — communist-themed system information tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(f"""\
            examples:
              {__app_name__}
              {__app_name__} --logo ussr --theme soviet
              {__app_name__} --logo random
              {__app_name__} --logo prc --theme china
              {__app_name__} --list-logos
              {__app_name__} --list-themes
              {__app_name__} --no-color
              {__app_name__} --config ~/.config/commiefetch/config.json
              {__app_name__} --gen-config

            docs: https://opencode.ai
        """),
    )
    parser.add_argument(
        "--logo", "-l",
        help="Logo to display (use --list-logos for options, 'random' for random)",
        default=None,
    )
    parser.add_argument(
        "--theme", "-t",
        help=f"Color theme (default: {DEFAULT_THEME})",
        default=None,
    )
    parser.add_argument(
        "--list-logos", action="store_true",
        help="List all available logos",
    )
    parser.add_argument(
        "--list-themes", action="store_true",
        help="List all available color themes",
    )
    parser.add_argument(
        "--no-color", action="store_true",
        help="Disable colored output",
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to config file",
        default=None,
    )
    parser.add_argument(
        "--gen-config", action="store_true",
        help=f"Generate example config at ~/.config/{__app_name__}/config.json",
    )
    parser.add_argument(
        "--modules", "-m",
        nargs="+",
        help="Modules to display (e.g., os kernel cpu memory)",
        default=None,
    )
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version and exit",
    )
    parser.add_argument(
        "--separator", "-s",
        help="Separator between label and value",
        default=None,
    )
    parser.add_argument(
        "--padding",
        type=int,
        help="Padding before values",
        default=None,
    )
    parser.add_argument(
        "--show-colors", action="store_true",
        help="Show color palette test",
    )
    parser.add_argument(
        "--title",
        help="Custom title text",
        default=None,
    )
    return parser


def get_module_value(name):
    mappers = {
        "title": lambda: "",
        "os": get_os,
        "host": lambda: f"{get_user()}@{get_hostname()}",
        "kernel": get_kernel,
        "uptime": get_uptime,
        "packages": lambda: str(get_packages()),
        "shell": get_shell,
        "de": get_desktop,
        "wm": get_wm,
        "terminal": get_terminal,
        "cpu": get_cpu,
        "gpu": get_gpu,
        "memory": lambda: _format_memory(get_memory()),
        "disk": lambda: _format_disk(get_disk("/")),
        "disks": lambda: _format_disks(get_disks()),
        "swap": lambda: _format_memory(get_swap()),
        "battery": get_battery,
        "processes": lambda: str(get_processes()),
        "local_ip": get_local_ip,
        "public_ip": get_public_ip,
        "resolution": get_resolution,
        "locale": get_locale,
        "cpu_temp": lambda: "" if get_cpu_temp() == "unknown" else get_cpu_temp(),
        "user_at_host": lambda: f"{get_user()}@{get_hostname()}",
    }
    func = mappers.get(name)
    if func:
        return func()
    return None


def _format_memory(mem):
    if not mem:
        return "unknown"
    if isinstance(mem, dict):
        return f"{mem.get('used', 0)} {mem.get('unit', 'MiB')} / {mem.get('total', 0)} {mem.get('unit', 'MiB')} ({mem.get('percent', 0)}%)"
    return str(mem)


def _format_disk(disk):
    if not disk:
        return "unknown"
    if isinstance(disk, dict):
        total = disk.get('total', 0)
        used = disk.get('used', 0)
        unit = disk.get('unit', 'MiB')
        pct = disk.get('percent', 0)
        if total >= 1024:
            total_g = total / 1024
            used_g = used / 1024
            return f"{used_g:.1f} GiB / {total_g:.1f} GiB ({pct}%)"
        return f"{used} {unit} / {total} {unit} ({pct}%)"
    return str(disk)


def _format_disks(disks):
    if not disks:
        return "unknown"
    parts = []
    for d in disks:
        info = d.get("info", {})
        mount = d.get("mount", "")
        total = info.get("total", 0)
        used = info.get("used", 0)
        pct = info.get("percent", 0)
        if total >= 1024:
            total_g = total / 1024
            used_g = used / 1024
            parts.append(f"{mount}: {used_g:.1f}/{total_g:.1f} GiB ({pct}%)")
        else:
            parts.append(f"{mount}: {used}/{total} MiB ({pct}%)")
    return "\n" + "\n".join(parts)


def color_palette():
    cols = [RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE,
            BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW,
            BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE]
    names = ["RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE",
             "BRED", "BGRN", "BYEL", "BBLU", "BMAG", "BCYN", "BWHT"]
    result = []
    for i, (c, n) in enumerate(zip(cols, names)):
        block = f"{c}██"
        if i > 0 and i % 7 == 0:
            result.append("\n")
        result.append(f"{block}{RESET} {n:<6} ")
    return "".join(result)


def bg_color_palette():
    bgs = [BG_RED, BG_GREEN, BG_YELLOW, BG_BLUE, BG_MAGENTA, BG_CYAN, BG_WHITE]
    names = ["BG_RED", "BG_GRN", "BG_YLW", "BG_BLU", "BG_MAG", "BG_CYN", "BG_WHT"]
    result = []
    for bg, name in zip(bgs, names):
        block = f"{bg}  {RESET}"
        result.append(f"{block} {name:<8} ")
    return "".join(result)


def render_logo(logo_name, theme):
    logo_raw = get_logo(logo_name)
    t = THEMES.get(theme, THEMES[DEFAULT_THEME])
    logo_color = t["logo_color"]
    accent_color = t["accent_color"]
    c = accent_color

    rendered = logo_raw.format(
        logo=logo_color,
        accent=accent_color,
        c=c,
    )

    return rendered


def render_info(modules, theme, cfg):
    t = THEMES.get(theme, THEMES[DEFAULT_THEME])
    label_color = t["label_color"]
    value_color = t["value_color"]
    sep_color = t["sep_color"]
    separator = cfg.get("separator", " -> ")
    padding = cfg.get("padding", 2)
    bold_labels = cfg.get("bold_labels", True)
    color_sep = cfg.get("color_separator", True)

    lines = []
    for mod in modules:
        label = MODULE_LABELS.get(mod, mod.replace("_", " ").title())
        value = get_module_value(mod)
        if value is None or value == "":
            continue

        if mod == "title":
            user = get_user()
            host = get_hostname()
            title = cfg.get("title")
            if title:
                display_text = title
            else:
                display_text = f"{user}@{host}"
            colored = colorize(display_text, label_color, bold=True)
            lines.append(colored)
            continue

        if mod == "user_at_host":
            colored = colorize(value, label_color, bold=True)
            lines.append(colored)
            continue

        sep = separator
        if color_sep:
            sep = f"{sep_color}{separator}{RESET}"

        pad = " " * padding if padding else " "
        label_str = label
        if bold_labels and not NO_COLOR:
            label_str = f"{BOLD}{label_color}{label}{RESET}"
        elif not NO_COLOR:
            label_str = f"{label_color}{label}{RESET}"

        val_str = value
        if not NO_COLOR:
            val_str = f"{value_color}{value}{RESET}"

        lines.append(f"{label_str}{sep}{pad}{val_str}")

    return lines


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.version:
        print(f"{__app_name__} v{__version__}")
        return 0

    if args.no_color:
        os.environ["NO_COLOR"] = "1"

    if args.list_logos:
        print(f"{BRIGHT_RED}Available Logos:{RESET}\n")
        logos = list_logos()
        for i, logo_name in enumerate(logos):
            print(f"  {BRIGHT_YELLOW}{logo_name}{RESET}")
        return 0

    if args.list_themes:
        print(f"{BRIGHT_RED}Available Themes:{RESET}\n")
        for name, info in THEMES.items():
            c = info["logo_color"]
            print(f"  {c}{name:<12}{RESET}  {info['name']}")
        return 0

    if args.gen_config:
        config_dir = os.path.expanduser(f"~/.config/{__app_name__}")
        config_path = os.path.join(config_dir, "config.json")
        path = write_example_config(config_path)
        print(f"Config written to: {path}")
        return 0

    if args.show_colors:
        print(f"{BRIGHT_RED}commiefetch Color Palette:{RESET}\n")
        print(color_palette())
        print()
        print(bg_color_palette())
        print()
        return 0

    cfg = load_config(args.config)

    # CLI overrides config
    if args.logo:
        cfg["logo"] = args.logo
    if args.theme:
        cfg["theme"] = args.theme
    if args.modules:
        cfg["modules"] = args.modules
    if args.separator:
        cfg["separator"] = args.separator
    if args.padding is not None:
        cfg["padding"] = args.padding
    if args.title:
        cfg["title"] = args.title

    logo_name = cfg.get("logo", "ussr")
    theme = cfg.get("theme", DEFAULT_THEME)
    modules = cfg.get("modules", DEFAULT_MODULES)
    padding = cfg.get("padding", 2)

    if logo_name == "random":
        import random
        logo_name = random.choice(list(LOGOS.keys()))

    logo_art = render_logo(logo_name, theme)
    info_lines = render_info(modules, theme, cfg)

    logo_lines = logo_art.split("\n")

    max_logo_width = max(len(line) for line in logo_lines)

    output_lines = []
    max_lines = max(len(logo_lines), len(info_lines))

    for i in range(max_lines):
        logo_line = logo_lines[i] if i < len(logo_lines) else ""
        info_line = info_lines[i] if i < len(info_lines) else ""

        if i == 0 and not info_line:
            output_lines.append(logo_line)
            continue

        if not info_line and logo_line:
            output_lines.append(logo_line)
            continue
        if not logo_line and info_line:
            pad_left = " " * (max_logo_width + padding)
            output_lines.append(f"{pad_left}{info_line}")
            continue

        if logo_line:
            pad_to = max_logo_width - len(logo_line) + padding
            if pad_to < 2:
                pad_to = 2
            output_lines.append(f"{logo_line}{' ' * pad_to}{info_line}")
        else:
            output_lines.append(f"{' ' * (max_logo_width + padding)}{info_line}")

    print()
    for line in output_lines:
        print(line)
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
