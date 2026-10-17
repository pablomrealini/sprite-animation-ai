"""Qué trae un GLB: objetos, caras, huesos (con su posición de reposo), acciones y rango de cuadros.

    blender -b --factory-startup -P characters/lowpoly/3d/inspeccionar.py -- archivo.glb [...]
"""

import sys

import bpy

for path in sys.argv[sys.argv.index("--") + 1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps = 24
    bpy.ops.import_scene.gltf(filepath=path)
    print(f"\n=== {path}")
    for o in bpy.context.scene.objects:
        extra = ""
        if o.type == "MESH":
            me = o.data
            extra = f" caras={len(me.polygons)} verts={len(me.vertices)} mats={[m.name for m in me.materials if m]}"
            extra += f" grupos={len(o.vertex_groups)} dims={tuple(round(d, 3) for d in o.dimensions)}"
        print(f"  {o.type:9s} {o.name!r} padre={o.parent.name if o.parent else None} loc={tuple(round(v, 3) for v in o.location)}"
              f" rot={tuple(round(v, 3) for v in o.rotation_euler)} esc={tuple(round(v, 3) for v in o.scale)}{extra}")
        if o.type == "ARMATURE":
            for b in o.data.bones:
                h = o.matrix_world @ b.head_local
                t = o.matrix_world @ b.tail_local
                print(f"    hueso {b.name!r} padre={b.parent.name if b.parent else None}"
                      f" cabeza={tuple(round(v, 3) for v in h)} cola={tuple(round(v, 3) for v in t)}")
        ad = o.animation_data
        if ad and ad.action:
            print(f"    acción {ad.action.name!r} rango={tuple(ad.action.frame_range)}")
    for a in bpy.data.actions:
        print(f"  acción {a.name!r} rango={tuple(a.frame_range)} usuarios={a.users}")
    for img in bpy.data.images:
        print(f"  imagen {img.name!r} {tuple(img.size)}")
