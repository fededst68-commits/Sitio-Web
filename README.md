# Kit de edición de reels · De Stefano Insumos

Herramientas para armar los reels verticales de Instagram a partir de tomas de video, fotos, música y la gráfica de la marca.
Lo usa el asistente que produce la serie. El manual con las reglas de la serie no está acá: vive en el proyecto privado de Claude.

## Qué hay

| Archivo | Para qué |
|---|---|
| `build.py` | Arma el reel (1080×1920, 24 fps, H.264) desde un `cfg.json`: cortes de voz, fotos, subtítulos, logo, placa final y música. |
| `asr.py` | Transcribe una toma con tiempos por palabra, para controlar que diga el guion completo y una sola vez. |
| `env.py` | Mide tramos de voz y pausas, para decidir cortes. |
| `contact.py` | Hoja de control con cuadros del video. |
| `hoja_casting.py` | Hoja numerada de opciones, para elegir por número. |
| `puente.sh` | Trae archivos a la sesión por la rama `puente-instagram`. |
| `setup.sh` | Deja lista una sesión nueva. |
| `fonts/` | Tipografía Archivo (licencia SIL OFL 1.1, ver `fonts/OFL.txt`). |
| `marca/`, `fotos/`, `musica/`, `personajes/` | Logo, fotos de producto, cortinas y cuadros iniciales de cada personaje (plano general, primer plano y calle). |
| `reels/NN_tema/cfg.json` | La receta de cada reel terminado. |

## Uso

```bash
bash setup.sh                                  # una vez por sesión
mkdir -p trabajo/reelNN                        # tomas del reel; esta carpeta no se guarda en el repositorio
python3 asr.py trabajo/reelNN/A.mp4            # texto y tiempos por palabra
python3 -I env.py trabajo/reelNN/A.mp4         # tramos de voz y pausas
python3 -I build.py reels/NN_tema/cfg.json     # resultado en reels/NN_tema/out/
```

Para traer archivos de internet (tomas, imágenes, música):

```bash
printf 'A.mp4\t%s\n' 'https://…url completa…' > lista.tsv
bash puente.sh lista.tsv trabajo/reelNN
```

## El `cfg.json`

Las rutas relativas se resuelven contra la carpeta del kit. Los tiempos se escriben en el reloj de cada toma.

- `takes`: las tomas, por ejemplo `{"A": "trabajo/reel02/A.mp4", "B": "trabajo/reel02/B.mp4"}`.
- `audio`: lista ordenada de tramos `[toma, desde, hasta]`. Define el reloj del reel: acá se recortan pausas largas y repeticiones.
- `gains` (opcional): decibeles por toma, por ejemplo `{"C": -1.6}`, para que la voz suene igual de fuerte en todas. Se mide con `ebur128` sobre cada tramo de `tmp/voice.wav` después de un armado; conviene emparejar por LUFS, no por picos.
- `video`: lista ordenada de lo que se ve. Cada elemento dura hasta que empieza el siguiente.
  - Toma: `{"take": "A", "at": ["A", 5.86], "zoom": 1.15}`. `zoom` es opcional (acercamiento); `zoom_y` mueve el encuadre (0 arriba, 1 abajo).
  - Zoom repentino: `{"take": "D", "at": ["D", 3.90], "zoom": 1.42, "zoom_from": 1.0, "zoom_ramp": 0.33, "zoom_y": 0.34}`. El elemento arranca en `zoom_from` y llega a `zoom` en `zoom_ramp` segundos (rápido al principio, frena al final). Queda mejor dentro de una pausa corta, para que llegue justo antes de la frase que se quiere marcar.
  - Las tomas de 1080 de ancho van sin realce de nitidez; las de 720 se agrandan con un realce suave.
  - Foto: `{"photo": "fotos/caja.jpg", "at": ["A", 10.86], "tag": "prod"}`. Con `"tag": "prod"` muestra la etiqueta del producto.
  - Cada `at` tiene que caer dentro de un tramo de `audio`. Si se corta el audio de una toma mientras se ve la cara, hay que empezar ahí un elemento nuevo de video.
- `captions`: subtítulos, `{"take": "A", "t0": 7.15, "t1": 8.74, "parts": [["si es", 0], ["embutido inmediato", 1]]}`. El `1` resalta.
- `endcard_at`: `[toma, tiempo]` en que entra la placa final. `endcard_seconds`: cuánto dura. `lift_lead`: cuánto antes empieza a subir la música.
- `music`: `{"file": "musica/rock.mp3"}`. Se usa el final de la pista, para que termine junto con el reel. `bed_lufs`: nivel bajo la voz (por defecto −33).
- Textos de la gráfica: `serie`, `tag_prod`, `endcard_title`, `endcard_sub`, `whatsapp`, `web`. Logo: `logo`.

`reels/01_fibrosa-EI/cfg.json` es un ejemplo completo. `cfg_v6.json`, en la misma carpeta, combina una caminata en la calle, un zoom repentino y un primer plano.

No correr dos armados del mismo reel a la vez: escriben los mismos archivos y el resultado sale roto.
