# Discusión de Othello: muestra cerrada de 19 partidas

## 6.1. Estructura del Torneo; 12.1. Para Othello

Actualización: 11 de octubre de 2026. Se conservan las ocho partidas iniciales y once posteriores: 19 completas de las 104 previstas. El usuario interrumpió la continuación y decidió cerrar la muestra por el costo computacional. Las 85 restantes no se ejecutaron; no se alcanzó el plan original ni el umbral de ≥100 de **20.3. Criterio 5: Análisis Estadístico (15 pts)**. No se alega avería, pérdida de resultados ni un plazo no documentado. El usuario eliminó el registro de la partida incompleta; nunca se contabiliza como resultado.

Los registros completos suman 5188.29 s de decisiones (86.47 min); 4085.24 s (68.09 min, 78.7%) corresponden a las cuatro partidas de profundidad 7. En ese nivel las decisiones por partida sumaron entre 811.56 y 1239.69 s (13.53–20.66 min). No se incluyen las pausas, la apertura, escritura ni el tiempo de la partida cancelada; no equivale al tiempo total de sesión. El costo restante no se extrapola como una cifra cierta. Esta explicación se basa en mediciones, no en una excusa inventada.

| Profundidad | Partidas | Bloques completos | Partidas sin pareja | V/D/E fija | Diferencia media fija | Tiempo fija/etapas (s por decisión) |
|---:|---:|---:|---:|---|---:|---|
| 4 | 6 | 3 | 0 | 4/2/0 | 7.33 | 0.225 / 0.233 |
| 5 | 5 | 2 | 1 | 4/1/0 | 14.40 | 0.775 / 0.778 |
| 6 | 4 | 2 | 0 | 3/1/0 | 7.50 | 3.813 / 4.172 |
| 7 | 4 | 2 | 0 | 3/1/0 | 6.50 | 19.213 / 20.084 |

`fija` obtuvo 14 victorias (73.7%), `etapas` 5 (26.3%), sin empates. Puntuación 1/0.5/0: 14 y 5 puntos. Diferencia media fija−etapas: +9.05 fichas. Los totales describen una mezcla desigual de profundidades; no son un test sobre 19 observaciones independientes.

La partida `a002_d5_0_1_c1` (fija con negras, derrota por 14 fichas) es válida y entra en los totales; no entra en inferencia porque no se completó su pareja de color. El conjunto quedó condicionado al orden de ejecución, primero por aperturas, y al costo. No se seleccionaron ganadores: se utilizan todos los registros completos disponibles. Aun así, el cierre no equivale a un muestreo balanceado del plan ni a una regla de parada estadística preestablecida.

Para comparar profundidades conservando las mismas aperturas se exportó `tabla_aperturas_comunes_othello.csv`: aperturas 0 y 1, dos colores, cuatro profundidades, 16 partidas. Las victorias de fija son 2/4, 4/4, 3/4 y 3/4. La curva no es monótona y ambos agentes aumentan profundidad: no demuestra mejora frente a un oponente fijo. Las curvas principales conservan las 19 partidas y deben leerse con su n desigual; el subconjunto común complementa, no reemplaza, la muestra completa.

## 5. Análisis Crítico Requerido; 7. Descripción de Funciones en el Artículo

La ventaja descriptiva de fija no prueba que los pesos constantes sean óptimos ni que variar por etapas perjudique a Othello en general. Se comparan dos combinaciones concretas de pesos con la misma búsqueda y un número pequeño de aperturas. Las funciones comparten pesos de medio juego, por lo que sus evaluaciones a las colocaciones 20, 30 y 40 coinciden. Los efectos de apertura y final pueden modificar las trayectorias completas; sin ablaciones no se atribuye el resultado a un componente aislado. Se mantienen separadas las justificaciones bibliográficas y estos resultados propios. No se incorporó ajuste de pesos después de observar las victorias.

## 13. Métodos Estadísticos Requeridos; 13.1. Ejemplo de Análisis Requerido

El bloque es una apertura con ambos colores, dentro de una profundidad. Hay 3/2/2/2 bloques; son sólo tres aperturas distintas en toda la muestra, reutilizadas entre niveles. No sumar esos nueve bloques como nueve aperturas independientes. Binomial bilateral: H0=P(fija gana el bloque | bloque decisivo)=0.5. Los empates de bloque se excluyen, aunque siguen en bootstrap; empates de partida aportarían 0.5 puntos. Holm ajusta los cuatro contrastes binomiales.

- Profundidad 4: bloques G/P/E=1/0/2; p=1; Wilson95 sobre decisivos [0.2065,1]; diferencia de pares 7.33, bootstrap95 [0,19]. Incluye cero y no establece ventaja inequívoca.
- Profundidad 5: 2/0/0; p=0.5; Wilson95 [0.3424,1]; diferencia de pares 21.50, bootstrap95 [18,25]. Excluye la partida sin pareja, de ahí la diferencia respecto a la media descriptiva 14.40.
- Profundidad 6: 1/0/1; p=1; Wilson95 [0.2065,1]; diferencia de pares 7.50, bootstrap95 [-4,19]. Incluye cero.
- Profundidad 7: 1/0/1; p=1; Wilson95 [0.2065,1]; diferencia de pares 6.50, bootstrap95 [1,12].

Todos los p ajustados por Holm son 1. No se rechaza H0; esto no demuestra igualdad. Con uno o dos bloques decisivos no hay capacidad para sostener conclusiones fuertes. Los IC de diferencia en 5 y 7 excluyen cero pero remuestrean sólo dos bloques; son intervalos percentiles marginales, de soporte muy limitado, sin ajuste múltiple y sobre un estimando diferente al binomial.

Bootstrap: 5000 réplicas, semilla 20261008. Los IC de proporción de victorias por partida, remuestreando bloques, son [0.5,1], [1,1], [0.5,1] y [0.5,1]. El [1,1] en profundidad 5 es degenerado: las cuatro partidas emparejadas fueron ganadas por fija; remuestrearlas no descubre derrotas no observadas. No representa certeza ni una probabilidad futura de victoria del 100%. Wilson por partidas se conserva sólo como descriptivo, pues ignora el emparejamiento.

Chi-cuadrado sigue no aplicable: las filas de los dos agentes comparten las mismas partidas y no son muestras independientes. Los reportes externos se conservan en otra muestra de condiciones desconocidas y tampoco sustentan esa comparación. No se fuerza el test para completar una lista.

## 14. Evidencia Formal de Eficiencia, punto 2

Evaluaciones y diferencia final se expresan desde negras y se promedian por apertura entre ambos colores. Se estratifica por profundidad, colocación y función. Sólo profundidad 4 tiene tres bloques: Pearson en 20/30/40/50 es −0.1448/0.7882/0.9709/~0.991; Spearman es 0.5/1/1/0.5. Los p bilaterales Monte Carlo de Pearson son 1/0.4998/0.1639/0.3288 y los de Spearman 1/0.3318/0.3318/1. Ninguno es <0.05. La asociación lineal observada aumenta en posiciones tardías de esta muestra, sin demostrar capacidad predictiva ni una diferencia fiable entre evaluadores.

Se ejecutaron 2000 permutaciones e igual número de réplicas bootstrap con semilla fija. Con tres aperturas sólo hay seis permutaciones del resultado: más réplicas Monte Carlo no añaden observaciones. Los IC bootstrap de correlación omiten réplicas con varianza cero; pueden ser degenerados o artificialmente estrechos porque al remuestrear se repiten sólo dos pares distintos. Por ejemplo, Spearman en 30/40 produce [1,1] pese a p≈0.332. No hay contradicción matemática: la distribución empírica del bootstrap diminuto y el contraste permutacional responden de forma distinta; no debe interpretarse ese IC como certeza. El CSV conserva el número de réplicas válidas.

En profundidades 5–7 se reporta NA, no cero: dos bloques no permiten el análisis previsto. Las coincidencias de ambas funciones en medio juego no son réplicas independientes. Todos estos análisis son exploratorios, con p sin ajuste múltiple. `INFERENCIA_OTHELLO.md`, `comparaciones_othello.csv` y `correlaciones_othello.csv` contienen todos los estratos e intervalos, sin selección de los favorables.

## 14. Evidencia Formal de Eficiencia, puntos 1 y 3

Los tiempos medios de decisión crecen marcadamente entre 4 y 7; las tasas de hojas evaluadas por segundo se sitúan aproximadamente entre 4660 y 5096 según agente y profundidad. Los totales son 13025137 hojas para fija y 13169894 para etapas. No son todos los nodos visitados. La tasa se calcula como suma de hojas dividida por suma de tiempo, no como promedio de tasas.

El costo de evaluar una posición O(n³) y el costo de explorar un árbol son distintos. Minimax/alfa-beta tienen peor caso exponencial en profundidad; el gráfico log-log no demuestra crecimiento polinomial. Se conserva la contradicción del punto 3 para aclararla con el docente. El benchmark original de 16 decisiones sobre dos matrices fijas se reutiliza sin repetirlo ni sumarlo a las partidas: controla mejor las posiciones, pero su única medición por condición no estima variabilidad. Los tiempos de escritorio también dependen de carga y frecuencia de CPU.

## 15. Estructura Requerida (Formato LATEX); 19. Distribución de Puntos; 22. Formato de Datos; 23. Política de Integridad Académica

Los fragmentos de `articulo/othello/` se actualizaron, sin editar el artículo compartido ni Cacho. Los 19 originales y el manifiesto permanecen intactos; los CSV, tablas y figuras se regeneran con `analizar.py --figuras --csv-principal ../../../datos/resultados_othello.csv` desde `codigo/othello/Othello-main/`. El cierre de muestra y las huellas se conservan fuera del manifiesto histórico. La evidencia de validación del piloto sigue identificada por su fecha; la nueva está en `datos/othello/validacion/VALIDACION_19_OTHELLO.md`.

Esta actualización de análisis, pruebas y redacción recibió asistencia de OpenAI Codex el 11 de octubre de 2026. El equipo debe revisar y comprender las conclusiones antes de entregar. La competencia externa se documenta por separado en `../competencia_externa/COMPETENCIA_EXTERNA_OTHELLO.md`, con cinco reportes y tres capturas; la integración conjunta permanece pendiente; las 85 partidas no ejecutadas se declaran como limitación del alcance actual.
