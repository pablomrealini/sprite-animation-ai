# Banco de efectos

Una página aparte del juego para comparar cómo se dibujan el fogonazo y los impactos del blaster del ranger: el código de hoy, los sprites de IA de `backgrounds/ranger_fx` o la mezcla de los dos. La investigación que la motivó está en [`reports/Fogonazos y efectos de disparo.md`](../../reports/Fogonazos%20y%20efectos%20de%20disparo.md).

```bash
uv run --project pipeline python prototypes/fx_lab/build.py
```

Mide el atlas del ranger con la misma función que el juego (`measure` de `prototypes/build.py`, sin tocarlo), achica las piezas de `backgrounds/ranger_fx/post/` a un tercio con su ancla y deja `dist/index.html`. Se abre con doble clic en Chrome, o con el servidor `fx-lab` de `.claude/launch.json` (puerto 8769).

El ranger dispara en loop contra un bloque con la cadencia del juego. Los valores por defecto reproducen el juego; el botón **La elegida** pone la mezcla que se eligió. Teclas: <kbd>1</kbd> <kbd>2</kbd> <kbd>3</kbd> técnica, <kbd>V</kbd> vista (una con lupa ×4 o las tres en fila), <kbd>Espacio</kbd> pausa, <kbd>→</kbd> un frame, <kbd>G</kbd> guías.

- **Código (hoy):** el `drawFlash` del juego copiado sin cambios, más el destello redondo y los cuadrados de cada impacto.
- **Sprites IA:** sólo las piezas de las hojas.
- **Mezcla:** las piezas, más un halo sumado y tres chispas en la boca, y en el impacto un destello y chispas hacia atrás (o siguiendo la bala).
- **Ancla:** "queda donde salió" es el juego de hoy; "sigue al arma" lee la boca del frame en pantalla y le suma los 3 px que el juego hunde al ranger en el piso (`FOOT_SINK`), que la copia del juego del fx_lab no suma (en el juego ya lo corrige `muzzleAt`).
- **Destello del clip:** "sacado" cambia el frame de disparo que trae el destello del video por el anterior del clip.

## La elegida (2026-10-16)

| | Valor |
|---|---|
| Técnica | Mezcla |
| Fogonazo | Hoja `muzzle/gpt-image-2.5-sunburst-fal_2`; las 3 formas se turnan (1-2-3). Primer dibujo 2 frames y segundo dibujo 3 frames a 60 Hz (83 ms: a 12 tiros/s queda en loop mientras se dispara). 26 px de largo (0,25 H), ×1,3 a dos manos |
| Impacto | Hoja `impact/gpt-image-2.5-sunburst-fal_1`; las dos filas se turnan. 4 dibujos de 2 frames (133 ms), 50 px de alto (0,49 H) |
| Color | Normal (los dibujos); suma de color sólo para el halo, el destello y las chispas |
| Chispas del impacto | Hacia el tirador, como Blazing Chrome |
| Ancla | Sigue al arma |
| Destello del clip | Sacado |

## Pasar la elegida al juego

Los cambios de abajo se probaron sobre una copia del juego del 2026-10-16 (el `src.html` con los cambios sin commitear de ese día). La copia, con todo aplicado, quedó en `dist/juego/index.html`. No se mantiene: es para verlo andando.

El juego ya trae `muzzleAt(frame, footY)` (la agregó la sesión de saltos): la boca en el mundo con el hundido en el piso (`FOOT_SINK`) y el squash del salto, la misma cuenta que `drawSprite`. `fire()` la usa, así que la bala ya sale de la lente; el fogonazo la usa a través de `muzzleNow()`. Los cambios se volvieron a probar con esa versión: son 12.

### 1. `prototypes/build.py`

Al lado de `BACKGROUNDS`, la hoja elegida de cada efecto y su tamaño en px del juego con el ranger al 80%:

```python
# efectos de spritepipe gen-images (backgrounds/<set>/post/), elegidos en prototypes/fx_lab: la hoja de cada efecto y su
# tamaño en px del juego con el personaje al 80%. El fogonazo se mide por el ancho medio de sus primeros dibujos; el
# impacto, por el alto medio de los más grandes (los 2)
FX = {
    "ranger": {
        "set": "ranger_fx",
        "muzzle": {"opt": "gpt-image-2.5-sunburst-fal_2", "len": 26, "ref": ("w", ["a1", "a2", "a3"])},
        "impact": {"opt": "gpt-image-2.5-sunburst-fal_1", "len": 50, "ref": ("h", ["a2", "b2"])},
    },
}
```

Dos funciones, después de `export_backgrounds`:

```python
def fx_anchor(a: np.ndarray, where: str) -> tuple[float, float]:
    """El punto que va en la boca (fogonazo: el borde izquierdo) o en el contacto (impacto: el centro del primer
    frame y la punta derecha de los demás), en px de la imagen."""
    ys, xs = np.nonzero(a >= 128)
    if where == "center":
        return float(xs.mean()), float(ys.mean())
    edge = int(xs.min()) if where == "left" else int(xs.max())
    band = max(2, round(0.04 * a.shape[1]))   # las filas de la punta, en el 4% del ancho más cerca del borde
    cols = slice(edge, edge + band) if where == "left" else slice(edge - band + 1, edge + 1)
    return float(edge), float(np.nonzero((a[:, cols] >= 128).any(1))[0].mean())


def export_fx(name: str, dist: Path) -> dict:
    """Achica las piezas elegidas a EXPORT px por px del juego; devuelve su tamaño y su ancla en px del juego."""
    cfg = FX[name]
    post, out = ROOT / "backgrounds" / cfg["set"] / "post", dist / "fx"
    out.mkdir(exist_ok=True)
    data = {}
    for asset in ("muzzle", "impact"):
        c = cfg[asset]
        pieces = {p.stem: Image.open(p).convert("RGBA") for p in sorted((post / asset / c["opt"]).glob("*.png"))}
        axis, ref = c["ref"]
        k = c["len"] / float(np.mean([pieces[r].width if axis == "w" else pieces[r].height for r in ref]))
        data[asset] = {"len": c["len"], "pieces": {}}
        for piece, im in pieces.items():
            a = np.asarray(im).copy()
            a[..., 3][a[..., 3] >= 250] = 255   # GPT Image llega a 254: lo opaco, opaco
            im = Image.fromarray(a, "RGBA").convert("RGBa")   # premultiplicado, como export_image
            im = im.resize((max(1, round(im.width * k * EXPORT)), max(1, round(im.height * k * EXPORT))), Image.LANCZOS).convert("RGBA")
            im.save(out / f"{asset}_{piece}.png", optimize=True)
            where = "left" if asset == "muzzle" else "center" if piece.endswith("1") else "right"
            ax, ay = fx_anchor(np.asarray(im)[..., 3], where)
            data[asset]["pieces"][piece] = {"src": f"fx/{asset}_{piece}.png", "w": round(im.width / EXPORT, 2),
                                            "h": round(im.height / EXPORT, 2), "ax": round(ax / EXPORT, 2),
                                            "ay": round(ay / EXPORT, 2)}
    return data
```

Y en `main()`, después del reemplazo de `__BG_DATA__`:

```python
    if name in FX:
        html = html.replace("__FX_DATA__", json.dumps(export_fx(name, dist), separators=(",", ":")))
```

Las piezas viven en `backgrounds/ranger_fx/post/`, que está en `.gitignore`. Para que el build ande en otra máquina hay que agregar las dos carpetas elegidas con `git add -f` (como las elegidas de `ranger_base`): `backgrounds/ranger_fx/post/muzzle/gpt-image-2.5-sunburst-fal_2/` y `backgrounds/ranger_fx/post/impact/gpt-image-2.5-sunburst-fal_1/`.

### 2. `prototypes/ranger/src.html`

**Los datos y las imágenes**, después de `const BG = __BG_DATA__;`:

```js
// efectos de backgrounds/ranger_fx (spritepipe gen-images), los elegidos en prototypes/fx_lab: por pieza, tamaño y
// ancla en px del juego con el personaje al 80% (prototypes/build.py los achica a fx/)
const FX = __FX_DATA__;
const FX_IMG = {};
for (const [asset, A] of Object.entries(FX)) for (const [name, p] of Object.entries(A.pieces)) { const im = new Image(); im.src = p.src; FX_IMG[`${asset}/${name}`] = im; }
// la mezcla elegida (2026-10-16), en frames de 60 Hz: el fogonazo, 2 del primer dibujo y 3 del segundo; el impacto, 2 por dibujo
const FXT = { flashA: 2 / 60, flashB: 3 / 60, impact: 2 / 60 };
```

**Sin el destello del clip.** `shotFrame` cambia el frame marcado por el anterior del clip:

```js
// el frame con el destello que dibujó el modelo de video (cortado por la limpieza) se cambia por el anterior del clip
const noBaked = (n, i) => (anim(n).f[i][11] ? (i + anim(n).f.length - 1) % anim(n).f.length : i);
const shotFrame = (n, t, per) => { const s = SHOT(n); return noBaked(n, t < per ? s[Math.min(s.length - 1, Math.floor(t / (per / s.length)))] : s[s.length - 1]); };
```

**`impact()` y la boca en pantalla.** Reemplazá `function impact(…)` por esto. El impacto lleva su fila (se turnan) y tira las chispas hacia el tirador; `muzzleNow()` es la boca del frame que está en pantalla, con la cuenta de `muzzleAt`:

```js
let shotN = 0, hitN = 0;
// impacto: el dibujo de 4 frames (las dos filas de la hoja se turnan) y chispas hacia el tirador, que se suman al fondo
function impact(x, y, dir, big) {
  impacts.push({ x, y, dir, t: 0, big, row: hitN++ % 2 ? "b" : "a" });
  for (let i = 0, n = big ? 10 : 6; i < n; i++) {
    const a = Math.PI * (0.55 + Math.random() * 0.9), v = 280 * (0.4 + Math.random() * 0.6);
    fx.push({ x, y, vx: Math.cos(a) * v * dir, vy: Math.sin(a) * v - 84, life: 0.3, t: 0.3, color: "#9ff5fa", size: (big ? 5 : 4) * (0.6 + Math.random() * 0.6), g: 900, add: true });
  }
}
// la boca del frame que está en pantalla, con la misma cuenta que el disparo (hundido en el piso y squash del salto)
function muzzleNow() {
  const d = P.draw, T = d.torso, f = T ? anim(T.name).f[T.i] : anim(d.name).f[d.i];
  return muzzleAt(f, d.y + (T ? T.dy * S.char : 0));
}
```

**En `fire()`**, el fogonazo ya no guarda posición:

```js
  flash = { t: 0, big: power > 1, v: (shotN++ % 3) + 1, seed: Math.random() * 1000 };   // sin x, y: va en la boca de cada frame
```

**En `finishUpdate()`**, los impactos van en la cara del blanco o del bloque, sin el `burst` cian (las chispas las tira `impact`); el `burst` de cuando el blanco se rompe queda:

```js
        impact(B.vx > 0 ? T.x : T.x + T.w, B.y, Math.sign(B.vx), B.power > 1);   // en la cara que mira al tirador
```

```js
      if (!dead) for (const S2 of solids) if (B.x > S2.x && B.x < S2.x + S2.w && B.y > S2.y && B.y < S2.y + S2.h) { dead = true; impact(B.vx > 0 ? S2.x : S2.x + S2.w, B.y, Math.sign(B.vx), false); break; }
```

Y los relojes del fogonazo y de los impactos cuentan para arriba:

```js
  for (let i = impacts.length - 1; i >= 0; i--) { impacts[i].t += dt; if (impacts[i].t >= 4 * FXT.impact) impacts.splice(i, 1); }
  if (flash) { flash.t += dt; if (flash.t >= FXT.flashA + FXT.flashB) flash = null; }
```

**`drawFlash` nuevo**, en lugar del de halo y cruz:

```js
function drawFlash(Fl) {
  // la mezcla elegida en prototypes/fx_lab: el dibujo pegado a la boca del frame en pantalla, un halo sumado que no
  // pasa de la boca para atrás y tres chispas finas hacia adelante. A dos manos, todo un 30% más grande
  const m = muzzleNow(), age = Fl.t, dur = FXT.flashA + FXT.flashB, q = age / dur, k = S.char / 0.8 * (Fl.big ? 1.3 : 1);
  const name = (age < FXT.flashA ? "a" : "b") + Fl.v, p = FX.muzzle.pieces[name];
  ctx.save(); ctx.translate(m.x - camX, m.y); ctx.scale(P.facing, 1);
  const R = FX.muzzle.len * k * (0.5 + 0.2 * q);
  ctx.save(); ctx.beginPath(); ctx.rect(-4, -200, 400, 400); ctx.clip();
  ctx.globalCompositeOperation = "lighter"; ctx.globalAlpha = 0.85 * (1 - q);
  const g = ctx.createRadialGradient(2, 0, 1, R * 0.45, 0, R);
  g.addColorStop(0, "rgba(235,255,255,0.9)"); g.addColorStop(0.45, "rgba(89,227,236,0.45)"); g.addColorStop(1, "rgba(89,227,236,0)");
  ctx.fillStyle = g; ctx.beginPath(); ctx.ellipse(R * 0.45, 0, R, R * 0.65, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  ctx.drawImage(FX_IMG[`muzzle/${name}`], -p.ax * k, -p.ay * k, p.w * k, p.h * k);
  if (age < 0.08) {
    const r = rng(Math.floor(Fl.seed)), L = FX.muzzle.len * S.char / 0.8;
    ctx.globalCompositeOperation = "lighter"; ctx.globalAlpha = 1 - age / 0.08; ctx.strokeStyle = "#eaffff"; ctx.lineWidth = 1.6; ctx.lineCap = "round";
    for (let i = 0; i < 3; i++) {
      const a = (r() - 0.5) * 1.1, d = L * 0.5 + (380 + r() * 260) * age, ln = 4 + r() * 4;
      ctx.beginPath(); ctx.moveTo(Math.cos(a) * d, Math.sin(a) * d); ctx.lineTo(Math.cos(a) * (d + ln), Math.sin(a) * (d + ln)); ctx.stroke();
    }
  }
  ctx.restore();
}
```

**En `render()`**, el loop de `impacts` dibuja el destello (más corto, 0,06 s) y el dibujo, espejado si la bala iba a la izquierda:

```js
  for (const I of impacts) {
    if (I.t < 0.06) {   // destello: el círculo que se abre y se apaga, en 0,06 s
      const k = I.t / 0.06, r = (I.big ? 26 : 18) * (0.5 + k);
      ctx.save(); ctx.globalCompositeOperation = "lighter"; ctx.globalAlpha = 1 - k;
      const g = ctx.createRadialGradient(I.x - camX, I.y, 1, I.x - camX, I.y, r); g.addColorStop(0, "rgba(240,255,255,1)"); g.addColorStop(1, "rgba(89,227,236,0)");
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(I.x - camX, I.y, r, 0, Math.PI * 2); ctx.fill(); ctx.restore();
    }
    const i = Math.floor(I.t / FXT.impact);   // el dibujo: salpica hacia el tirador; con la bala hacia la izquierda, espejado
    if (i > 3) continue;
    const name = I.row + (i + 1), p = FX.impact.pieces[name], s = S.char / 0.8 * (I.big ? 1.3 : 1);
    ctx.save(); ctx.translate(I.x - camX, I.y); ctx.scale(I.dir * s, s); ctx.drawImage(FX_IMG[`impact/${name}`], -p.ax, -p.ay, p.w, p.h); ctx.restore();
  }
```

En el loop de `fx`, las partículas con `add` se suman al fondo; después de la primera línea del loop:

```js
    ctx.globalCompositeOperation = E.add ? "lighter" : "source-over";
```

y a la salida del loop, junto con `ctx.globalAlpha = 1;`, `ctx.globalCompositeOperation = "source-over";`.

**Guías:** el punto amarillo de la boca, en `muzzleNow()`:

```js
    const m = muzzleNow(); ctx.fillStyle = "#ffef5a"; ctx.beginPath(); ctx.arc(m.x - camX, m.y, 3.5, 0, Math.PI * 2); ctx.fill();
```

### 3. Qué probar en el juego

- Parado, a una y a dos manos, agachado, corriendo y saltando (con el squash del despegue y el aterrizaje): el fogonazo tiene que quedar en la lente en todos los frames (con <kbd>G</kbd> se ve la boca).
- Mirando a la izquierda: el fogonazo y el impacto se espejan.
- Contra los blancos y contra los bloques: el impacto cae en la cara que mira al tirador.
- Personaje al 100% y cámara al 100%: los efectos escalan con `S.char` y con la cámara.

### Pendiente

- **El destello del clip, en el pipeline.** `noBaked` repite el frame anterior en lugar del de disparo, que tiene el brazo 1–2 px más extendido. Lo prolijo es correr `remove_flash` sobre los clips de disparo del ranger, como en el comando; falta probarlo después de la limpieza previa.
- **Otra tanda de fogonazos.** La hoja elegida tiene las púas laterales hacia atrás (se lee bien a 26 px; en cámara lenta parece un dardo). Si molesta, otra tanda con las púas hacia adelante cuesta US$0,23 (ver el reporte).
