# ADS-B Radar Screensaver

A full-screen, ATC-style radar screensaver showing **real live air traffic** received by your own
ADS-B station — with a rotating sweep, position trails, non-overlapping labels, live METAR that
types itself out like a teletype, and numbers that roll like a cash register.

![ADS-B radar screensaver showing 30 live aircraft over Ibiza](docs/screenshot.png)

**Live demo (real traffic over Ibiza, right now):**
https://strato88.duckdns.org/status/radar.html

[Versión en español →](README.es.md)

## What you need

- An ADS-B receiver feeding **readsb** or **dump1090-fa** (any Raspberry Pi + RTL-SDR dongle setup
  works — if you feed FlightRadar24/FlightAware/ADSBx you almost certainly already have this).
  The only requirement is the standard `aircraft.json` file these decoders write.
- Python 3 (standard library only, no pip packages).
- A Mac or Windows PC for the screensaver itself.

## Quick start

```bash
git clone https://github.com/strato88/stratostation-radar-screensaver.git
cd stratostation-radar-screensaver
```

1. **Configure the radar** — edit the `CONFIG` block at the top of the `<script>` in
   [radar.html](radar.html): your receiver's latitude/longitude, range, station label,
   METAR airport, locale, animation speeds. Everything is commented.

2. **Configure the server** — defaults work for a stock readsb install. Override with
   environment variables if needed:

   | Variable | Default | Purpose |
   |---|---|---|
   | `RADAR_PORT` | `8095` | HTTP port |
   | `RADAR_AIRCRAFT_JSON` | `/run/readsb/aircraft.json` | decoder output (use `/run/dump1090-fa/aircraft.json` for dump1090-fa) |
   | `RADAR_METAR_STATION` | `LEIB` | ICAO code for the footer METAR (empty string disables it) |

3. **Run it** on the machine that receives ADS-B:

   ```bash
   python3 server.py
   ```

   Open `http://<host>:8095/radar.html` in a browser to check it works.
   To run it permanently, see [examples/adsb-radar.service](examples/adsb-radar.service).

4. **(Optional) expose it through your reverse proxy / dynamic DNS** if you want the screensaver
   to work outside your LAN. Note the two API endpoints are public data (aircraft broadcast
   their position in the clear; METARs are public), but review what you expose as with any service.

## Install the screensaver

### macOS

1. Download [WebViewScreenSaver](https://github.com/liquidx/webviewscreensaver/releases)
   (free, open source) and double-click `WebViewScreenSaver.saver` to install.
   If Gatekeeper complains, allow it under **System Settings → Privacy & Security**.
2. **System Settings → Wallpaper → Screen Saver** → select **WebViewScreenSaver** → **Options**:
   - Untick *Fetch URLs Remotely*.
   - In **Addresses**, remove the sample URL and add yours:
     `http://<host>:8095/radar.html` (or your public HTTPS URL).
   - Set *Seconds* to a large value (e.g. `999999`) — the page refreshes its own data.
3. Multiple displays: enable **"Show on all displays"** next to the preview.

### Windows

1. Install [Lively Wallpaper](https://rocksdanister.github.io/lively/) (free, open source) —
   use the **installer** version, not the Microsoft Store one, so the screensaver runs without
   the app open.
2. In Lively: **+** → **Webpage/URL** tab → paste your radar URL.
3. Lively settings (gear) → **Screensaver** tab → enable using the current wallpaper as
   screensaver. Optionally install Lively's `.scr` from the same tab to pick it from the native
   Windows screensaver dialog.

## How it works

- `server.py` (~100 lines, stdlib only) serves the static page, relays your decoder's
  `aircraft.json`, and caches the METAR from
  [aviationweather.gov](https://aviationweather.gov/data/api/) for 5 minutes.
- `radar.html` is a single self-contained page: a `<canvas>` renders rings, bearings, sweep,
  trails and blips at 60 fps; data refreshes every 10 s. Blip labels get placed by a small
  collision solver that spirals outwards until it finds free space, so dense airport ramps
  stay readable. Aircraft on the ground (or reporting negative baro altitude) show as `Ground`.
- Fonts ([Space Grotesk](https://github.com/floriankarsten/space-grotesk),
  [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono)) are bundled in `vendor/` under
  the SIL Open Font License so the page works with no external requests.

## License

[MIT](LICENSE). Fonts under the [SIL OFL 1.1](vendor/FONT-LICENSES.md).
