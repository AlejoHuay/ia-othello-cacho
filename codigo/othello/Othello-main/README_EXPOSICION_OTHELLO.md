# Othello: síntesis para una exposición de 8:20 minutos

**Propósito:** explicar los aportes sobre la base del docente, las dos evaluaciones, los resultados y sus límites. Sólo Othello, fase 3. **11 diapositivas, duración estimada 8:20; ensayar para terminar entre 7 y 9 minutos.** Los números de este README organizan la exposición; no sustituyen los apartados de la guía, citados expresamente en cada bloque.

**Uso:** trasladar las ideas y tablas a diapositivas. No leer todas las celdas, referencias ni nombres de archivos. El respaldo final queda fuera de la exposición. La duración se confirma con ensayo, no por el número de diapositivas.

| Diapositiva | Tema | Tiempo |
|---:|---|---:|
| 1 | Juego y objetivo | 0:25 |
| 2 | Base docente y aportes | 0:40 |
| 3 | Agente y búsqueda | 0:40 |
| 4 | Dos evaluaciones | 1:05 |
| 5 | Análisis crítico | 0:30 |
| 6 | Experimento y registros | 0:40 |
| 7 | Resultados internos y estadística | 1:15 |
| 8 | Competencia externa | 0:55 |
| 9 | Eficiencia y validación | 0:55 |
| 10 | Artículo y conclusión | 0:50 |
| 11 | Aclaraciones al docente | 0:25 |

## 1. Juego y objetivo

**Guía:** 2. Objetivos de Aprendizaje, O2; 3. Contexto del Juego; 3.1. Reglas Fundamentales.

- Tablero **8×8**; negras inicia. Una jugada legal encierra y voltea fichas rivales en las direcciones correspondientes.
- Sin movimientos, se pasa; termina cuando ninguno puede mover, incluso con casillas vacías. Gana quien tiene más fichas; puede haber empate.
- **Objetivo:** comparar pesos fijos frente a pesos por etapa, manteniendo la misma búsqueda.

## 2. Base docente y aportes

**Guía:** 19. Distribución de Puntos, criterio 7 “Código Fuente”; 21. Estructura de Archivos.

| Conservamos | Implementamos o corregimos |
|---|---|
| Clases, herencia, `ElEstado` y matriz NumPy | Turnos, pases, profundidad, terminales y copia del estado |
| Motor de movimientos y volteos | Dos evaluaciones seleccionables y búsqueda instrumentada |
| Servidor, clientes y Pygame | Cliente automático, controles del servidor y marcador sin tapar tablero |
| Organización del docente | Torneo reanudable, análisis, registros, pruebas y secciones LaTeX |

Sin sustituir el motor ni modificar Cacho. NumPy/Pygame como base; Matplotlib para gráficos. Estadística con NumPy y biblioteca estándar, sin SciPy.

## 3. Agente y búsqueda

**Guía:** 2. Objetivos de Aprendizaje, O2; 3.1. Reglas Fundamentales; 19. Distribución de Puntos, criterio 2 “Agente Othello funcional”.

**Agente planificador adversarial:** determinista, de información perfecta y utilidad de suma cero. No aprende mediante entrenamiento.

`Estado → movimientos legales → Minimax con Alpha-Beta → evaluación → acción`

- MAX favorece al jugador de la raíz; MIN representa al rival. Alpha-Beta descarta ramas que no cambian la decisión de Minimax.
- Profundidad configurable, predeterminada **4**: colocación = un nivel; pase = cero. Se respeta el turno real y no se altera el tablero original.
- Final antes del corte: utilidad 0 para empate; si no, `signo(Δ) × (10000 + |Δ|)`. Ganar domina la heurística.

## 4. Dos funciones de evaluación

**Guía:** 4. Formulación de la Función de Evaluación; 7. Descripción de Funciones en el Artículo; 20.1. Criterio 1: Función de Evaluación Othello (20 pts).

`j`: jugador propio; `o`: rival. N cuenta fichas; C esquinas; M movimientos legales; F fichas frontera, adyacentes a alguna casilla vacía.

| Componente | Fórmula normalizada | Intención |
|---|---|---|
| D | `(N_j−N_o)/64` | Más fichas |
| C | `(C_j−C_o)/4` | Controlar esquinas |
| M | `(M_j−M_o)/(M_j+M_o)` | Conservar opciones |
| F | `(F_o−F_j)/(F_o+F_j)` | Reducir exposición |

Denominador cero → componente cero. Todos en `[-1,1]`.

**Fija:** `H_f = 10D + 40C + 35M + 15F`.

**Etapas:** `H_e = w_D(t)D + w_C(t)C + w_M(t)M + w_F(t)F`; `t` = fichas ocupadas.

| Etapa | Condición | D | C | M | F |
|---|---|---:|---:|---:|---:|
| Apertura | t < 20 | 0 | 35 | 45 | 20 |
| Medio juego | 20 ≤ t < 45 | 10 | 40 | 35 | 15 |
| Final | t ≥ 45 | 55 | 30 | 10 | 5 |

**Idea:** movilidad temprana y conteo al final. Coinciden en medio juego. Pesos en `[0,55]`, suma 100, evaluación en `[-100,100]`; al menos tres componentes activos. Son decisiones propias, no pesos óptimos ni límites numéricos impuestos por el docente.

Cálculo: **contar → normalizar → elegir pesos → sumar productos**. Detalle y pseudocódigo: [DISENO_OTHELLO.md](DISENO_OTHELLO.md); código: [evaluador.py](evaluador.py).

## 5. Análisis crítico

**Guía:** 5. Análisis Crítico Requerido, puntos 1–4; 7. Descripción de Funciones en el Artículo.

| Punto | Qué aprendimos |
|---:|---|
| 1 | Capturar muchas fichas ahora puede empeorar el futuro; un valor fijo de casilla ignora contexto. |
| 2 | Importa la movilidad, pero no todas las opciones son buenas. La frontera penaliza exposición, no mide estabilidad exacta; pesos negativos dependen del contexto. |
| 3 | Prioridades distintas por etapa; nuestros umbrales introducen saltos y no están optimizados. |
| 4 | Más costo de evaluación exige justificar beneficio. Comparamos pesos, sin aislar el efecto de cada componente mediante ablaciones. |

Las 13 etapas y cifras de Logistello citadas por la guía no son resultados propios. *Sandwich squares* se reserva para la última diapositiva.

## 6. Experimento y registros

**Guía:** 6. Descripción de la Competencia; 6.1. Estructura del Torneo; 12.1. Para Othello; 22. Formato de Datos.

- Plan: **13 aperturas × 2 colores × 4 profundidades = 104 partidas**; fija y etapas a igual profundidad (4–7). Aperturas de ocho colocaciones, semilla `20261008`, descartando equivalencias por simetría.
- Muestra cerrada por costo computacional: **19 completas; 85 no ejecutadas**. No se cumple el umbral de ≥100 para excelencia estadística.
- Bloque = apertura con ambos colores. Hay **3/2/2/2 bloques completos**; una partida de profundidad 5 no tiene pareja. Repeticiones deterministas no son evidencia independiente.
- Victoria/empate/derrota: **1/0.5/0 puntos**. JSON conserva jugadas, nodos, tiempos y posiciones intermedias; manifiesto conserva hardware, versiones, semillas y huellas. Torneo reanudable y con adaptadores externos.

CSV de ocho columnas: `agente_a,agente_b,ganador,diferencia_fichas,profundidad_a,profundidad_b,tiempo_a,tiempo_b`. Diferencia=A−B; tiempos=segundos medios por decisión; empate=`empate`. Derivados regenerables desde originales.

## 7. Resultados internos y estadística

**Guía:** 12. Resultados Requeridos; 12.1. Para Othello, punto 2; 13. Métodos Estadísticos Requeridos; 13.1. Ejemplo de Análisis Requerido; 20.3. Criterio 5: Análisis Estadístico (15 pts).

| Prof. | Partidas | Victorias fija / etapas | Δ media fija | s/jugada fija / etapas |
|---:|---:|---|---:|---|
| 4 | 6 | 4 / 2 | +7.33 | 0.225 / 0.233 |
| 5 | 5 | 4 / 1 | +14.40 | 0.775 / 0.778 |
| 6 | 4 | 3 / 1 | +7.50 | 3.813 / 4.172 |
| 7 | 4 | 3 / 1 | +6.50 | 19.213 / 20.084 |
| Total | 19 | **14 / 5** | **+9.05** | — |

Sin empates: **14 y 5 puntos**. Ventaja descriptiva de fija, **no superioridad general demostrada**.

- **Binomial bilateral:** H0=P(ganar bloque decisivo)=0.5; excluye bloques empatados. Todos los p ajustados por Holm son 1. No rechazar H0 no prueba igualdad.
- **Wilson 95% y bootstrap por apertura:** calculados, pero sólo 2–3 bloques. Un intervalo degenerado no significa certeza.
- **Pearson/Spearman:** evaluación y resultado desde negras, por apertura y estrato. Sólo d4 tiene tres bloques; ninguna correlación alcanza p nominal <0.05. En d5–7: no estimables.
- **Chi-cuadrado:** no aplicable; las filas de rivales comparten partidas.

La partida sin pareja sólo entra en totales descriptivos. Una tabla adicional compara las mismas dos aperturas en todos los niveles (**16 partidas**). Las curvas principales tienen muestras desiguales y ambos rivales aumentan profundidad; no miden mejora contra un rival fijo.

**Visual:** [victorias frente a profundidad](../../../datos/othello/analisis/victorias_profundidad_othello.png).

## 8. Competencia externa y mejoras

**Guía:** 6. Descripción de la Competencia; 6.1. Estructura del Torneo; 12.1. Para Othello; 5. Análisis Crítico Requerido.

Ispis: **fija, profundidad 4, Minimax con Alpha-Beta** en los cinco encuentros reportados.

| Partida | Rival | Color Ispis | Fichas Ispis–rival | Resultado |
|---:|---|---|---|---|
| 1 | Juan Pablo | Negras | 25–39 | Derrota |
| 2 | Juan Pablo | Blancas | 31–33 | Derrota |
| 3 | Juan Pablo | Negras | 25–39 | Derrota |
| 4 | Daniela | Negras | 49–15 | Victoria |
| 5 | Daniela | Blancas | 4–59 | Derrota reportada* |

**1 victoria, 4 derrotas, 0 empates; 1 punto; Δ media −10.20.** Tres capturas originales respaldan los marcadores contra Juan Pablo. Independencia de P1/P3 no establecida; sin trazas, tiempos ni configuración rival. *P5: 63 fichas; final legal posible, pero no confirmado. Muestra separada de las 19 internas, sin inferencia estadística.

**Mejora propuesta:** no sabemos qué decisiones causaron las derrotas. Profundidad 4 y falta de estabilidad exacta/riesgo contextual de esquinas son limitaciones plausibles. Registrar jugadas, revisar decisiones, contrastar pesos y probar mayor profundidad con igual presupuesto, un cambio por vez y ambos colores. Sin garantía de ganar.

**Evidencia:** [tabla y capturas](../../../datos/othello/competencia_externa/COMPETENCIA_EXTERNA_OTHELLO.md).

## 9. Eficiencia y validación

**Guía:** 14. Evidencia Formal de Eficiencia, puntos 1–3; 3.1. Reglas Fundamentales; 19. Distribución de Puntos, criterios 2 y 7.

| Aspecto | Evidencia |
|---|---|
| Evaluar un tablero n×n | Fichas/frontera O(n²), esquinas O(1), movilidad O(n³); total **O(n³)**. Tablero real: 8×8. |
| Explorar el árbol | Minimax/Alpha-Beta: **O(b^d) nodos en peor caso**; la poda depende del orden. |
| Costo observado | **86.47 min** de decisiones; **68.09 min** en las cuatro partidas de profundidad 7. No equivale al tiempo total de sesión. |
| Instrumentación | Nodo evaluado = hoja terminal o de corte; nodos/segundo y tiempo por movimiento. |
| Benchmark | **16 decisiones**, dos posiciones fijas; una medición por condición. Sin nuevas partidas ni estimación de variabilidad. |
| Verificación | **20 pruebas correctas y 19 registros reproducidos**: reglas, pases, terminales, copias, búsqueda, red y análisis. Externos: totales y capturas, no reproducción legal. |

**Visual:** [tiempo por profundidad](../../../datos/othello/analisis/tiempo_profundidad_othello.png) o [benchmark log-log](../../../datos/othello/analisis/benchmark_loglog_othello.png).

## 10. Artículo, entrega y conclusión

**Guía:** 1. Información General; 15. Estructura Requerida (Formato LATEX); 16. Formato de Tablas y Figuras; 17. Referencias Bibliográficas; 18. Longitud; 21. Estructura de Archivos; 23. Política de Integridad Académica.

**Preparado:** introducción, teoría, evaluaciones, competencia interna/externa, estadística/eficiencia, conclusiones y aporte al resumen. LaTeX con `booktabs`, ecuaciones y figuras; capturas para apéndice y compilación aislada revisada. Entrega: código, dependencias, comandos, datos, gráficos, pruebas y fuentes.

**Bibliografía:** Rosenbloom (1982, IAGO), Lee y Mahajan (1990, BILL), Buro (1999, construcción de características); Wilson, Efron y NIST para estadística. Fuentes y títulos completos: [FUENTES.md](../../../articulo/othello/FUENTES.md). Sus resultados no se atribuyen a nuestros agentes.

**Pendiente conjunto:** integrar Cacho, revisar resumen de 150–250 palabras, mínimo de ocho referencias y máximo de diez páginas sin referencias/apéndices. Declarar en el artículo final la base docente y asistencia de **OpenAI Codex**, ya explícitas en la documentación; revisión humana antes de entregar.

**Conclusión oral:** “Implementamos dos agentes comparables y un análisis reproducible sobre la base docente. Fija ganó más partidas internas, pero no demostramos superioridad general. El costo y la competencia externa señalan límites concretos para futuras mejoras”.

## 11. Aclaraciones al docente — una sola diapositiva

| Apartado exacto | Aclaración pendiente |
|---|---|
| **14. Evidencia Formal de Eficiencia, punto 3** | La petición de demostrar crecimiento polinomial en profundidad contradice el peor caso exponencial. Presentamos teoría y mediciones reales, sin afirmar esa propiedad. |
| **5. Análisis Crítico Requerido, punto 2** | Precisar la definición operativa de *sandwich squares*. Se discutió movilidad/contexto sin inventarla ni equipararla automáticamente con casillas X/C. |

**25 segundos, sin ampliar a otra diapositiva.**

---

## Respaldo para preguntas — fuera de los 8:20

### Estadística: 13. Métodos Estadísticos Requeridos

| Profundidad | Bloques | p binomial / Holm | Δ media en pares | Bootstrap 95% Δ |
|---:|---:|---|---:|---|
| 4 | 3 | 1 / 1 | 7.33 | [0,19] |
| 5 | 2 | 0.5 / 1 | 21.50 | [18,25] |
| 6 | 2 | 1 / 1 | 7.50 | [−4,19] |
| 7 | 2 | 1 / 1 | 6.50 | [1,12] |

D5 excluye la partida sin pareja para inferencia, por eso su media no es 14.40. Los IC que excluyen cero usan sólo dos bloques: no prueban superioridad. Bootstrap de medias: 5000 réplicas; correlación/permutación: 2000; semilla `20261008`. Wilson por bloques decisivos; por partidas, sólo descriptivo. Correlaciones en colocaciones 20/30/40/50, p exploratorios sin ajuste múltiple. [Informe completo](../../../datos/othello/analisis/INFERENCIA_OTHELLO.md).

### Reproducción: 19. Distribución de Puntos, criterio 7; 22. Formato de Datos

Desde la raíz, en un entorno Python preparado; estos comandos no amplían el experimento:

```bash
cd codigo/othello/Othello-main
python -m pip install -r requirements.txt -r requirements-analisis.txt
python -B -m unittest discover -s pruebas -v
python -B verificar_registros.py
python -B analizar.py --figuras --csv-principal ../../../datos/resultados_othello.csv
python -B analizar_externa_othello.py
```

Las pruebas tienen sus propias partidas temporales, excluidas del experimento. Instalación y juego: [README técnico](README_OTHELLO.md); demo en vivo fuera del tiempo propuesto.

### Evidencias y estado: 19. Distribución de Puntos; 20.1. Criterio 1: Función de Evaluación Othello (20 pts); 20.3. Criterio 5: Análisis Estadístico (15 pts)

- [Base docente y cambios](REVISION_BASE_OTHELLO.md).
- [Fórmulas, justificación, pseudocódigo y complejidad](DISENO_OTHELLO.md).
- [Discusión de las 19 partidas](../../../datos/othello/analisis/DISCUSION_OTHELLO.md).
- [Integración del artículo y referencias](../../../articulo/othello/INTEGRACION.md).
- [Matriz completa de requisitos, evidencias y estados](MATRIZ_CUMPLIMIENTO_OTHELLO.md).
- [Validación del análisis](../../../datos/othello/validacion/VALIDACION_19_OTHELLO.md).

**Límites:** no se completaron 104 partidas, no hay torneo externo plenamente instrumentado y falta integrar el artículo conjunto. Los apartados 8–11, 12.2 y 20.2 de la guía corresponden a Cacho y no se incluyen. Síntesis elaborada con asistencia de OpenAI Codex, basada en resultados del repositorio.
