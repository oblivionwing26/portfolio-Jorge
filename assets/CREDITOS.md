# Créditos de los assets

Todas las texturas de `tex/` se generan con `tools/build-assets.py`.

## Poly Haven (CC0, dominio público) — https://polyhaven.com
Fuentes a 1k descargadas de la API de Poly Haven y convertidas a WebP:

- Superficies: `leafy_grass`, `forest_ground_04`, `stony_dirt_path`, `rock_face`, `mossy_rock`, `river_small_rocks`, `snow_02`.
- Arquitectura y corteza: `japanese_cedar_planks`, `white_plaster_rough_01`, `grey_roof_tiles`, `japanese_stone_wall`, `thatch_roof_angled`, `sakura_bark`, `pine_bark`.
- Follaje: ramas de `fir_tree_01`, hojas de `shrub_01`, frondas de `fern_02`, matas de `grass_medium_01`.

Los mapas `t_*.webp` están normalizados (media ≈ 0,5) para usarse como detalle sobre el color pintado del mundo.

## Dibujados por código
- `f_blossom.webp` (racimo de flores de cerezo) y `f_blades.webp` (hierba estilizada) se dibujan en `tools/build-assets.py`.

## Personaje humano — `human.glb`
- Modelo y animaciones **Xbot** de los ejemplos oficiales de three.js (`examples/models/gltf/Xbot.glb`, licencia MIT del repositorio de three.js; animaciones de Mixamo incluidas en ese ejemplo). Reempaquetado con gltf-transform y comprimido con meshoptimizer.

## Polyspoon (kit local, Apache-2.0; contenido de inicio CC0) — `models/`
Generados con `node .polyspoon/runtime.mjs build` (diseños, controles e informes en `exports/`):
- `fox.glb` (familia `stylized-fox`, parámetros por defecto), `rabbit.glb` (`rigged-rabbit`), con esqueleto y animaciones idle/walk.
- `hydrangea_blue.glb`, `hydrangea_pink.glb` (`hydrangea`), `mushrooms.glb` (`mushroom-cluster`).

## Dibujados por código
- `f_maple.webp`, `f_ginkgo.webp` y `f_willow.webp` (hojas de arce, ginkgo y sauce) en `tools/build-assets.py`.
