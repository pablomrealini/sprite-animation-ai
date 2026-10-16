// Graduación de color de las arenas: la misma para el juego (prototypes/arena/src.html, que build.py arma con esto
// adentro) y para el editor (prototypes/arena/editor). Sin dependencias; define funciones globales (y module.exports).
//
// gradePixels(px, lut, g, haze): gradúa en el lugar el Uint8ClampedArray RGBA de getImageData.
//   lut: la paleta de prototypes/arena/paleta.py ya decodificada, {n, bytes}: n³ × 3 bytes, r mayor, después g, después b
//        (decodeLut convierte el {n, data} en base64 de lut_payload). Puede ser null: entonces la paleta no hace nada.
//   g: los controles de un grupo, {paleta, saturacion, contraste, brillo, bruma}; los que faltan, neutros.
//   haze: el color de la bruma, [r, g, b] de 0 a 255.
//   En orden: la paleta (mezcla con el color del LUT, interpolado trilineal, según paleta de 0 a 1), la saturación
//   alrededor de la luma, el contraste alrededor de 128, el brillo multiplicando (los tres, 1 es neutro) y la bruma
//   (mezcla hacia haze según bruma, de 0 a 1). El alfa no se toca y los píxeles transparentes se saltean.
(function (root) {
  "use strict";
  const NEUTRAL = { paleta: 0, saturacion: 1, contraste: 1, brillo: 1, bruma: 0 };

  function isNeutral(g) {
    const q = { ...NEUTRAL, ...g };
    return q.paleta === 0 && q.saturacion === 1 && q.contraste === 1 && q.brillo === 1 && q.bruma === 0;
  }

  function decodeLut(p) {
    if (!p || !p.data || !p.n) return null;
    const s = atob(p.data), bytes = new Uint8Array(s.length);
    for (let i = 0; i < s.length; i++) bytes[i] = s.charCodeAt(i);
    return bytes.length === p.n * p.n * p.n * 3 ? { n: p.n, bytes } : null;
  }

  function gradePixels(px, lut, g, haze) {
    const q = { ...NEUTRAL, ...g };
    const P = lut && q.paleta > 0 ? Math.min(1, q.paleta) : 0, S = q.saturacion, C = q.contraste, B = q.brillo, H = Math.max(0, Math.min(1, q.bruma));
    const [hr, hg, hb] = haze || [128, 128, 128];
    const n = lut ? lut.n : 2, L = lut ? lut.bytes : null, k = (n - 1) / 255, top = n - 2;
    const dB = 3, dG = 3 * n, dR = 3 * n * n;
    for (let i = 0; i < px.length; i += 4) {
      if (px[i + 3] === 0) continue;
      let r = px[i], gg = px[i + 1], b = px[i + 2];
      if (P) {
        const x = r * k, y = gg * k, z = b * k;
        let i0 = x | 0, j0 = y | 0, k0 = z | 0;
        if (i0 > top) i0 = top; if (j0 > top) j0 = top; if (k0 > top) k0 = top;
        const fx = x - i0, fy = y - j0, fz = z - k0, base = i0 * dR + j0 * dG + k0 * dB;
        const lerp3 = c => {
          const o = base + c;
          const a00 = L[o] + (L[o + dB] - L[o]) * fz, a01 = L[o + dG] + (L[o + dG + dB] - L[o + dG]) * fz;
          const a10 = L[o + dR] + (L[o + dR + dB] - L[o + dR]) * fz, a11 = L[o + dR + dG] + (L[o + dR + dG + dB] - L[o + dR + dG]) * fz;
          const a0 = a00 + (a01 - a00) * fy, a1 = a10 + (a11 - a10) * fy;
          return a0 + (a1 - a0) * fx;
        };
        r += (lerp3(0) - r) * P; gg += (lerp3(1) - gg) * P; b += (lerp3(2) - b) * P;
      }
      if (S !== 1) { const l = 0.299 * r + 0.587 * gg + 0.114 * b; r = l + (r - l) * S; gg = l + (gg - l) * S; b = l + (b - l) * S; }
      if (C !== 1) { r = (r - 128) * C + 128; gg = (gg - 128) * C + 128; b = (b - 128) * C + 128; }
      if (B !== 1) { r *= B; gg *= B; b *= B; }
      if (H > 0) { r += (hr - r) * H; gg += (hg - gg) * H; b += (hb - b) * H; }
      px[i] = r; px[i + 1] = gg; px[i + 2] = b;   // Uint8ClampedArray: redondea y recorta a 0–255
    }
    return px;
  }

  // una copia graduada de una imagen o un canvas, a su tamaño natural (un canvas nuevo)
  function gradeImage(im, lut, g, haze) {
    const w = im.naturalWidth || im.width, h = im.naturalHeight || im.height, c = document.createElement("canvas");
    c.width = w; c.height = h;
    const x = c.getContext("2d"); x.drawImage(im, 0, 0);
    const d = x.getImageData(0, 0, w, h); gradePixels(d.data, lut, g, haze); x.putImageData(d, 0, 0);
    return c;
  }

  // el color de bruma por defecto, la misma cuenta que el editor: el promedio RGB del sexto de arriba de la lámina,
  // achicada a 96 de ancho (96 × 54 en una de 16:9: las filas 0 a 8). Sin lámina, HAZE_DEFAULT
  const HAZE_DEFAULT = [143, 179, 224];
  function hazeOf(im) {
    if (!im || !(im.naturalWidth || im.width)) return HAZE_DEFAULT.slice();
    const w = 96, h = Math.max(1, Math.round(96 * (im.naturalHeight || im.height) / (im.naturalWidth || im.width)));
    const c = document.createElement("canvas"); c.width = w; c.height = h;
    const x = c.getContext("2d"); x.drawImage(im, 0, 0, w, h);
    const rows = Math.max(1, Math.round(h / 6)), d = x.getImageData(0, 0, w, rows).data, s = [0, 0, 0];
    for (let i = 0; i < d.length; i += 4) { s[0] += d[i]; s[1] += d[i + 1]; s[2] += d[i + 2]; }
    return s.map(v => Math.round(v / (w * rows)));
  }

  const api = { NEUTRAL, HAZE_DEFAULT, isNeutral, decodeLut, gradePixels, gradeImage, hazeOf };
  Object.assign(root, api);
  if (typeof module === "object" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
