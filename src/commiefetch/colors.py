import os
import sys

NO_COLOR = os.environ.get("NO_COLOR") or not sys.stdout.isatty()

RESET = "\033[0m" if not NO_COLOR else ""
BOLD = "\033[1m" if not NO_COLOR else ""
DIM = "\033[2m" if not NO_COLOR else ""
ITALIC = "\033[3m" if not NO_COLOR else ""
BLINK = "\033[5m" if not NO_COLOR else ""

BLACK = "\033[30m" if not NO_COLOR else ""
RED = "\033[31m" if not NO_COLOR else ""
GREEN = "\033[32m" if not NO_COLOR else ""
YELLOW = "\033[33m" if not NO_COLOR else ""
BLUE = "\033[34m" if not NO_COLOR else ""
MAGENTA = "\033[35m" if not NO_COLOR else ""
CYAN = "\033[36m" if not NO_COLOR else ""
WHITE = "\033[37m" if not NO_COLOR else ""

BRIGHT_RED = "\033[91m" if not NO_COLOR else ""
BRIGHT_GREEN = "\033[92m" if not NO_COLOR else ""
BRIGHT_YELLOW = "\033[93m" if not NO_COLOR else ""
BRIGHT_BLUE = "\033[94m" if not NO_COLOR else ""
BRIGHT_MAGENTA = "\033[95m" if not NO_COLOR else ""
BRIGHT_CYAN = "\033[96m" if not NO_COLOR else ""
BRIGHT_WHITE = "\033[97m" if not NO_COLOR else ""

BG_RED = "\033[41m" if not NO_COLOR else ""
BG_GREEN = "\033[42m" if not NO_COLOR else ""
BG_YELLOW = "\033[43m" if not NO_COLOR else ""
BG_BLUE = "\033[44m" if not NO_COLOR else ""
BG_MAGENTA = "\033[45m" if not NO_COLOR else ""
BG_CYAN = "\033[46m" if not NO_COLOR else ""
BG_WHITE = "\033[47m" if not NO_COLOR else ""

THEMES = {
    "soviet": {
        "name": "Soviet Union",
        "logo_color": BRIGHT_RED,
        "label_color": BRIGHT_RED,
        "value_color": BRIGHT_WHITE,
        "accent_color": YELLOW,
        "sep_color": RED,
    },
    "china": {
        "name": "PRC",
        "logo_color": RED,
        "label_color": RED,
        "value_color": BRIGHT_YELLOW,
        "accent_color": YELLOW,
        "sep_color": RED,
    },
    "cuba": {
        "name": "Cuba",
        "logo_color": BRIGHT_BLUE,
        "label_color": RED,
        "value_color": BRIGHT_WHITE,
        "accent_color": BLUE,
        "sep_color": RED,
    },
    "vietnam": {
        "name": "Vietnam",
        "logo_color": YELLOW,
        "label_color": RED,
        "value_color": BRIGHT_YELLOW,
        "accent_color": YELLOW,
        "sep_color": RED,
    },
    "dprk": {
        "name": "DPRK",
        "logo_color": RED,
        "label_color": RED,
        "value_color": BRIGHT_WHITE,
        "accent_color": BRIGHT_BLUE,
        "sep_color": RED,
    },
    "anarcho": {
        "name": "Anarcho-Communism",
        "logo_color": RED,
        "label_color": RED,
        "value_color": BRIGHT_WHITE,
        "accent_color": BLACK,
        "sep_color": RED,
    },
    "minimal": {
        "name": "Minimal",
        "logo_color": WHITE,
        "label_color": WHITE,
        "value_color": WHITE,
        "accent_color": WHITE,
        "sep_color": DIM,
    },
    "retro": {
        "name": "Retro Soviet",
        "logo_color": YELLOW,
        "label_color": BRIGHT_RED,
        "value_color": BRIGHT_YELLOW,
        "accent_color": RED,
        "sep_color": YELLOW,
    },
}

DEFAULT_THEME = "soviet"


def apply_theme(theme_name="soviet"):
    t = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    return t


def colorize(text, color, bold=False):
    if NO_COLOR:
        return text
    return f"{BOLD if bold else ''}{color}{text}{RESET}"
