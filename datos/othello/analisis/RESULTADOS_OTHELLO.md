# Resultados de Othello

Referencia: 12.1. Para Othello; 13. Métodos Estadísticos Requeridos; 14. Evidencia Formal de Eficiencia.

Partidas completas: 8/104. Competencia externa: pendiente: sin agentes externos.

Condiciones emparejadas por apertura; no contar repeticiones deterministas como independientes. Curva a igual profundidad para ambos, no contra rival de profundidad fija.

## 13. Métodos Estadísticos Requeridos
Binomial bilateral por bloques decisivos; H0: probabilidad de ganar un bloque no empatado = 0.5. Empates de bloque excluidos, partidas empatadas valen 0.5 puntos. Ajuste Holm para comparaciones binomiales. Wilson por partida es descriptivo: ignora dependencia; Wilson por bloque y bootstrap por apertura son los análisis pertinentes. IC bootstrap percentil: 5000 réplicas, semilla 20261008. Pocas aperturas limitan la inferencia.

- fija vs etapas, profundidad 4: 1 bloques; ganados/perdidos/empatados=0/0/1; p bilateral=None; p Holm=None; IC95 diferencia=None. Sin bloques decisivos: prueba no aplicable.
- fija vs etapas, profundidad 5: 1 bloques; ganados/perdidos/empatados=1/0/0; p bilateral=1.0; p Holm=1.0; IC95 diferencia=None. No se rechaza H0; no demuestra igualdad.
- fija vs etapas, profundidad 6: 1 bloques; ganados/perdidos/empatados=1/0/0; p bilateral=1.0; p Holm=1.0; IC95 diferencia=None. No se rechaza H0; no demuestra igualdad.
- fija vs etapas, profundidad 7: 1 bloques; ganados/perdidos/empatados=0/0/1; p bilateral=None; p Holm=None; IC95 diferencia=None. Sin bloques decisivos: prueba no aplicable.

Chi-cuadrado: Torneo emparejado: filas por agente comparten partidas; no hay muestras independientes de múltiples agentes contra un rival común.

## 14. Evidencia Formal de Eficiencia
Pearson/Spearman: se correlaciona la media por apertura de evaluaciones desde negras con la media de diferencia final negras-blancas, por profundidad y movimiento. No se mezclan profundidades ni perspectivas. P bilateral por permutación de bloques (2000 réplicas); IC por bootstrap. Son asociaciones exploratorias, no causalidad ni validación predictiva fuera de muestra.
Resultados completos y motivos de no aplicabilidad: analisis_othello.json. Menos de tres bloques o varianza nula: r e inferencia no definidos.
El gráfico log-log describe medidas; no demuestra crecimiento polinomial. Minimax/alfa-beta tienen peor caso exponencial en profundidad. Los tiempos de partidas completas también dependen de las posiciones elegidas. benchmark_othello.py permite controlar el conjunto de posiciones.
