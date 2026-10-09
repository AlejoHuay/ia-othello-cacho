# Diseño de las funciones de Othello

## 4. Formulación de la Función de Evaluación; 7. Descripción de Funciones en el Artículo

Sea s un tablero, j el jugador de referencia y o=3-j. N_j cuenta fichas, C_j esquinas, M_j movimientos legales y F_j fichas frontera (ocupadas y adyacentes en cualquiera de las ocho direcciones a una casilla vacía). Definimos R(a,b)=(a-b)/(a+b), con R(0,0)=0.

Componentes, todos en [-1,1]:

- D=(N_j-N_o)/64: diferencia de fichas, no paridad de regiones vacías.
- C=(C_j-C_o)/4: control de esquinas (cuatro esquinas posibles).
- M=R(M_j,M_o): movilidad actual normalizada.
- F=R(F_o,F_j): frontera inversa; valores positivos significan menos fichas propias expuestas. Es una aproximación de exposición, **no un detector exacto de estabilidad**.

**fija:** H_f(s,j)=10D+40C+35M+15F.

**etapas:** H_e(s,j)=w_D(t)D+w_C(t)C+w_M(t)M+w_F(t)F, t=N_j+N_o:

| Etapa | Condición | w_D | w_C | w_M | w_F |
|---|---|---:|---:|---:|---:|
| Apertura | t<20 | 0 | 35 | 45 | 20 |
| Medio | 20<=t<45 | 10 | 40 | 35 | 15 |
| Final | t>=45 | 55 | 30 | 10 | 5 |

Cada evaluación tiene al menos tres componentes activos en toda etapa. Las dos coinciden durante el medio juego: el experimento contrasta específicamente el cambio de prioridades en apertura/final. Todos los pesos están en [0,55], suman 100 y garantizan |H|<=100 por desigualdad triangular. H(s,j)=-H(s,o). No es una probabilidad calibrada.

**Decisión de diseño consultada — 20.1. Criterio 1: Función de Evaluación Othello (20 pts):** la guía y las diapositivas no definen un intervalo para “valores estáticos restringidos”. El usuario aceptó estos límites explícitos, sin atribuirlos al docente. La evaluación por etapas sigue siendo estática en el sentido de calcularse sobre un estado sin búsqueda interna ni aprendizaje; sus pesos dependen del estado, no son globalmente constantes.

Justificación: C recibe peso elevado por la permanencia de una esquina capturada. M favorece conservar elecciones y restringir al rival. F penaliza exposición, sin contar todas las fichas interiores como estables. D recibe poco peso temprano y mayor peso cerca del final, donde el objetivo real es el conteo. Umbrales 20/45 y pesos son hipótesis de ingeniería definidas antes del piloto, **no valores óptimos aprendidos ni valores prescritos por la literatura**. No se ajustaron con los resultados del piloto. El análisis posterior debe poder refutar su conveniencia; que una función gane pocas partidas no prueba un óptimo universal.

Utilidad terminal, separada de ambas funciones: U(s,j)=0 si Δ=N_j-N_o=0; de lo contrario U=signo(Δ)*(10000+|Δ|). Se maximiza primero ganar, luego el margen. Se comprueba terminalidad antes del corte por profundidad.

### 7. Descripción de Funciones en el Artículo, punto 3

Pseudocódigo (implementación completa: `evaluador.py`):

```text
EVALUAR(tablero,j,version):
    o = 3-j
    contar fichas y esquinas por color
    obtener movimientos legales de j y o con el motor del docente
    para cada ficha: marcar frontera si tiene alguna casilla vacía vecina
    calcular D,C,M,F con las normalizaciones definidas
    seleccionar pesos fijos o etapa por número total de fichas
    devolver producto escalar pesos · (D,C,M,F)
```

### 7. Descripción de Funciones en el Artículo, punto 4; 14. Evidencia Formal de Eficiencia, punto 1

Para distinguir constantes del tablero de costos algorítmicos, generalizamos analíticamente a un tablero n×n, B=n² (el programa sólo acepta 8×8):

| Operación | Tiempo | Espacio adicional |
|---|---|---|
| D, conteo de ocupadas | O(B) | O(B) por comparaciones NumPy |
| C, cuatro esquinas | O(1) | O(1) |
| F, hasta ocho vecinos por ficha | O(B) | O(1) en el recorrido |
| Movimiento legal individual | O(n) | O(1) |
| M, examinar B casillas y rayos para dos jugadores | O(Bn)=O(n³) | O(B) para listas |
| Selección de pesos y suma de cuatro términos | O(1), reutilizando ocupadas; el código vuelve a contarlas en O(B) | O(B) |
| H_f y H_e completas | O(n³) | O(B) |
| Transición: copia, volteo y nuevas acciones | O(n³) | O(B) |

Con n=8 estos recorridos tienen cotas constantes, pero no es correcto ocultar el costo de los rayos al generalizar. La normalización cuesta O(1) por componente. El orden de acciones usado (esquinas antes, después coordenadas) cuesta O(b log b) por nodo; no valora estados adicionales y es el mismo en ambos agentes.

Con ramificación b y profundidad d: Minimax tiene O(b^d) nodos; alfa-beta mantiene ese peor caso, y en un árbol regular de niveles MAX/MIN alternados con orden ideal se aproxima a O(b^(d/2)). Esa cota ideal no es una garantía para todos los árboles reales con pases. Incluyendo generación y evaluación, una cota simple es O(b^d*(n³+b log b)). La exploración en profundidad mantiene O(d*(B+b)) de memoria para tableros y listas de acciones por nivel, sin tabla de transposición. No se crean todos los hijos simultáneamente. Aumentar d no tiene garantía de crecimiento polinomial.

## 5. Análisis Crítico Requerido

**Punto 1.** Un peso ligado sólo a la coordenada ignora quién controla la esquina vecina, las líneas abiertas y las respuestas del adversario. Contar capturas inmediatas puede mejorar D ahora y empeorar M/F, exponiendo líneas para el siguiente turno. El “máximo local” de la guía describe esa miopía estratégica; no significa que aquí se implemente ascenso de colinas. IAGO, BILL y el trabajo de Buro son antecedentes de evaluaciones más ricas que un único conteo; sus resultados no demuestran por sí solos que nuestros pesos concretos sean superiores. No afirmamos una victoria empírica de una función sobre otra sin datos propios.

**Punto 2.** La movilidad representa alternativas legales y restricciones del rival. Contar cada alternativa igual sigue siendo limitado: una jugada forzada peligrosa no vale lo mismo que una esquina segura. La guía menciona *sandwich squares* sin definir un patrón formal ni aportar fuente específica. Su advertencia puede discutirse sin inventar una tabla: una configuración que facilita flanqueos al rival puede correlacionarse negativamente con la ventaja aunque visualmente parezca favorable. El signo de un peso aprendido es condicional al resto de rasgos, sus correlaciones y la etapa; no demuestra una regla universal sobre una casilla. No equiparamos sin evidencia *sandwich squares* con todas las casillas X/C, ni añadimos penalizaciones arbitrarias a ellas. La definición operativa concreta del término queda pendiente de fuente o aclaración docente. Nuestra penalización de frontera sí está definida: usar F=(F_o-F_j)/(F_o+F_j) con peso positivo equivale a penalizar exposición propia. Menos frontera tampoco garantiza más estabilidad.

**Punto 3.** Al inicio hay pocos discos pero muchas decisiones futuras; al final el conteo determina el ganador. `etapas` representa esa hipótesis con tres rangos. Los saltos de pesos en t=20 y t=45 pueden crear discontinuidades y efectos de horizonte. La guía atribuye a Logistello 13 etapas: es un antecedente indicado por la guía, no un resultado nuestro ni una obligación de implementar 13. Tampoco la diferencia de fichas D implementa la paridad regional de casillas vacías usada en otros programas.

**Punto 4.** Calcular movilidad para ambos colores domina el costo de las cuatro características. Una evaluación más elaborada puede reducir nodos por orden/prioridades diferentes o empeorar el tiempo aunque mejore el juego. La frase de la guía sobre una pérdida de velocidad de aproximadamente 15% al calcular paridad en Logistello se conserva como afirmación de ese material, no como cifra verificada de este proyecto. Nuestro contraste mantiene exactamente las mismas características para aislar el efecto de los pesos: no mide aisladamente el costo/beneficio de añadir frontera o movilidad. Para eso haría falta una ablación adicional. Tiempos y nodos propios se reportan por separado y no validan automáticamente fuerza estratégica.

## 14. Evidencia Formal de Eficiencia, puntos 2 y 3

Las correlaciones intermedias y la diferencia final usan una perspectiva común: negras. La etapa se cuenta por colocaciones (20,30,40,50), no por turnos que pueden incluir pases. Estas posiciones están seleccionadas por las políticas del torneo y no constituyen una muestra independiente de todas las posiciones posibles. Las observaciones de ambos colores, de varias profundidades y de varios momentos de la misma apertura están relacionadas. Se agrupan por apertura y se separan los estratos; el piloto de una sola apertura no permite estimar correlación entre bloques.

La medición log-log describe el costo observado. Incluso una recta aproximada en un rango corto no prueba crecimiento polinomial. La contradicción del punto 3 fue consultada y se acordó explicar la cota exponencial, publicar tiempos reales y dejar la aclaración con el docente pendiente.
