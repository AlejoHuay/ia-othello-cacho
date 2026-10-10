# Cacho — Mejora de la función de evaluación y selección de jugadas

Parte III y IV de la práctica EC02 (Inteligencia Artificial).

## Ejecución

Desde `codigo/cacho/Cacho/` (Python 3.10+, `pip install -r ../requirements.txt`):

```bash
python main.py                              # Humano vs IA mejorada (pygame)
python main.py --base                       # Humano vs IA del programa base
python -m unittest discover -s pruebas -v   # Pruebas unitarias (18 pruebas)
python torneo_cacho.py                      # Ejecución de torneos y análisis estadístico
```

Partida IA vs IA sin interfaz:

```python
from simulador import jugar_partida
from agente_ia import AgenteCachoMejorado, AgenteCachoBase
r = jugar_partida(AgenteCachoMejorado(), AgenteCachoBase(), semilla=7, empieza=0)
print(r['puntajes'], r['ganador'])
```

## Estructura de Archivos

| Archivo | Contenido |
|---|---|
| `funcion_evaluacion.py` | Tablas exactas de probabilidad, `FuncionEvaluacionBase` (ec. 1), `FuncionEvaluacionMejorada` (ec. 2), `Pesos` |
| `agente_ia.py` | `AgenteCachoMejorado` (Expectiminimax del turno + memo + poda + métricas) y `AgenteCachoBase` (base sin cambios + métricas) |
| `simulador.py` | `jugar_partida()`: simulación de partida IA vs IA reproducible por semilla |
| `torneo_cacho.py` | Ejecución de torneos controlados (100 partidas), tests estadísticos y experimentos de eficiencia |
| `pruebas/test_cacho.py` | Pruebas unitarias completas |
| `EntornoCacho.py`, `AgenteCacho.py`, `VistaCacho.py` | Reglas y entorno de Cacho con soporte simétrico de IA vs IA |
| `AgenteCachoIA.py` | Agente base de referencia |

## 1. Análisis crítico del programa base

1. **Error de perspectiva:** Tras `anotar`, `getResultado` cambiaba el turno y `funcion_evaluacion` se calculaba desde la perspectiva del rival, pero el nodo raíz tomaba el máximo. Resultado: anotar 0 puntos se valoraba por encima de anotar puntajes altos.
2. **Indiferencia en tiradas intermedias:** Con altura = 1, la hoja tras tirar se evaluaba con $p + 0.6 \cdot V_{\text{futuro}} - p_{\text{rival}}$, que no dependía de los dados obtenidos, resultando en elecciones de reserva arbitrarias.
3. **Valores esperados estáticos sesgados:** Se promediaban los 252 multiconjuntos equiprobablemente y para una sola tirada sin re-lanzamientos.
4. **Soporte de turno y simetría:** Se corrigió el fin de partida a 10 rondas completas por jugador y se añadió vista espejada para juego simétrico IA vs IA.

## 2. Nueva función de evaluación (Ecuación 2)

Desde la perspectiva del jugador $j$ (rival $o$), con $\mathcal{L}_j$ las categorías libres:

$$E_{\text{nueva}}(s) = w_1 \cdot f_1 + w_2 \cdot f_2 + w_3 \cdot f_3 + w_4 \cdot f_4$$

| $f_i$ | Definición | Aspecto que cubre |
|---|---|---|
| $f_1 = p_j - p_o$ | Diferencia de puntaje real acumulado | Estado actual |
| $f_2 = \Phi(\mathcal{L}_j) - \Phi(\mathcal{L}_o)$ | Valor futuro con $\mu(c)$ exacto y peso adaptativo por etapa | Proyección del futuro y apertura |
| $f_3 = \pm \max_{c \in \mathcal{L}_m} [V_r^c(\text{dados}) - \mu(c)]$ | Oportunidad dinámica de la mano y tiradas restantes | Valor táctico inmediato |
| $f_4 = -\tanh(\Delta_{\text{esp}} / K) \cdot \sqrt{\sum \sigma^2(\mathcal{L}_j) + \sum \sigma^2(\mathcal{L}_o)}$ | Ajuste de riesgo según si se proyecta ventaja o desventaja | Control de varianza y estrategia |

## 3. Búsqueda y Optimizaciones (`AgenteCachoMejorado`)

- **Profundidad adaptativa:** Búsqueda Expectiminimax hasta el final del propio turno (eliminando la miopía de altura 1).
- **Memoización:** Tablas de transposición para tuplas MAX, AZAR y hojas, reduciendo las evaluaciones en más de $32\times$.
- **Poda Star1 y reducción de simetrías:** Poda analítica en nodos probabilísticos sin pérdida de optimalidad.
