# commiefetch ☭

> communist-themed system information tool — like neofetch, but red.

**commiefetch** displays your system info with communist iconography, red color
schemes, and configurable output. Works on **Linux**, **macOS**, **Windows**,
**FreeBSD**, **OpenBSD**, and **NetBSD**.

## Quick start

```bash
# run directly
python3 commiefetch

# install globally (Linux/macOS/BSD)
make install

# or install for current user
make install-user

# or via pip
pip install -e .
```

## Usage

```bash
commiefetch                    # default (USSR logo, soviet theme)
commiefetch -l prc -t china    # PRC logo + China theme
commiefetch -l random          # random logo
commiefetch --list-logos       # show all available logos
commiefetch --list-themes      # show all color themes
commiefetch --no-color         # plain output
commiefetch -m os kernel cpu memory  # pick specific modules
commiefetch --gen-config       # create ~/.config/commiefetch/config.json
commiefetch -c my-config.json  # use custom config
commiefetch --show-colors      # display color palette
```

## Logos

| Flag          | Description                          |
|---------------|--------------------------------------|
| `ussr`        | Hammer & sickle CCCP                 |
| `soviet_star` | Red star with hammer & sickle        |
| `cccp_shield` | Shield-style CCCP logo               |
| `hammer_sickle` | Minimal hammer & sickle            |
| `red_flag`    | Soviet red flag                      |
| `prc`         | People's Republic of China           |
| `prc_flag`    | PRC flag with stars                  |
| `cuba`        | Republic of Cuba                     |
| `dprk`        | Democratic People's Republic of Korea|
| `vietnam`     | Socialist Republic of Vietnam        |
| `east_germany`| German Democratic Republic (DDR)     |
| `laos`        | Lao PDR                             |
| `mao`         | Mao Zedong themed                     |
| `anarcho`     | Anarcho-communist A-in-circle         |
| `tankie`      | T-34 tank                            |
| `simple_commie` | Minimal communist text             |
| `small_hammer` | Compact hammer & sickle            |
| `random`      | Pick one at random                   |

## Themes

| Theme       | Description              |
|-------------|--------------------------|
| `soviet`    | Red & yellow, USSR style |
| `china`     | Red & gold, PRC style    |
| `cuba`      | Blue, red & white        |
| `vietnam`   | Yellow & red             |
| `dprk`      | Red, white & blue        |
| `anarcho`   | Red & black              |
| `retro`     | Yellow & red retro       |
| `minimal`   | Monochrome, no colors    |

## Modules

`title`, `os`, `host`, `kernel`, `uptime`, `packages`, `shell`, `de`, `wm`,
`terminal`, `cpu`, `gpu`, `memory`, `disk`, `disks`, `swap`, `battery`,
`processes`, `local_ip`, `public_ip`, `resolution`, `locale`, `cpu_temp`,
`user_at_host`

## Configuration

Config files are loaded from (in order):
1. `~/.config/commiefetch/config.json` (or `.toml`, `.ini`)
2. `./configs/config.*`
3. `/etc/commiefetch/config.*`

Generate a config:

```bash
commiefetch --gen-config
# writes to ~/.config/commiefetch/config.json
```

### JSON config

```json
{
  "logo": "ussr",
  "theme": "soviet",
  "separator": " -> ",
  "color_separator": true,
  "bold_labels": true,
  "padding": 2,
  "modules": ["title", "os", "cpu", "memory"]
}
```

### TOML config

```toml
logo = "prc"
theme = "china"
separator = " :: "
modules = ["title", "os", "host", "kernel", "cpu", "memory"]
```

## Cross-platform

| Feature      | Linux | macOS | Windows | BSDs |
|--------------|-------|-------|---------|------|
| OS info      | ✓     | ✓     | ✓       | ✓    |
| Kernel       | ✓     | ✓     | ✓       | ✓    |
| CPU          | ✓     | ✓     | ✓       | ✓    |
| GPU          | ✓     | ✓     | ✓       | ✓    |
| Memory       | ✓     | ✓     | ✓       | ✓    |
| Disk         | ✓     | ✓     | partial | ✓    |
| Uptime       | ✓     | ✓     | ✓       | ✓    |
| Packages     | ✓     | ✓     | ✗       | ✓    |
| Battery      | ✓     | ✓     | ✓       | ✗    |
| Resolution   | ✓     | ✓     | ✓       | ✗    |

## License

MIT — use it, share it, comrade.
