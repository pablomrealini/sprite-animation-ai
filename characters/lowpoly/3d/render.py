"""Render de costado del personaje 3D (Blender sin ventana): cada clip a PNG con alfa, con el encuadre de la pose.

    blender -b --factory-startup -P characters/lowpoly/3d/render.py -- idle idle_mano correr correr_mano caminar
        [--cuadros 0,10] [--sin-arma] [--crudo] [--sufijo _prueba]

- La cámara es ortográfica, del lado derecho del personaje (mira a la derecha, como en
  `poses/perfil_dullmagenta_16x9.png`), con una elevación chica. El encuadre sale del cuadro 0 del idle: alto del
  personaje 518 px, pies en y = 778 y la nuca del casco en x = 788, como en la pose. Se guarda en
  `encuadre.json` y todos los clips usan el mismo (misma escala, misma línea de piso).
- Correr y caminar vienen con avance (root motion): se le saca la tendencia lineal al hueso de la cadera y queda en
  el lugar, con el rebote.
- El arma va emparentada al pecho y los brazos la agarran por IK (la mano derecha en la empuñadura, la izquierda
  debajo, sosteniendo): es la capa de torso que haría un juego. El idle y la carrera de la biblioteca traen los
  brazos sueltos.
- Los pesos del auto-rig se rehacen en memoria (el GLB no se toca, ver `repesar`): casco rígido a la cabeza, tronco
  y cinturón a la columna, hombreras rígidas a un hueso propio que sigue al brazo a medias. `--crudo` renderiza con
  los pesos de Meshy y la carrera sin achicar, para comparar.
- `correr` es la carrera de la biblioteca con la patada achicada (`achicar`) y apoyada en el piso; `correr_mano` y
  `idle_mano` están hechos acá (ver "a mano"): un ciclo de 16 cuadros desde el reposo y un idle de respiración y
  rebote, con los pies quietos, sobre el cuadro 0 del idle de la biblioteca.
"""

import argparse
import collections
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from bpy_extras import anim_utils
from mathutils import Matrix, Quaternion, Vector

AQUI = Path(__file__).resolve().parent
OUT = AQUI / "out"
RENDER = AQUI / "render"
ENCUADRE = AQUI / "encuadre.json"

W, H_IMG = 1920, 1080
FPS = 24
# La pose de costado, en px de 1920 × 1080 (medida sobre perfil_dullmagenta_16x9.png).
POSE = {"arriba": 260, "pies": 778, "nuca": 788}
# El arma en la pose, en fracción del alto del personaje: largo, cola (desde la nuca) y borde de arriba (desde el piso).
ARMA = {"largo": 0.28, "cola": 0.38, "arriba": 0.50, "lado": -0.02}

CLIPS = {
    # el "Idle" de la biblioteca (id 0) mira a un costado: gira el cuerpo ~90° y vuelve (en el chibi, hasta ±130°)
    "idle": {"glb": OUT / "personaje" / "animation_glb.glb", "en_el_lugar": False, "sin_giro": True},
    # hecho acá sobre el cuadro 0 del idle de arriba (ver IDLE_MANO)
    "idle_mano": {"glb": OUT / "personaje" / "animation_glb.glb", "en_el_lugar": False, "sin_giro": True,
                  "a_mano": True},
    # la básica de Meshy patea muy atrás para piernas tan cortas: se achica la amplitud (ver ACHICAR)
    "correr": {"glb": OUT / "personaje" / "basic_animations__running_glb.glb", "en_el_lugar": True,
               "achicar": True, "al_piso": True},
    # hecha acá desde el reposo (ver CORRER_MANO)
    "correr_mano": {"glb": OUT / "personaje" / "basic_animations__running_glb.glb", "en_el_lugar": False,
                    "a_mano": True, "al_piso": True},
    "caminar": {"glb": OUT / "personaje" / "basic_animations__walking_glb.glb", "en_el_lugar": True,
                "al_piso": True},
}
ARMA_GLB = OUT / "arma" / "model_glb.glb"
ELEVACION = 6.0  # grados, mirando un poco desde arriba como la pose
ARMA_CARAS = 20000  # Hunyuan la entrega con 500k caras
POLO_ANGULO = -90.0


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="+", choices=list(CLIPS))
    ap.add_argument("--cuadros", help="sólo estos cuadros (prueba), separados por coma")
    ap.add_argument("--sin-arma", action="store_true")
    ap.add_argument("--luz", default="eevee", choices=["eevee", "plana"])
    ap.add_argument("--crudo", action="store_true", help="sin los arreglos: pesos del auto-rig y sin achicar")
    ap.add_argument("--sufijo", default="", help="render/<clip><sufijo>/ (para comparar)")
    ap.add_argument("--depurar", action="store_true")
    return ap.parse_args(argv)


# --- escena -----------------------------------------------------------------------------------------------------

def cargar(glb: Path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = FPS  # el importador de glTF pasa segundos a cuadros con esta tasa
    bpy.ops.import_scene.gltf(filepath=str(glb))
    arm = next(o for o in sc.objects if o.type == "ARMATURE")
    # el GLB de Meshy trae una Icosphere suelta de 2 m que no es parte del personaje
    for o in [o for o in sc.objects if o.type == "MESH" and not o.vertex_groups]:
        bpy.data.objects.remove(o)
    mallas = [o for o in sc.objects if o.type == "MESH"]
    return sc, arm, mallas


def curvas(obj):
    ad = obj.animation_data
    cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
    return cb.fcurves


def hueso(arm, *nombres):
    """El primer hueso cuyo nombre (sin mayúsculas ni separadores) coincide con alguno de los pedidos."""
    norm = {b.name.lower().replace("_", "").replace(".", "").replace(":", ""): b.name for b in arm.pose.bones}
    for n in nombres:
        for k, v in norm.items():
            if k == n or k.endswith(n):
                return arm.pose.bones[v]
    raise KeyError(f"no hay hueso {nombres}: {sorted(norm)}")


def en_el_lugar(arm, cadera):
    """Saca el avance: a cada canal de posición de la cadera le resta la recta entre el primer y el último cuadro."""
    for fc in curvas(arm):
        if fc.data_path == f'pose.bones["{cadera.name}"].location':
            k = fc.keyframe_points
            (t0, v0), (t1, v1) = k[0].co, k[-1].co
            m = (v1 - v0) / (t1 - t0) if t1 != t0 else 0
            for p in k:
                d = m * (p.co[0] - t0)
                p.co[1] -= d
                p.handle_left[1] -= d
                p.handle_right[1] -= d
            fc.update()


TRONCO = ("Hips", "Spine02", "Spine01", "Spine", "neck", "Head")


def sin_giro(arm):
    """Saca el giro alrededor de la vertical (el twist) de cadera, columna, cuello y cabeza en cada clave: queda el
    resto (el peso que pasa de un pie al otro, la respiración) y el personaje sigue de perfil."""
    por_hueso = {}
    for fc in curvas(arm):
        for b in TRONCO:
            if fc.data_path == f'pose.bones["{b}"].rotation_quaternion':
                por_hueso.setdefault(b, [None] * 4)[fc.array_index] = fc
    for b, fcs in por_hueso.items():
        # la vertical del mundo en el espacio de reposo del hueso
        eje = (arm.data.bones[b].matrix_local.to_3x3().inverted() @ Vector((0, 0, 1))).normalized()
        for i in range(len(fcs[0].keyframe_points)):
            q = Quaternion([fcs[c].keyframe_points[i].co[1] for c in range(4)])
            v = Vector((q.x, q.y, q.z))
            proy = eje * v.dot(eje)
            twist = Quaternion((q.w, proy.x, proy.y, proy.z))
            if twist.magnitude < 1e-6:
                continue
            twist.normalize()
            swing = q @ twist.inverted()
            for c in range(4):
                fcs[c].keyframe_points[i].co[1] = swing[c]
                fcs[c].keyframe_points[i].handle_left[1] = swing[c]
                fcs[c].keyframe_points[i].handle_right[1] = swing[c]
        for fc in fcs:
            fc.update()


def rotaciones(arm, huesos):
    """Las cuatro curvas de rotación (cuaternión) de cada hueso pedido que esté animado."""
    por_hueso = {}
    for fc in curvas(arm):
        for b in huesos:
            if fc.data_path == f'pose.bones["{b}"].rotation_quaternion':
                por_hueso.setdefault(b, [None] * 4)[fc.array_index] = fc
    return {b: fcs for b, fcs in por_hueso.items() if None not in fcs}


# Carrera: factor de la amplitud de cada grupo de huesos alrededor de su rotación media (1 = como viene). La básica de
# Meshy lleva el muslo ±43° y la rodilla ±80° de su media: en el chibi la bota patea hasta la cadera.
ACHICAR = {"piernas": 0.55, "pies": 0.5, "cadera": 0.6, "columna": 0.6, "rebote": 0.7}
PIERNAS = [f"{s}{n}" for s in ("Left", "Right") for n in ("UpLeg", "Leg")]
PIES = [f"{s}{n}" for s in ("Left", "Right") for n in ("Foot", "ToeBase")]


def achicar(arm, cadera):
    """Achica la amplitud de la carrera: cada clave de rotación q pasa a media · (media⁻¹ · q)^k (el mismo eje, el
    ángulo por k) y el rebote vertical de la cadera se escala alrededor de su media."""
    grupos = {"piernas": PIERNAS, "pies": PIES, "cadera": [cadera.name], "columna": ["Spine02", "Spine01", "Spine"]}
    for g, huesos in grupos.items():
        k = ACHICAR[g]
        for b, fcs in rotaciones(arm, huesos).items():
            n = len(fcs[0].keyframe_points)
            qs = [Quaternion([fcs[c].keyframe_points[i].co[1] for c in range(4)]) for i in range(n)]
            for q in qs[1:]:
                if q.dot(qs[0]) < 0:
                    q.negate()
            media = Quaternion([sum(q[c] for q in qs) / n for c in range(4)]).normalized()
            for i, q in enumerate(qs):
                eje, ang = (media.inverted() @ q).to_axis_angle()
                if ang > math.pi:
                    ang -= 2 * math.pi
                nq = media @ Quaternion(eje, ang * k)
                for c in range(4):
                    p = fcs[c].keyframe_points[i]
                    d = nq[c] - p.co[1]
                    p.co[1] += d
                    p.handle_left[1] += d
                    p.handle_right[1] += d
            for fc in fcs:
                fc.update()
    # el rebote: el eje Y del hueso de la cadera es la vertical (la cola apunta arriba)
    for fc in curvas(arm):
        if fc.data_path == f'pose.bones["{cadera.name}"].location' and fc.array_index == 1:
            ks = fc.keyframe_points
            m = sum(p.co[1] for p in ks) / len(ks)
            for p in ks:
                d = (m + (p.co[1] - m) * ACHICAR["rebote"]) - p.co[1]
                p.co[1] += d
                p.handle_left[1] += d
                p.handle_right[1] += d
            fc.update()


# --- a mano ----------------------------------------------------------------------------------------------------
#
# Las animaciones hechas acá dan, por cuadro, un giro total de cada hueso en el espacio de la armadura (T; los que no
# están heredan el de su padre) y un desplazamiento de algunas cabezas de hueso. La rotación local de cada hueso pasa
# a Q · M⁻¹ · P⁻¹ · T · M (M: su rotación en la pose base; P: el giro total de su padre): así los giros se componen
# como en una cadena y no hace falta conocer los ejes de reposo de Meshy. Las piernas se resuelven con IK de dos
# huesos (cadera, rodilla, tobillo) y el pie queda con el giro que se le pida (sin giro: como en la pose base).

LADO = Vector((1, 0, 0))  # el eje de los costados del personaje (mira a -Y); girar + alrededor de él es ir adelante
ADELANTE_A = Vector((0, -1, 0))


def pose_base(arm):
    bpy.context.view_layer.update()
    return {pb.name: {"q": pb.rotation_quaternion.copy(), "loc": pb.location.copy(), "M": pb.matrix.to_quaternion(),
                      "cabeza": pb.head.copy()} for pb in arm.pose.bones}


def clave(arm, base, T, mover, f):
    """Escribe el cuadro f: T (giros totales) y mover (desplazamiento en la armadura de la cabeza de cada hueso)."""
    for pb in arm.pose.bones:
        b = base[pb.name]
        p = pb.parent
        while p is not None and p.name not in T:
            p = p.parent
        P = T[p.name] if p is not None else Quaternion()
        Tb = T.get(pb.name, P)
        pb.rotation_quaternion = b["q"] @ (b["M"].inverted() @ P.inverted() @ Tb @ b["M"])
        # la posición local va en el marco del hueso antes de su propia rotación: M · Q⁻¹, girado por el padre
        marco = P @ b["M"] @ b["q"].inverted()
        pb.location = b["loc"] + marco.inverted() @ mover.get(pb.name, Vector())
        pb.keyframe_insert("rotation_quaternion", frame=f)
        pb.keyframe_insert("location", frame=f)


def pierna(T, base, s, H, A, hacia, pie=None):
    """IK de la pierna s: la cadera (cabeza del muslo) en H y el tobillo en A, con la rodilla doblada para el lado de
    `hacia`. Si no llega, la pierna queda estirada hacia A."""
    H0, K0, A0 = (base[f"{s}{n}"]["cabeza"] for n in ("UpLeg", "Leg", "Foot"))
    l1, l2 = (K0 - H0).length, (A0 - K0).length
    d = A - H
    u = d.normalized()
    cos_a = max(-1.0, min(1.0, (l1 * l1 + d.length_squared - l2 * l2) / (2 * l1 * d.length)))
    w = (hacia - u * hacia.dot(u)).normalized()
    K = H + (u * cos_a + w * math.sqrt(1 - cos_a * cos_a)) * l1
    r1 = (K0 - H0).rotation_difference(K - H)
    r2 = (r1 @ (A0 - K0)).rotation_difference(A - K)
    T[f"{s}UpLeg"] = r1
    T[f"{s}Leg"] = r2 @ r1
    T[f"{s}Foot"] = pie if pie is not None else Quaternion()


def nueva_accion(arm, nombre):
    arm.animation_data.action = None
    arm.animation_data.action = bpy.data.actions.new(nombre)


# Idle a mano, sobre el cuadro 0 del idle de la biblioteca (ya sin el giro): un ciclo de `cuadros` a 24 fps. La cadera
# baja y sube (rebote, m) con las rodillas que se doblan y los pies quietos; el pecho respira (grados; − es abrirse
# hacia atrás), los hombros suben (m) y la cabeza cabecea con retraso (fracción del ciclo).
IDLE_MANO = {"cuadros": 48, "rebote": 0.016, "pecho": -1.6, "pecho_retraso": 0.12, "cabeza": 2.2,
             "cabeza_retraso": 0.22, "hombros": 0.006}


def idle_a_mano(sc, arm, cadera):
    ir(sc, arm.animation_data.action.frame_range[0])
    base = pose_base(arm)
    nueva_accion(arm, "idle_mano")
    esc = arm.matrix_world.to_scale().z  # la armadura viene a escala 0,01: sus unidades son cm
    cfg = IDLE_MANO
    N = cfg["cuadros"]
    for f in range(N + 1):
        def onda(retraso=0.0):
            # 0 arriba (la pose base), 1 abajo
            return (1 - math.cos(2 * math.pi * (f / N - retraso))) / 2

        baja = Vector((0, 0, -cfg["rebote"] * onda() / esc))
        resp = math.radians(cfg["pecho"]) * (1 - onda(cfg["pecho_retraso"]))
        T = {"Spine01": Quaternion(LADO, resp * 0.5), "Spine": Quaternion(LADO, resp)}
        T["Head"] = Quaternion(LADO, resp + math.radians(cfg["cabeza"]) * onda(cfg["cabeza_retraso"]))
        for s in ("Left", "Right"):
            H0, K0, A0 = (base[f"{s}{n}"]["cabeza"] for n in ("UpLeg", "Leg", "Foot"))
            pierna(T, base, s, H0 + baja, A0, K0 - H0)
        sube = Vector((0, 0, cfg["hombros"] * (1 - onda(cfg["pecho_retraso"])) / esc))
        clave(arm, base, T, {cadera.name: baja, "LeftShoulder": sube, "RightShoulder": sube}, f)


# Correr a mano, desde la pose de reposo: un ciclo de `cuadros` a 24 fps con dos pasos. Cada pie está en el piso una
# fracción `apoyo` del ciclo, yendo de `adelante` a `atras` (m, respecto de la cadera), y en el aire sube `levanta` (m)
# con la punta abajo hasta `punta` grados al despegar y arriba `sube_punta` antes de caer; en la primera mitad de
# `talon` (fracción del vuelo) el pie sólo sube, atrás. La cadera queda `baja` m por debajo del reposo y rebota `rebote` m (lo más
# bajo a mitad del apoyo); el pecho se inclina `inclina` grados y oscila `oscila`; la cabeza compensa `cabeza`. Los
# tobillos van a `abre` m del costado de la cadera (en reposo, las piernas del chibi se abren 14 cm y no llegan).
CORRER_MANO = {"cuadros": 16, "apoyo": 0.34, "adelante": 0.21, "atras": 0.20, "levanta": 0.19, "punta": 35.0,
               "sube_punta": -12.0, "talon": 0.3, "abre": 0.07, "baja": 0.045, "rebote": 0.035, "inclina": 10.0,
               "oscila": 2.0, "cabeza": -5.0}


def correr_a_mano(sc, arm, cadera):
    nueva_accion(arm, "correr_mano")
    for pb in arm.pose.bones:
        pb.rotation_quaternion = Quaternion()
        pb.location = Vector()
    base = pose_base(arm)
    esc = arm.matrix_world.to_scale().z
    cfg = CORRER_MANO
    N, ap = cfg["cuadros"], cfg["apoyo"]
    for f in range(N + 1):
        t = f / N
        q = (2 * t) % 1  # medio ciclo: un paso
        rebote = 0.5 * (1 + math.cos(2 * math.pi * (q - ap / 2)))  # 1 a mitad del apoyo, 0 a mitad del vuelo
        baja = Vector((0, 0, -(cfg["baja"] + cfg["rebote"] * rebote) / esc))
        lean = math.radians(cfg["inclina"] + cfg["oscila"] * (2 * rebote - 1))
        T = {"Spine01": Quaternion(LADO, lean * 0.5), "Spine": Quaternion(LADO, lean)}
        T["Head"] = Quaternion(LADO, lean + math.radians(cfg["cabeza"]))
        for s, desfase in (("Left", 0.0), ("Right", 0.5)):
            H0, A0 = base[f"{s}UpLeg"]["cabeza"], base[f"{s}Foot"]["cabeza"]
            p = (t + desfase) % 1
            y_ad = base[cadera.name]["cabeza"].y + cfg["adelante"] / esc * ADELANTE_A.y
            y_at = base[cadera.name]["cabeza"].y - cfg["atras"] / esc * ADELANTE_A.y
            if p < ap:  # en el piso, de adelante para atrás
                u = p / ap
                y, z, ang = y_ad + (y_at - y_ad) * u, 0.0, 0.0
            else:  # en el aire: primero sube el talón atrás, después la rodilla lleva el pie adelante
                u = (p - ap) / (1 - ap)
                v = max(0.0, (u - cfg["talon"] * 0.5) / (1 - cfg["talon"] * 0.5))
                y = y_at + (y_ad - y_at) * (v * v * (3 - 2 * v))
                z = cfg["levanta"] / esc * math.sin(math.pi * u ** 0.75)
                if u < 0.45:  # al despegar, la punta abajo
                    ang = cfg["punta"] * math.sin(math.pi * u / 0.45)
                else:  # yendo adelante, la punta arriba para caer plano
                    ang = cfg["sube_punta"] * math.sin(math.pi * (u - 0.45) / 0.55)
            A = Vector((H0.x + math.copysign(cfg["abre"] / esc, A0.x - H0.x), y, A0.z + z))
            pierna(T, base, s, H0 + baja, A, ADELANTE_A, Quaternion(LADO, math.radians(ang)))
        clave(arm, base, T, {cadera.name: baja}, f)


def al_piso(sc, arm, mallas, ts, cam, enc):
    """Sube o baja la armadura para que lo más bajo del ciclo, visto por la cámara, caiga en la línea de los pies del
    encuadre (y = POSE["pies"]). Con la cámara un poco desde arriba, el pie del lado de la cámara se ve ~12 px más
    abajo que el de atrás a la misma altura: por eso se apoya en la imagen y no por la z. Devuelve cuánto sube (m)."""
    _, arr = ejes(cam)
    v_piso = enc["v"] - (POSE["pies"] - H_IMG / 2) * enc["ortho_scale"] / W
    bajo = math.inf
    for t in ts:
        ir(sc, t)
        bajo = min(bajo, min(p.dot(arr) for p in verts_mundo(mallas)))
    sube = (v_piso - bajo) / arr.z
    arm.location.z += sube
    bpy.context.view_layer.update()
    return sube


# --- pesos ------------------------------------------------------------------------------------------------------
#
# El auto-rig de Meshy pesa mal al chibi: el pecho va 0,4–0,8 a la cabeza (el casco es enorme y su influencia baja
# hasta el cinturón), la panza y el cinturón ~0,5 al muslo, y las hombreras mezclan cabeza, hombro y brazo, así que se
# rompen al llevar el brazo adelante. Acá se rehacen por zonas, sobre la posición de reposo (T-pose, metros, Z arriba,
# el personaje mira a -Y): las copias de un vértice que el glTF parte en las costuras de UV caen en la misma zona y
# reciben los mismos pesos, así que no se abren grietas.

Z_CASCO = 0.99      # de acá para arriba, el casco y la cara: rígidos a Head
Z_OREJERA = 1.035   # entre 0,30 y 0,47 de x, sólo es casco (la orejera) de acá arriba: abajo es el brazo
Z_PIERNA = (0.515, 0.545)  # debajo del cinturón: de los pesos de la pierna (abajo) a la cadera (arriba)
X_BRAZO = (0.21, 0.30)     # al costado del pecho (arriba de Z_AXILA): del tronco al brazo
Z_AXILA = 0.76
# La hombrera va rígida a un hueso propio, hijo del hombro, que copia esta fracción de la rotación del brazo: con 0
# queda quieta y el brazo sale por debajo, con 1 gira entera con el brazo y se mete en el casco.
HOMBRERA_SIGUE = 0.6
# Las hombreras: caras rojas de la textura conectadas desde una semilla arriba del hombro, dentro de esta caja.
HOMBRERA_SEMILLA = (0.27, 0.0, 0.97)
HOMBRERA_CAJA = {"x": (0.08, 0.50), "z": (0.80, 1.03)}
CABEZA = ("Head", "neck", "head_end", "headfront")
COLUMNA = ("Hips", "Spine02", "Spine01", "Spine")


def textura(malla) -> np.ndarray:
    """Los píxeles de la textura de color (alto, ancho, RGB), con la fila 0 abajo como las UV."""
    img = max((n.image for n in malla.data.materials[0].node_tree.nodes if n.type == "TEX_IMAGE" and n.image),
              key=lambda im: im.size[0] * im.size[1])
    w, h = img.size
    px = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(px)
    return px.reshape(h, w, 4)[..., :3]


def soldar(pos: np.ndarray) -> np.ndarray:
    """El id de cada vértice entre los de la misma posición (el glTF parte los vértices en las costuras de UV)."""
    _, inv = np.unique(np.round(pos, 4), axis=0, return_inverse=True)
    return inv.ravel()


def colores(malla, sold: np.ndarray):
    """El color de la textura en el centro (de UV) de cada cara y el color medio de cada vértice soldado."""
    me = malla.data
    px = textura(malla)
    h, w = px.shape[:2]
    uv = np.empty(len(me.loops) * 2, np.float32)
    me.uv_layers.active.data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)

    def muestra(u, v):
        return px[np.clip((v * h).astype(int), 0, h - 1), np.clip((u * w).astype(int), 0, w - 1)]

    cara = np.array([muestra(*uv[f.loop_start:f.loop_start + f.loop_total].mean(0)) for f in me.polygons])
    lv = np.empty(len(me.loops), np.int64)
    me.loops.foreach_get("vertex_index", lv)
    acc = np.zeros((sold.max() + 1, 3))
    np.add.at(acc, sold[lv], muestra(uv[:, 0], uv[:, 1]))
    n = np.bincount(sold[lv], minlength=len(acc))[:, None]
    return cara, acc / np.maximum(n, 1)


def es_rojo(c):
    return c[0] > 0.45 and c[1] < 0.3 and c[2] < 0.3


def es_casco(c):
    """Blanco del casco o piel de la cara: lo único de esos colores en el personaje."""
    blanco = min(c) > 0.6
    piel = c[0] > 0.7 and c[1] > 0.45 and c[2] > 0.3 and c[0] > c[2] + 0.15
    return blanco or piel


def hombreras(malla, pos: np.ndarray, sold: np.ndarray, color_cara: np.ndarray) -> dict[str, set[int]]:
    """Los vértices (soldados) de cada hombrera: caras rojas conectadas desde la semilla, sin salir de la caja."""
    me = malla.data
    caras = [[sold[i] for i in f.vertices] for f in me.polygons]
    centros = np.array([pos[list(f.vertices)].mean(0) for f in me.polygons])
    rojo = [es_rojo(c) for c in color_cara]
    por_arista = collections.defaultdict(list)
    for fi, vs in enumerate(caras):
        for a, b in zip(vs, vs[1:] + vs[:1]):
            por_arista[(min(a, b), max(a, b))].append(fi)
    vecinas = collections.defaultdict(set)
    for fs in por_arista.values():
        for a in fs:
            vecinas[a].update(f for f in fs if f != a)
    res = {}
    for s, sx in (("R", -1), ("L", 1)):
        def dentro(c):
            return (HOMBRERA_CAJA["x"][0] < sx * c[0] < HOMBRERA_CAJA["x"][1]
                    and HOMBRERA_CAJA["z"][0] < c[2] < HOMBRERA_CAJA["z"][1])
        semilla = np.array(HOMBRERA_SEMILLA) * (sx, 1, 1)
        cands = [i for i in range(len(caras)) if rojo[i] and dentro(centros[i])]
        s0 = min(cands, key=lambda i: np.linalg.norm(centros[i] - semilla))
        sel, pila = {s0}, [s0]
        while pila:
            for b in vecinas[pila.pop()]:
                if b not in sel and rojo[b] and dentro(centros[b]):
                    sel.add(b)
                    pila.append(b)
        res[s] = {v for f in sel for v in caras[f]}
    return res


def rehacer_rig(arm, crudo: bool):
    """Colas de los brazos para el IK y, si no es crudo, un hueso por hombrera (hijo del hombro, con el reposo del
    brazo) que copia HOMBRERA_SIGUE de la rotación del brazo."""
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.data.edit_bones
    for s in ("Left", "Right"):
        # los huesos de Meshy vienen con colas absurdas (el antebrazo termina a 20 m) y el IK usa la cola como
        # efector: se rehacen hombro → codo → muñeca → mano. A esos huesos los maneja el IK.
        a, f, h = eb[f"{s}Arm"], eb[f"{s}ForeArm"], eb[f"{s}Hand"]
        a.tail = f.head.copy()
        f.tail = h.head.copy()
        h.tail = h.head + (h.head - f.head) * 0.6
        if not crudo:
            b = eb.new(f"{s}Hombrera")
            b.head, b.tail, b.roll = a.head.copy(), a.tail.copy(), a.roll
            b.parent = eb[f"{s}Shoulder"]
            b.use_deform = True
    bpy.ops.object.mode_set(mode="OBJECT")
    if crudo:
        return
    for s in ("Left", "Right"):
        c = arm.pose.bones[f"{s}Hombrera"].constraints.new("COPY_ROTATION")
        c.target, c.subtarget = arm, f"{s}Arm"
        c.target_space = c.owner_space = "LOCAL"
        c.influence = HOMBRERA_SIGUE


def repesar(arm, malla):
    """Pesos nuevos por zona (ver arriba). Devuelve cuántos vértices quedaron en cada una."""
    me = malla.data
    mw = malla.matrix_world
    pos = np.array([tuple(mw @ v.co) for v in me.vertices])
    sold = soldar(pos)
    color_cara, _ = colores(malla, sold)
    pads = hombreras(malla, pos, sold, color_cara)
    # el casco: todo vértice que toca una cara blanca o de piel (Meshy funde el borde del casco con la hombrera: la
    # costura va con el casco y las caras rojas de arriba de la hombrera se estiran un poco, tapadas por el casco)
    casco = {sold[v] for f, c in zip(me.polygons, color_cara) if es_casco(c) for v in f.vertices}
    nombre = {g.index: g.name for g in malla.vertex_groups}
    viejos = [{nombre[g.group]: g.weight for g in v.groups} for v in me.vertices]
    alto = {b.name: (arm.matrix_world @ b.head_local).z for b in arm.data.bones}
    # el tronco por altura: cada hueso de la columna manda en la mitad de su tramo y se mezcla con el vecino
    tramos = [(b, (alto[b] + alto[n]) / 2) for b, n in zip(COLUMNA, COLUMNA[1:] + ("neck",))]

    def tronco(z):
        if z <= tramos[0][1]:
            return {tramos[0][0]: 1.0}
        for (b0, z0), (b1, z1) in zip(tramos, tramos[1:]):
            if z <= z1:
                t = (z - z0) / (z1 - z0)
                return {b0: 1 - t, b1: t}
        return {tramos[-1][0]: 1.0}

    def solo(w, huesos):
        w = {k: v for k, v in w.items() if k in huesos}
        tot = sum(w.values())
        return {k: v / tot for k, v in w.items()} if tot > 1e-3 else None

    def mezcla(a, b, t):
        out = collections.Counter()
        for k, v in a.items():
            out[k] += v * (1 - t)
        for k, v in b.items():
            out[k] += v * t
        return dict(out)

    def liso(t):
        t = min(1.0, max(0.0, t))
        return t * t * (3 - 2 * t)

    nuevos, cuenta = [], collections.Counter()
    for i, (x, y, z) in enumerate(pos):
        lado = "Right" if x < 0 else "Left"
        ax = abs(x)
        brazo = solo(viejos[i], [f"{lado}{n}" for n in ("Shoulder", "Arm", "ForeArm", "Hand")])
        if (z >= Z_CASCO and (ax < X_BRAZO[1] or z >= Z_OREJERA)) or (z > 0.9 and sold[i] in casco):
            w, zona = {"Head": 1.0}, "casco"
        elif sold[i] in pads["R" if x < 0 else "L"]:
            w, zona = {f"{lado}Hombrera": 1.0}, "hombrera"
        elif z < Z_PIERNA[1]:
            pierna = solo(viejos[i], ["Hips"] + [f"{s}{n}" for s in ("Left", "Right")
                                                 for n in ("UpLeg", "Leg", "Foot", "ToeBase")]) or {"Hips": 1.0}
            w = mezcla(pierna, {"Hips": 1.0}, liso((z - Z_PIERNA[0]) / (Z_PIERNA[1] - Z_PIERNA[0])))
            zona = "pierna"
        elif z > Z_AXILA and ax > X_BRAZO[0] and brazo:
            t = liso((ax - X_BRAZO[0]) / (X_BRAZO[1] - X_BRAZO[0]))
            w, zona = mezcla(tronco(z), brazo, t), ("brazo" if t >= 1 else "axila")
        else:
            w, zona = tronco(z), "tronco"
        nuevos.append({k: v for k, v in w.items() if v > 1e-3})
        cuenta[zona] += 1
    for b in ("RightHombrera", "LeftHombrera"):
        if b not in malla.vertex_groups:
            malla.vertex_groups.new(name=b)
    todos = list(range(len(me.vertices)))
    for g in malla.vertex_groups:
        g.remove(todos)
    grupos = {g.name: g for g in malla.vertex_groups}
    for i, w in enumerate(nuevos):
        for k, v in w.items():
            grupos[k].add([i], v, "REPLACE")
    return cuenta


def plano(mallas, luz: str):
    """Caras planas (low-poly) y material: con luz o sólo la textura."""
    for o in mallas:
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        try:
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
        except RuntimeError:
            pass
        o.data.shade_flat()
        o.select_set(False)
        for m in o.data.materials:
            if not m or not m.use_nodes:
                continue
            nt = m.node_tree
            bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if bsdf is None:
                continue
            bsdf.inputs["Roughness"].default_value = 0.85
            bsdf.inputs["Metallic"].default_value = 0.0
            if "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = 0.2
            for nombre in ("Normal",):  # sin normal map: las caras quedan planas de verdad
                for l in list(bsdf.inputs[nombre].links):
                    nt.links.remove(l)
            if luz == "plana":
                col = bsdf.inputs["Base Color"].links[0].from_socket if bsdf.inputs["Base Color"].links else None
                em = nt.nodes.new("ShaderNodeEmission")
                if col:
                    nt.links.new(col, em.inputs["Color"])
                out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
                nt.links.new(em.outputs[0], out.inputs["Surface"])


# Luces calibradas contra la pose: la textura de Meshy ya trae los colores iluminados del concept (traje 40 contra 44,
# rojo 216–232 contra 231, blanco 248 contra 249), así que lo que mira a la cámara o arriba tiene que quedar en ~1,0 y
# lo de abajo más oscuro. Dirección = hacia dónde está la luz (X: lado de afuera de la cámara, Y: atrás, Z: arriba).
LUCES = {"ambiente": 0.45,
         "clave": {"dir": (-0.6, 0.0, 0.75), "fuerza": 2.0},     # del lado de la cámara y de arriba
         "frente": {"dir": (-0.3, -0.85, 0.4), "fuerza": 0.8}}   # de adelante (la cara y el frente del casco)


def luces(sc, luz: str):
    w = bpy.data.worlds.new("mundo")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (1, 1, 1, 1)
    bg.inputs["Strength"].default_value = LUCES["ambiente"] if luz == "eevee" else 0.0
    if luz != "eevee":
        return
    for nombre in ("clave", "frente"):
        L = bpy.data.lights.new(nombre, "SUN")
        L.energy = LUCES[nombre]["fuerza"]
        L.angle = math.radians(10)
        ob = bpy.data.objects.new(nombre, L)
        # el sol alumbra por su -Z: se apunta el -Z en contra de la dirección hacia la luz
        ob.rotation_euler = (-Vector(LUCES[nombre]["dir"])).normalized().to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(ob)


def ajustes(sc):
    r = sc.render
    r.engine = "BLENDER_EEVEE"
    r.resolution_x, r.resolution_y, r.resolution_percentage = W, H_IMG, 100
    r.film_transparent = True
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.eevee.taa_render_samples = 32


# --- encuadre ---------------------------------------------------------------------------------------------------

def verts_mundo(mallas):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in mallas:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ev.matrix_world
        pts += [mw @ v.co for v in me.vertices]
        ev.to_mesh_clear()
    return pts


def camara(sc):
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    ob = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(ob)
    sc.camera = ob
    e = math.radians(ELEVACION)
    # el personaje mira a -Y (glTF +Z): la cámara va a -X, mirando a +X, y la derecha de la imagen es -Y
    d = Vector((math.cos(e), 0, -math.sin(e)))
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return ob


def ejes(cam):
    m = cam.matrix_world.to_3x3()
    return m @ Vector((1, 0, 0)), m @ Vector((0, 1, 0))


def encuadrar(sc, cam, mallas):
    """Escala y posición de la cámara para que el cuadro 0 caiga como la pose: alto, pies y nuca."""
    bpy.context.view_layer.update()
    der, arr = ejes(cam)
    pts = verts_mundo(mallas)
    us = [p.dot(der) for p in pts]
    vs = [p.dot(arr) for p in pts]
    vmin, vmax = min(vs), max(vs)
    alto_px = POSE["pies"] - POSE["arriba"]
    k = alto_px / (vmax - vmin)  # px por metro
    cabeza = [u for u, v in zip(us, vs) if v > vmin + 0.55 * (vmax - vmin)]
    umin = min(cabeza)
    uc = umin + (W / 2 - POSE["nuca"]) / k
    vc = vmax - (H_IMG / 2 - POSE["arriba"]) / k
    piso = min(p.z for p in pts)
    nuca_y = max(p.y for p, v in zip(pts, vs) if v > vmin + 0.55 * (vmax - vmin))
    return {"ortho_scale": W / k, "u": uc, "v": vc, "alto_m": vmax - vmin, "piso_z": piso, "nuca_y": nuca_y,
            "elevacion": ELEVACION}


def aplicar_encuadre(cam, enc):
    cam.data.ortho_scale = enc["ortho_scale"]
    der, arr = ejes(cam)
    fwd = cam.matrix_world.to_3x3() @ Vector((0, 0, -1))
    cam.location = der * enc["u"] + arr * enc["v"] - fwd * 20


# --- arma y brazos ----------------------------------------------------------------------------------------------

# Dónde agarra cada mano, en fracciones de la caja del arma: x de la cola (0) a la boca (1), z de abajo (0) a arriba
# (1), y de -1 (lado de afuera de la cámara) a 1 (lado de la cámara). El objetivo del IK es la muñeca; la mano apunta
# a "mira". En la pose, el puño derecho tapa la parte de abajo de la empuñadura.
AGARRE = {"R": {"muñeca": (0.0, 0.9, 0.45), "mira": (0.6, 0.9, 0.40)},
          "L": {"muñeca": (0.05, -0.9, 0.30), "mira": (0.6, -0.9, 0.25)}}
# La muñeca derecha en la pose (px): el puño está en (1005, 605); la muñeca, un poco atrás.
POSE_MUÑECA = (985, 600)
ALCANCE = 0.93  # fracción del largo del brazo hasta la muñeca (el codo queda apenas doblado)
# El codo apunta abajo y un poco afuera y atrás (en fracción del alto del personaje, desde el hombro).
CODO = {"afuera": 0.25, "atras": 0.10, "abajo": 0.35}
ADELANTE, CAMARA, ARRIBA = Vector((0, -1, 0)), Vector((-1, 0, 0)), Vector((0, 0, 1))


def vacio(nombre, pos=(0, 0, 0)):
    ob = bpy.data.objects.new(nombre, None)
    ob.empty_display_size = 0.03
    bpy.context.scene.collection.objects.link(ob)
    ob.matrix_world = Matrix.Translation(Vector(pos))
    return ob


def emparentar(ob, padre, b=None):
    """Emparenta sin mover: el objeto queda donde está en el mundo."""
    bpy.context.view_layer.update()
    mw = ob.matrix_world.copy()
    ob.parent = padre
    if b is not None:
        ob.parent_type = "BONE"
        ob.parent_bone = b.name
    bpy.context.view_layer.update()
    ob.matrix_world = mw


def desde_pose(cam, enc, px, x0):
    """El punto de la escena, en el plano x = x0, que la cámara ve en el píxel px de la pose."""
    k = W / enc["ortho_scale"]
    der, arr = ejes(cam)
    fwd = cam.matrix_world.to_3x3() @ Vector((0, 0, -1))
    q = der * (enc["u"] + (px[0] - W / 2) / k) + arr * (enc["v"] + (H_IMG / 2 - px[1]) / k)
    return q + fwd * ((x0 - q.x) / fwd.x)


def poner_arma(sc, arm, enc, cam, sin_arma: bool):
    alto = enc["alto_m"]
    pecho = hueso(arm, "spine02", "spine2", "chest", "upperchest", "spine01", "spine1")
    largo = ARMA["largo"] * alto
    if sin_arma:
        dims = Vector((largo, 0.33 * largo, 0.64 * largo))
        arma = vacio("arma")
    else:
        antes = set(sc.objects)
        bpy.ops.import_scene.gltf(filepath=str(ARMA_GLB))
        nuevos = [o for o in sc.objects if o not in antes]
        partes = [o for o in nuevos if o.type == "MESH"]
        for o in partes:
            dec = o.modifiers.new("decimar", "DECIMATE")
            dec.ratio = min(1.0, ARMA_CARAS / max(1, len(o.data.polygons)))
        plano(partes, "eevee")
        bpy.context.view_layer.update()
        # Hunyuan deja el lateral (la vista de frente) mirando a -Y de Blender: el largo va en X
        pts = verts_mundo(partes)
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        centro, d = (lo + hi) / 2, hi - lo
        bajos = [p.x for p in pts if p.z < lo.z + 0.2 * d.z]  # la empuñadura está atrás
        boca_x = -1 if sum(bajos) / len(bajos) > centro.x else 1
        esc = largo / d.x
        dims = Vector((d.x, d.y, d.z)) * esc
        arma = vacio("arma")
        for o in nuevos:
            if o.parent is None:
                emparentar(o, arma)
        # centro al origen del vacío, escala y la boca hacia adelante del personaje (-Y)
        arma.matrix_world = (Matrix.Rotation(math.radians(-90 if boca_x > 0 else 90), 4, "Z")
                             @ Matrix.Scale(esc, 4) @ Matrix.Translation(-centro))
        bpy.context.view_layer.update()
        hijo = vacio("arma_centro")
        for o in nuevos:
            if o.parent is arma:
                emparentar(o, hijo)
        emparentar(hijo, arma)
    bpy.context.view_layer.update()

    def en_caja(c, fx, fy, fz):
        return c + ADELANTE * (fx - 0.5) * dims.x + CAMARA * fy * dims.y / 2 + ARRIBA * (fz - 0.5) * dims.z

    # La muñeca derecha va hacia donde está el puño en la pose (proyectado a la escena), pero hasta donde llega el
    # brazo: el hombro del rig queda ~10 cm más alto y ~9 cm más atrás que en el concept y el brazo no alcanza.
    mw = arm.matrix_world
    hombro = mw @ arm.pose.bones["RightArm"].head
    largo_brazo = sum(((mw @ arm.pose.bones[n].tail) - (mw @ arm.pose.bones[n].head)).length
                      for n in ("RightArm", "RightForeArm"))
    hacia = desde_pose(cam, enc, POSE_MUÑECA, -0.10) - hombro
    muñeca = hombro + hacia.normalized() * min(hacia.length, ALCANCE * largo_brazo)
    c = Vector((ARMA["lado"] * alto, 0, 0))
    off = en_caja(Vector(), *AGARRE["R"]["muñeca"])
    c.y, c.z = (muñeca - off).y, (muñeca - off).z
    arma.matrix_world = Matrix.Translation(c) @ arma.matrix_world
    bpy.context.view_layer.update()

    def en_arma(fx, fy, fz):
        return en_caja(c, fx, fy, fz)

    lado = {"R": CAMARA, "L": -CAMARA}
    for s, nombre in (("R", "Right"), ("L", "Left")):
        brazo, ante, mano = (arm.pose.bones[f"{nombre}{n}"] for n in ("Arm", "ForeArm", "Hand"))
        objetivo = vacio(f"muñeca_{s}", en_arma(*AGARRE[s]["muñeca"]))
        mira = vacio(f"mira_{s}", en_arma(*AGARRE[s]["mira"]))
        hombro = arm.matrix_world @ brazo.head
        polo = vacio(f"codo_{s}", hombro + lado[s] * CODO["afuera"] * alto - ADELANTE * CODO["atras"] * alto
                     - ARRIBA * CODO["abajo"] * alto)
        for o in (objetivo, mira):
            emparentar(o, arma)
        emparentar(polo, arm, pecho)
        ik = ante.constraints.new("IK")
        ik.target = objetivo
        ik.pole_target = polo
        ik.pole_angle = math.radians(POLO_ANGULO)
        ik.chain_count = 2
        dt = mano.constraints.new("DAMPED_TRACK")
        dt.target = mira
        dt.track_axis = "TRACK_Y"
    emparentar(arma, arm, pecho)
    return arma


# --- render -----------------------------------------------------------------------------------------------------

def tiempos(arm):
    """Un ciclo muestreado parejo a 24 fps: el clip de Meshy va de 0,8 a 96,8 (no cae en cuadros enteros) y su
    último cuadro es igual al primero, así que no se repite."""
    a, b = arm.animation_data.action.frame_range
    n = max(1, round(b - a))
    return [a + i * (b - a) / n for i in range(n)]


def ir(sc, t):
    sc.frame_set(int(math.floor(t)), subframe=t - math.floor(t))


def main():
    a = args()
    enc = json.loads(ENCUADRE.read_text()) if ENCUADRE.exists() else None
    for clip in a.clips:
        c = CLIPS[clip]
        sc, arm, mallas = cargar(c["glb"])
        cadera = hueso(arm, "hips", "pelvis", "root")
        if c["en_el_lugar"]:
            en_el_lugar(arm, cadera)
        if c.get("sin_giro"):
            sin_giro(arm)
        if c.get("achicar") and not a.crudo:
            achicar(arm, cadera)
        if c.get("a_mano"):
            (correr_a_mano if clip.startswith("correr") else idle_a_mano)(sc, arm, cadera)
        rehacer_rig(arm, a.crudo)
        if not a.crudo:
            zonas = repesar(arm, mallas[0])
            print("pesos por zona:", dict(zonas))
        ajustes(sc)
        plano(mallas, a.luz)
        luces(sc, a.luz)
        cam = camara(sc)
        ts = tiempos(arm)
        ir(sc, ts[0])
        if enc is None:
            if clip != "idle":
                raise SystemExit("el encuadre sale del idle: renderizar el idle primero")
            enc = encuadrar(sc, cam, mallas)
            ENCUADRE.write_text(json.dumps(enc, indent=1))
            print("encuadre", enc)
        aplicar_encuadre(cam, enc)
        poner_arma(sc, arm, enc, cam, a.sin_arma)
        if c.get("al_piso") and not a.crudo:
            print(f"al piso: la armadura sube {al_piso(sc, arm, mallas, ts, cam, enc) * 100:.1f} cm")
        if a.depurar:
            ir(sc, ts[0])
            bpy.context.view_layer.update()
            for n in ("RightArm", "RightForeArm", "RightHand", "LeftArm", "LeftForeArm", "LeftHand"):
                pb = arm.pose.bones[n]
                print("DEP", n, "escala", tuple(round(x, 3) for x in pb.matrix.to_scale()))
                print("DEP", n, "cabeza", tuple(round(x, 3) for x in arm.matrix_world @ pb.head),
                      "cola", tuple(round(x, 3) for x in arm.matrix_world @ pb.tail),
                      "conectado", arm.data.bones[n].use_connect, [c.type for c in pb.constraints])
            for o in sc.objects:
                if o.type == "EMPTY" or o.name == "arma":
                    print("DEP", o.name, tuple(round(x, 3) for x in o.matrix_world.translation))
        cuadros = [int(x) for x in a.cuadros.split(",")] if a.cuadros else list(range(len(ts)))
        dest = RENDER / f"{clip}{a.sufijo}"
        dest.mkdir(parents=True, exist_ok=True)
        if not a.cuadros:
            for viejo in dest.glob("*.png"):
                viejo.unlink()
        for i in cuadros:
            ir(sc, ts[i])
            sc.render.filepath = str(dest / f"{i:04d}.png")
            bpy.ops.render.render(write_still=True)
        print(f"{clip}: {len(ts)} cuadros en el ciclo, {ts[0]:.2f}–{ts[-1]:.2f} → {dest.relative_to(AQUI)}/ ({len(cuadros)})")


if __name__ == "__main__":
    main()
