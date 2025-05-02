## 👾 Space Invaders - Proyecto en Pygame

### 🎮 ¿En qué consiste el proyecto?

Este proyecto es una recreación del clásico **Space Invaders** utilizando la biblioteca **Pygame**. El juego incluye:

- Modo **Single Player** con niveles progresivos y sistema de ranking.
- Modo **Multiplayer cooperativo**, donde dos jugadores luchan juntos.
- Modo **P vs P**, donde dos jugadores compiten uno contra otro.
- Menú principal animado con estrellas, música, ranking visual y puntero personalizado.
- Mecánicas como enemigos, obstáculos, power-ups, naves misteriosas y explosiones.
- Sistema de vidas representadas gráficamente con naves.
- Sonidos personalizados y diseño adaptativo a pantalla completa.

-------------------------------------------------------------------------

## 📘 Bitácora de desarrollo (17 días)

### Día 1
- Planificación del proyecto y definición de funcionalidades mínimas.
- Investigación sobre cómo usar Pygame y configurar un entorno básico.

### Día 2
- Creación del entorno base de `pygame`.
- Implementación de la ventana, bucle principal y pantalla en blanco.
- Carga de imágenes y primer sprite (nave del jugador).

### Día 3
- Movimiento del jugador y disparo de láseres.
- Introducción de enemigos básicos que se mueven lateralmente.

### Día 4
- Implementación de colisiones entre balas y enemigos.
- Destrucción de enemigos y sistema de puntaje inicial.

### Día 5
- Diseño del **menú principal**: botones, textos y animación de estrellas.
- Implementación de sonidos para disparos y explosiones.

### Día 6
- Añadido de niveles progresivos: enemigos más rápidos y nuevos patrones.
- Sistema de vidas con visualización de naves debajo del puntaje.

### Día 7
- Refactorización del código: separación en archivos (`single_player.py`, `game_objects.py`, etc.)
- Reutilización de clases para mejorar la escalabilidad.

### Día 8
- Creación del modo **Multiplayer cooperativo**: dos jugadores con controles separados.
- Implementación de ranking combinado y guardado de puntuaciones.

### Día 9
- Desarrollo del modo **P vs P**: sin aliens, jugadores enfrentados con sus propias barreras.
- Condiciones de victoria y pantallas finales.

### Día 10
- Mejora del diseño adaptativo a pantalla completa.
- Ajustes gráficos y limpieza visual de menús y HUD.

### Día 11
- Implementación del puntero personalizado usando `ship.png` rotado.
- Ajuste de sonidos de fondo y ambientación musical.

### Día 12
- Optimización del rendimiento, ajuste del framerate y manejo de eventos.

### Día 13
- Testeo intensivo de los tres modos de juego y corrección de errores.
- Validación del sistema de ranking y guardado en archivos JSON.

### Día 14
- Documentación del proyecto y preparación del repositorio para entrega.
- Redacción de este `README.md` y últimas pruebas.

### Día 15
- Implementación del menú de pausa.
- Implementación de una barra de volumen y teclas personalizables en el nuevo modo **Settings**.

### Día 16
- Se le agrega un cuarto botón al menú de pausa para ir a **Settings**.
- Se le agrega a **Settings** un modo 'black' al desplazar la barra de volumen y evitar apretar botones accidentalmente.

### Día 17
- Implementación de una **Introducción** animada al juego.
- Se mejora la forma de importar los sonidos y se les agrega un valor de volumen base.

-------------------------------------------------------------------------
