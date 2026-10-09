# Revisión del proyecto del docente

Referencia: **3. Contexto del Juego; 3.1. Reglas Fundamentales; 19. Distribución de Puntos, criterio 7 “Código Fuente”**.

Othello es un juego adversarial de dos jugadores, determinista, secuencial, de información perfecta y suma cero cuando se expresa la utilidad como diferencia de fichas. El entorno observable es discreto y completamente conocido. El agente utiliza búsqueda y una utilidad aproximada: no es un agente que aprenda por entrenamiento. La evaluación heurística es una estimación para decidir, no una probabilidad de victoria.

## Inventario y decisiones — 19. Distribución de Puntos, criterio 7 “Código Fuente”

| Módulo original | Responsabilidad y metodología | Decisión en esta práctica |
|---|---|---|
| `AgenteIA/Agente.py` | Encapsula percepciones, acciones y habilitación; `programa` abstracto | Conservado; la acción sigue publicándose con `set_acciones` |
| `AgenteIA/Entorno.py` | Ciclo percibir/actuar y colección de agentes | Conservado; Othello especializa la selección por turno |
| `AgenteIA/AgenteJugador.py` | `ElEstado` y búsqueda adversarial mediante funciones anidadas MAX/MIN | Misma clase/tupla; corregidos perspectiva, profundidad, pases y terminales; agregado Minimax usando la misma recursión y métricas |
| `AgentesEspecificos/AgenteOthello.py` | Reglas específicas, copia de matriz, recorridos direccionales y evaluación | Se conserva el motor; se añaden las dos evaluaciones seleccionables y se mantiene la fórmula docente como referencia |
| `TableroOthello.py` | Entorno local; estado inicial y ejecución | Corrige referencia a clase inexistente y despacho por color; delega legalidad al agente |
| `servidor.py` | Autoridad del juego, sockets, JSON delimitado por salto de línea, hilos de clientes | Reutiliza el motor; controla turno, límites, final, dos clientes y arranque único |
| `cliente_base.py` | Conexión, recepción en hilo, estado, envío y callbacks | Conservado; base del nuevo cliente automático |
| `cliente_humano.py` | Traduce clics legales a mensajes y actualiza interfaz | Conservado |
| `interfaz_grafica.py` | Dibuja tablero, fichas, opciones, estado y procesa eventos Pygame | Reserva espacio inferior para no tapar la última fila |
| `README.md` | Instrucciones originales | Conservado; menciona archivos “Oficial” no entregados, según confirmó el usuario |
| `intro.png`, `musica.mp3` | Recursos existentes | Conservados |

La matriz NumPy es 8×8 (`0` vacío, `1` negras, `2` blancas). `ElEstado(jugador,get_utilidad,tablero,movidas)` es la tupla del docente; su segundo campo es legado, no un método. Las transiciones copian la matriz. Se conservan métodos como `jugadas`, `getResultado`, `testTerminal`, `funcion_evaluacion` y `programa` y el patrón de herencia. La búsqueda llama a las reglas del dominio; el evaluador añade una función sin sustituir el motor. El servidor publica el estado y los clientes actúan sobre mensajes, no sobre un segundo motor propio.

## Extensiones — 21. Estructura de Archivos

`evaluador.py` reúne las fórmulas; `torneo.py` instrumenta y conserva originales; `estadistica.py` implementa métodos con NumPy/biblioteca estándar; `analizar.py` genera derivados; `verificar_registros.py` reproduce las partidas y `benchmark_othello.py` mide posiciones fijas. `cliente_agente.py` hereda la comunicación original y realiza búsqueda en un hilo separado del dibujo. Las dependencias base son NumPy y Pygame; Matplotlib es opcional para figuras. Las instrucciones ejecutables están en `README_OTHELLO.md`.

## Límites de la revisión — 19. Distribución de Puntos, criterios 2 y 7

Las pruebas verifican reglas, búsqueda, partidas, intercambio cliente-servidor local y exportación. No equivalen a una auditoría de seguridad de red ni a pruebas de carga. El torneo usa adaptadores locales de confianza; no impone un plazo duro por jugada. La ventana gráfica requiere sesión de escritorio; su disposición se verifica mediante renderizado aparte. Cacho queda fuera de esta revisión.
