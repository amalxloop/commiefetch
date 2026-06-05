import os
import sys
import platform
import subprocess
import time
import shutil
import socket
import pwd
import grp
from pathlib import Path

from .colors import NO_COLOR


def is_termux():
    if bool(os.environ.get("TERMUX_VERSION")):
        return True
    if "/com.termux/" in __file__:
        return True
    if os.environ.get("PREFIX", "").startswith("/data/data/com.termux"):
        return True
    if os.path.exists("/data/data/com.termux/files/usr/bin/termux-setup-package"):
        return True
    return False

_cache = {}
_cache_time = {}
_cache_ttl = 5


def cached(name, ttl=30):
    def decorator(func):
        def wrapper(*args, **kwargs):
            now = time.time()
            if name in _cache and now - _cache_time.get(name, 0) < ttl:
                return _cache[name]
            result = func(*args, **kwargs)
            _cache[name] = result
            _cache_time[name] = now
            return result
        return wrapper
    return decorator


def run_cmd(cmd, timeout=3):
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


@cached("user", 3600)
def get_user():
    try:
        user = os.environ.get("USER") or os.environ.get("LOGNAME") or ""
        return user
    except Exception:
        return "unknown"


@cached("hostname", 3600)
def get_hostname():
    try:
        host = socket.gethostname()
        if host in ("localhost", "localhost.localdomain", ""):
            model = run_cmd(["getprop", "ro.product.model"], timeout=2)
            if model:
                return model.replace(" ", "-")
        return host
    except Exception:
        return platform.node() or "unknown"


@cached("os", 3600)
def get_os():
    system = platform.system()
    if is_termux():
        return f"Termux {os.environ.get('TERMUX_VERSION', '?')} on Android"
    if system == "Linux":
        info = ""
        os_release = "/etc/os-release"
        if os.path.exists(os_release):
            with open(os_release) as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        info = line.split("=", 1)[1].strip().strip('"')
                        break
        if not info:
            for f in ["/etc/arch-release", "/etc/debian_version",
                      "/etc/redhat-release", "/etc/SuSE-release",
                      "/etc/gentoo-release", "/etc/slackware-version",
                      "/etc/alpine-release"]:
                if os.path.exists(f):
                    with open(f) as fh:
                        info = fh.read().strip()
                    break
        if not info:
            info = f"Linux {platform.release()}"
        return info
    elif system == "Darwin":
        ver = platform.mac_ver()[0]
        codenames = {
            "14": "Sonoma", "13": "Ventura", "12": "Monterey",
            "11": "Big Sur", "10.16": "Big Sur", "10.15": "Catalina",
            "10.14": "Mojave", "10.13": "High Sierra",
        }
        codename = ""
        for k, v in codenames.items():
            if ver.startswith(k):
                codename = v
                break
        arch = platform.machine()
        info = f"macOS {ver}"
        if codename:
            info += f" ({codename})"
        return info
    elif system == "Windows":
        ver = platform.version()
        release = platform.release()
        return f"Windows {release} (build {ver})"
    elif system == "FreeBSD":
        ver = platform.release()
        return f"FreeBSD {ver}"
    elif system == "OpenBSD":
        ver = platform.release()
        return f"OpenBSD {ver}"
    elif system == "NetBSD":
        ver = platform.release()
        return f"NetBSD {ver}"
    else:
        return f"{system} {platform.release()}"


@cached("kernel", 3600)
def get_kernel():
    return platform.release()


@cached("uptime", 10)
def get_uptime():
    try:
        if is_termux():
            out = run_cmd(["uptime"], timeout=3)
            if out and "up" in out:
                import re
                m = re.search(r'up\s+(.+?)(?:,\s+\d+ users|,\s+load)', out)
                if m:
                    raw = m.group(1).strip()
                    parts = []
                    dm = re.search(r'(\d+)\s+days?', raw)
                    hm = re.search(r'(\d+):(\d+)', raw)
                    mm = re.search(r'(\d+)\s+min', raw)
                    if dm: parts.append(f"{dm.group(1)}d")
                    if hm:
                        parts.append(f"{hm.group(1)}h")
                        parts.append(f"{hm.group(2)}m")
                    elif mm:
                        parts.append(f"{mm.group(1)}m")
                    return " ".join(parts) if parts else raw
        if platform.system() == "Linux":
            try:
                with open("/proc/uptime") as f:
                    uptime_sec = float(f.read().split()[0])
            except Exception:
                return "unknown"
        elif platform.system() == "Darwin":
            out = run_cmd(["sysctl", "-n", "kern.boottime"])
            if out:
                import re
                m = re.search(r'sec = (\d+)', out)
                if m:
                    uptime_sec = time.time() - int(m.group(1))
                else:
                    uptime_sec = 0
            else:
                uptime_sec = 0
        elif platform.system() == "Windows":
            import ctypes
            lib = ctypes.windll.kernel32
            t = lib.GetTickCount64()
            uptime_sec = t / 1000
        elif platform.system() in ("FreeBSD", "OpenBSD", "NetBSD"):
            out = run_cmd(["sysctl", "-n", "kern.boottime"])
            uptime_sec = 0
            if out:
                import re
                m = re.search(r'sec = (\d+)', out)
                if m:
                    uptime_sec = time.time() - int(m.group(1))
        else:
            uptime_sec = 0

        days, rem = divmod(int(uptime_sec), 86400)
        hours, rem = divmod(rem, 3600)
        mins, secs = divmod(rem, 60)
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if mins > 0:
            parts.append(f"{mins}m")
        parts.append(f"{secs}s")
        return " ".join(parts)
    except Exception:
        return "unknown"


@cached("cpu", 3600)
def get_cpu():
    try:
        system = platform.system()
        if is_termux() or (system == "Linux" and not os.path.exists("/proc/cpuinfo")):
            name = run_cmd(["getprop", "ro.soc.model"], timeout=2)
            if not name:
                name = run_cmd(["getprop", "ro.chipname"], timeout=2)
            if not name:
                name = run_cmd(["getprop", "ro.board.platform"], timeout=2)
            cores = os.cpu_count() or 0
            if name:
                return f"{name} ({cores} cores)"
            out = run_cmd(["cat", "/proc/cpuinfo"], timeout=3)
            if out:
                for line in out.split("\n"):
                    if line.startswith("model name") or line.startswith("Hardware"):
                        name = line.split(":", 1)[1].strip()
                        return f"{name} ({cores} cores)"
            return f"Unknown ARM ({cores} cores)"
        if system == "Linux":
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.startswith("model name"):
                        name = line.split(":", 1)[1].strip()
                        cores = os.cpu_count() or 0
                        # get physical cores
                        phys = 0
                        try:
                            with open("/proc/cpuinfo") as f2:
                                phys = sum(
                                    1 for l in f2
                                    if l.startswith("cpu cores")
                                )
                        except Exception:
                            phys = cores
                        name = f"{name} ({cores} cores)"
                        return name
        elif system == "Darwin":
            brand = run_cmd(["sysctl", "-n", "machdep.cpu.brand_string"])
            cores = run_cmd(["sysctl", "-n", "hw.logicalcpu"])
            if brand:
                return f"{brand} ({cores} cores)"
        elif system == "Windows":
            import ctypes
            out = run_cmd(["wmic", "cpu", "get", "name"])
            if out:
                lines = out.strip().split("\n")
                if len(lines) > 1:
                    return lines[1].strip()
        elif system in ("FreeBSD", "OpenBSD", "NetBSD"):
            brand = run_cmd(["sysctl", "-n", "hw.model"])
            cores = run_cmd(["sysctl", "-n", "hw.ncpu"])
            if brand:
                return f"{brand} ({cores} cores)"
        return platform.processor() or "unknown"
    except Exception:
        return "unknown"


@cached("gpu", 3600)
def get_gpu():
    try:
        system = platform.system()
        if is_termux() or system == "Linux":
            if is_termux():
                renderer = run_cmd(["getprop", "ro.product.board"], timeout=2)
                if renderer:
                    return f"{renderer} (Android GPU)"
            out = run_cmd(
                ["lspci"], timeout=5
            )
            if out:
                for line in out.split("\n"):
                    if any(x in line.lower() for x in
                           ["vga", "3d", "display", "gpu"]):
                        name = line.split(":", 2)[-1].strip()
                        return name
            # try /sys
            try:
                gpu_dir = "/sys/class/drm"
                if os.path.exists(gpu_dir):
                    for d in sorted(os.listdir(gpu_dir)):
                        if "render" in d:
                            continue
                        dev_path = os.path.join(gpu_dir, d, "device")
                        if os.path.exists(dev_path):
                            vendor_file = os.path.join(
                                gpu_dir, d, "device", "vendor"
                            )
                            name_file = os.path.join(
                                gpu_dir, d, "device", "device"
                            )
                            if os.path.exists(vendor_file):
                                with open(vendor_file) as f:
                                    vendor = f.read().strip()
                                return f"GPU (vendor: {vendor})"
            except Exception:
                pass
        elif system == "Darwin":
            out = run_cmd(
                ["system_profiler", "SPDisplaysDataType"], timeout=10
            )
            if out:
                for line in out.split("\n"):
                    stripped = line.strip()
                    if "Chipset Model" in stripped:
                        return stripped.split(":")[-1].strip()
        elif system == "Windows":
            out = run_cmd(["wmic", "path", "win32_videocontroller",
                          "get", "name"])
            if out:
                lines = out.strip().split("\n")
                if len(lines) > 1:
                    return lines[1].strip()
        elif system in ("FreeBSD", "OpenBSD", "NetBSD"):
            out = run_cmd(["pciconf", "-lv"], timeout=5)
            if out:
                for line in out.split("\n"):
                    if "display" in line.lower() or "vga" in line.lower():
                        if "chip" in line.lower():
                            return line.split("=")[-1].strip().strip("'")
        return "unknown"
    except Exception:
        return "unknown"


@cached("memory", 5)
def get_memory():
    try:
        system = platform.system()
        if system == "Linux":
            meminfo = {}
            try:
                with open("/proc/meminfo") as f:
                    for line in f:
                        parts = line.split(":")
                        if len(parts) == 2:
                            val = parts[1].strip()
                            if val.endswith(" kB"):
                                val = int(val.split()[0]) // 1024
                            meminfo[parts[0]] = val
            except Exception:
                out = run_cmd(["cat", "/proc/meminfo"], timeout=3)
                if out:
                    for line in out.split("\n"):
                        parts = line.split(":")
                        if len(parts) == 2:
                            val = parts[1].strip()
                            if val.endswith(" kB"):
                                val = int(val.split()[0]) // 1024
                            meminfo[parts[0]] = val
            total = meminfo.get("MemTotal", 0)
            avail = meminfo.get("MemAvailable", 0)
            if total == 0:
                return {"total": 0, "used": 0, "unit": "MiB", "percent": 0}
            if avail == 0:
                free = meminfo.get("MemFree", 0)
                buffers = meminfo.get("Buffers", 0)
                cached = meminfo.get("Cached", 0)
                slab = meminfo.get("SReclaimable", 0)
                avail = free + buffers + cached + slab
            used = total - avail
            if used < 0:
                used = 0
            return {
                "total": total,
                "used": used,
                "available": avail,
                "unit": "MiB",
                "percent": round(used / total * 100, 1) if total else 0,
            }
        elif system == "Darwin":
            out = run_cmd(["vm_stat"])
            pagesize = run_cmd(["sysctl", "-n", "hw.pagesize"])
            memsize = run_cmd(["sysctl", "-n", "hw.memsize"])
            pagesize = int(pagesize) if pagesize else 4096
            memsize = int(memsize) if memsize else 0
            total_mb = memsize // (1024 * 1024)
            if out:
                free_pages = 0
                for line in out.split("\n"):
                    if "pages free" in line:
                        free_pages = int(line.split(":")[-1].strip().rstrip("."))
                        break
                used_mb = (memsize - free_pages * pagesize) // (1024 * 1024)
                return {
                    "total": total_mb,
                    "used": used_mb,
                    "unit": "MiB",
                    "percent": round(used_mb / total_mb * 100, 1) if total_mb else 0,
                }
            return {"total": total_mb, "used": 0, "unit": "MiB", "percent": 0}
        elif system == "Windows":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            mem = MEMORYSTATUSEX()
            mem.dwLength = ctypes.sizeof(mem)
            kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
            total_mb = mem.ullTotalPhys // (1024 * 1024)
            used_mb = (mem.ullTotalPhys - mem.ullAvailPhys) // (1024 * 1024)
            return {
                "total": total_mb,
                "used": used_mb,
                "unit": "MiB",
                "percent": round(used_mb / total_mb * 100, 1) if total_mb else 0,
            }
        elif system in ("FreeBSD", "OpenBSD", "NetBSD"):
            out = run_cmd(["sysctl", "-n", "hw.physmem"])
            total = int(out) // (1024 * 1024) if out else 0
            out2 = run_cmd(["sysctl", "-n", "vm.stats.vm.v_page_count"])
            out3 = run_cmd(["sysctl", "-n", "vm.stats.vm.v_free_count"])
            pagesize = run_cmd(["sysctl", "-n", "hw.pagesize"])
            if out2 and out3 and pagesize:
                total_pages = int(out2)
                free_pages = int(out3)
                ps = int(pagesize)
                total_mb = (total_pages * ps) // (1024 * 1024)
                used_mb = ((total_pages - free_pages) * ps) // (1024 * 1024)
                return {
                    "total": total_mb,
                    "used": used_mb,
                    "unit": "MiB",
                    "percent": round(used_mb / total_mb * 100, 1) if total_mb else 0,
                }
            return {"total": total, "used": 0, "unit": "MiB", "percent": 0}
        return {"total": 0, "used": 0, "unit": "MiB", "percent": 0}
    except Exception:
        return {"total": 0, "used": 0, "unit": "MiB", "percent": 0}


@cached("swap", 30)
def get_swap():
    try:
        system = platform.system()
        if system == "Linux":
            with open("/proc/meminfo") as f:
                total = 0
                free = 0
                for line in f:
                    if line.startswith("SwapTotal:"):
                        total = int(line.split()[1]) // 1024
                    elif line.startswith("SwapFree:"):
                        free = int(line.split()[1]) // 1024
            used = total - free
            return {
                "total": total,
                "used": used,
                "free": free,
                "unit": "MiB",
                "percent": round(used / total * 100, 1) if total else 0,
            }
        return None
    except Exception:
        return None


@cached("disk", 30)
def get_disk(path="/"):
    try:
        usage = shutil.disk_usage(path)
        total = usage.total // (1024 * 1024)
        used = usage.used // (1024 * 1024)
        free = usage.free // (1024 * 1024)
        return {
            "total": total,
            "used": used,
            "free": free,
            "unit": "MiB",
            "mount": path,
            "percent": round(used / total * 100, 1) if total else 0,
        }
    except Exception:
        if is_termux() and path == "/":
            out = run_cmd(["df", "-m", path], timeout=5)
            if out:
                for line in out.split("\n"):
                    parts = line.split()
                    if len(parts) >= 6 and parts[-1] == path:
                        total = int(parts[1])
                        used = int(parts[2])
                        return {
                            "total": total,
                            "used": used,
                            "free": total - used,
                            "unit": "MiB",
                            "mount": path,
                            "percent": round(used / total * 100, 1) if total else 0,
                        }
        return None


@cached("disks", 30)
def get_disks():
    system = platform.system()
    disks = []
    if system == "Linux":
        try:
            with open("/proc/mounts") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        dev, mount = parts[0], parts[1]
                        if dev.startswith("/dev/") and mount.startswith("/"):
                            info = get_disk(mount)
                            if info and info["total"] >= 1024:
                                disks.append({
                                    "device": dev,
                                    "mount": mount,
                                    "info": info,
                                })
            if not disks and is_termux():
                root = get_disk("/")
                if root and root["total"] >= 1024:
                    disks.append({
                        "device": "rootfs",
                        "mount": "/",
                        "info": root,
                    })
            return disks[:4]
        except Exception:
            pass
    elif system == "Darwin":
        out = run_cmd(["df", "-lk"])
        if out:
            for line in out.split("\n")[1:]:
                parts = line.split()
                if len(parts) >= 6 and parts[0].startswith("/dev/"):
                    total = int(parts[1]) // 1024
                    used = int(parts[2]) // 1024
                    mount = parts[-1]
                    if total >= 1024:
                        disks.append({
                            "device": parts[0],
                            "mount": mount,
                            "info": {
                                "total": total,
                                "used": used,
                                "free": total - used,
                                "unit": "MiB",
                                "mount": mount,
                                "percent": round(used / total * 100, 1) if total else 0,
                            },
                        })
        return disks[:4]
    elif system == "FreeBSD":
        out = run_cmd(["df", "-k"])
        if out:
            for line in out.split("\n")[1:]:
                parts = line.split()
                if len(parts) >= 6 and parts[0].startswith("/dev/"):
                    total = int(parts[1]) // 1024
                    used = int(parts[2]) // 1024
                    mount = parts[-1]
                    if total >= 1024:
                        disks.append({
                            "device": parts[0],
                            "mount": mount,
                            "info": {
                                "total": total,
                                "used": used,
                                "free": total - used,
                                "unit": "MiB",
                                "mount": mount,
                                "percent": round(used / total * 100, 1) if total else 0,
                            },
                        })
        return disks[:4]
    return disks


@cached("terminal", 3600)
def get_terminal():
    terms = os.environ.get("TERM_PROGRAM") or os.environ.get("TERM")
    if not terms and is_termux():
        terms = "Termux"
    return terms or "unknown"


@cached("shell", 3600)
def get_shell():
    return os.environ.get("SHELL", os.environ.get("ComSpec", "unknown"))


@cached("desktop", 3600)
def get_desktop():
    system = platform.system()
    if is_termux():
        return "Android (Termux)"
    if system == "Linux":
        de = os.environ.get("XDG_CURRENT_DESKTOP") or \
             os.environ.get("DESKTOP_SESSION") or \
             os.environ.get("GDMSESSION") or ""
        wm = os.environ.get("WINDOW_MANAGER") or ""
        if de:
            return de
        if wm:
            return wm
        return "unknown"
    elif system == "Darwin":
        return "Aqua"
    elif system == "Windows":
        return "Windows Explorer"
    return "unknown"


@cached("packages", 30)
def get_packages():
    system = platform.system()
    count = 0
    if is_termux():
        out = run_cmd(["dpkg", "--list"], timeout=5)
        if out:
            count = len([l for l in out.split("\n") if l.startswith("ii")])
        if not count:
            out = run_cmd(["apt", "list", "--installed", "2>/dev/null"], timeout=5)
            if out:
                count = len([l for l in out.split("\n") if "/" in l])
        return count or 0
    if system == "Linux":
        methods = [
            (["dpkg", "--list"], lambda l: len(l.split("\n")) - 5),
            (["rpm", "-qa"], lambda l: len(l.split("\n"))),
            (["pacman", "-Q"], lambda l: len(l.split("\n"))),
            (["xbps-query", "-l"], lambda l: len(l.split("\n"))),
            (["apk", "list", "--installed"], lambda l: len(l.split("\n")) - 1),
            (["equery", "list", "*"], lambda l: len(l.split("\n"))),
            (["nix-env", "-q"], lambda l: len(l.split("\n"))),
            (["flatpak", "list"], lambda l: len(l.split("\n")) - 1),
            (["snap", "list"], lambda l: len(l.split("\n")) - 1),
        ]
        for cmd, counter in methods:
            out = run_cmd(cmd, timeout=5)
            if out and out.strip():
                c = counter(out)
                if c > 0:
                    count += c
                    break
        return count if count else 0
    elif system == "Darwin":
        methods = [
            (["brew", "list", "--formula"], lambda l: len(l.split("\n"))),
            (["port", "list", "installed"], lambda l: len(l.split("\n")) - 1),
        ]
        for cmd, counter in methods:
            out = run_cmd(cmd, timeout=5)
            if out and out.strip():
                c = counter(out)
                if c > 0:
                    count += c
                    break
        return count if count else 0
    elif system == "FreeBSD":
        out = run_cmd(["pkg", "info"], timeout=5)
        if out:
            return len(out.split("\n"))
    return 0


@cached("resolution", 300)
def get_resolution():
    try:
        system = platform.system()
        if is_termux():
            out = run_cmd(["wm", "size"], timeout=3)
            if out:
                import re
                m = re.search(r'(\d+x\d+)', out)
                if m:
                    return m.group(1)
            out = run_cmd(["getprop", "ro.sf.lcd_density"], timeout=2)
            if out:
                phys = run_cmd(["getprop", "persist.sys.physicaldisplay.dimensions"], timeout=2)
                if phys:
                    return phys
            return "unknown"
        if system == "Linux":
            out = run_cmd(["xrandr"], timeout=5)
            if out:
                for line in out.split("\n"):
                    if " connected" in line and "x" in line:
                        import re
                        m = re.search(r'(\d+x\d+)', line)
                        if m:
                            return m.group(1)
            # try wlr-randr for wayland
            out = run_cmd(["wlr-randr"], timeout=5)
            if out:
                for line in out.split("\n"):
                    if "x" in line and any(c.isdigit() for c in line):
                        import re
                        m = re.search(r'(\d+x\d+)', line)
                        if m:
                            return m.group(1)
        elif system == "Darwin":
            out = run_cmd(
                ["system_profiler", "SPDisplaysDataType"], timeout=10
            )
            if out:
                for line in out.split("\n"):
                    if "Resolution" in line:
                        return line.split(":")[-1].strip()
        elif system == "Windows":
            import ctypes
            user32 = ctypes.windll.user32
            w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
            return f"{w}x{h}"
        return "unknown"
    except Exception:
        return "unknown"


@cached("de", 3600)
def get_de():
    return get_desktop()


@cached("wm", 3600)
def get_wm():
    system = platform.system()
    if is_termux():
        return "N/A (Android)"
    if system == "Linux":
        wm = os.environ.get("WINDOW_MANAGER") or ""
        if wm:
            return wm

        out = run_cmd(["wmctrl", "-m"], timeout=3)
        if out:
            for line in out.split("\n"):
                if "Name:" in line:
                    return line.split(":")[-1].strip()

        procs = run_cmd(["pgrep", "-l", "."], timeout=3)
        if not procs:
            try:
                procs = ""
                for f in Path("/proc").iterdir():
                    if f.is_dir() and (f / "comm").exists():
                        name = (f / "comm").read_text().strip()
                        procs += name + "\n"
            except Exception:
                procs = ""

        if procs:
            proc_names = set()
            for line in procs.splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = line.split(None, 1)
                if len(parts) == 2 and parts[0].isdigit():
                    proc_names.add(parts[1])
                else:
                    proc_names.add(line)
            wm_names = (
                "i3", "sway", "hyprland", "bspwm", "dwm", "awesome",
                "qtile", "xmonad", "herbstluftwm", "spectrwm", "ratpoison",
                "stumpwm", "openbox", "fluxbox", "icewm", "fvwm", "fvwm2",
                "fvwm3", "windowmaker", "afterstep", "enlightenment",
                "blackbox", "pekwm", "sawfish", "twm", "cwm", "wm2",
                "kwin_x11", "kwin_wayland", "weston", "river", "wayfire",
                "niri", "labwc", "dwl", "hikari", "marco", "muffin",
                "xfwm4", "budgie-wm", "deepin-wm", "compiz", "gnome-shell",
            )
            for name in wm_names:
                if name in proc_names:
                    return name

        if os.environ.get("WAYLAND_DISPLAY"):
            return "Wayland"
        if os.environ.get("DISPLAY"):
            return "X11"

        return "unknown"
    return "unknown"


@cached("cpu_temp", 30)
def get_cpu_temp():
    try:
        system = platform.system()
        if system == "Linux":
            thermal = "/sys/class/thermal"
            if os.path.exists(thermal):
                temps = []
                for d in sorted(os.listdir(thermal)):
                    if d.startswith("thermal_zone"):
                        temp_file = os.path.join(thermal, d, "temp")
                        if os.path.exists(temp_file):
                            with open(temp_file) as f:
                                raw = f.read().strip()
                                if raw:
                                    temps.append(int(raw) // 1000)
                if temps:
                    return f"{max(temps)}°C"
        return "unknown"
    except Exception:
        return "unknown"


@cached("processes", 10)
def get_processes():
    try:
        system = platform.system()
        if system == "Linux":
            pids = os.listdir("/proc")
            count = sum(1 for p in pids if p.isdigit())
            return count
        elif system == "Darwin":
            out = run_cmd(["ps", "-A", "--no-headers"], timeout=5)
            return len(out.split("\n")) if out else 0
        elif system in ("FreeBSD", "OpenBSD", "NetBSD"):
            out = run_cmd(["ps", "-a", "-x", "-o", "pid"], timeout=5)
            return len(out.split("\n")) - 1 if out else 0
        return 0
    except Exception:
        return 0


@cached("local_ip", 60)
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unknown"


@cached("public_ip", 3600)
def get_public_ip():
    out = run_cmd(
        ["curl", "-s", "--max-time", "5", "https://ipv4.icanhazip.com"],
        timeout=6
    )
    if out and out.strip():
        return out.strip()
    out2 = run_cmd(
        ["curl", "-s", "--max-time", "5", "https://api.ipify.org"],
        timeout=6
    )
    return out2.strip() if out2 else "unknown"


@cached("battery", 30)
def get_battery():
    try:
        system = platform.system()
        if is_termux():
            out = run_cmd(["termux-battery-status"], timeout=5)
            if out:
                import json
                try:
                    data = json.loads(out)
                    pct = data.get("percentage", "?")
                    plug = data.get("plugged", "")
                    status = data.get("status", "")
                    plug_str = f" ({plug})" if plug else ""
                    return f"{pct}%{plug_str}"
                except Exception:
                    pass
        if system == "Linux":
            power = "/sys/class/power_supply"
            if os.path.exists(power):
                for d in os.listdir(power):
                    if "BAT" in d.upper() or "battery" in d.lower():
                        bat_dir = os.path.join(power, d)
                        capacity_file = os.path.join(bat_dir, "capacity")
                        status_file = os.path.join(bat_dir, "status")
                        if os.path.exists(capacity_file):
                            with open(capacity_file) as f:
                                cap = f.read().strip()
                            status = ""
                            if os.path.exists(status_file):
                                with open(status_file) as f:
                                    status = f.read().strip()
                            return f"{cap}% ({status})"
        elif system == "Darwin":
            out = run_cmd(["pmset", "-g", "batt"], timeout=5)
            if out:
                for line in out.split("\n"):
                    if "InternalBattery" in line or "Battery" in line:
                        import re
                        m = re.search(r'(\d+)%', line)
                        if m:
                            return f"{m.group(1)}%"
        elif system == "Windows":
            out = run_cmd(
                ["wmic", "path", "Win32_Battery",
                 "get", "EstimatedChargeRemaining"]
            )
            if out:
                lines = out.strip().split("\n")
                if len(lines) > 1 and lines[1].strip():
                    return f"{lines[1].strip()}%"
        return "unknown"
    except Exception:
        return "unknown"


@cached("locale", 3600)
def get_locale():
    for v in ["LANG", "LC_ALL", "LC_CTYPE"]:
        val = os.environ.get(v)
        if val:
            return val
    return "unknown"
