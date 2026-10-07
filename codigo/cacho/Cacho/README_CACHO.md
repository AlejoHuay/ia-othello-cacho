# Cacho — Mejora de la función de evaluación y selección de jugadas

Parte III de la práctica EC02. Este documento cubre la **primera mitad** del
trabajo de Cacho (función de evaluación + agente). La **segunda mitad**
(torneo, estadística, ajuste de pesos y redacción) está detallada al final en
[Pendiente para el compañero](#pendiente-para-el-compañero-segunda-mitad).

## Ejecución

Desde `codigo/cacho/Cacho/` (Python 3.10+, `pip install -r ../requirements.txt`):

```bash
python main.py                 # Humano vs IA mejorada (pygame)
python main.py --base          # Humano vs IA del programa base
python -m unittest discover -s pruebas -v   # 18 pruebas
```

Partida IA vs IA sin interfaz:

```python
from simulador import jugar_partida
from agente_ia import AgenteCachoMejorado, AgenteCachoBase
r = jugar_partida(AgenteCachoMejorado(), AgenteCachoBase(), semilla=7, empieza=0)
print(r['puntajes'], r['ganador'])
```

## Archivos

| Archivo | Estado | Contenido |
|---|---|---|
| `funcion_evaluacion.py` | nuevo | Tablas exactas de probabilidad, `FuncionEvaluacionBase` (ec. 1), `FuncionEvaluacionMejorada` (ec. 2), `Pesos` |
| `agente_ia.py` | nuevo | `AgenteCachoMejorado` (Expectiminimax del turno + memo + poda + métricas) y `AgenteCachoBase` (base sin cambios + métricas) |
| `simulador.py` | nuevo | `jugar_partida()`: una partida IA vs IA reproducible por semilla |
| `pruebas/test_cacho.py` | nuevo | Pruebas unitarias |
| `EntornoCacho.py`, `AgenteCacho.py`, `VistaCacho.py` | corregidos | Fin de partida a 10 rondas por jugador, primera mano tirada, contador de ronda |
| `main.py` | modificado | Permite elegir IA mejorada o base |
| `AgenteCachoIA.py` | **sin cambios** | Agente base, se usa como referencia en el torneo |

## 1. Análisis crítico del programa base (hallazgos verificados)

1. **Error de perspectiva.** Tras `anotar`, `getResultado` cambia el turno y
   `funcion_evaluacion` se calcula desde la perspectiva del *rival*, pero el nodo
   raíz igual toma el máximo. Resultado: anotar 0 puntos "vale más" que anotar
   muchos. Ejemplo medido con dados (2,3,3,5,6): anotar `1` (0 pts) = 16.9,
   anotar `3` (6 pts) = 10.9. El parche `pts >= 20` solo lo oculta en parte.
2. **Todas las tiradas valen lo mismo.** Con altura = 1, la hoja tras tirar se
   evalúa con `p + 0.6·Vfut − p_rival`, que **no depende de los dados**. Las 31
   opciones de re-tirada empatan y se elige la primera del conjunto (orden
   arbitrario); en el ejemplo, re-tira los 5 dados descartando el par de 3.
3. **Valores esperados estáticos mal ponderados.** `_valor_esperado_cat` promedia
   los 252 multiconjuntos como si fueran equiprobables y considera **una sola
   tirada**. Comparación con el valor exacto (4 tiradas, 1ª + 3 re-tiradas):

   | Categoría | Base (estático) | Exacto μ(c) | σ(c) |
   |---|---|---|---|
   | 1 … 6 | 0.83 … 5.00 | 2.59 … 15.53 | 1.12 … 6.70 |
   | escalera | 0.20 | 9.76 | 12.20 |
   | full | 3.57 | 15.36 | 15.00 |
   | póker | 5.71 | 17.92 | 19.89 |
   | grande | 1.19 | 5.03 | 15.04 |

4. **El rival no tiene término futuro** en el código (la ecuación (1) sí lo incluye).
5. **Fin de partida incorrecto:** terminaba con 10 anotaciones *en total*
   (5 por jugador), contra la regla "10 rondas, una categoría por ronda por jugador".
6. **Primer turno distinto:** iniciaba con dados (1,1,1,1,1) sin tirar; los demás
   turnos empiezan con mano tirada + 3 re-tiradas.
7. **Supone ser el jugador 0** (`es_max_nodo = turno == 0`): no puede jugar IA vs IA
   como jugador 1. El simulador le entrega una vista espejada para que juegue igual.

Prueba informal (20 partidas, semillas 0–19): mejorada 174.1 pts de media vs
base 14.7; la mejorada gana 20/20. **La evaluación formal (≥ 100 partidas,
tests) es parte de la segunda mitad.**

## 2. Nueva función de evaluación (ecuación 2)

Desde la perspectiva del jugador *j* (rival *o*), con L_j las categorías libres:

E_nueva(s) = w1·f1 + w2·f2 + w3·f3 + w4·f4

| f_i | Definición | Mejora del enunciado que cubre |
|---|---|---|
| f1 = p_j − p_o | diferencia de puntaje | — |
| f2 = Φ(L_j) − Φ(L_o), Φ(L) = (1 + β·(\|L\|−1)/9)·Σ_{c∈L} μ(c) | valor futuro con μ(c) **exacto** y peso por etapa | valores esperados dinámicos, pesos adaptativos por etapa |
| f3 = ± max_{c∈L_m} [V_r^c(dados) − μ(c)] | oportunidad de la mano en curso del que mueve *m* (+ si es j); si la mano aún no se tiró se usa su esperanza | valores dinámicos según dados y tiradas restantes |
| f4 = −tanh(Δ_esp / K) · sqrt(Σ σ²(L_j) + Σ σ²(L_o)) | riesgo: si se espera ir ganando (Δ_esp > 0) penaliza la varianza restante; si se espera ir perdiendo, la premia | penalización por varianza, interacción estratégica |

- **V_r^c(d)**: valor esperado exacto de la categoría *c* con mano *d* y *r* re-tiradas,
  jugando óptimamente para *c* (programación dinámica sobre la cadena de Markov
  de los dados: 252 manos × 210 reservas). μ(c) = Σ_d P₀(d)·V_3^c(d).
- Σ μ(c) es una **cota inferior** del futuro real (estrategia "fijar una categoría
  por turno"); por eso w2 = 1 en vez del α = 0.6 arbitrario, y β > 0 agrega la
  flexibilidad de tener más categorías para elegir al inicio.
- Δ_esp = f1 + Σμ(L_j) − Σμ(L_o) (diferencia final esperada). f4 aproxima maximizar
  P(ganar) ≈ Φ(Δ_esp / σ_total) en lugar de solo la diferencia esperada.
- La función es de **suma cero**: E(s, j) = −E(s, o) (verificado en las pruebas).

**Pesos por defecto y rangos** (`funcion_evaluacion.Pesos`):

| Peso | Defecto | Rango para ajustar |
|---|---|---|
| w1 `w_puntaje` | 1.0 | fijo (escala) |
| w2 `w_futuro` | 1.0 | [0.5, 1.5] |
| β `beta_etapa` | 0.10 | [0.0, 0.5] |
| w3 `w_oportunidad` | 1.0 | [0.0, 1.5] |
| w4 `w_riesgo` | 0.10 | [0.0, 0.5] |
| K `escala_riesgo` | 25 | [10, 60] |

Los valores por defecto son iniciales justificados teóricamente; **el ajuste
experimental es tarea de la segunda mitad.**

## 3. Selección de jugadas (`AgenteCachoMejorado`)

- **Profundidad adaptativa / anti-miopía:** Expectiminimax con nodos MAX (decidir)
  y AZAR (tirada) hasta el **final del propio turno**; la profundidad es igual a
  las tiradas restantes (3 → 0). Las hojas son siempre "anotar c" evaluadas con
  E_nueva. La IA ve que debe anotar al final, por lo que no hacen falta el umbral
  `pts >= 20` ni el "forzar anotar" del base. El turno del rival no se expande
  porque en Cacho las acciones del rival no dependen de las propias (solo f4 los
  relaciona). Con `profundidad=k` se limita a k niveles de AZAR (útil para la
  curva rendimiento vs profundidad).
- **Memoización:** tablas de transposición para nodos MAX `(mano, r)`, AZAR
  `(reserva, r)` y hojas `(categoría, puntos)`. Con profundidad 1: 18 512 → 296
  evaluaciones por decisión (≈ 60×).
- **Poda:** (a) re-tiradas equivalentes (mismo multiconjunto conservado) se
  exploran una vez; (b) poda **Star1** (Ballard 1983) en nodos AZAR con la cota
  superior `cota_superior_anotar`. Ninguna cambia la decisión (prueba
  `test_memo_y_poda_no_cambian_la_decision`).
- **Costo:** precálculo O(|C|·R·|Res|·|E|) ≈ 10·3·210·252 una sola vez (~0.35 s).
  Por decisión, con memo, como máximo O(R·|E|·K·|E|) con |E| = 252 manos,
  K ≤ 31 reservas, R ≤ 3; medido: ~5 ms y ~13 000 nodos en promedio. Cada
  evaluación de E_nueva es O(|C|) = O(10).

### Métricas disponibles para el torneo

- `agente.metricas` (lista, una entrada por decisión): `tiempo`, `nodos_max`,
  `nodos_azar`, `evaluaciones`, `cortes`, `tiradas_restantes`, `ronda`, `accion`,
  `valor`. `AgenteCachoBase.metricas` registra `tiempo` y `evaluaciones`.
- `agente.ultima_valoracion`: dict acción → valor de la última decisión (para el
  análisis de decisiones).
- Variantes: `AgenteCachoMejorado(evaluador=FuncionEvaluacionBase())` (búsqueda
  nueva + función base), `usar_memo=False`, `usar_poda=False`, `profundidad=1|2|None`.
  Sin memo usar solo `profundidad=1` (más profundo es exponencial).

Resultado informal: misma búsqueda, E_nueva vs E_base, 60 partidas
(semillas 1000–1059): 33 victorias, +13.5 pts de diferencia media.
**No es concluyente; hay que confirmarlo con ≥ 100 partidas y tests.**

## Pendiente para el compañero (segunda mitad)

1. **`torneo_cacho.py`** (en esta carpeta) usando `simulador.jugar_partida`:
   - ≥ 100 partidas (recomendado 200) por enfrentamiento, alternando `empieza`,
     semillas documentadas y comunes para todos los enfrentamientos.
   - Enfrentamientos: `AgenteCachoBase` vs `AgenteCachoMejorado`;
     `AgenteCachoMejorado(evaluador=FuncionEvaluacionBase())` vs `AgenteCachoMejorado()`
     (aísla el aporte de la función respecto al de la búsqueda).
   - Guardar `datos/resultados_cacho.csv` con al menos
     `agente_a,agente_b,puntaje_a,puntaje_b,version_funcion,tiempo_decision_promedio`
     (sugerido agregar `semilla,empieza,ganador,evaluaciones_promedio`).
2. **Métricas de eficiencia:** tiempo y evaluaciones promedio por decisión;
   comparación antes/después de memoización y poda (`usar_memo`, `usar_poda`,
   `profundidad`).
3. **Estadística** (scipy/numpy): test binomial, intervalo de Wilson 95 %,
   chi-cuadrado, bootstrap de la diferencia media, Pearson/Spearman entre el
   valor de la función a mitad de partida (`metricas['valor']`) y la diferencia final.
4. **Ajuste de pesos** dentro de los rangos de la tabla: barrido experimental o
   algoritmo genético (cromosoma real, selección por torneo, cruce, mutación
   gaussiana, elitismo; fitness = diferencia media contra un rival fijo con semillas comunes).
5. **Análisis de decisiones:** casos donde la mejorada decide distinto que la base
   (usar `ultima_valoracion`) y explicación cualitativa.
6. **Gráficos** (matplotlib) y **redacción** de la sección Cacho del artículo
   (secciones 8–11 y 12.2 del enunciado), incluyendo la discusión de
   exploración vs explotación y el efecto de la varianza.

## Referencias sugeridas para la sección de Cacho (verificar antes de citar)

- Michie, D. (1966). Game-playing and game-learning automata (origen de Expectiminimax).
- Ballard, B. W. (1983). The *-minimax search procedure for trees containing chance nodes. *Artificial Intelligence*, 21(3).
- Verhoeff, T. (1999). Optimal solitaire Yahtzee strategies.
- Glenn, J. (2006). An optimal strategy for Yahtzee. Loyola College, Technical Report.
- Russell, S. & Norvig, P. *Artificial Intelligence: A Modern Approach*, cap. de juegos estocásticos.
- Wilson, E. B. (1927). Probable inference... *JASA*, 22(158) (intervalo de Wilson).

## Uso de IA

El código de esta mitad se desarrolló con asistencia de Claude (Anthropic);
debe citarse según la política de integridad de la práctica.
