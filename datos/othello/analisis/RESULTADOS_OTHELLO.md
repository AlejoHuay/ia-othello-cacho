# Resultados de Othello

Referencia: 12.1. Para Othello; 13. Métodos Estadísticos Requeridos; 14. Evidencia Formal de Eficiencia.

Partidas completas: 19/104. Competencia externa: pendiente: sin agentes externos.

Condiciones emparejadas por apertura; no contar repeticiones deterministas como independientes. Curva a igual profundidad para ambos, no contra rival de profundidad fija.

## 13. Métodos Estadísticos Requeridos
Binomial bilateral por bloques decisivos; H0: probabilidad de ganar un bloque no empatado = 0.5. Empates de bloque excluidos, partidas empatadas valen 0.5 puntos. Ajuste Holm para comparaciones binomiales. Wilson por partida es descriptivo: ignora dependencia; Wilson por bloque y bootstrap por apertura son los análisis pertinentes. IC bootstrap percentil: 5000 réplicas, semilla 20261008. Pocas aperturas limitan la inferencia.

- fija vs etapas, profundidad 4: 3 bloques; ganados/perdidos/empatados=1/0/2; p bilateral=1.0; p Holm=1.0; IC95 diferencia=[0.0, 19.0]. No se rechaza H0; no demuestra igualdad.
- fija vs etapas, profundidad 5: 2 bloques; ganados/perdidos/empatados=2/0/0; p bilateral=0.5; p Holm=1.0; IC95 diferencia=[18.0, 25.0]. No se rechaza H0; no demuestra igualdad.
- fija vs etapas, profundidad 6: 2 bloques; ganados/perdidos/empatados=1/0/1; p bilateral=1.0; p Holm=1.0; IC95 diferencia=[-4.0, 19.0]. No se rechaza H0; no demuestra igualdad.
- fija vs etapas, profundidad 7: 2 bloques; ganados/perdidos/empatados=1/0/1; p bilateral=1.0; p Holm=1.0; IC95 diferencia=[1.0, 12.0]. No se rechaza H0; no demuestra igualdad.

Con dos o tres aperturas, los intervalos bootstrap tienen soporte empírico muy limitado. Un intervalo degenerado (por ejemplo [1,1] para victorias) refleja bloques observados idénticos; no garantiza victoria futura ni incertidumbre nula. La interrupción deja un diseño incompleto y una muestra condicionada al orden de ejecución y al costo: estos resultados son exploratorios.

Chi-cuadrado: Torneo emparejado: filas por agente comparten partidas; no hay muestras independientes de múltiples agentes contra un rival común.

## 14. Evidencia Formal de Eficiencia
Pearson/Spearman: se correlaciona la media por apertura de evaluaciones desde negras con la media de diferencia final negras-blancas, por profundidad y movimiento. No se mezclan profundidades ni perspectivas. P bilateral por permutación de bloques (2000 réplicas); IC por bootstrap. Son asociaciones exploratorias, no causalidad ni validación predictiva fuera de muestra.
Resultados completos y motivos de no aplicabilidad: analisis_othello.json. Menos de tres bloques o varianza nula: r e inferencia no definidos.
Las tablas descriptivas incluyen partidas sin pareja. Para comparar profundidades con las mismas aperturas y colores, consultar tabla_aperturas_comunes_othello.csv; la curva principal usa toda la muestra desigual y no aísla un efecto causal de profundidad.
El gráfico log-log describe medidas; no demuestra crecimiento polinomial. Minimax/alfa-beta tienen peor caso exponencial en profundidad. Los tiempos de partidas completas también dependen de las posiciones elegidas. benchmark_othello.py permite controlar el conjunto de posiciones.
