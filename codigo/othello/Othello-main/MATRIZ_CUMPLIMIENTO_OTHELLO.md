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
| 6. Descripción de la Competencia | Dos versiones e integración con otros grupos | `cliente_agente.py`, `torneo.py`, `README_OTHELLO.md` | Integración implementada; competencia externa pendiente por falta de agentes |
| 6.1. Estructura del Torneo | Round-robin, colores, profundidad, hardware y métricas | `torneo.py`, `datos/othello/torneo_104/manifest_othello.json`, `hardware_othello.json` | Implementado; plan 104; ejecución limitada por el usuario al piloto |
| 7. Descripción de Funciones en el Artículo | Fórmulas, pesos, escalas, pseudocódigo, justificación, complejidad | `DISENO_OTHELLO.md`, `evaluador.py`, `articulo/othello/funcion.tex` | Documentado y contrastado con código |
| 12. Resultados Requeridos; 12.1. Para Othello | Tabla round-robin, V/D/E, diferencia media y puntos | `datos/othello/analisis/tabla_othello.csv`, `round_robin_othello.csv`, `tabla_othello.tex` | Generados desde partidas completas; consultar conteo actualizado en `analisis_othello.json` |
| 12.1. Para Othello | Victorias y tiempo por movimiento a profundidades 4–7 | `analizar.py`, figuras `victorias_profundidad_othello` y `tiempo_profundidad_othello` en `datos/othello/analisis/` | Implementado; sólo se grafican niveles ejecutados, sin rellenar ausencias |
| 12.1. Para Othello, punto 2; 13. Métodos Estadísticos Requeridos | Binomial, Wilson, bootstrap y chi-cuadrado cuando proceda | `estadistica.py`, `analizar.py`, `analisis_othello.json` | Implementado y verificado; binomial/Wilson calculados si procede; bootstrap no estimable con un bloque; chi-cuadrado no aplicable al diseño emparejado |
| 13.1. Ejemplo de Análisis Requerido | Hipótesis e interpretación correctas | `README_OTHELLO.md`, `pruebas/test_estadistica.py`, `RESULTADOS_OTHELLO.md` | Verificado: ejemplo unilateral distinto del contraste bilateral; no significancia no demuestra igualdad |
| 14. Evidencia Formal de Eficiencia, punto 1 | Costo de evaluar separado del árbol | `DISENO_OTHELLO.md`, `articulo/othello/estadistica_eficiencia.tex` | Documentado: evaluación O(n³), árbol exponencial en profundidad en peor caso |
| 14. Evidencia Formal de Eficiencia, punto 2 | Correlación de evaluaciones intermedias y resultado | JSON originales, `analisis_othello.json` | Posiciones y perspectiva registradas; Pearson/Spearman implementados/verificados; inferencia pendiente de suficientes aperturas |
| 14. Evidencia Formal de Eficiencia, punto 3 | Tiempos y gráfico log-log | `benchmark_othello.py`, `analizar.py`, `tiempo_loglog_othello.pdf` | Medición implementada; no se afirma crecimiento polinomial; contradicción pendiente de aclaración con docente |
| 15. Estructura Requerida (Formato LATEX) | Secciones integrables de Othello | `articulo/othello/*.tex`, `INTEGRACION.md` | Redactadas separadamente; integración en documento principal pendiente de autorización |
| 16. Formato de Tablas y Figuras | booktabs, ecuaciones referenciables, leyendas y unidades | `tabla_othello.tex`, `funcion.tex`, figuras PDF/PNG | Implementado; revisión visual registrada en evidencia de validación |
| 17. Referencias Bibliográficas | Tres papers verificables de Othello y fuentes estadísticas | `articulo/othello/FUENTES.md`, `referencias_othello_adicionales.bib` | Verificado; reutiliza claves compartidas; corrección de ficha Buro propuesta, no aplicada |
| 18. Longitud | Diez páginas y resumen conjunto de 150–250 palabras | `articulo/othello/INTEGRACION.md`, `aporte_resumen.tex` | Pendiente de integración con Cacho; aporte parcial no es resumen definitivo |
| 19. Distribución de Puntos, criterio 2 “Agente Othello funcional” | Agente funcional a profundidad mínima 4 | `cliente_agente.py`, originales del piloto, `pruebas/test_red.py` | Implementado; pruebas de red a profundidad 1 y experimentos reales desde profundidad 4 |
| 19. Distribución de Puntos, criterio 7 “Código Fuente” | Código, ejecución limpia y pruebas proporcionadas | `requirements*.txt`, `README_OTHELLO.md`, `pruebas/` | Implementado; pruebas automatizadas y auditoría de registros |
| 20.1. Criterio 1: Función de Evaluación Othello (20 pts) | ≥3 componentes, valores acotados, análisis con referencias | `evaluador.py`, `DISENO_OTHELLO.md`, `funcion.tex` | Ambas propuestas verificadas; restricciones numéricas son decisión consultada, no atribución al docente |
| 20.3. Criterio 5: Análisis Estadístico (15 pts) | Evidencia estadística y ≥100 partidas para excelencia | `datos/othello/torneo_104/`, `analisis_othello.json` | No se alcanza el nivel muestral: piloto autorizado; resto pendiente. No se promete puntuación de rúbrica |
| 21. Estructura de Archivos | Relación agente/evaluador/torneo sin romper imports | `README_OTHELLO.md`, `REVISION_BASE_OTHELLO.md` | Documentado; ruta original conservada |
| 22. Formato de Datos | Ocho columnas exactas, signo, unidades, empates y complementos | `datos/resultados_othello.csv`, JSON originales, `movimientos_othello.csv` | Implementado y verificado; originales conservados y derivados regenerables |
| 23. Política de Integridad Académica | Atribución, transparencia y no inventar resultados | `README_OTHELLO.md`, `FUENTES.md`, `INTEGRACION.md` | Declarada asistencia Codex y material docente; revisión humana y declaración final conjunta pendientes |

## Cierre verificado — 12.1. Para Othello; 14. Evidencia Formal de Eficiencia; 19. Distribución de Puntos

Al 9 de octubre de 2026: **8/104 partidas ejecutadas y reproducidas, 96 pendientes**. Una apertura, dos colores y profundidades 4, 5, 6 y 7. `fija`: 6 victorias y 2 derrotas; `etapas`: 2 victorias y 6 derrotas; ningún empate. No son ocho observaciones independientes. Tiempo acumulado de partidas: 2971.13 s (49 min 31 s). Se generaron las tablas y cuatro gráficos PDF/PNG, incluido el benchmark de 16 decisiones sobre dos posiciones fijas, sin añadir partidas.

**19 pruebas automatizadas correctas**, CSV principal contrastado con originales y huellas verificadas. Fragmentos LaTeX compilados en una envoltura temporal de cinco páginas y revisados visualmente; no se modifica el artículo conjunto. Evidencia: `datos/othello/validacion/validacion_othello.json`, `pruebas_finales_othello.txt` y `VERIFICACION_OTHELLO.md`.

Bootstrap y correlaciones por bloques no son estimables con una sola apertura; chi-cuadrado no procede en este diseño. Binomial bilateral en profundidades 5 y 6: p=1, también tras Holm; en 4 y 7 los bloques empatan y se excluyen. No se rechaza H0, lo cual no demuestra igualdad. La afirmación de crecimiento polinomial sigue sin aceptarse: se presentan teoría y mediciones reales.

## Fuera de alcance

Los apartados 8–11, 12.2 y 20.2 corresponden a Cacho. No se modifica su código, datos ni secciones del artículo. No se realizaron commits, push ni merge. Los cambios permanecen en `feature/othello`.

## Condiciones para completar los pendientes

El usuario limitó expresamente la ejecución al piloto de ocho partidas; las otras 96 requieren que indique continuar. La competencia externa requiere recibir agentes y condiciones del torneo. Los fragmentos están preparados para integrarse, pero el archivo principal y la bibliografía compartida requieren consulta previa. Las correlaciones y bootstrap necesitan más bloques de apertura: ninguna cifra de la guía se presenta como resultado propio.
