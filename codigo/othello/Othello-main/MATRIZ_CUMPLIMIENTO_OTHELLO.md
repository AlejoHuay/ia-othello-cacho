# Matriz de cumplimiento de Othello

Referencia: **19. Distribución de Puntos; 20.1. Criterio 1: Función de Evaluación Othello (20 pts); 20.3. Criterio 5: Análisis Estadístico (15 pts)**.

Estados: **implementado** = existe código o documento; **verificado** = comprobado mediante pruebas o revisión; **ejecutado** = existe resultado real; **pendiente** = no realizado. Un script implementado no demuestra que se hayan ejecutado todos los experimentos. Las rutas `datos/` y `articulo/` son relativas a la raíz; los demás archivos son relativos a `codigo/othello/Othello-main/`.

| Apartado exacto de la guía | Requisito | Archivo o evidencia | Estado |
|---|---|---|---|
| 1. Información General | Instrucciones y alcance de entrega | `README_OTHELLO.md` | Documentado; confirmar discrepancias administrativas con docente |
| 2. Objetivos de Aprendizaje, O2 | Integrar evaluación y búsqueda adversarial | `AgenteIA/AgenteJugador.py`, `AgentesEspecificos/AgenteOthello.py` | Implementado y verificado |
| 3. Contexto del Juego; 3.1. Reglas Fundamentales | Revisar base, representación y reglas | `REVISION_BASE_OTHELLO.md`, `pruebas/test_othello.py` | Verificado: 8×8, ocho direcciones, negras, pases, final y empate |
| 3.1. Reglas Fundamentales | Coherencia de pases, MAX/MIN y copia de estado | `AgenteIA/AgenteJugador.py`, `AgentesEspecificos/AgenteOthello.py`, pruebas contra referencia independiente | Implementado y verificado; profundidad cuenta colocaciones, pase cero |
| 4. Formulación de la Función de Evaluación | Al menos dos propuestas distintas | `evaluador.py`, `DISENO_OTHELLO.md` | Implementado y verificado: fija y etapas; cuatro componentes normalizados |
| 5. Análisis Crítico Requerido, puntos 1–4 | Estáticos/greedy, movilidad/sandwich/pesos negativos, etapas, costo | `DISENO_OTHELLO.md`, `articulo/othello/funcion.tex` | Documentado; antecedentes separados de decisiones y resultados |
| 6. Descripción de la Competencia | Dos versiones e integración con otros grupos | `cliente_agente.py`, `torneo.py`, `README_OTHELLO.md` | Integración implementada; cinco encuentros externos reportados (1 V/4 D) y tres capturas en `datos/othello/competencia_externa/`; métricas y reproducción no disponibles |
| 6.1. Estructura del Torneo | Round-robin, colores, profundidad, hardware y métricas | `torneo.py`, `datos/othello/torneo_104/manifest_othello.json`, `hardware_othello.json` | Implementado y ejecutado parcialmente: 19/104; cierre por costo computacional, 85 no ejecutadas |
| 7. Descripción de Funciones en el Artículo | Fórmulas, pesos, escalas, pseudocódigo, justificación, complejidad | `DISENO_OTHELLO.md`, `evaluador.py`, `articulo/othello/funcion.tex` | Documentado y contrastado con código |
| 12. Resultados Requeridos; 12.1. Para Othello | Tabla round-robin, V/D/E, diferencia media y puntos | `datos/othello/analisis/tabla_othello.csv`, `round_robin_othello.csv`, `tabla_othello.tex` | Generados desde partidas completas; consultar conteo actualizado en `analisis_othello.json` |
| 12.1. Para Othello | Victorias y tiempo por movimiento a profundidades 4–7 | `analizar.py`, figuras `victorias_profundidad_othello` y `tiempo_profundidad_othello` en `datos/othello/analisis/` | Implementado; sólo se grafican niveles ejecutados, sin rellenar ausencias |
| 12.1. Para Othello, punto 2; 13. Métodos Estadísticos Requeridos | Binomial, Wilson, bootstrap y chi-cuadrado cuando proceda | `estadistica.py`, `analizar.py`, `analisis_othello.json` | Implementado y verificado; binomial/Wilson calculados si procede; bootstrap calculado con 3/2/2/2 bloques, precisión limitada; chi-cuadrado no aplicable al diseño emparejado |
| 13.1. Ejemplo de Análisis Requerido | Hipótesis e interpretación correctas | `README_OTHELLO.md`, `pruebas/test_estadistica.py`, `RESULTADOS_OTHELLO.md` | Verificado: ejemplo unilateral distinto del contraste bilateral; no significancia no demuestra igualdad |
| 14. Evidencia Formal de Eficiencia, punto 1 | Costo de evaluar separado del árbol | `DISENO_OTHELLO.md`, `articulo/othello/estadistica_eficiencia.tex` | Documentado: evaluación O(n³), árbol exponencial en profundidad en peor caso |
| 14. Evidencia Formal de Eficiencia, punto 2 | Correlación de evaluaciones intermedias y resultado | JSON originales, `analisis_othello.json` | Posiciones y perspectiva registradas; Pearson/Spearman implementados/verificados; ejecutadas en profundidad 4 (n=3), no estimables en 5–7 (n=2); exploratorias |
| 14. Evidencia Formal de Eficiencia, punto 3 | Tiempos y gráfico log-log | `benchmark_othello.py`, `analizar.py`, `tiempo_loglog_othello.pdf` | Medición implementada; no se afirma crecimiento polinomial; contradicción pendiente de aclaración con docente |
| 15. Estructura Requerida (Formato LATEX) | Secciones integrables de Othello | `articulo/othello/*.tex`, `INTEGRACION.md` | Redactadas separadamente; integración en documento principal pendiente de autorización |
| 16. Formato de Tablas y Figuras | booktabs, ecuaciones referenciables, leyendas y unidades | `tabla_othello.tex`, `funcion.tex`, figuras PDF/PNG | Implementado; revisión visual registrada en evidencia de validación |
| 17. Referencias Bibliográficas | Tres papers verificables de Othello y fuentes estadísticas | `articulo/othello/FUENTES.md`, `referencias_othello_adicionales.bib` | Verificado; reutiliza claves compartidas; corrección de ficha Buro propuesta, no aplicada |
| 18. Longitud | Diez páginas y resumen conjunto de 150–250 palabras | `articulo/othello/INTEGRACION.md`, `aporte_resumen.tex` | Pendiente de integración con Cacho; aporte parcial no es resumen definitivo |
| 19. Distribución de Puntos, criterio 2 “Agente Othello funcional” | Agente funcional a profundidad mínima 4 | `cliente_agente.py`, originales del piloto, `pruebas/test_red.py` | Implementado; pruebas de red a profundidad 1 y experimentos reales desde profundidad 4 |
| 19. Distribución de Puntos, criterio 7 “Código Fuente” | Código, ejecución limpia y pruebas proporcionadas | `requirements*.txt`, `README_OTHELLO.md`, `pruebas/` | Implementado; pruebas automatizadas y auditoría de registros |
| 20.1. Criterio 1: Función de Evaluación Othello (20 pts) | ≥3 componentes, valores acotados, análisis con referencias | `evaluador.py`, `DISENO_OTHELLO.md`, `funcion.tex` | Ambas propuestas verificadas; restricciones numéricas son decisión consultada, no atribución al docente |
| 20.3. Criterio 5: Análisis Estadístico (15 pts) | Evidencia estadística y ≥100 partidas para excelencia | `datos/othello/torneo_104/`, `analisis_othello.json` | No se alcanza el nivel muestral: 19 partidas, 85 no ejecutadas por cierre de muestra. No se promete puntuación de rúbrica |
| 21. Estructura de Archivos | Relación agente/evaluador/torneo sin romper imports | `README_OTHELLO.md`, `REVISION_BASE_OTHELLO.md` | Documentado; ruta original conservada |
| 22. Formato de Datos | Ocho columnas exactas, signo, unidades, empates y complementos | `datos/resultados_othello.csv`, JSON originales, `movimientos_othello.csv` | Implementado y verificado; originales conservados y derivados regenerables |
| 23. Política de Integridad Académica | Atribución, transparencia y no inventar resultados | `README_OTHELLO.md`, `FUENTES.md`, `INTEGRACION.md` | Declarada asistencia Codex y material docente; revisión humana y declaración final conjunta pendientes |

## Cierre verificado — 12.1. Para Othello; 14. Evidencia Formal de Eficiencia; 19. Distribución de Puntos

Al 11 de octubre de 2026: **19/104 partidas ejecutadas y reproducidas; 85 no ejecutadas**. El usuario cerró la muestra tras cancelar la ampliación por costo computacional. `fija`: 14 victorias; `etapas`: 5; sin empates. La diferencia descriptiva media de fija es +9.05 fichas. Hay 6/5/4/4 partidas por profundidad y 3/2/2/2 bloques completos; no son 19 observaciones independientes. Tiempo acumulado de decisiones: 5188.29 s (86.47 min), sin sumar pausas ni la partida interrumpida.

Se regeneraron tablas, CSV principal y complementarios, cuatro gráficos PDF/PNG e informes estadísticos. El benchmark conserva sus 16 decisiones originales sobre dos posiciones; no se volvieron a ejecutar búsquedas del torneo. El análisis incluye bootstrap, Wilson y binomial por bloques (todos los p Holm=1). Pearson/Spearman sólo se estiman a profundidad 4, con tres bloques; no se obtuvo significancia nominal. Los IC bootstrap degenerados o estrechos no se presentan como precisión fiable. Chi-cuadrado no aplica.

**20 pruebas automatizadas correctas**, reproducción legal de las 19 partidas y conservación de originales verificada. Evidencia actual: `datos/othello/validacion/VALIDACION_19_OTHELLO.md` y `validacion_19_othello.json`. La evidencia de ocho partidas del 9 de octubre se conserva como histórica; no debe confundirse con la muestra actual. Las secciones LaTeX se revisan aisladamente; la integración conjunta sigue pendiente.

## Fuera de alcance

Los apartados 8–11, 12.2 y 20.2 corresponden a Cacho. No se modifica su código, datos ni secciones del artículo. Esta actualización no ejecuta commits, push ni merge. Los cambios permanecen en `feature/othello`.

## Condiciones para completar los pendientes

La muestra actual queda cerrada en 19; completar las otras 85 no forma parte de esta ejecución y el umbral de excelencia de ≥100 sigue incumplido. La participación externa está documentada con cinco resultados reportados y tres capturas; faltan configuraciones rivales, tiempos, trazas y confirmación de terminalidad de P5 para una validación completa. El archivo principal y la bibliografía compartida requieren consulta antes de integrar. Quedan para el docente las aclaraciones conceptuales ya señaladas (crecimiento polinomial y definición operativa de sandwich squares). Ninguna cifra ilustrativa de la guía se presenta como resultado propio.
