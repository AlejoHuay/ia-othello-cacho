# Validación de la actualización a 19 partidas de Othello

Fecha: 11 de octubre de 2026. Rama: `feature/othello`. Referencias: **3.1. Reglas Fundamentales; 12.1. Para Othello; 13. Métodos Estadísticos Requeridos; 14. Evidencia Formal de Eficiencia; 16. Formato de Tablas y Figuras; 19. Distribución de Puntos; 22. Formato de Datos; 23. Política de Integridad Académica**.

| Apartado de la guía | Requisito | Evidencia | Estado |
|---|---|---|---|
| 3.1. Reglas Fundamentales; 19. Distribución de Puntos | Registros de partidas legales y pruebas de código | `verificar_registros.py`: 19 reproducidas; `pruebas_19_partidas_othello.txt`: 20 pruebas correctas | Verificado |
| 6.1. Estructura del Torneo; 12.1. Para Othello | Muestra real y alcance de ejecución | `../cierre_muestra_19_othello.json`: 19 completas, 85 no ejecutadas, sin nuevas partidas del experimento | Ejecutado parcialmente; muestra cerrada |
| 12.1. Para Othello | V/D/E, puntos, diferencia, tiempos y profundidad | `../analisis/tabla_othello.csv`, `tabla_global_othello.csv`, `round_robin_othello.csv`, cuatro gráficos PDF/PNG | Regenerado y verificado |
| 12.1. Para Othello; 13. Métodos Estadísticos Requeridos | Control de aperturas y colores | 6/5/4/4 partidas; 3/2/2/2 pares; partida sin pareja excluida de inferencia; `tabla_aperturas_comunes_othello.csv` con 16 partidas | Verificado |
| 13. Métodos Estadísticos Requeridos; 13.1. Ejemplo de Análisis Requerido | Binomial, Wilson y bootstrap con interpretación | `../analisis/INFERENCIA_OTHELLO.md`, `comparaciones_othello.csv`; todos los p Holm=1; advertencia sobre IC degenerados | Calculado, reproducido e interpretado; precisión limitada |
| 13. Métodos Estadísticos Requeridos | Chi-cuadrado pertinente | Motivo de no aplicabilidad en JSON e informes: filas emparejadas/dependientes | No aplicable |
| 14. Evidencia Formal de Eficiencia, punto 2 | Correlación con perspectiva coherente | `correlaciones_othello.csv`: Pearson/Spearman sólo en d4, n=3; d5–7 NA | Calculado cuando procede; exploratorio |
| 14. Evidencia Formal de Eficiencia, punto 3 | Tiempo log-log y evidencia real | Cuatro gráficos revisados; benchmark histórico intacto, 16 decisiones | Regenerado; no se afirma crecimiento polinomial |
| 15. Estructura Requerida (Formato LATEX); 16. Formato de Tablas y Figuras | Fragmentos compatibles y revisión visual | Compilación temporal de seis páginas, `latex_19_othello.txt`; revisión de seis páginas y cuatro figuras | Verificado aisladamente; integración conjunta pendiente |
| 20.3. Criterio 5: Análisis Estadístico (15 pts) | ≥100 partidas para nivel excelente | 19/104; limitación de costo documentada | No alcanzado |
| 22. Formato de Datos | CSV exacto y trazabilidad | CSV principal, CSV del torneo y CSV del análisis: mismos 19 registros y ocho columnas | Verificado |
| 23. Política de Integridad Académica | Originales intactos y atribución | SHA256 antes/después; declaraciones Codex en README, fuentes y discusión | Verificado; revisión humana e integración final pendientes |

La suite incluye casos sintéticos en carpetas temporales y una prueba de red. No son nuevas observaciones del torneo. Se añadió una comprobación de que agregar una partida sin pareja cambia los totales descriptivos, pero no los bloques ni las correlaciones.

Una segunda ejecución del análisis en una carpeta temporal produjo las mismas tablas, intervalos, correlaciones e informes. Se contrastaron además los p Monte Carlo de correlación contra la enumeración de las seis permutaciones posibles con tres aperturas (diferencias menores de 0.03). Los valores exactos de control están en `validacion_19_othello.json`; los resultados publicados mantienen el método Monte Carlo documentado.

Las huellas de los 19 originales, manifiesto, benchmark, artículo principal y bibliografía compartida coinciden con las tomadas antes de esta actualización. El motor, evaluaciones y torneo permanecen sin cambios. La evidencia antigua de ocho partidas se conserva con fecha explícita.

La compilación usa la organización y preámbulo actuales del artículo en una envoltura temporal, sin escribir en el principal. Se corrigió un desbordamiento por un nombre de archivo largo. Queda una advertencia `Underfull hbox` en la leyenda de la tabla, sin recorte ni solapamiento visible, y una advertencia Fontconfig no bloqueante. Se resolvieron referencias y citas. Las seis páginas no prueban el límite del artículo conjunto; la revisión de Cacho y su integración quedan fuera de esta actualización.

No se ejecutaron commits, push, merge ni nuevas partidas del experimento. El análisis se cierra sobre los 19 registros completos existentes.
