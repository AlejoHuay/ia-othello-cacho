# Inferencia de Othello por bloques

Referencia: 12.1. Para Othello, punto 2; 13. Métodos Estadísticos Requeridos; 13.1. Ejemplo de Análisis Requerido; 14. Evidencia Formal de Eficiencia; 20.3. Criterio 5: Análisis Estadístico (15 pts).

Muestra disponible: 19/104 partidas. Una unidad es una apertura con sus dos colores; las profundidades se analizan por separado.

Distribución (profundidad: partidas / bloques completos / partidas sin pareja): 4: 6 / 3 / 0; 5: 5 / 2 / 1; 6: 4 / 2 / 0; 7: 4 / 2 / 0. Las partidas sin pareja sólo entran en tablas descriptivas.

## 13. Métodos Estadísticos Requeridos

Binomial exacto bilateral: H0 = P(A gana el bloque | bloque decisivo)=0.5. Bloques empatados excluidos; partidas empatadas aportan medio punto. Holm corrige la familia de contrastes binomiales disponibles. Wilson al 95% estima la proporción de bloques decisivos ganados. Bootstrap percentil por apertura (5000 réplicas, semilla 20261008) estima diferencia media de fichas A-B y proporción de victorias por partida. Son estimandos distintos.

| A / B | Prof. | Bloques G/P/E | p bilateral | p Holm | Wilson 95% decisivos | Diferencia A-B | Bootstrap 95% diferencia | Victorias A | Bootstrap 95% victorias |
|---|---:|---|---:|---:|---|---:|---|---:|---|
| fija / etapas | 4 | 1/0/2 | 1.0000 | 1.0000 | [0.2065, 1.0000] | 7.3333 | [0.0000, 19.0000] | 0.6667 | [0.5000, 1.0000] |
| fija / etapas | 5 | 2/0/0 | 0.5000 | 1.0000 | [0.3424, 1.0000] | 21.5000 | [18.0000, 25.0000] | 1.0000 | [1.0000, 1.0000] |
| fija / etapas | 6 | 1/0/1 | 1.0000 | 1.0000 | [0.2065, 1.0000] | 7.5000 | [-4.0000, 19.0000] | 0.7500 | [0.5000, 1.0000] |
| fija / etapas | 7 | 1/0/1 | 1.0000 | 1.0000 | [0.2065, 1.0000] | 6.5000 | [1.0000, 12.0000] | 0.7500 | [0.5000, 1.0000] |

Profundidad 4: No se rechaza H0; no demuestra igualdad.
El intervalo bootstrap de diferencia incluye cero; no establece igualdad ni una ventaja inequívoca.

Profundidad 5: No se rechaza H0; no demuestra igualdad.
El intervalo bootstrap de diferencia excluye cero en esta muestra. Es un intervalo marginal sin corrección por multiplicidad, no una prueba de superioridad universal.

Profundidad 6: No se rechaza H0; no demuestra igualdad.
El intervalo bootstrap de diferencia incluye cero; no establece igualdad ni una ventaja inequívoca.

Profundidad 7: No se rechaza H0; no demuestra igualdad.
El intervalo bootstrap de diferencia excluye cero en esta muestra. Es un intervalo marginal sin corrección por multiplicidad, no una prueba de superioridad universal.

Con dos o tres aperturas, los intervalos bootstrap tienen soporte empírico muy limitado. Un intervalo degenerado (por ejemplo [1,1] para victorias) refleja bloques observados idénticos; no garantiza victoria futura ni incertidumbre nula. La interrupción deja un diseño incompleto y una muestra condicionada al orden de ejecución y al costo: estos resultados son exploratorios.

Chi-cuadrado: no aplicable. Torneo emparejado: filas por agente comparten partidas; no hay muestras independientes de múltiples agentes contra un rival común.

Wilson por partidas está en analisis_othello.json y es sólo descriptivo: ignora la dependencia de colores y aperturas. No sustituye la inferencia por bloques.

## 14. Evidencia Formal de Eficiencia, punto 2

Evaluación y diferencia final desde negras, promediadas entre ambos colores de cada apertura. Pearson: asociación lineal; Spearman: asociación de rangos. P bilateral por permutación de bloques, 2000 réplicas; IC bootstrap percentil. Se muestran todos los estratos, también los no significativos o no estimables. Los p de correlación son exploratorios y no están ajustados por multiplicidad; no permiten afirmar causalidad ni capacidad predictiva fuera de muestra. Los intervalos omiten réplicas con varianza nula, cuyo número válido se conserva en el CSV.

| Prof. | Colocación | Función | Bloques | Pearson r | p | IC95 r | Spearman rho | p | IC95 rho |
|---:|---:|---|---:|---:|---:|---|---:|---:|---|
| 4 | 20 | etapas | 3 | -0.1448 | 1.0000 | [-1.0000, 1.0000] | 0.5000 | 1.0000 | [-1.0000, 1.0000] |
| 4 | 20 | fija | 3 | -0.1448 | 1.0000 | [-1.0000, 1.0000] | 0.5000 | 1.0000 | [-1.0000, 1.0000] |
| 4 | 30 | etapas | 3 | 0.7882 | 0.4998 | [0.7882, 1.0000] | 1.0000 | 0.3318 | [1.0000, 1.0000] |
| 4 | 30 | fija | 3 | 0.7882 | 0.4998 | [0.7882, 1.0000] | 1.0000 | 0.3318 | [1.0000, 1.0000] |
| 4 | 40 | etapas | 3 | 0.9709 | 0.1639 | [0.9709, 1.0000] | 1.0000 | 0.3318 | [1.0000, 1.0000] |
| 4 | 40 | fija | 3 | 0.9709 | 0.1639 | [0.9709, 1.0000] | 1.0000 | 0.3318 | [1.0000, 1.0000] |
| 4 | 50 | etapas | 3 | 0.9913 | 0.3288 | [-1.0000, 1.0000] | 0.5000 | 1.0000 | [-1.0000, 1.0000] |
| 4 | 50 | fija | 3 | 0.9912 | 0.3288 | [-1.0000, 1.0000] | 0.5000 | 1.0000 | [-1.0000, 1.0000] |
| 5 | 20 | etapas | 2 | NA | NA | NA | NA | NA | NA |
| 5 | 20 | fija | 2 | NA | NA | NA | NA | NA | NA |
| 5 | 30 | etapas | 2 | NA | NA | NA | NA | NA | NA |
| 5 | 30 | fija | 2 | NA | NA | NA | NA | NA | NA |
| 5 | 40 | etapas | 2 | NA | NA | NA | NA | NA | NA |
| 5 | 40 | fija | 2 | NA | NA | NA | NA | NA | NA |
| 5 | 50 | etapas | 2 | NA | NA | NA | NA | NA | NA |
| 5 | 50 | fija | 2 | NA | NA | NA | NA | NA | NA |
| 6 | 20 | etapas | 2 | NA | NA | NA | NA | NA | NA |
| 6 | 20 | fija | 2 | NA | NA | NA | NA | NA | NA |
| 6 | 30 | etapas | 2 | NA | NA | NA | NA | NA | NA |
| 6 | 30 | fija | 2 | NA | NA | NA | NA | NA | NA |
| 6 | 40 | etapas | 2 | NA | NA | NA | NA | NA | NA |
| 6 | 40 | fija | 2 | NA | NA | NA | NA | NA | NA |
| 6 | 50 | etapas | 2 | NA | NA | NA | NA | NA | NA |
| 6 | 50 | fija | 2 | NA | NA | NA | NA | NA | NA |
| 7 | 20 | etapas | 2 | NA | NA | NA | NA | NA | NA |
| 7 | 20 | fija | 2 | NA | NA | NA | NA | NA | NA |
| 7 | 30 | etapas | 2 | NA | NA | NA | NA | NA | NA |
| 7 | 30 | fija | 2 | NA | NA | NA | NA | NA | NA |
| 7 | 40 | etapas | 2 | NA | NA | NA | NA | NA | NA |
| 7 | 40 | fija | 2 | NA | NA | NA | NA | NA | NA |
| 7 | 50 | etapas | 2 | NA | NA | NA | NA | NA | NA |
| 7 | 50 | fija | 2 | NA | NA | NA | NA | NA | NA |

Con tres bloques sólo hay seis permutaciones posibles del resultado. Las 2000 permutaciones aleatorias aproximan esa distribución discreta, no amplían la muestra. El bootstrap de correlación puede repetir sólo dos pares distintos o producir varianza nula; intervalos estrechos o degenerados no son evidencia de precisión con n=3. No deben prevalecer sobre el tamaño muestral ni sobre el contraste permutacional.

NA: no estimable/no aplicable, nunca cero ficticio. Las funciones comparten pesos de medio juego; sus evaluaciones y correlaciones coinciden en las colocaciones 20, 30 y 40. Esos duplicados no son evidencia independiente.

Las conclusiones se restringen a estas aperturas, agentes y profundidades. Ni la no significancia demuestra igualdad, ni una correlación significativa implica causalidad.
