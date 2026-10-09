# Othello — desarrollo y reproducción

## 1. Información General; 21. Estructura de Archivos; 23. Política de Integridad Académica

Alcance exclusivo: Othello. No se modifican Cacho, el artículo principal, el PDF compartido ni la bibliografía existente. Trabajo en `feature/othello`, sin commits, push ni merge. Se conserva la carpeta del docente. La guía se entregó como `practicaEC02_a.pdf`; las presentaciones de apoyo son `Diapo-IA1-03.pdf`, `Diapo-IA04_Informado.pdf` y `Diapo-ED01.pdf`.

La portada y 1. Información General difieren en ponderación y tamaño máximo de grupo; no afectan el algoritmo. La fecha indicada en 1. Información General es 10 de octubre, 23:59. Confirmar aspectos administrativos con el docente.

El código base pertenece al material entregado por el docente (Víctor Rodríguez Estévez). Las extensiones de búsqueda, evaluaciones, torneo, análisis, pruebas y borradores de texto fueron desarrolladas con asistencia de **OpenAI Codex**, en esta conversación del 8–9 de octubre de 2026. El grupo debe revisar, comprender y declarar esa asistencia según 23. Política de Integridad Académica. No se incorporó un motor de Othello de terceros ni código de los papers. Las fórmulas estadísticas se implementaron localmente; sus referencias están en `articulo/othello/FUENTES.md`.

### Correspondencia con 21. Estructura de Archivos

| Rol de la guía | Archivo conservado o añadido |
|---|---|
| agente.py | `AgentesEspecificos/AgenteOthello.py` y `AgenteIA/AgenteJugador.py` |
| evaluador.py | `evaluador.py` |
| torneo.py | `torneo.py` |
| instrucciones | este `README_OTHELLO.md` |
| resultados_othello.csv | `datos/resultados_othello.csv`, desde la raíz del repositorio |
| fuentes del artículo | `articulo/othello/`, fragmentos para la plantilla existente |

No se crean wrappers redundantes ni se trasladan paquetes; los imports del docente se mantienen.

## 3. Contexto del Juego; 3.1. Reglas Fundamentales

Tablero 8×8, 0 vacío, 1 negras, 2 blancas. Coordenadas `(fila,columna)` desde cero. Negras empiezan. Se revisan ocho direcciones y se voltean todas las líneas flanqueadas. Si el rival carece de acciones se devuelve el turno al jugador anterior; si ambos carecen de acciones se termina y se cuentan fichas, aunque queden huecos. Igual conteo significa empate.

La transición legal permanece en `AgenteOthello.getResultado`, que copia la matriz. Servidor y entorno delegan la legalidad al mismo agente, evitando otra implementación del motor. `ElEstado` conserva sus cuatro campos originales. `get_utilidad` dentro de la tupla es un campo legado (0), no un método; la utilidad real se consulta en el agente.

El ciclo local de `TableroOthello` selecciona los agentes insertados por color: primero negras, segundo blancas. La referencia inexistente a `HumanoOthello` fue reemplazada por el color del estado. En red, el servidor evita inicios duplicados, más de dos jugadores y movimientos fuera de rango. La barra inferior de Pygame ocupa 60 píxeles adicionales, sin tapar la última fila.

## 2. Objetivos de Aprendizaje, O2; 19. Distribución de Puntos, criterio 2 “Agente Othello funcional”

El agente es planificador adversarial, determinista, de suma cero e información perfecta. Simula acciones, no aprende pesos. `programa()` almacena la acción mediante `set_acciones`.

- Profundidad predeterminada 4; configurable como entero positivo. Niveles = **fichas colocadas**, no rondas completas. Los pases consumen cero niveles.
- Todas las valoraciones de una búsqueda usan el jugador de la raíz (`self.estado.jugador`). MAX/MIN se selecciona por el jugador del estado, no alternando ciegamente tras un pase.
- Minimax y alfa-beta comparten la recursión; alfa-beta activa los cortes, Minimax los desactiva. No se implementan A*, Expectimax, MCTS ni técnicas ajenas al objetivo.
- Orden determinista común: esquinas primero y luego fila/columna. Empate de valor: primera jugada. No hay desempate aleatorio.
- La utilidad terminal es `signo(Δ)*(10000+abs(Δ))`, empate 0. Siempre domina las heurísticas propuestas, limitadas a [-100,100]. La variante `docente` conserva la fórmula anterior como referencia, pero usa la búsqueda corregida; tampoco supera la utilidad terminal.
- Un nodo evaluado es **una hoja en que se llama a la utilidad terminal o a la evaluación por corte de profundidad**. No son todos los nodos visitados ni las llamadas auxiliares a movilidad. El agente distingue visitados, evaluados, terminales, cortes y pases de búsqueda. El registro por movimiento conserva visitados, evaluados, cortes y pases reales del oponente.
- Las mediciones por movimiento abarcan `programa()` (búsqueda e instrumentación) mediante `perf_counter`, sin red, dibujo ni escritura de registros.

## 19. Distribución de Puntos, criterio 7 “Código Fuente”: instalación y ejecución

Desde la raíz del repositorio, usar Python 3.10 o superior (ver versiones exactas del experimento en su manifiesto):

```powershell
cd codigo/othello/Othello-main
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -B -m unittest discover -s pruebas -v
```

En Linux/macOS la activación es `source .venv/bin/activate`. No se necesita una librería estadística externa. Para figuras, opcionalmente instalar `python -m pip install -r requirements-analisis.txt`. Matplotlib sólo produce los gráficos; NumPy y Pygame ya forman parte de la base. El README original describe archivos “Oficial” ausentes; usar las instrucciones presentes.

Partida en red: en tres terminales situadas en `Othello-main`:

```powershell
python servidor.py
python cliente_humano.py
python cliente_agente.py --evaluacion etapas --profundidad 4 --grafica
```

El servidor solicita host y puerto (por defecto 127.0.0.1:5555); el humano solicita la misma conexión. Para dos IAs, reemplazar el cliente humano por `python cliente_agente.py --evaluacion fija --profundidad 4`. El primer cliente conectado recibe negras. Quitar `--grafica` evita la ventana; `--tecnica minimax` permite la búsqueda sin poda (mucho más costosa).

## 4. Formulación de la Función de Evaluación; 7. Descripción de Funciones en el Artículo; 20.1. Criterio 1: Función de Evaluación Othello (20 pts)

Ver `DISENO_OTHELLO.md` y `articulo/othello/funcion.tex`: dos propuestas identificables `fija` y `etapas`, cuatro componentes, fórmulas, pesos y límites explícitos. La interpretación de “valores estáticos restringidos” fue consultada y aceptada por el usuario como decisión propia, no como límite del docente.

## 6. Descripción de la Competencia; 6.1. Estructura del Torneo; 12.1. Para Othello

Diseño aprobado: 13 aperturas × dos colores × cuatro profundidades (4,5,6,7) = 104 partidas internas. Aperturas generadas con ocho colocaciones legales uniformes entre las disponibles y semilla 20261008; se rechazan estados equivalentes por rotación/reflexión. Esto define una distribución de aperturas aleatorias, no uniformidad sobre todos los tableros ni partidas expertas. Las dos versiones usan siempre la misma profundidad en cada enfrentamiento: se estudia su comparación relativa, no el efecto de profundidad contra un rival fijo.

**Decisión posterior del usuario: terminar sólo el piloto de ocho partidas (primera apertura, dos colores, profundidades 4–7) y dejar las otras 96 pendientes.** No lanzar el comando sin límite hasta que se autorice continuar.

```powershell
# Para iniciar el piloto desde una carpeta de experimento sin partidas:
# --max-partidas cuenta sólo partidas nuevas; no repetir este comando tras las ocho.
python torneo.py --max-partidas 8
# Reanudar después del piloto, sólo cuando el usuario lo indique:
python torneo.py
```

El torneo guarda cada partida inmediatamente y omite las ya completas. `--max-segundos` limita el presupuesto entre partidas; no corta una búsqueda ni garantiza plazo por jugada. Una interrupción conserva el archivo `.progreso.json` como evidencia incompleta, no como resultado; al reanudar se reinicia esa partida desde su apertura. No editar originales ni confundir archivos de progreso con partidas completas. Cambiar plan o fuentes relevantes requiere otra carpeta de salida; el manifiesto impide mezclar versiones.

Puntuación: victoria 1, empate 0.5, derrota 0. No se calcula Elo con un piloto pequeño. Las repeticiones del mismo enfrentamiento determinista no se consideran nuevas observaciones. Una apertura es un bloque; sus colores y profundidades están relacionados. Las comparaciones estadísticas se separan por profundidad.

### Agentes externos — 6. Descripción de la Competencia, punto 3

Pendientes de recepción. El torneo interno no sustituye competencia externa. Se puede usar el protocolo de `ClienteBase` o un adaptador local de confianza registrado por JSON:

```json
[
  {"nombre":"fija","evaluacion":"fija"},
  {"nombre":"etapas","evaluacion":"etapas"},
  {"nombre":"grupo_otro","factory":"adaptador_grupo:crear","opciones":{}}
]
```

`crear(altura, **opciones)` devuelve un objeto con `estado`, `programa()` y `get_acciones()`. Se entrega un `ElEstado` copiado; el adaptador debe devolver una tupla legal y respetar la profundidad convenida. Si conoce sus métricas, publica `metricas['nodos_evaluados']` bajo la definición anterior; si no, queda `null`, nunca cero ficticio. El proceso local no aísla código hostil ni impone timeout a un adaptador; usar sólo código confiable. Ejecución: `python torneo.py --agentes agentes_externos.json --salida ../../../datos/othello/externo`. Confirmar formato, presupuesto y protocolo con el organizador cuando exista torneo externo.

## 22. Formato de Datos; 14. Evidencia Formal de Eficiencia

CSV principal, ocho columnas exactas:

```text
agente_a,agente_b,ganador,diferencia_fichas,profundidad_a,profundidad_b,tiempo_a,tiempo_b
```

`agente_a/b` son identificadores de versiones, no colores. `ganador` es su nombre o el literal `empate`. `diferencia_fichas` = fichas finales de A menos fichas finales de B (negativa si pierde A); empate 0. `tiempo_a/b` = media aritmética del tiempo de decisión por movimiento del agente, en segundos, sin contar los ocho movimientos de apertura. Las filas se identifican en los JSON originales por `id`; su exportación se ordena por el mismo identificador. No añadir columnas al CSV principal.

En `datos/othello/torneo_104/` quedan el manifiesto (hardware, Python, NumPy, semilla, configuración, aperturas, SHA256 de fuentes) y un JSON por partida con colores, cada jugada legal, tiempos, nodos, pases, tablero final y posiciones intermedias. Los movimientos 20,30,40,50 son **colocaciones posteriores a las cuatro fichas iniciales**; se registra la evaluación de ambas funciones desde negras y el tablero para auditoría. No son resultados citados de la guía.

```powershell
python analizar.py --figuras --csv-principal ../../../datos/resultados_othello.csv
python verificar_registros.py
```

El análisis regenera CSV, JSON, tabla LaTeX, resumen LaTeX de resultados y figuras PDF/PNG sin alterar originales. Ver `datos/othello/analisis/RESULTADOS_OTHELLO.md`. Las figuras indican niveles, unidades y cantidad de partidas. Los niveles no ejecutados no se rellenan.

## 13. Métodos Estadísticos Requeridos; 13.1. Ejemplo de Análisis Requerido; 20.3. Criterio 5: Análisis Estadístico (15 pts)

`estadistica.py`: binomial exacto bilateral contra 0.5, Wilson 95%, bootstrap percentil, Pearson/Spearman con rangos medios para empates y chi-cuadrado. La guía ilustra un binomial **unilateral** (58/100, cola superior ≈0.067); nuestro contraste es **bilateral** (≈0.13321), no una discrepancia de cálculo.

En cada profundidad, un bloque gana si A obtiene más de un punto entre sus dos partidas. Se excluyen bloques empatados para el binomial; H0: P(A gana bloque | bloque decisivo)=0.5. Se aplica Holm a la familia de comparaciones. Este estimando no es idéntico a la probabilidad de ganar una partida. Wilson sobre victorias/partidas se rotula descriptivo porque omite el emparejamiento; se añade Wilson sobre bloques decisivos y bootstrap por apertura para diferencia media y proporción de victorias. Semilla 20261008, 5000 réplicas. Con menos de dos bloques no se publica IC bootstrap degenerado.

Correlaciones: por pareja de agentes, profundidad, movimiento y función; evaluación media desde negras frente a diferencia final media negras-blancas, agregadas por apertura. Pearson mide asociación lineal y Spearman asociación de rangos; no equivalen a causalidad ni a precisión predictiva fuera de muestra. Menos de tres bloques o varianza cero: resultado no definido. Cuando procede, p bilateral por permutación de bloques e IC bootstrap con 2000 réplicas; son análisis exploratorios múltiples.

Chi-cuadrado sólo procede con observaciones independientes y frecuencias esperadas suficientes. El round-robin emparejado no cumple esa independencia: no convertir automáticamente sus filas por agente en muestras independientes, pues cada partida aparece para ambos rivales. La función `chi_cuadrado(tabla, independientes=True)` permite analizar futuros diseños de muestras disjuntas (p.ej., agentes contra un rival común con aperturas independientes); requiere todas las esperadas >=5. Por ahora se registra “no aplicable” con motivo. No se fuerza una prueba sólo para llenar la rúbrica.

El piloto no alcanza ≥100 partidas y tiene un solo bloque por profundidad. Que p>=0.05 no demuestra igualdad. Los análisis confirmatorios, bootstrap por bloques y correlaciones fiables quedan limitados por el tamaño muestral; su código está preparado y probado con casos matemáticos de referencia, separados de los resultados reales.

## 14. Evidencia Formal de Eficiencia

Ver complejidad en `DISENO_OTHELLO.md`. La evaluación de una posición y la exploración del árbol son costos distintos. La exigencia del punto 3 de “demostrar” crecimiento polinomial con profundidad contradice el peor caso de Minimax/alfa-beta. El usuario aprobó explicar esa contradicción y mantener pendiente su aclaración con el docente. No se ajusta artificialmente una curva ni se afirma una ley polinomial a partir de cuatro puntos.

`benchmark_othello.py` permite medir las mismas posiciones a distintas profundidades. Su configuración y tiempo quedan separados del torneo. Las mediciones de partidas completas no aíslan por sí solas el efecto de profundidad porque las trayectorias cambian.

Para una comprobación corta y separada, después de terminar el torneo, usar:

```powershell
python benchmark_othello.py --plies 50
python analizar.py --figuras --csv-principal ../../../datos/resultados_othello.csv
```

Esto mide la posición inicial y la posición tras 50 colocaciones de la primera partida: dos versiones × cuatro profundidades × dos posiciones, con una medición por condición. No añade partidas a la competencia. Conserva matrices, turno, versiones, huellas y tiempos en `datos/othello/benchmark_othello.json`; se niega a sobrescribir ese original. Para repetir, especificar otro `--salida` y analizar el archivo correspondiente mediante `figura_benchmark(entrada,salida)` de `analizar.py`. El análisis ordinario detecta el archivo predeterminado y genera `benchmark_loglog_othello.pdf/png` y su CSV.

Son tiempos de pared en un equipo de escritorio, sin aislamiento de CPU ni control de frecuencia. Durante el piloto también se hicieron revisiones y pruebas cortas; no se ejecutaron dos torneos simultáneos. El benchmark se ejecuta después del piloto. Una sola medición por condición no estima variabilidad ni prueba una ley de crecimiento. Las diferencias en nodos explorados ayudan a distinguir trabajo algorítmico de fluctuaciones del sistema.

## 15. Estructura Requerida (Formato LATEX); 17. Referencias Bibliográficas; 18. Longitud

`articulo/othello/INTEGRACION.md` describe las inserciones propuestas, las citas existentes reutilizadas y el suplemento bibliográfico nuevo. No se modifican `articulo.tex`, `articulo.pdf` ni `referencias.bib`. Resumen, diez páginas y ocho referencias son restricciones del artículo conjunto. La integración final requiere autorización del usuario.
