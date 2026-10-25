# Mapa y zonas jugables

Ejes: +x = este, −z = norte. Unidades ≈ metros. Agua del río a y = 0.

## API expuesta en `window.__valle`
- `H(x, z)` → altura del terreno exterior (la misma función que genera la malla). Dentro de la cueva de Ouro el suelo está en `zones.ouro.y` (≈ −32). En la torre celestial el suelo lo dan los colisionadores (rampa y plataformas), no `H`.
- `zones` → `{ x, z, r, y }` de cada arena y del Nexo. `zones.nexo.spawn` = punto de aparición del jugador.
- `spawn` → igual que `zones.nexo.spawn`.
- `colliders` → `{ boxes: [{x,y,z,hx,hy,hz,ry,walk}], cyls: [{x,z,y0,y1,r}] }`. `walk: true` = superficie pisable (plataformas, puentes, rampa). Los cilindros con `ring` son anillos (radio interior), no discos: anillo de Ouro y balaustrada de la arena celestial.
- `pickups` → hitos de equipo `{ id, type: 'espada'|'monolito'|'cofre', x, y, z }` (8 en total), pensados para los elementos del stack.
- `toggleColliders()` o la tecla **C** → muestra los colisionadores en verde.
- `debugNaN(true)` → pinta en verde cualquier píxel inválido (diagnóstico de los cuadros negros).
- `goView(i)`, `setMood('blue'|'dawn'|'rain', instant)`, `applyQuality('high'|'low')`, `camera`, `controls`.

## Zonas
| Zona | Centro (x, z) | Arena r | Notas |
|---|---|---|---|
| Nexo (en la aldea inicial) | (−16, 112) | 2,5 | Hoguera con katana clavada (aparición al oeste); yunque-altar rúnico en (−32,5, 112) para el menú del stack; estanque al este |
| Aldea inicial | (−24, 112) | 9 | 7 casas alrededor de la fuente |
| Templo en ruinas | (−122, −121) | 15 | Árbol gigante en (−112, −152); verja de Ouro detrás del salón en (−122, −167) |
| Claro del bosque | (134, −32) | 15 | Camino con antorchas desde (35, −63); 6 hitos en desvíos |
| Torre del Reloj Quebrada (Kronos) | (118, −157) | 12 (y ≈ 112) | Meseta acantilada al noreste; subida en zigzag desde el claro; puente roto al pilar (161, −172) |
| Bóveda del Uróboros (Ouro) | (−80, −215) | 10 (y = −32) | Caverna bajo la montaña; entrada desde la verja de las ruinas |
| Palacio de jade | (−12, −281) | 13 | Cumbre norte sobre un mar de nubes; ascensor de jaula (atajo) en (−45, −289) |
| **Arena celestial (jefe final)** | (−12, −356) | 24 (y ≈ 226) | Cima de la Torre Celestial, la zona más alta del mapa |

## Torre Celestial y Arena
- Inspiración visual: Enir-Ilim (Elden Ring), reinterpretada en clave celestial japonesa; diseño propio, no réplica.
- Pedestal de roca, plinto en y ≈ 104, cuatro cuerpos de arcadas con aleros de jade y oro, seis torretas con cúpula y corona en voladizo con agujas colgantes.
- Acceso: rampa en espiral de 2,25 vueltas (radio 38) desde el sur del plinto; calzada desde la terraza del palacio.
- Arena: disco de 32 m con crisantemo dorado, anillos grabados, balaustrada con entradas al oeste y al norte, guerreros caídos, campo de katanas y arcada en halo rota.
- Al norte: puente con colosos arrodillados → isla flotante con torii divino y gigantes guardianes → puerta al cielo (monolito partido, aureola y escalones de luz).
- Al subir por encima del palacio la luz pasa de forma gradual a un dorado divino.

## Conectividad
- Valle → ruinas: puente de vértebras fósiles sobre una garganta (≈ (−80,5, −90,5)).
- Río: tronco caído como puente cerca de (11, −95).
- Ruinas → verja → Ouro → ascensor al palacio (atajo).
- Claro del bosque → zigzag → Kronos.
- Palacio de jade → rampa en espiral → arena celestial → puerta al cielo.

## Pendiente para la fase de juego
- El túnel entre la verja de las ruinas y la cueva de Ouro no existe como geometría (teletransporte o transición).
- Los árboles tienen colisionador cilíndrico; la hierba y las rocas pequeñas no.
- La rampa en espiral tiene colisionadores por tramos sin cabeceo; conviene suavizar la pendiente al implementar el movimiento.
