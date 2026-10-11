# Integración pendiente de las secciones de Othello

Referencia: **15. Estructura Requerida (Formato LATEX); 16. Formato de Tablas y Figuras; 17. Referencias Bibliográficas; 18. Longitud**.

Se inspeccionaron antes de escribir estos fragmentos `articulo.tex`, `referencias.bib` y la existencia de `articulo.pdf`. Se conserva la clase `article` a 10 pt/A4, español, amsmath/amssymb, graphicx, booktabs, hyperref, márgenes 2.5 cm y bibliografía plain. No se duplica la plantilla. Los fragmentos no tienen preámbulo ni `document`.

**No se ha modificado ni regenerado el documento principal, su bibliografía o PDF.** Los cambios propuestos abajo requieren consultar al usuario antes de aplicarlos. Ninguna sección de Cacho debe reemplazarse.

| Ubicación actual | Fragmento propuesto | Operación posterior, sujeta a autorización |
|---|---|---|
| Introducción: Motivación/Objetivos/Contribuciones | introduccion.tex | Distribuir sus aportes en esas subsecciones, preservando los de Cacho |
| Marco Teórico: Othello | marco_teorico.tex | Sustituir únicamente el contenido de Othello; conservar Cacho y párrafos estocásticos |
| Función de Evaluación para Othello | funcion.tex | Reemplazar la sección anterior, no añadir otra duplicada |
| Competencia de IAs en Othello | competencia.tex | Reemplazar afirmaciones sin respaldo por los registros de las 19 partidas completas |
| Evaluación Estadística y Eficiencia | estadistica_eficiencia.tex | Añadir como subsección propia; conservar resultados de Cacho |
| Conclusiones/Limitaciones/Trabajo Futuro | conclusiones.tex | Integrar sólo las conclusiones de Othello |
| Resumen conjunto | aporte_resumen.tex | Insumo parcial; redactar 150–250 palabras después de integrar ambos juegos |

Ejemplo de inserción, desde el directorio `articulo/`: `\input{othello/funcion.tex}`. La sección de competencia usa `../datos/othello/analisis/tabla_othello.tex`, figuras PDF en esa carpeta y `../datos/othello/analisis/resumen_resultados_othello.tex`. Regenerarlos con `analizar.py` después de cambiar la muestra. El texto de discusión no debe actualizarse sólo cambiando cifras sin revisar el tamaño muestral.

Propuesta de bibliografía: cambiar posteriormente `\bibliography{referencias}` por `\bibliography{referencias,othello/referencias_othello_adicionales}`. Reutiliza las claves existentes y añade únicamente material docente y estadístico. La corrección de metadatos de Buro se propone en `FUENTES.md`, no se aplica.

**Revisión necesaria antes de integración — 12.1. Para Othello; 23. Política de Integridad Académica:** el artículo actual afirma tasas >85% y 92% en Othello, describe un rival de paridad simple y experimentos en profundidades 4 y 6. No había registros de Othello en el repositorio al comenzar esta fase. Esas afirmaciones no constituyen evidencia de nuestro experimento y no se trasladan a estos fragmentos. También debe revisarse cualquier afirmación global de superioridad en introducción/resumen/conclusiones que alcance a Othello. Las secciones de Cacho no fueron auditadas ni alteradas.

**18. Longitud:** el máximo de diez páginas excluyendo referencias/apéndices aplica al artículo integrado, no a diez páginas por juego. Las ocho referencias mínimas también son conjuntas; tres papers verificados de Othello ya figuran en la bibliografía actual. Estos fragmentos deben condensarse al integrarlos si el conjunto excede el límite. No se declara cumplida la longitud ni la maquetación final sin compilar el documento integrado autorizado.

**23. Política de Integridad Académica:** agregar en la versión final una declaración explícita de asistencia de OpenAI Codex y del uso del código/material docente. Texto sugerido: “Se utilizó OpenAI Codex para asistir en implementación, pruebas y redacción de Othello; el equipo revisó el código y las afirmaciones. Se reutilizó el programa base y las diapositivas entregadas por el docente.” La revisión humana efectiva debe realizarse antes de afirmar esa última validación.

La compilación aislada se comprobó con Tectonic 0.17.0 usando una envoltura temporal y el preámbulo existente. El compilador LaTeX sólo es necesario para el artículo; no para jugar, ejecutar el torneo ni analizar sus CSV. Evidencia de revisión: `datos/othello/validacion/VERIFICACION_OTHELLO.md`.

**Actualización del 11 de octubre de 2026 — 12.1. Para Othello; 13. Métodos Estadísticos Requeridos; 14. Evidencia Formal de Eficiencia:** los fragmentos ya discuten las 19 partidas, las 85 no ejecutadas y la interrupción por costo computacional. La subsección estadística incorpora `inferencia_othello.tex` y `correlaciones_othello.tex` desde `datos/othello/analisis/`. El benchmark sigue siendo el original de 16 decisiones, sin nuevas partidas. Revisar el límite conjunto de páginas al integrar las nuevas tablas.

**6. Descripción de la Competencia; 12.1. Para Othello; 16. Formato de Tablas y Figuras:** `competencia.tex` incorpora `competencia_externa.tex`, con cinco resultados reportados (fija, altura 4, Alpha-Beta), una victoria y cuatro derrotas. `evidencias_competencia_externa.tex` contiene las tres capturas originales y se puede insertar en los apéndices mediante `\input{othello/evidencias_competencia_externa.tex}`. No añadir otro preámbulo ni duplicar la sección. No se ha aplicado esa inserción al principal. Las capturas acreditan los contadores de P1–P3; la terminalidad de P5 no está verificada. La competencia externa queda documentada con evidencia parcial, sin mezclarla con los 19 registros internos. Los apéndices pueden ayudar a respetar el límite conjunto de diez páginas, que debe revisarse al integrar.
