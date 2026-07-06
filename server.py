#!/usr/bin/env python3
"""ADS-B Radar Screensaver — minimal data server.

Serves radar.html + vendor/ and exposes:
  /api/aircraft -> your local readsb/dump1090 aircraft.json (real positions)
  /api/metar    -> {"raw": "METAR ..."} fetched from aviationweather.gov (cached)

No auth, no database, no external dependencies — Python 3 stdlib only.
Run it on the same machine as your ADS-B receiver:

    python3 server.py

Then point your screensaver (or browser) at http://<host>:8095/radar.html
"""
import json
import os
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ---------------------------------------------------------------------------
# CONFIG — adapt to your setup
# ---------------------------------------------------------------------------
PORT = int(os.environ.get('RADAR_PORT', 8095))

# readsb writes here by default; dump1090-fa uses /run/dump1090-fa/aircraft.json
AIRCRAFT_JSON = os.environ.get('RADAR_AIRCRAFT_JSON', '/run/readsb/aircraft.json')

# ICAO code of the airport whose METAR you want in the footer ('' disables it)
METAR_STATION = os.environ.get('RADAR_METAR_STATION', 'LEIB')
METAR_CACHE_S = 300  # aviationweather.gov updates METARs at most ~2x/hour
# ---------------------------------------------------------------------------

ROOT = os.path.dirname(os.path.abspath(__file__))
METAR_URL = ('https://aviationweather.gov/api/data/metar?ids={}&format=raw'
             .format(METAR_STATION))

MIME = {'.html': 'text/html; charset=utf-8',
        '.js': 'application/javascript',
        '.css': 'text/css',
        '.json': 'application/json',
        '.svg': 'image/svg+xml',
        '.png': 'image/png',
        '.woff2': 'font/woff2'}

_metar_cache = {'raw': '', 'ts': 0}


def get_metar():
    now = time.time()
    if now - _metar_cache['ts'] < METAR_CACHE_S:
        return _metar_cache['raw']
    req = urllib.request.Request(METAR_URL, headers={'User-Agent': 'adsb-radar-screensaver'})
    with urllib.request.urlopen(req, timeout=10) as r:
        raw = r.read().decode().strip()
    _metar_cache.update(raw=raw, ts=now)
    return raw


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/api/aircraft':
            try:
                with open(AIRCRAFT_JSON) as f:
                    self._json(json.load(f))
            except Exception as e:
                self._json({'error': str(e)}, 502)
            return
        if path == '/api/metar':
            if not METAR_STATION:
                self._json({'raw': ''})
                return
            try:
                self._json({'raw': get_metar()})
            except Exception as e:
                self._json({'error': str(e)}, 502)
            return
        if path == '/':
            path = '/radar.html'
        fpath = os.path.normpath(os.path.join(ROOT, path.lstrip('/')))
        if not fpath.startswith(ROOT) or not os.path.isfile(fpath):
            self.send_error(404)
            return
        ext = os.path.splitext(fpath)[1]
        with open(fpath, 'rb') as f:
            body = f.read()
        self.send_response(200)
        self.send_header('Content-Type', MIME.get(ext, 'application/octet-stream'))
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    print(f'ADS-B radar server on http://0.0.0.0:{PORT}/radar.html')
    print(f'  aircraft source: {AIRCRAFT_JSON}')
    print(f'  METAR station:   {METAR_STATION or "(disabled)"}')
    ThreadingHTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
