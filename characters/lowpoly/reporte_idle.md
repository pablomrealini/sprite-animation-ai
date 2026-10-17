# Low-poly: cómo sacar un idle (y un correr) consistente (2026-10-17)

Prueba con un personaje nuevo en estilo 3D low-poly (`characters/lowpoly/`), sin tocar el juego. El problema: el modelo de video inventa en cada clip lo que no ve (el pecho, con la pose de costado). La comparación con los clips está en [compare.html](compare.html). Se sirve con la config `sprite-previews` de `.claude/launch.json` o con `python3 -m http.server 8765 --bind 127.0.0.1 --directory characters` desde la raíz, y se abre en http://127.0.0.1:8765/lowpoly/compare.html.

## Qué se probó

Un idle de 5 s, dos tomas por estrategia, siempre con el último cuadro igual al primero para que el loop cierre:

- **A**: sólo el primer cuadro, en Seedance 2.0 (el de hoy), MiniMax H3 Max y Kling O3 standard.
- **B**: el primer cuadro más las vistas del personaje (T-pose de frente, tres cuartos y espalda, y tres cuartos con el arma) y del arma (lateral y frente). En H3 Max van como "Image 1…6"; en Kling, como dos *elements* (personaje y arma). Son los dos modelos de fal que aceptan primer cuadro y referencias en el mismo pedido. Seedance y Veo no: su endpoint de referencias no tiene primer cuadro.
- **B ¾**: B con la pose de tres cuartos leve, sólo en H3 Max.
- **C**: el personaje sin arma (la mano en pose de agarre, editada con Nano Banana 2.1) más sus vistas. El arma se pega después como sprite detrás del puño, siguiéndolo cuadro a cuadro ([pegar_arma.py](pegar_arma.py)).

Todas las referencias y poses tienen el cinturón rojo (la hoja nueva de Pablo). Las vistas están cortadas con una sola escala: el personaje mide 766 px de frente en todas. Las poses de costado miden lo mismo (343×518 px en el 16:9).

## Cuánto costó

US$9,00 estimados a precio de lista para el idle, US$1,20 para correr, US$8,59 para el resto del set y US$6,72 para las dos pruebas sin fogonazo (lo cobrado de verdad está en el dashboard de fal). Ningún pedido bloqueado. Aparte, la vía 3D gastó US$2,05 (ver `3d/README.md`).

| Concepto | US$ |
|---|---:|
| Idle A (Seedance 3,03 · H3 Max 0,52 · Kling 0,84) | 4,39 |
| Idle B y B ¾ (H3 Max 0,88 + 0,88 · Kling 0,84) | 2,60 |
| Idle C (H3 Max 0,80 · Kling 0,84) | 1,64 |
| Pose sin arma (4 imágenes: GPT Image 2.5 y Nano Banana 2.1) | 0,36 |
| **Total** | **9,00** |

## Números

Torso = de la base del casco al cinturón, con el brazo que lo cruza ([medir_torso.py](medir_torso.py)).

- **ΔE**: diferencia de color (CIE76) contra el cuadro 0 alineado, mediana de los cuadros.
- **Cambiado**: fracción del torso con ΔE > 20, o sea, lo que a ojo es otra cosa.
- **Movimiento**: cuánto se traslada el torso, p95 en px de la pose. Un idle quieto tiene un torso consistente sin mérito.
- **Entre tomas**: ΔE entre los torsos medios de las dos tomas: si inventan lo mismo, da bajo.
- **Cuadro 0**: MAD del cuadro 0 contra la pose según el QA; el pipeline ancla y escala con él.

Los rangos son las dos tomas.

| Estrategia | Modelo | Cuadro 0 | ¿Se queda de perfil? | ΔE torso | Cambiado | Movimiento | Entre tomas |
|---|---|---:|---|---:|---:|---:|---:|
| **A** | **Kling O3** | **1,8** | **sí, las dos** | **4,0–4,5** | **2,8–3,2 %** | 6–9 px | **3,2** |
| A | Seedance 2.0 | 45 | sí, pero re-renderiza el cuadro 0 (fondo y colores más claros) | 8,1–8,3 | 7,3–7,4 % | 6–19 px | 4,6 |
| A | H3 Max | 8,2–8,3 | una de dos: A1 corta a un primer plano | 11,3–11,7 | 16–17 % | 15–65 px | 11,4 |
| B | Kling O3 | 1,9–2,0 | no: gira a tres cuartos de frente y apunta a cámara | 16,8–22,5 | 27–41 % | 23–32 px | 10,9 |
| B | H3 Max | 9,4–9,9 | no: corta a otra toma sobre el gris de las referencias | 36,6–42,6 | 61–67 % | 67–69 px | 32,5 |
| B ¾ | H3 Max | 9,3–9,5 | no: el mismo corte | 26,8–40,9 | 47–63 % | 49–91 px | 26,6 |
| C | Kling O3 | 1,7 | casi: con la mano vacía estira los brazos y señala, gira un poco | 18,1–27,4 | 29–43 % | 13–24 px | 19,0 |
| C | H3 Max | 9,0 | no: corta a otra toma | 29,6–33,5 | 54–60 % | 21–27 px | 9,2 |
| hoy | ranger 2D, Seedance (5 idles) | — | — | 5,9–17,0 | 6–30 % | 3–22 px | — |

Los colores que no están en la hoja ("ajenos") dan 0–2 % en todos. Los modelos no inventan colores: inventan ángulo y forma.

## Correr, con la receta que ganó

Kling O3 standard, sólo el primer cuadro (y el último igual), sin referencias: 2 tomas de 5 s, US$0,84. La pose de zancada (GPT Image 2.5, US$0,36 las 4 opciones) se eligió por fidelidad de proporciones y se escaló para que el casco mida lo mismo que en el idle. En el 16:9 mide 505 px, contra 518 parado, y los pies quedan en la misma línea. En el atlas, idle y correr salen a la misma escala.

| Toma | Cuadro 0 | Loop | ΔE torso | Cambiado | Movimiento | Entre tomas |
|---|---:|---|---:|---:|---:|---:|
| correr 1 | 2,1 | 28 cuadros, costura 0,40 | 16,9 | 27,6 % | 47 px | 8,5 |
| correr 2 | 2,1 | 28 cuadros, costura 0,31 | 15,5 | 25,1 % | 38 px | 8,5 |
| vía 3D (sin invento, por construcción) | — | — | 15,1 | 21,5 % | 26 px | — |

- **Al nivel del render 3D.** Correr mueve y gira el torso, así que la métrica mide sobre todo movimiento real. La comparación justa es con el correr renderizado de la vía 3D, donde nada es inventado: Kling queda casi igual, moviéndose más. Revisado cuadro por cuadro sobre verde: zancada clara de perfil, el mismo diseño en todos los cuadros.
- **Dispara rayos aunque nadie se lo pida**, en casi todo el clip. Puede ser por la mención del brillo cian en el prompt. En el atlas los borra `remove_flash`, que además exporta la boca del arma por cuadro (`out/fx/correr_*_muzzle.json`). En la toma 1 se come la punta del arma en un par de cuadros. Para el próximo pedido conviene sacar del prompt la mención al brillo y pedir explícitamente que no dispare.

## Ajustes después de la revisión de Pablo (blur, arma)

- **Blur.** No venía del video (el personaje mide ~360 px en el clip de Kling) sino del tamaño. El atlas salía a 128 px y el visor abre en Zoom 2, pero la arena también lo agranda: dibuja al personaje a 128 × 0,8 de una vista de 960×540, o sea ~205 px en pantalla completa a 1080p (el doble en retina). Ahora el atlas sale a **256 px** con `sharpen = 0,3`, y la variante 0,5× queda a 128. Le pasa lo mismo al ranger de hoy (128 px).
- **Color.** fal entrega los videos en **BT.601 sin etiqueta**, y el pipeline los decodificaba como BT.709: el rojo se corría a naranja. Con `color_matrix = "bt601"`, el cuadro 0 de Kling coincide con la pose (diferencia de color 0,5 contra 10,6; fondo #C32D7D). Lo usan character.toml, medir_torso.py, comparar.py y pegar_arma.py (los clips sin etiqueta se leen como BT.601). Remedidos así, los números del torso cambian menos de medio punto, porque se miden contra el propio cuadro 0, así que las tablas de arriba siguen valiendo. Sólo baja "cuadro 0 contra la pose" de medir_torso (Kling, de 7,6 a 3,8).
- **Arma cortada en correr.** `remove_flash` corta desde el contorno oscuro del arma; con el rayo pegado al disco cian se llevaba la tapa y el disco. [sacar_rayos.py](sacar_rayos.py) sigue el cuerpo del arma con su forma del cuadro 0 y borra sólo lo que está delante de la boca, que queda entera. El modelo dispara en 106 y 73 de los 121 cuadros.
- **Arma mal agarrada en C.** No es el pegado: con el brazo estirado, Kling abre la mano y señala con el índice, y el arma queda flotando arriba del dedo. C salió del atlas (sigue en compare.html).

## El set de la arena (17 animaciones, 12 clips)

Con la receta de Kling O3 (primer cuadro y último igual, sin referencias) salieron los 10 clips que faltaban: US$8,59 (8 del set, la pose colgada y la subida con el colgado a dos manos). Ninguno bloqueado. El seguimiento está en [planilla.html](planilla.html): el ranger y el low-poly lado a lado, clip por clip, con la toma elegida y una nota. El atlas (`character.toml`) usa los mismos nombres que la arena.

- **Kling dispara en casi todos los clips con arma**, aunque el prompt diga "He never shoots". `remove_flash` con `method = "shape"` (nuevo en spritepipe) borra lo que está delante de la boca, la estrella y el anillo. Para eso sigue el arma con su forma del cuadro 0 y, si la pierde (el destello la tapa), la deja donde estaba. En los clips que dan vueltas (doble salto, subida, granada), el recorte deja afuera los cuadros con rayo.
- **El fogonazo ilumina al personaje**: en el disparo a dos manos la cara queda amarilla mientras dispara. No se borra.
- **Lo que inventa**: en el colgado dibuja la cornisa (la limpieza con `prop_rows` la saca casi toda; quedan restos chicos arriba de la mano). En la granada, el cuerpo gira hacia cámara al tirar. En el doble salto, el cuadro del medio del mortal sale borroso.
- **Consistencia de diseño**: el casco, el cinturón rojo y el arma se mantienen en todos los clips. Una de las dos tomas de cada clip sirvió siempre; la otra tenía disparos, una vuelta de más o el pantalón de otro color.

## Prueba sin fogonazo (2026-10-17, US$3,36)

Pablo pidió que el video no traiga fogonazo, porque lo pone el juego y limpiarlo deja restos. Se probó en el disparo y el salto disparando, con dos tomas de cada variante:
- **P:** un prompt sin "fire" ni "shot" que describe el retroceso de apretar el gatillo y que el arma es una utilería apagada.
- **P+D:** lo mismo, con el disco cian de la boca pintado de gris en la pose.

**Las 8 tomas traen fogonazo.** Con el arma apagada cambia de rayo cian a estrella blanca, pero sigue estando. Cuando la acción es disparar, Kling dibuja el fogonazo aunque el prompt lo prohíba. Configs: `generate_sin_fogonazo.toml` y `prompts/*_sin_fogonazo.txt`.

**Segunda prueba, donde el video no dispara** (`generate_apuntar.toml`, US$3,36): sube el brazo, lo deja quieto y lo baja, sin gatillo ni retroceso.
- **Con el arma apagada, de parado:** la toma 1 sale sin ningún fogonazo; la 2 trae un solo cuadro con fogonazo (el 24).
- **Con el arma apagada, saltando:** sigue disparando en varios saltos. El gesto de estirar el brazo de golpe en el aire lo dispara.
- **Sin arma, de parado:** el puño queda cerrado; sirve para pegar el arma por código.
- **Sin arma, saltando:** apunta con el dedo índice ("pistolita").

**Conclusión:** el video sólo apunta, con el arma apagada, y el retroceso, el fogonazo y el disco cian de la boca los pone el juego. Para los saltos hay que arrancar desde una pose con el brazo ya estirado, para que no haya gesto de disparar.

## Lo que se aprendió

1. **Lo que más pesó fue el modelo, no las referencias.** Kling O3 con sólo el primer y el último cuadro respeta el cuadro 0 casi exacto (MAD 1,8: el pipeline ancla y escala sin ayuda), se queda de perfil y cambia el 3 % del torso. El ranger 2D de hoy, con Seedance, cambia entre el 6 y el 30 %, con el mismo movimiento. Las dos tomas de Kling salen casi iguales (3,2). Revisadas cuadro por cuadro sobre verde a 12 fps, las dos son limpias.
2. **Las referencias empeoran un idle de costado.** Los modelos las usan para mostrar lo que hay en ellas. H3 Max abre en el cuadro 0, corta a una toma nueva armada con las referencias (de tres cuartos, sobre su fondo gris, con primeros planos) y vuelve recién en el último cuadro. Kling no corta, pero gira al personaje hacia cámara para mostrar el frente. Para un sprite de costado es justo lo contrario de lo que se busca.
3. **El arma aparte funciona técnicamente, pero el modelo inventa gestos con la mano vacía.** El seguimiento del puño (traslación y giro, con continuidad cuadro a cuadro) deja el arma bien puesta aunque el brazo se estire (ver `kling_c_2_arma` en el atlas). Lo que falla es el clip: sin nada en la mano, Kling la mueve (estira los brazos, señala). C llevaba referencias, que probablemente explican parte del giro. **No se probó C sin referencias.**
4. **H3 Max tiende a cambiar de plano** incluso sin referencias (A1 corta a un primer plano sobre otro fondo) y a agregar cosas (un rayo del arma en A2). No sirve para sprites.
5. **Seedance no respeta el cuadro 0 con este estilo.** Re-renderiza la imagen (MAD 45): el pipeline no puede sacar la escala de la pose y hay que declararla a mano.
6. **El tres cuartos leve quedó sin evaluar**, porque sólo se probó en H3 Max y cortó.

## Recomendación

- **Para producir:** Kling O3 standard, primer cuadro (y último igual en los loops), **sin referencias**, pose de costado sobre magenta apagado. Cuesta US$0,42 por toma de 5 s. La consistencia entre animaciones tiene que venir de las **poses de arranque**, todas editadas desde la misma pose base con la API de imagen y a la misma escala, no de las referencias en el video.
- **El arma en la mano, en el video.** En A, Kling la mantiene igual en todos los cuadros. El sprite aparte conviene sólo si hay que cambiar de arma o el juego la dibuja aparte (apuntar en 8 direcciones). Si se sigue por ahí, conviene probar C sin referencias y pidiendo la mano quieta.
- **Correr ya salió bien con la misma receta** (ver arriba): US$1,20 en total. La receta sirve para las dos animaciones probadas.
- **En paralelo, la vía 3D** (otra sesión): modelo desde las vistas (Hunyuan 3.1 Pro, US$0,53), rig y animaciones de Meshy (US$0,20 + 0,12 por animación), arma con Tripo (~US$0,30) y render en Blender. Unos US$1,50 una pasada. Ahí la consistencia es total por construcción; el riesgo es que el auto-rig no aguante las proporciones chibi.
- **Si queda tiempo para medir:** Kling O3 A con la pose de tres cuartos (US$0,84) y Kling O3 pro, que es más caro (US$0,112/s) y no hace falta para un sprite de 128 px.

## Archivos

- `refs/`: las hojas de Pablo; `refs/vistas/`: las 12 vistas sueltas a escala común (`escala.json`).
- `poses/`: las poses de costado (perfil, tres cuartos, sin arma) en concept RGBA y 16:9; [cinturon_rojo.py](cinturon_rojo.py) pintó el cinturón de las de costado.
- `generate_idle.toml`, `generate_idle_c.toml`, `prompts/`: el bake-off. `clips/idle*/bakeoff.md`: la tabla del QA.
- `torso/`: los números por cuadro (`torso.json`) y las tiras de torsos.
- [character.toml](character.toml) → `out/preview.html`: las 17 animaciones de la arena con sus nombres, anclados, a 256 px (y 128 en 0,5×), con una sola escala y la boca del arma por cuadro en `out/fx/`.
- [planilla.toml](planilla.toml) + [planilla.py](planilla.py) → [planilla.html](planilla.html): el set, clip por clip, ranger contra low-poly.
- `generate_set.toml`, `generate_subida.toml`, [subida_frames.py](subida_frames.py): los clips del set y los cuadros de la subida.
- [sacar_rayos.py](sacar_rayos.py): borra los rayos que Kling dispara sin pedirlo, sin cortar el arma.
- `generate_correr.toml`, `poses/correr_*`: correr.
- [compare.html](compare.html) + `compare/` (videos sobre verde y hojas de cuadros a 12 fps; 78 MB, se rearman con [comparar.py](comparar.py)).
