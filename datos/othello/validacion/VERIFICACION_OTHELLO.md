# Verificación de Othello

Referencia: **3.1. Reglas Fundamentales; 19. Distribución de Puntos, criterios 2 y 7; 20.1. Criterio 1: Función de Evaluación Othello (20 pts); 20.3. Criterio 5: Análisis Estadístico (15 pts)**.

## Pruebas de código

Se ejecutó `python -X utf8 -B -m unittest discover -s pruebas -v` desde una copia temporal de `codigo/othello/Othello-main/`, sin cachés ni resultados del repositorio. Resultado: **19 pruebas correctas**. La salida íntegra está en `pruebas_othello.txt`. Entorno: Python 3.13.15, NumPy 2.5.3, Pygame 2.6.1, Windows. Esta comprobación usa las dependencias instaladas; no representa una instalación de paquetes en un sistema operativo virgen.

Cobertura relevante:

- Inicio de negras, acciones legales, copia de matriz, volteo simultáneo en ocho direcciones, pase, final con huecos, empate y dominancia terminal.
- Veinte partidas aleatorias de prueba, con pases observados, comparando servidor y motor en cada movimiento. No se contabilizan como partidas de competencia.
- Minimax y Alpha-Beta a profundidad 4 sobre inicio y posiciones tardías/con pases; misma acción y valor, menor o igual número de hojas con poda. Oráculo exhaustivo adicional de final de partida.
- Rango y antisimetría de ambas evaluaciones; aperturas reproducibles.
- Partida completa con dos clientes automáticos y servidor TCP local; rechazo de tercer cliente y de reinicio duplicado. Esta prueba de red usa profundidad 1 para aislar el protocolo.
- Exportación de ocho columnas, reanudación sin cambiar originales, análisis y detección de registro alterado. Sus dos partidas de profundidad 1 viven sólo en carpetas temporales.
- Valores de referencia de binomial, Wilson, bootstrap, correlaciones, chi-cuadrado y Holm. Son casos de prueba, no resultados de nuestro torneo.

## Interfaz — 19. Distribución de Puntos, criterio 2 “Agente Othello funcional”

`interfaz_othello.png` se generó con Pygame y el controlador de pantalla `dummy`, sin ventana visible. Se revisaron las ocho filas, fichas y separación de marcador/turno. Se comprobó que un clic en la barra inferior no sea una casilla y que la esquina inferior derecha corresponda a (7,7). No se afirma una sesión manual completa de humano contra IA.

## LaTeX — 15. Estructura Requerida (Formato LATEX); 16. Formato de Tablas y Figuras

Se compiló una envoltura temporal con el preámbulo del artículo existente, las secciones de Othello y la bibliografía compartida más el suplemento. Tectonic 0.17.0 produjo un PDF y resolvió referencias y citas; se renderizaron y revisaron sus páginas. La envoltura y ese PDF de revisión no sustituyen ni duplican la plantilla en el repositorio. Una advertencia de caja poco llena en la leyenda de la tabla no afecta legibilidad; no se encontraron desbordamientos visibles.

Esto valida los fragmentos aisladamente. No demuestra el límite de diez páginas, el resumen conjunto ni la maquetación del artículo integrado con Cacho, que permanecen pendientes de integración autorizada.

## Alcance y conservación — 21. Estructura de Archivos; 23. Política de Integridad Académica

La rama es `feature/othello`. Los únicos archivos previamente versionados modificados pertenecen a Othello: búsqueda, agente específico, entorno, servidor e interfaz. Los nuevos archivos se limitan al subproyecto y carpetas de Othello. El artículo principal, su PDF, la bibliografía compartida y Cacho permanecen sin cambios. No se hicieron commits, push ni merge.

## Cierre de datos — 12.1. Para Othello; 14. Evidencia Formal de Eficiencia; 22. Formato de Datos

El 9 de octubre se verificaron las ocho partidas del piloto por reproducción completa y se contrastaron las ocho filas del CSV principal con los originales. Se comprobaron ambas asignaciones de color en cada profundidad y ausencia de archivos de progreso incompletos. Quedan 96 partidas pendientes por indicación del usuario. El benchmark añadió 16 decisiones sobre dos matrices fijas y ninguna partida. Sus huellas coinciden con las del experimento.

La compilación final incorpora resultados 8/104 y el benchmark, produjo cinco páginas temporales y se revisaron todas. Se revisaron además las cuatro figuras PNG/PDF. Las 19 pruebas volvieron a pasar después de cerrar el generador de resultados (`pruebas_finales_othello.txt`). Los detalles y hashes de originales están en `validacion_othello.json`.
