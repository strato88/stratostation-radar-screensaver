# ADS-B Radar Screensaver

Salvapantallas a pantalla completa estilo control de tráfico aéreo que muestra **tráfico aéreo
real en vivo** recibido por tu propia estación ADS-B — con barrido giratorio, estelas de posición,
etiquetas sin solapes, METAR en directo que se teclea solo como un teletipo, y números que ruedan
como una caja registradora.

![Salvapantallas radar ADS-B con 38 aeronaves reales sobre Ibiza](docs/screenshot.png)

**Demo en vivo (tráfico real sobre Ibiza, ahora mismo):**
https://strato88.duckdns.org/status/radar.html
· con costa: https://strato88.duckdns.org/status/radar-terrain.html

[English version →](README.md)

## Qué necesitas

- Un receptor ADS-B con **readsb** o **dump1090-fa** (cualquier montaje de Raspberry Pi + RTL-SDR
  sirve — si alimentas FlightRadar24/FlightAware/ADSBx casi seguro que ya lo tienes).
  El único requisito es el fichero estándar `aircraft.json` que escriben esos decodificadores.
- Python 3 (solo librería estándar, sin paquetes pip).
- Un Mac o PC con Windows para el salvapantallas en sí.

## Puesta en marcha

```bash
git clone https://github.com/strato88/stratostation-radar-screensaver.git
cd stratostation-radar-screensaver
```

1. **Configura el radar** — edita el bloque `CONFIG` al inicio del `<script>` de
   [radar.html](radar.html): latitud/longitud de tu receptor, alcance, etiqueta de estación,
   aeropuerto del METAR, idioma, velocidades de animación. Todo está comentado.

2. **Configura el servidor** — los valores por defecto funcionan con un readsb estándar.
   Se pueden cambiar con variables de entorno:

   | Variable | Por defecto | Función |
   |---|---|---|
   | `RADAR_PORT` | `8095` | puerto HTTP |
   | `RADAR_AIRCRAFT_JSON` | `/run/readsb/aircraft.json` | salida del decodificador (para dump1090-fa: `/run/dump1090-fa/aircraft.json`) |
   | `RADAR_METAR_STATION` | `LEIB` | código ICAO del METAR del pie (cadena vacía lo desactiva) |

3. **Arráncalo** en la máquina que recibe ADS-B:

   ```bash
   python3 server.py
   ```

   Abre `http://<host>:8095/radar.html` en un navegador para comprobar que funciona.
   Para dejarlo permanente, mira [examples/adsb-radar.service](examples/adsb-radar.service).

4. **(Opcional) publícalo** a través de tu proxy inverso / DNS dinámico si quieres que el
   salvapantallas funcione fuera de tu LAN. Los dos endpoints sirven datos públicos (las
   aeronaves emiten su posición en abierto; los METAR son públicos), pero revisa lo que expones
   como con cualquier servicio.

## Instalar el salvapantallas

### macOS — instalación rápida (compilado, sin configuración)

Descarga **[ADSB-Radar-Screensaver-macOS.zip](https://github.com/strato88/stratostation-radar-screensaver/releases/download/macos-v1.0/ADSB-Radar-Screensaver-macOS.zip)**,
descomprime y haz doble clic en `ADSB Radar.saver` — macOS ofrecerá instalarlo. Viene precargado
con el feed en vivo de Ibiza, y puedes apuntarlo a tu propio receptor desde **Opciones**. Al no
estar notarizado por Apple, si Gatekeeper lo bloquea ve a **Ajustes del Sistema → Privacidad y
Seguridad** y pulsa **Abrir de todos modos**. ¿Prefieres la
[vista minimal](#vista-minimal-sin-lista-de-aeronaves-ni-texto-de-pie) (sin lista de aeronaves
ni texto de pie)? Mismo panel de **Opciones** — sustituye `radar.html` por `radar-minimal.html`
al final de la URL.

### macOS — instalación manual (cargador genérico)

1. Descarga [WebViewScreenSaver](https://github.com/liquidx/webviewscreensaver/releases)
   (gratuito, código abierto) y haz doble clic en `WebViewScreenSaver.saver` para instalarlo.
   Si Gatekeeper protesta, autorízalo en **Ajustes del Sistema → Privacidad y Seguridad**.
2. **Ajustes del Sistema → Fondo de pantalla → Salvapantallas** → selecciona
   **WebViewScreenSaver** → **Opciones**:
   - Desmarca *Fetch URLs Remotely*.
   - En **Addresses**, borra la URL de ejemplo y añade la tuya:
     `http://<host>:8095/radar.html` (o tu URL pública HTTPS) — cambia a `radar-minimal.html`
     para la [vista minimal](#vista-minimal-sin-lista-de-aeronaves-ni-texto-de-pie).
   - Pon en *Seconds* un valor grande (p. ej. `999999`) — la página ya refresca sola sus datos.
3. Varias pantallas: activa **"Mostrar en todas las pantallas"** junto a la vista previa.

### Windows

1. Instala [Lively Wallpaper](https://rocksdanister.github.io/lively/) (gratuito, código
   abierto) — usa la versión **installer**, no la de Microsoft Store, para que el salvapantallas
   funcione sin tener la app abierta.
2. En Lively: **+** → pestaña **Webpage/URL** → pega tu URL del radar (usa `radar-minimal.html`
   en vez de `radar.html` para la [vista minimal](#vista-minimal-sin-lista-de-aeronaves-ni-texto-de-pie)).
3. Ajustes de Lively (engranaje) → pestaña **Screensaver** → activa usar el wallpaper actual
   como salvapantallas. Opcionalmente instala el `.scr` de Lively desde esa misma pestaña para
   elegirlo desde el diálogo nativo de salvapantallas de Windows.

## Vista minimal (sin lista de aeronaves ni texto de pie)

[radar-minimal.html](radar-minimal.html) es una alternativa reducida de `radar.html`: mismo radar en
vivo —anillos, barrido, estelas, etiquetas de cada aeronave, reloj— pero sin el panel de la lista/contador
de aeronaves (abajo a la izquierda) ni el texto de pie de página (línea kicker + METAR abajo en el centro).
Solo quedan el reloj, la fecha y la etiqueta de la estación en la esquina. Mismo bloque `CONFIG`, mismos
endpoints del servidor.

También incluye el overlay de costa de la vista con terreno de abajo (`CONFIG.coastUrl`, activado por
defecto con el ejemplo de Ibiza incluido) — pon `coastUrl: null` en su bloque `CONFIG` para desactivarlo.

## Vista con costa (overlay de terreno opcional)

[radar-terrain.html](radar-terrain.html) es una alternativa a `radar.html` — mismo radar en vivo, mismos
datos, pero con el contorno de la costa dibujado bajo los anillos para que la posición de cada aeronave
tenga una referencia geográfica, no solo un rumbo y una distancia en NM.

Lee la costa de `CONFIG.coastUrl` (por defecto `examples/coast-example.json`, un array JSON de cadenas
`[[lon, lat], ...]`, una por costa/isla). El ejemplo incluido cubre Ibiza/Formentera, el resto de las
Islas Baleares y la costa peninsular de Valencia/Alicante, suficiente para el alcance por defecto de
150 NM. Pon `coastUrl: null` en el bloque `CONFIG` para desactivar el overlay, o apúntalo a tu propia
región.

Para generar la costa de tu propia estación: consulta [Overpass API](https://overpass-api.de/api/interpreter)
pidiendo `way["natural"="coastline"]` dentro de un bounding box alrededor de tu receptor (`out geom;`
devuelve los puntos de cada segmento en línea), une los segmentos devueltos en cadenas continuas
emparejando extremos compartidos —OSM corta la costa en trozos arbitrarios en los límites de las
teselas— y simplifica. Douglas-Peucker normal conserva picos estrechos (espigones, marinas, muelles)
porque tienen mucha desviación perpendicular; usa **Visvalingam-Whyatt** en su lugar (elimina en cada
paso el vértice con menor área de triángulo, así los picos finos caen primero) y termina con una pasada
de suavizado Chaikin (corte de esquinas) para redondear las uniones que queden. Ese es exactamente el
proceso usado para generar el ejemplo incluido — solo Python estándar (`urllib`, `heapq`), sin
dependencias extra.

## Despliegue continuo (opcional)

[.github/workflows/deploy.yml](.github/workflows/deploy.yml) actualiza tu clon de producción cada
vez que cambia `main`, usando un **runner de GitHub Actions autohospedado** instalado en tu propio
servidor de la estación — nada corre en la nube de GitHub, y no necesitas abrir ningún puerto
entrante (el runner se conecta hacia afuera a GitHub, no al revés).

Es normal que un clon de producción tenga personalizaciones locales permanentes —un bloque `CONFIG`
editado a mano, páginas propias, lo que sea— que nunca van a coincidir con `main`. El workflow hace
fast-forward cuando puede, un merge real cuando los cambios de `main` y tus personalizaciones no
tocan las mismas líneas, y solo cuando de verdad chocan da marcha atrás limpiamente (nunca deja
marcadores de conflicto en vivo en un archivo que el servidor está sirviendo) y falla el job para
que te enteres. Resuélvelo a mano por SSH — como cualquier conflicto de git: `cd $DEPLOY_PATH`,
`git status`, arregla los archivos marcados, `git add`, `git commit`.

1. En el servidor, ve a **Settings → Actions → Runners → New self-hosted runner** de este repo y
   sigue los comandos de descarga/configuración que te da GitHub (elige el paquete según la
   arquitectura de tu servidor — `uname -m`: `aarch64` → arm64, `armv7l`/`armv6l` → arm, `x86_64` →
   x64). Instálalo como servicio para que sobreviva a reinicios:
   ```bash
   sudo ./svc.sh install
   sudo ./svc.sh start
   ```
2. Añade una **variable** de repositorio (Settings → Secrets and variables → Actions → Variables)
   llamada `DEPLOY_PATH` con la ruta absoluta de tu clon de producción en ese servidor, p. ej.
   `/home/pi/stratostation-radar-screensaver`. Si tus archivos de producción todavía no son un clon
   git, conviértelos primero: `git init`, `git add -A && git commit`, `git remote add origin <este
   repo>`, `git fetch origin`, y luego `git merge origin/main --allow-unrelated-histories` resolviendo
   los conflictos de tus archivos personalizados de la misma forma (`git checkout --ours <archivo>`
   conserva tu versión de producción intacta en ese merge inicial).
3. Si instalaste [examples/adsb-radar.service](examples/adsb-radar.service), el workflow intenta
   hacer `sudo systemctl restart adsb-radar.service` después de cada pull (no hace nada si no lo
   usas, y no falla el despliegue si el comando falla — el usuario del runner necesita `sudo` sin
   contraseña para ese comando concreto si quieres que el reinicio realmente ocurra).

Sin un runner registrado, el workflow simplemente se queda en cola sin hacer nada — es seguro
mergearlo aunque todavía no lo hayas configurado.

## Cómo funciona

- `server.py` (~100 líneas, solo stdlib) sirve la página estática, reenvía el `aircraft.json`
  de tu decodificador y cachea 5 minutos el METAR de
  [aviationweather.gov](https://aviationweather.gov/data/api/).
- `radar.html` es una única página autocontenida: un `<canvas>` pinta anillos, rumbos, barrido,
  estelas y blips a 60 fps; los datos se refrescan cada 10 s. Las etiquetas se colocan con un
  pequeño resolutor de colisiones que va probando posiciones en espiral hasta encontrar hueco,
  para que las rampas de aeropuerto densas sigan siendo legibles. Las aeronaves en tierra
  (o con altitud barométrica negativa) se muestran como `Ground`.
- Las fuentes ([Space Grotesk](https://github.com/floriankarsten/space-grotesk),
  [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono)) van incluidas en `vendor/`
  bajo licencia SIL Open Font License, así la página funciona sin peticiones externas.

## Licencia

[MIT](LICENSE). Fuentes bajo [SIL OFL 1.1](vendor/FONT-LICENSES.md).
