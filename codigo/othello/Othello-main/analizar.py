"""12.1. Para Othello; 13. Métodos Estadísticos Requeridos;
14. Evidencia Formal de Eficiencia; 16. Formato de Tablas y Figuras; 22. Formato de Datos.
Sólo lee originales JSON y regenera derivados. No mezcla carpetas/planes.
"""
import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
import numpy as np
from estadistica import binomial, wilson, bootstrap_media, correlacion_bloques, holm
from torneo import RAIZ, leer_partidas, exportar, guardar_json

REF='12.1. Para Othello; 13. Métodos Estadísticos Requeridos; 14. Evidencia Formal de Eficiencia'

def csv_escribir(path,filas,campos):
    with Path(path).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=campos);w.writeheader();w.writerows(filas)

def resumen(partidas):
    tabla={};bloques=defaultdict(list);corr=defaultdict(lambda:defaultdict(list))
    for p in partidas:
        f=p['fila'];d=f['profundidad_a'];a=f['agente_a'];b=f['agente_b']
        bloques[(a,b,d,p['apertura_id'])].append(p)
        for nombre,signo in [(a,1),(b,-1)]:
            clave=(nombre,d)
            if clave not in tabla:
                tabla[clave]=dict(agente=nombre,profundidad=d,partidas=0,victorias=0,derrotas=0,
                                 empates=0,diferencia_total=0,puntos=0.,tiempo_total_s=0.,
                                 movimientos=0,nodos_evaluados=0,nodos_completos=True)
            r=tabla[clave];r['partidas']+=1;r['diferencia_total']+=signo*f['diferencia_fichas']
            categoria='empates' if f['ganador']=='empate' else 'victorias' if f['ganador']==nombre else 'derrotas'
            r[categoria]+=1;r['puntos']+=1 if categoria=='victorias' else .5 if categoria=='empates' else 0
            for m in p['movimientos']:
                if m['agente']!=nombre:continue
                r['tiempo_total_s']+=m['tiempo_s'];r['movimientos']+=1
                if m['nodos_evaluados'] is None:r['nodos_completos']=False
                else:r['nodos_evaluados']+=m['nodos_evaluados']
        for pos in p['posiciones']:
            for v,val in pos['evaluaciones'].items():
                corr[(a,b,d,pos['ply'],v)][p['apertura_id']].append((val,p['negras']-p['blancas']))
    for r in tabla.values():
        r['diferencia_media']=r['diferencia_total']/r['partidas']
        r['tiempo_medio_s']=r['tiempo_total_s']/r['movimientos'] if r['movimientos'] else 0
        r['nodos_por_segundo']=r['nodos_evaluados']/r['tiempo_total_s'] if r['tiempo_total_s'] and r['nodos_completos'] else None
        r['ic_wilson_descriptivo_partidas']=wilson(r['victorias'],r['partidas'])
    comparaciones=defaultdict(list)
    for (a,b,d,apertura),ps in bloques.items():
        # Inferencia sólo sobre pares de colores completos, una vez por apertura.
        if len(ps)!=2 or {p['color_a'] for p in ps}!={1,2}:continue
        wins=sum(p['fila']['ganador']==a for p in ps)
        draws=sum(p['fila']['ganador']=='empate' for p in ps)
        score=(wins+.5*draws)/2
        comparaciones[(a,b,d)].append(dict(apertura=apertura,score=score,winrate=wins/2,
                    diferencia=float(np.mean([p['fila']['diferencia_fichas'] for p in ps]))))
    tests=[]
    for (a,b,d),bs in sorted(comparaciones.items()):
        k=sum(x['score']>.5 for x in bs);l=sum(x['score']<.5 for x in bs);n=k+l
        tests.append(dict(agente_a=a,agente_b=b,profundidad=d,n_bloques=len(bs),
            bloques_ganados=k,bloques_perdidos=l,bloques_empatados=len(bs)-n,
            h0='P(bloque ganado por A | bloque no empatado)=0.5',alternativa='bilateral',
            diferencia_media_bloques=float(np.mean([x['diferencia'] for x in bs])),
            proporcion_victorias_bloques=float(np.mean([x['winrate'] for x in bs])),
            p_binomial=binomial(k,n) if n else None,
            ic_wilson_bloques_decisivos=wilson(k,n),
            ic_bootstrap_diferencia=bootstrap_media([x['diferencia'] for x in bs]),
            ic_bootstrap_winrate=bootstrap_media([x['winrate'] for x in bs]),
            nota='Aperturas muestreadas sin reemplazo; inferencia aproximada a esa población de aperturas, no a todo Othello.'))
    validos=[t for t in tests if t['p_binomial'] is not None]
    for t,p in zip(validos,holm([t['p_binomial'] for t in validos])):
        t['p_holm']=p
        t['interpretacion']='Evidencia contra H0 al 5% (familia ajustada)' if p<.05 else 'No se rechaza H0; no demuestra igualdad'
    correlaciones=[]
    for (a,b,d,ply,v),bs in sorted(corr.items()):
        # Incluir únicamente los pares completos también para las correlaciones.
        completos={x['apertura'] for x in comparaciones.get((a,b,d),[])}
        xy=[np.mean(vals,axis=0) for ap,vals in bs.items() if ap in completos and len(vals)==2]
        x=[z[0] for z in xy];y=[z[1] for z in xy]
        correlaciones.append(dict(agente_a=a,agente_b=b,profundidad=d,ply=ply,evaluacion=v,
             perspectiva='negras; resultado=negras-blancas; promedios por apertura',
             n_bloques=len(x),exploratorio=True,**correlacion_bloques(x,y)))
    globales=[]
    for nombre in sorted({x['agente'] for x in tabla.values()}):
        rs=[x for x in tabla.values() if x['agente']==nombre]
        total={k:sum(x[k] for x in rs) for k in ('partidas','victorias','derrotas','empates','puntos','diferencia_total','tiempo_total_s','movimientos','nodos_evaluados')}
        total['agente']=nombre
        total['diferencia_media']=total['diferencia_total']/total['partidas']
        total['tiempo_medio_s']=total['tiempo_total_s']/total['movimientos'] if total['movimientos'] else 0.
        total['nodos_por_segundo']=total['nodos_evaluados']/total['tiempo_total_s'] if total['tiempo_total_s'] and all(x['nodos_completos'] for x in rs) else None
        globales.append(total)
    return dict(referencia=REF,tabla_global=globales,tabla=list(sorted(tabla.values(),key=lambda x:(x['profundidad'],x['agente']))),
                comparaciones=tests,correlaciones=correlaciones,
                chi_cuadrado=dict(aplicable=False,motivo='Torneo emparejado: filas por agente comparten partidas; no hay muestras independientes de múltiples agentes contra un rival común.'))

def figuras(tabla,salida):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        return 'Pendiente: instalar requirements-analisis.txt y ejecutar con --figuras'
    for nombre,ylabel,clave,log in [
        ('victorias_profundidad','Victorias / partidas (%)','victorias',False),
        ('tiempo_profundidad','Tiempo medio por movimiento (s)','tiempo_medio_s',False),
        ('tiempo_loglog','Tiempo medio por movimiento (s)','tiempo_medio_s',True)]:
        fig,ax=plt.subplots(figsize=(4.4,3.2),layout='constrained')
        for indice,agente in enumerate(sorted({r['agente'] for r in tabla})):
            rs=sorted([r for r in tabla if r['agente']==agente],key=lambda r:r['profundidad'])
            ys=[100*r[clave]/r['partidas'] if clave=='victorias' else r[clave] for r in rs]
            ax.plot([r['profundidad'] for r in rs],ys,'o-',label=agente)
            if clave=='victorias':
                for r,y in zip(rs,ys):ax.annotate('n='+str(r['partidas']),(r['profundidad'],y),xytext=(-28 if r['profundidad']==7 else 4,5 if indice or y<=0 else -13),textcoords='offset points',fontsize=9)
        ax.set_xlabel('Profundidad (colocaciones; pases = 0)');ax.set_ylabel(ylabel)
        ax.set_title('Othello: comparación a igual profundidad\nGuía: '+('14. Evidencia Formal de Eficiencia' if log else '12.1. Para Othello'),fontsize=10)
        if log:ax.set_xscale('log');ax.set_yscale('log')
        ax.set_xticks([4,5,6,7],labels=['4','5','6','7'])
        if clave=='victorias':ax.set_ylim(-5,110)
        ax.grid(alpha=.25);ax.legend()
        fig.savefig(salida/(nombre+'_othello.pdf'))
        fig.savefig(salida/(nombre+'_othello.png'),dpi=160)
        plt.close(fig)
    return 'Generadas a partir de partidas completas; niveles ausentes no se interpolan'


def figura_benchmark(entrada,salida):
    """14. Evidencia Formal de Eficiencia, punto 3: tiempos sobre posiciones fijas."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    datos=json.loads(Path(entrada).read_text(encoding='utf-8'))
    filas=datos['registros']
    csv_escribir(salida/'benchmark_othello.csv',filas,list(filas[0]))
    plies=sorted({r['ply'] for r in filas})
    fig,axes=plt.subplots(1,len(plies),figsize=(3.8*len(plies),3.5),squeeze=False,layout='constrained')
    for ax,ply in zip(axes[0],plies):
        for v in sorted({r['evaluacion'] for r in filas}):
            rs=[r for r in filas if r['ply']==ply and r['evaluacion']==v]
            ds=sorted({r['profundidad'] for r in rs})
            ts=[np.mean([r['tiempo_s'] for r in rs if r['profundidad']==d]) for d in ds]
            ax.loglog(ds,ts,'o-',label=v)
        ax.set_xticks([4,5,6,7],labels=['4','5','6','7'])
        ax.set_xlabel('Profundidad (colocaciones)');ax.set_ylabel('Tiempo de búsqueda (s)')
        ax.set_title('Posición inicial' if ply==0 else f'Posición tras {ply} colocaciones')
        ax.grid(alpha=.25);ax.legend()
    fig.suptitle('Othello: mismas posiciones a cada profundidad\n14. Evidencia Formal de Eficiencia',fontsize=10)
    for ext in ('pdf','png'):fig.savefig(salida/('benchmark_loglog_othello.'+ext),dpi=160)
    plt.close(fig)
    texto=[r'% 14. Evidencia Formal de Eficiencia, punto 3. Generado por analizar.py.',
           f"Se registraron {len(filas)} decisiones sobre posiciones fijas, separadas de las partidas del torneo. "]
    for ply in plies:
        texto.append('En la posición '+('inicial' if ply==0 else f'tras {ply} colocaciones')+', ')
        for d in (4,7):
            ts=[r['tiempo_s'] for r in filas if r['ply']==ply and r['profundidad']==d]
            if ts: texto.append(f"a profundidad {d} se midieron entre {min(ts):.4f} y {max(ts):.4f} segundos; ")
        texto.append('estos extremos corresponden a las condiciones medidas, no a un intervalo de confianza. ')
    texto.append('Se conserva una medición por condición en este piloto; no se estima variabilidad ni se demuestra crecimiento polinomial.')
    (salida/'resumen_benchmark_othello.tex').write_text('\n'.join(texto)+'\n',encoding='utf-8')


def latex(tabla,path):
    lineas=[r'% 12.1. Para Othello; 16. Formato de Tablas y Figuras. Generado por analizar.py.',
        r'\begin{table}[htbp]',r'\centering\small',
        r'\caption{Othello: resultados internos disponibles a igual profundidad. V/D/E: victorias/derrotas/empates; puntos: 1/0/0.5.}',
        r'\label{tab:othello_resultados}',r'\begin{tabular}{lrrrrrrr}',r'\toprule',
        r'Agente & Prof. & V & D & E & $\overline{\Delta}$ & Puntos & s/jugada \\',r'\midrule']
    for r in tabla:
        nombre=r['agente'].replace('_',r'\_')
        lineas.append(f"{nombre} & {r['profundidad']} & {r['victorias']} & {r['derrotas']} & {r['empates']} & {r['diferencia_media']:.2f} & {r['puntos']:.1f} & {r['tiempo_medio_s']:.3f}"+r' \\')
    lineas += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
    path.write_text('\n'.join(lineas)+'\n',encoding='utf-8')


def informes_estadisticos(resultado,salida):
    """13. Métodos Estadísticos Requeridos; 14. Evidencia Formal de Eficiencia.
    Expone todos los contrastes e intervalos; no selecciona sólo significativos.
    """
    def numero(x):
        return 'NA' if x is None else f'{x:.4f}'
    def intervalo(x):
        return 'NA' if x is None else f'[{x[0]:.4f}, {x[1]:.4f}]'
    lineas=['# Inferencia de Othello por bloques', '',
        'Referencia: 12.1. Para Othello, punto 2; 13. Métodos Estadísticos Requeridos; 13.1. Ejemplo de Análisis Requerido; 14. Evidencia Formal de Eficiencia; 20.3. Criterio 5: Análisis Estadístico (15 pts).', '',
        f"Muestra disponible: {resultado['ejecutadas']}/{resultado['planificadas']} partidas. Una unidad es una apertura con sus dos colores; las profundidades se analizan por separado.", '',
        '## 13. Métodos Estadísticos Requeridos', '',
        'Binomial exacto bilateral: H0 = P(A gana el bloque | bloque decisivo)=0.5. Bloques empatados excluidos; partidas empatadas aportan medio punto. Holm corrige la familia de contrastes binomiales disponibles. Wilson al 95% estima la proporción de bloques decisivos ganados. Bootstrap percentil por apertura (5000 réplicas, semilla 20261008) estima diferencia media de fichas A-B y proporción de victorias por partida. Son estimandos distintos.', '',
        '| A / B | Prof. | Bloques G/P/E | p bilateral | p Holm | Wilson 95% decisivos | Diferencia A-B | Bootstrap 95% diferencia | Victorias A | Bootstrap 95% victorias |',
        '|---|---:|---|---:|---:|---|---:|---|---:|---|']
    filas=[]
    tex=[r'% 13. Métodos Estadísticos Requeridos; 16. Formato de Tablas y Figuras.',
        r'\begin{table}[htbp]',r'\centering\small',
        r'\caption{Contrastes por bloques de apertura; A/B identifica los agentes. IC: bootstrap percentil al 95\% para diferencia media A-B. G/P/E: bloques ganados/perdidos/empatados.}',
        r'\label{tab:othello_inferencia}',r'\begin{tabular}{lrrrrrr}',r'\toprule',
        r'A/B & Prof. & G/P/E & $p$ & $p_{\mathrm{Holm}}$ & $\overline{\Delta}$ & IC95 $\Delta$ \\',r'\midrule']
    for t in resultado['comparaciones']:
        conteos=f"{t['bloques_ganados']}/{t['bloques_perdidos']}/{t['bloques_empatados']}"
        filas.append(dict(agente_a=t['agente_a'],agente_b=t['agente_b'],profundidad=t['profundidad'],n_bloques=t['n_bloques'],
            bloques_ganados=t['bloques_ganados'],bloques_perdidos=t['bloques_perdidos'],bloques_empatados=t['bloques_empatados'],
            p_binomial=t['p_binomial'],p_holm=t.get('p_holm'),wilson95=intervalo(t['ic_wilson_bloques_decisivos']),
            diferencia_media=t['diferencia_media_bloques'],bootstrap95_diferencia=intervalo(t['ic_bootstrap_diferencia']),
            proporcion_victorias=t['proporcion_victorias_bloques'],bootstrap95_victorias=intervalo(t['ic_bootstrap_winrate'])))
        lineas.append(f"| {t['agente_a']} / {t['agente_b']} | {t['profundidad']} | {conteos} | {numero(t['p_binomial'])} | {numero(t.get('p_holm'))} | {intervalo(t['ic_wilson_bloques_decisivos'])} | {numero(t['diferencia_media_bloques'])} | {intervalo(t['ic_bootstrap_diferencia'])} | {numero(t['proporcion_victorias_bloques'])} | {intervalo(t['ic_bootstrap_winrate'])} |")
        par=(t['agente_a']+'/'+t['agente_b']).replace('_',r'\_')
        tex.append(f"{par} & {t['profundidad']} & {conteos} & {numero(t['p_binomial'])} & {numero(t.get('p_holm'))} & {t['diferencia_media_bloques']:.2f} & {intervalo(t['ic_bootstrap_diferencia'])}"+r' \\')
    tex += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
    (salida/'inferencia_othello.tex').write_text('\n'.join(tex)+'\n',encoding='utf-8')
    if filas:csv_escribir(salida/'comparaciones_othello.csv',filas,list(filas[0]))
    for t in resultado['comparaciones']:
        lineas += ['',f"Profundidad {t['profundidad']}: "+t.get('interpretacion','Sin bloques decisivos: el binomial no es aplicable')+'.']
        ci=t['ic_bootstrap_diferencia']
        if ci is None:lineas.append('Bootstrap: no estimable con menos de dos bloques.')
        elif ci[0]<=0<=ci[1]:lineas.append('El intervalo bootstrap de diferencia incluye cero; no establece igualdad ni una ventaja inequívoca.')
        else:lineas.append('El intervalo bootstrap de diferencia excluye cero en esta muestra. Es un intervalo marginal sin corrección por multiplicidad, no una prueba de superioridad universal.')
    lineas += ['', 'Chi-cuadrado: no aplicable. '+resultado['chi_cuadrado']['motivo'], '',
        'Wilson por partidas está en analisis_othello.json y es sólo descriptivo: ignora la dependencia de colores y aperturas. No sustituye la inferencia por bloques.', '',
        '## 14. Evidencia Formal de Eficiencia, punto 2', '',
        'Evaluación y diferencia final desde negras, promediadas entre ambos colores de cada apertura. Pearson: asociación lineal; Spearman: asociación de rangos. P bilateral por permutación de bloques, 2000 réplicas; IC bootstrap percentil. Se muestran todos los estratos, también los no significativos o no estimables. Los p de correlación son exploratorios y no están ajustados por multiplicidad; no permiten afirmar causalidad ni capacidad predictiva fuera de muestra. Los intervalos omiten réplicas con varianza nula, cuyo número válido se conserva en el CSV.', '',
        '| Prof. | Colocación | Función | Bloques | Pearson r | p | IC95 r | Spearman rho | p | IC95 rho |',
        '|---:|---:|---|---:|---:|---:|---|---:|---:|---|']
    correlaciones=[]
    for c in resultado['correlaciones']:
        pe,sp=c['pearson'],c['spearman']
        lineas.append(f"| {c['profundidad']} | {c['ply']} | {c['evaluacion']} | {c['n_bloques']} | {numero(pe['r'])} | {numero(pe['p'])} | {intervalo(pe['ic95'])} | {numero(sp['r'])} | {numero(sp['p'])} | {intervalo(sp['ic95'])} |")
        for metodo in ('pearson','spearman'):
            z=c[metodo]
            if z['r'] is None:lectura=z['motivo']
            else:
                direccion='positiva' if z['r']>0 else 'negativa' if z['r']<0 else 'nula'
                lectura='Asociación '+direccion+('; p nominal <0.05, exploratorio y sin ajuste múltiple' if z['p']<.05 else '; no se rechaza ausencia de asociación con este contraste')
            correlaciones.append(dict(agente_a=c['agente_a'],agente_b=c['agente_b'],profundidad=c['profundidad'],ply=c['ply'],evaluacion=c['evaluacion'],n_bloques=c['n_bloques'],metodo=metodo,r=z['r'],p=z['p'],ic95=intervalo(z['ic95']),replicas_bootstrap_validas=z.get('replicas_validas',0),interpretacion=lectura))
    if correlaciones:csv_escribir(salida/'correlaciones_othello.csv',correlaciones,list(correlaciones[0]))
    tabla_corr=[r'% 14. Evidencia Formal de Eficiencia, punto 2; 16. Formato de Tablas y Figuras.',
        r'\begin{table}[htbp]',r'\centering\small',
        r'\caption{Correlaciones por apertura desde negras. Cada celda muestra Pearson/Spearman; las columnas son colocaciones. N: rango de bloques disponibles. IC, p exploratorios y réplicas válidas: archivo complementario de correlaciones.}',
        r'\label{tab:othello_correlaciones}',r'\begin{tabular}{rlrrrrr}',r'\toprule',
        r'Prof. & Función & N & 20 & 30 & 40 & 50 '+chr(92)*2,r'\midrule']
    grupos=sorted({(c['agente_a'],c['agente_b'],c['profundidad'],c['evaluacion']) for c in resultado['correlaciones']})
    for a,b,d,v in grupos:
        cs={c['ply']:c for c in resultado['correlaciones'] if (c['agente_a'],c['agente_b'],c['profundidad'],c['evaluacion'])==(a,b,d,v)}
        ns=[c['n_bloques'] for c in cs.values()]
        n=str(min(ns)) if min(ns)==max(ns) else f'{min(ns)}--{max(ns)}'
        celdas=[]
        for ply in (20,30,40,50):
            c=cs.get(ply)
            celdas.append('--' if c is None or c['pearson']['r'] is None or c['spearman']['r'] is None else f"{c['pearson']['r']:.2f}/{c['spearman']['r']:.2f}")
        nombre=v.replace('_',chr(92)+'_')
        tabla_corr.append(f'{d} & {nombre} & {n} & '+' & '.join(celdas)+' '+chr(92)*2)
    tabla_corr += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
    (salida/'correlaciones_othello.tex').write_text('\n'.join(tabla_corr)+'\n',encoding='utf-8')

    lineas += ['', 'NA: no estimable/no aplicable, nunca cero ficticio. Las funciones comparten pesos de medio juego; sus evaluaciones y correlaciones coinciden en las colocaciones 20, 30 y 40. Esos duplicados no son evidencia independiente.', '',
        'Las conclusiones se restringen a estas aperturas, agentes y profundidades. Ni la no significancia demuestra igualdad, ni una correlación significativa implica causalidad.', '']
    (salida/'INFERENCIA_OTHELLO.md').write_text('\n'.join(lineas),encoding='utf-8')


def analizar(carpeta,salida,graficos=False,principal=None):
    carpeta=Path(carpeta);salida=Path(salida);salida.mkdir(parents=True,exist_ok=True)
    ps=leer_partidas(carpeta)
    if not ps:raise ValueError('No hay partidas completas; no se fabrican datos')
    if len({p['id'] for p in ps})!=len(ps):raise ValueError('Partidas duplicadas')
    r=resumen(ps);meta=json.loads((carpeta/'manifest_othello.json').read_text(encoding='utf-8'))
    n_agentes=len(meta['plan']['agentes'])
    esperado=meta['plan']['aperturas']*len(meta['plan']['profundidades'])*n_agentes*(n_agentes-1)
    r['ejecutadas']=len(ps);r['planificadas']=esperado;r['completo']=len(ps)==esperado
    r['configuracion_estadistica']=dict(numpy=np.__version__,semilla=20261008,bootstrap_replicas=5000,correlacion_replicas=2000,alpha=.05,binomial='bilateral',ajuste='Holm')
    r['advertencia']='Condiciones emparejadas por apertura; no contar repeticiones deterministas como independientes. Curva a igual profundidad para ambos, no contra rival de profundidad fija.'
    if graficos:
        r['figuras']=figuras(r['tabla'],salida)
        benchmark=carpeta.parent/'benchmark_othello.json'
        if benchmark.exists() and r['figuras'].startswith('Generadas'):
            figura_benchmark(benchmark,salida)
            r['benchmark']=str(benchmark.relative_to(carpeta.parent))
    guardar_json(salida/'analisis_othello.json',r)
    informes_estadisticos(r,salida)
    campos=['agente','profundidad','partidas','victorias','derrotas','empates','diferencia_media','puntos','tiempo_medio_s','nodos_evaluados','nodos_por_segundo']
    csv_escribir(salida/'tabla_othello.csv',[{k:v[k] for k in campos} for v in r['tabla']],campos)
    latex(r['tabla'],salida/'tabla_othello.tex')
    campos_globales=[c for c in campos if c!='profundidad']
    csv_escribir(salida/'tabla_global_othello.csv',[{k:v[k] for k in campos_globales} for v in r['tabla_global']],campos_globales)
    texto=[r'% 12.1. Para Othello; 13. Métodos Estadísticos Requeridos. Generado por analizar.py.',
        f"Se completaron {len(ps)} de {esperado} partidas planificadas; quedan {esperado-len(ps)} pendientes. "]
    for agente in sorted({x['agente'] for x in r['tabla']}):
        filas_agente=[x for x in r['tabla'] if x['agente']==agente]
        v=sum(x['victorias'] for x in filas_agente);e=sum(x['empates'] for x in filas_agente)
        der=sum(x['derrotas'] for x in filas_agente)
        nombre=agente.replace('_',r'\_')
        texto.append(f"La versión {nombre} obtuvo {v} victorias, {der} derrotas y {e} empates. ")
    texto.append('Estos totales mezclan profundidades y sólo describen las partidas disponibles; no prueban superioridad general. ')
    for t in r['comparaciones']:
        valor='no aplicable (bloque empatado)' if t['p_binomial'] is None else f"{t['p_binomial']:.3f}"
        texto.append(f"A profundidad {t['profundidad']}, con {t['n_bloques']} bloque(s), el valor $p$ binomial bilateral es {valor}. ")
    texto.append('Las aperturas son las unidades de inferencia; el número de partidas no equivale al número de observaciones independientes. Los intervalos y las condiciones de aplicabilidad se conservan en el registro estadístico reproducible.')
    (salida/'resumen_resultados_othello.tex').write_text('\n'.join(texto)+'\n',encoding='utf-8')

    filas=[]
    for p in ps:
        for m in p['movimientos']:filas.append(dict(partida=p['id'],apertura=p['apertura_id'],profundidad=p['fila']['profundidad_a'],**{**m,'accion':json.dumps(m['accion'])}))
    if filas:csv_escribir(salida/'movimientos_othello.csv',filas,list(filas[0]))
    # Matriz round-robin, separada por profundidad: puntos del agente fila.
    matriz=[]
    for d in sorted({p['fila']['profundidad_a'] for p in ps}):
        for a in sorted({c['nombre'] for c in meta['plan']['agentes']}):
            for b in sorted({c['nombre'] for c in meta['plan']['agentes']}):
                if a==b:continue
                juegos=[p for p in ps if p['fila']['profundidad_a']==d and {p['fila']['agente_a'],p['fila']['agente_b']}=={a,b}]
                matriz.append(dict(profundidad=d,agente=a,rival=b,partidas=len(juegos),puntos=sum(1 if p['fila']['ganador']==a else .5 if p['fila']['ganador']=='empate' else 0 for p in juegos)))
    csv_escribir(salida/'round_robin_othello.csv',matriz,list(matriz[0]))
    lineas=['# Resultados de Othello', '', 'Referencia: '+REF+'.', '',
        f"Partidas completas: {len(ps)}/{esperado}. Competencia externa: {meta['externa']}.", '',r['advertencia'],'',
        '## 13. Métodos Estadísticos Requeridos',
        'Binomial bilateral por bloques decisivos; H0: probabilidad de ganar un bloque no empatado = 0.5. Empates de bloque excluidos, partidas empatadas valen 0.5 puntos. Ajuste Holm para comparaciones binomiales. Wilson por partida es descriptivo: ignora dependencia; Wilson por bloque y bootstrap por apertura son los análisis pertinentes. IC bootstrap percentil: 5000 réplicas, semilla 20261008. Pocas aperturas limitan la inferencia.', '']
    for t in r['comparaciones']:
        lineas.append(f"- {t['agente_a']} vs {t['agente_b']}, profundidad {t['profundidad']}: {t['n_bloques']} bloques; ganados/perdidos/empatados={t['bloques_ganados']}/{t['bloques_perdidos']}/{t['bloques_empatados']}; p bilateral={t['p_binomial']}; p Holm={t.get('p_holm')}; IC95 diferencia={t['ic_bootstrap_diferencia']}. {t.get('interpretacion','Sin bloques decisivos: prueba no aplicable')}.")
    lineas += ['', 'Chi-cuadrado: '+r['chi_cuadrado']['motivo'], '',
        '## 14. Evidencia Formal de Eficiencia',
        'Pearson/Spearman: se correlaciona la media por apertura de evaluaciones desde negras con la media de diferencia final negras-blancas, por profundidad y movimiento. No se mezclan profundidades ni perspectivas. P bilateral por permutación de bloques (2000 réplicas); IC por bootstrap. Son asociaciones exploratorias, no causalidad ni validación predictiva fuera de muestra.',
        'Resultados completos y motivos de no aplicabilidad: analisis_othello.json. Menos de tres bloques o varianza nula: r e inferencia no definidos.',
        'El gráfico log-log describe medidas; no demuestra crecimiento polinomial. Minimax/alfa-beta tienen peor caso exponencial en profundidad. Los tiempos de partidas completas también dependen de las posiciones elegidas. benchmark_othello.py permite controlar el conjunto de posiciones.','']
    (salida/'RESULTADOS_OTHELLO.md').write_text('\n'.join(lineas),encoding='utf-8')
    exportar(carpeta,salida/'resultados_othello.csv')
    if principal:
        if Path(principal).name!='resultados_othello.csv':
            raise ValueError('El CSV principal debe llamarse resultados_othello.csv')
        exportar(carpeta,principal)
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--entrada',default=str(RAIZ/'datos/othello/torneo_104'))
    p.add_argument('--salida',default=str(RAIZ/'datos/othello/analisis'))
    p.add_argument('--figuras',action='store_true')
    p.add_argument('--csv-principal',help='Ruta de datos/resultados_othello.csv; nunca archivos de Cacho')
    args=p.parse_args();r=analizar(args.entrada,args.salida,args.figuras,args.csv_principal)
    print(f"Analizadas {r['ejecutadas']}/{r['planificadas']} partidas completas")
