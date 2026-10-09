# Fuentes verificadas de Othello

Referencia: **17. Referencias Bibliográficas; 23. Política de Integridad Académica**. Verificación: 8 de octubre de 2026. Los tres papers de Othello ya existen en `../referencias.bib`; se reutilizan sus claves, sin sobrescribir el archivo.

| Clave existente | Publicación | Fuente primaria verificada | Uso y límite |
|---|---|---|---|
| rosenbloom1982iob | P. S. Rosenbloom (1982), A World-Championship-Level Othello Program, Artificial Intelligence 19(3), 279–320 | https://doi.org/10.1016/0004-3702(82)90003-0 | IAGO: análisis del dominio e implementación/evaluación; ficha y resumen editorial consultados. No se atribuyen a nuestro agente sus resultados. |
| lee1990bill | K.-F. Lee y S. Mahajan (1990), The Development of a World Class Othello Program, Artificial Intelligence 43(1), 21–36 | https://doi.org/10.1016/0004-3702(90)90068-B | BILL: combinación de búsqueda y evaluación; resumen editorial consultado. No copiamos tablas precalculadas ni código. |
| buro1999logistello | M. Buro (1999), From Simple Features to Sophisticated Evaluation Functions, Computers and Games, LNCS 1558, 126–145 | https://doi.org/10.1007/3-540-48957-6_8 | Construcción y ajuste de características; ficha editorial y versión del autor https://skatgame.net/mburo/ps/pattern.pdf. No prueba nuestros pesos. |

La entrada existente de Buro está tipada como `@article`, pero la editorial identifica un trabajo de congreso/capítulo en LNCS. **Propuesta pendiente de autorización**: conservar la clave y convertirla a `@inproceedings` (booktitle=Computers and Games, series=Lecture Notes in Computer Science, volumen 1558, editores H. J. van den Herik e H. Iida, DOI anterior). Añadir los DOI a las otras dos entradas también sería útil. No se aplicó ninguna modificación a la bibliografía compartida.

Estadística: se reutiliza `wilson1927interval` (Wilson, 1927, JASA 22(158), 209–212). La fórmula se contrastó con NIST, https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm. El bootstrap se fundamenta en Efron (1979), The Annals of Statistics 7(1), 1–26, DOI https://doi.org/10.1214/aos/1176344552 (artículo disponible en https://blogs.helsinki.fi/bk-club/files/2012/05/Efron_Bootstrap_AS1979.pdf). Tabla de contingencia: NIST, https://www.itl.nist.gov/div898/handbook/prc/section4/prc45.htm. Sus entradas nuevas están aisladas en `referencias_othello_adicionales.bib`.

Referencia: **5. Análisis Crítico Requerido, puntos 2–4**. Las frases sobre sandwich squares, 13 etapas y aproximadamente 15% de velocidad están en la guía docente. No se verificó su atribución precisa en un pasaje de los tres papers consultados: se citan explícitamente como afirmaciones de la guía, no como resultados experimentales propios ni como especificaciones que debamos copiar. La definición operativa de sandwich squares permanece sin fuente precisa; no se inventa una equivalencia con casillas X/C.

Referencia: **23. Política de Integridad Académica**. La formulación de las variantes, el código nuevo, las pruebas y estos textos recibieron asistencia de OpenAI Codex en la conversación del 8 de octubre de 2026. El equipo debe revisar las afirmaciones, verificar los resultados y declarar esa asistencia en el artículo final. Las presentaciones y el programa original del docente son la base metodológica; no se descargó una implementación de juego externa.
