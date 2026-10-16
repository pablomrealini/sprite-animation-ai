# ranger_industrial: comparación de modelos (2026-10-16)

Modelos: gpt-image-2.5-sunburst-fal, nano-banana-2.1. Abrí `compare.html` para verlas lado a lado.

| asset | modelo | estado | tamaño | post | notas | US$ |
|---|---|---|---|---|---|---:|
| walkway | gpt-image-2.5-sunburst-fal #1 | ok | 2560×1440 | ok, costura top_a:x fail→ok, costura top_b:x fail→warn |  | 0,17 |
| walkway | gpt-image-2.5-sunburst-fal #2 | ok | 2560×1440 | ok, costura top_a:x warn→ok, costura top_b:x ok |  | 0,17 |
| substructure | gpt-image-2.5-sunburst-fal #1 | ok | 2560×1440 | warn, costura truss_a:x warn, costura truss_a:y ok, costura truss_b:x fail→ok, costura truss_b:y ok, costura column:y warn→ok, costura machine_a:x ok, costura machine_a:y ok, costura machine_b:x warn, costura machine_b:y ok, costura machine_c:x ok, costura machine_c:y ok | el contenido toca el borde (bottom): puede estar cortado | 0,17 |
| substructure | gpt-image-2.5-sunburst-fal #2 | ok | 2560×1440 | warn, costura truss_a:x ok, costura truss_a:y ok, costura truss_b:x ok, costura truss_b:y ok, costura column:y fail→ok, costura machine_a:x warn→ok, costura machine_a:y ok, costura machine_b:x ok, costura machine_b:y ok, costura machine_c:x ok, costura machine_c:y ok | el contenido toca el borde (bottom): puede estar cortado | 0,17 |
| bridge | gpt-image-2.5-sunburst-fal #1 | ok | 2560×1440 | ok, costura bridge_a:x ok, costura bridge_b:x ok |  | 0,17 |
| bridge | gpt-image-2.5-sunburst-fal #2 | ok | 2560×1440 | ok, costura bridge_a:x ok, costura bridge_b:x ok |  | 0,17 |
| platforms | gpt-image-2.5-sunburst-fal #1 | ok | 2560×1440 | ok |  | 0,17 |
| platforms | gpt-image-2.5-sunburst-fal #2 | ok | 2560×1440 | ok |  | 0,17 |
| pipes | gpt-image-2.5-sunburst-fal #1 | ok | 2560×1440 | ok, costura thick:x ok, costura thin:x fail→ok |  | 0,17 |
| pipes | gpt-image-2.5-sunburst-fal #2 | ok | 2560×1440 | ok, costura thick:x fail→ok, costura thin:x ok |  | 0,17 |
| landmarks | gpt-image-2.5-sunburst-fal #1 | ok | 2560×1440 | warn | el contenido toca el borde (left): puede estar cortado | 0,17 |
| landmarks | gpt-image-2.5-sunburst-fal #2 | ok | 2560×1440 | ok |  | 0,17 |
| small_props | gpt-image-2.5-sunburst-fal #1 | ok | 2560×1440 | ok, costura wall_a:x fail→ok, costura wall_a:y fail→ok, costura wall_b:x ok, costura wall_b:y fail→ok |  | 0,17 |
| small_props | gpt-image-2.5-sunburst-fal #2 | ok | 2560×1440 | ok, costura wall_a:x fail→warn, costura wall_a:y fail→ok, costura wall_b:x fail→ok, costura wall_b:y fail→ok |  | 0,17 |
| sky | nano-banana-2.1 #1 | ok | 2752×1536 | ok, costura x fail→ok |  | 0,06 |
| sky | nano-banana-2.1 #2 | ok | 2752×1536 | ok, costura x warn→ok |  | 0,06 |
| sky | nano-banana-2.1 #3 | ok | 2752×1536 | ok, costura x fail→ok |  | 0,06 |
| far | nano-banana-2.1 #1 | ok | 3168×1344 | ok, costura x warn→ok |  | 0,06 |
| far | nano-banana-2.1 #2 | ok | 3168×1344 | ok, costura x ok |  | 0,06 |
| far | nano-banana-2.1 #3 | ok | 3168×1344 | ok, costura x ok |  | 0,06 |
| mid | nano-banana-2.1 #1 | ok | 3168×1344 | ok, costura x warn→ok |  | 0,06 |
| mid | nano-banana-2.1 #2 | ok | 3168×1344 | ok, costura x warn→warn |  | 0,06 |
| mid | nano-banana-2.1 #3 | ok | 3168×1344 | ok, costura x fail→warn |  | 0,06 |
| near | nano-banana-2.1 #1 | ok | 3168×1344 | ok, costura x fail→ok |  | 0,06 |
| near | nano-banana-2.1 #2 | ok | 3168×1344 | ok, costura x warn→ok |  | 0,06 |
| near | nano-banana-2.1 #3 | ok | 3168×1344 | ok, costura x fail→ok |  | 0,06 |

Gastado (estimado, a precio de lista): US$ 3,15.
