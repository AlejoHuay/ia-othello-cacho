"""13. Métodos Estadísticos Requeridos; 13.1. Ejemplo de Análisis Requerido.
Implementaciones transparentes con biblioteca estándar y NumPy; sin SciPy.
"""
import math
from statistics import NormalDist
import numpy as np

def binomial(k,n):
    """Exacto bilateral, H0:p=0.5. Empates se excluyen antes de llamar."""
    if not 0 <= k <= n or n < 1:
        raise ValueError('Requiere 0<=k<=n y n>=1')
    # Simetría de Bin(n,.5): duplicar la cola menor, incluyendo k.
    return min(1.0,2*sum(math.comb(n,i) for i in range(min(k,n-k)+1))/2**n)

def wilson(k,n):
    if n < 1:
        return None
    if not 0 <= k <= n:
        raise ValueError('Conteos inválidos')
    z=NormalDist().inv_cdf(.975);p=k/n;den=1+z*z/n
    centro=(p+z*z/(2*n))/den
    radio=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0.,centro-radio),min(1.,centro+radio)]

def bootstrap_media(valores,semilla=20261008,repeticiones=5000):
    """Cada elemento debe ser una unidad independiente (media de un bloque)."""
    x=np.asarray(valores,dtype=float)
    if len(x)<2:
        return None
    rng=np.random.default_rng(semilla)
    muestras=x[rng.integers(0,len(x),(repeticiones,len(x)))].mean(axis=1)
    return [float(v) for v in np.quantile(muestras,[.025,.975])]

def rangos(valores):
    x=np.asarray(valores);orden=np.argsort(x,kind='stable');r=np.empty(len(x),dtype=float)
    i=0
    while i<len(x):
        j=i+1
        while j<len(x) and x[orden[j]]==x[orden[i]]: j+=1
        r[orden[i:j]]=(i+j-1)/2+1
        i=j
    return r

def correlacion(x,y,metodo='pearson'):
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
    if len(x)!=len(y): raise ValueError('Longitudes diferentes')
    if len(x)<3 or np.ptp(x)==0 or np.ptp(y)==0: return None
    if metodo=='spearman': x,y=rangos(x),rangos(y)
    elif metodo!='pearson': raise ValueError('Método desconocido')
    return float(np.corrcoef(x,y)[0,1])

def correlacion_bloques(x,y,semilla=20261008,repeticiones=2000):
    """Entradas: promedios por apertura de un estrato fijo; p bilateral permutacional."""
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float);salida={}
    for metodo in ('pearson','spearman'):
        r=correlacion(x,y,metodo)
        if r is None:
            salida[metodo]=dict(r=None,p=None,ic95=None,motivo='Menos de 3 bloques o varianza nula')
            continue
        rng=np.random.default_rng(semilla);extremos=0;muestras=[]
        for _ in range(repeticiones):
            rp=correlacion(x,rng.permutation(y),metodo)
            extremos+=abs(rp)>=abs(r)-1e-12
            indices=rng.integers(0,len(x),len(x))
            rb=correlacion(x[indices],y[indices],metodo)
            if rb is not None: muestras.append(rb)
        salida[metodo]=dict(r=r,p=(extremos+1)/(repeticiones+1),
            ic95=[float(v) for v in np.quantile(muestras,[.025,.975])] if muestras else None,
            replicas_validas=len(muestras),n_bloques=len(x))
    return salida

def _gamma_superior(a,x):
    """Q(a,x), serie de P o fracción continua de Q (tolerancia 1e-13)."""
    if x==0: return 1.0
    pref=math.exp(a*math.log(x)-x-math.lgamma(a))
    if x<a+1:
        term=total=1/a
        for i in range(1,10000):
            term*=x/(a+i);total+=term
            if abs(term)<abs(total)*1e-13: break
        return max(0.,min(1.,1-pref*total))
    tiny=1e-300;b=x+1-a;c=1/tiny;d=1/b;h=d
    for i in range(1,10000):
        an=-i*(i-a);b+=2;d=an*d+b
        if abs(d)<tiny:d=tiny
        c=b+an/c
        if abs(c)<tiny:c=tiny
        d=1/d;delta=d*c;h*=delta
        if abs(delta-1)<1e-13:break
    return max(0.,min(1.,pref*h))

def chi_cuadrado(tabla,independientes=False):
    """Homogeneidad sin Yates; sólo observaciones disjuntas e independientes.
    Rechaza cualquier frecuencia esperada <5 (criterio conservador).
    No introducir filas W/D/L de rivales del mismo round-robin: duplican partidas.
    """
    t=np.asarray(tabla,dtype=float)
    if not independientes: return dict(aplicable=False,motivo='Independencia no establecida')
    if t.ndim!=2 or min(t.shape)<2 or np.any(t<0) or not np.all(t==np.floor(t)):
        raise ValueError('Tabla de conteos inválida')
    if t.sum()==0 or np.any(t.sum(axis=0)==0) or np.any(t.sum(axis=1)==0):
        return dict(aplicable=False,motivo='Margen vacío')
    esperados=np.outer(t.sum(axis=1),t.sum(axis=0))/t.sum()
    if np.any(esperados<5): return dict(aplicable=False,motivo='Frecuencias esperadas menores que 5',esperados=esperados.tolist())
    chi=float(((t-esperados)**2/esperados).sum());gl=(t.shape[0]-1)*(t.shape[1]-1)
    return dict(aplicable=True,chi2=chi,gl=gl,p=_gamma_superior(gl/2,chi/2),esperados=esperados.tolist())

def holm(valores):
    """Ajuste para una familia de comparaciones; conserva orden original."""
    orden=sorted(range(len(valores)),key=lambda i:valores[i]);ajustados=[None]*len(valores);prev=0.
    for rango,i in enumerate(orden):
        prev=max(prev,min(1.,(len(valores)-rango)*valores[i]));ajustados[i]=prev
    return ajustados
