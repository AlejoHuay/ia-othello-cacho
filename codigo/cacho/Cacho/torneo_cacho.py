"""
Torneo y Evaluación Estadística para Cacho (Parte III y IV de la práctica EC02).

Ejecuta los experimentos rigurosos requeridos por la rúbrica:
1. Torneo IA Base vs IA Mejorada (100 partidas, alternando inicio).
2. Torneo IA Mejorada(FuncionBase) vs IA Mejorada(FuncionMejorada) (100 partidas).
3. Evaluación de Eficiencia (Impacto de Memoización, Poda Star1 y Profundidad).
4. Tests Estadísticos Formales:
   - Test Binomial exacto (p-valor contra H0: win_rate = 0.5)
   - Intervalos de confianza Wilson al 95% para win-rate
   - Test Chi-cuadrado y t-Student / Bootstrap para diferencia de puntajes
   - Correlación de Pearson y Spearman (valor intermedio vs resultado final)
5. Análisis cualitativo de decisiones divergentes.

Genera los archivos CSV requeridos en la carpeta datos/:
- datos/resultados_cacho.csv
- datos/eficiencia_cacho.csv
- datos/analisis_estadistico_cacho.json
"""

import os
import sys
import json
import random
import csv
from time import perf_counter
from collections import Counter
import numpy as np
from scipy import stats

# Permitir ejecución desde cualquier subdirectorio
directorio_actual = os.path.dirname(os.path.abspath(__file__))
if directorio_actual not in sys.path:
    sys.path.insert(0, directorio_actual)

from AgenteCacho import CATEGORIAS, puntuar, normalizar
from AgenteIA.AgenteJugador import ElEstado
from funcion_evaluacion import (
    FuncionEvaluacionBase,
    FuncionEvaluacionMejorada,
    Pesos,
    TIRADAS_POR_TURNO,
    N_DADOS,
)
from agente_ia import AgenteCachoMejorado, AgenteCachoBase
from simulador import jugar_partida, vista_para


def intervalo_wilson(exitos, total, confianza=0.95):
    """Calcula el intervalo de confianza de Wilson para una proporción binomial."""
    if total == 0:
        return 0.0, 0.0
    z = stats.norm.ppf(1 - (1 - confianza) / 2)
    p = exitos / total
    denom = 1 + z**2 / total
    centro = (p + z**2 / (2 * total)) / denom
    margen = z * np.sqrt((p * (1 - p) + z**2 / (4 * total)) / total) / denom
    return max(0.0, centro - margen), min(1.0, centro + margen)


def bootstrap_diferencia_medias(p1, p2, n_bootstrap=2000, semilla=42):
    """Calcula el intervalo de confianza bootstrap al 95% de la diferencia de medias."""
    rng = np.random.default_rng(semilla)
    diffs = np.array(p1) - np.array(p2)
    n = len(diffs)
    indices = rng.integers(0, n, size=(n_bootstrap, n))
    medias_boot = np.mean(diffs[indices], axis=1)
    ic_inf = float(np.percentile(medias_boot, 2.5))
    ic_sup = float(np.percentile(medias_boot, 97.5))
    return float(np.mean(diffs)), ic_inf, ic_sup


def ejecutar_torneo(creador_a, creador_b, nombre_a, nombre_b, n_partidas=100, semilla_base=1000):
    """
    Ejecuta un torneo de n_partidas alternando jugador inicial.
    Retorna resultados detallados y métricas agregadas.
    """
    resultados = []
    print(f"\n{'='*60}")
    print(f"Iniciando Torneo: {nombre_a} (A) vs {nombre_b} (B) [{n_partidas} partidas]")
    print(f"{'='*60}")

    for i in range(n_partidas):
        semilla = semilla_base + i
        empieza = i % 2  # alternar quién empieza (0 = A, 1 = B)
        agente_a = creador_a()
        agente_b = creador_b()

        t0 = perf_counter()
        r = jugar_partida(agente_a, agente_b, semilla=semilla, empieza=empieza)
        t_total = perf_counter() - t0

        pts_a, pts_b = r['puntajes'][0], r['puntajes'][1]
        ganador_idx = r['ganador']
        if ganador_idx == 0:
            ganador = nombre_a
        elif ganador_idx == 1:
            ganador = nombre_b
        else:
            ganador = "Empate"

        # Tiempos y métricas por agente
        dec_a = [d for d in r['decisiones'] if d['jugador'] == 0]
        dec_b = [d for d in r['decisiones'] if d['jugador'] == 1]
        t_prom_a = np.mean([d['tiempo'] for d in dec_a]) if dec_a else 0.0
        t_prom_b = np.mean([d['tiempo'] for d in dec_b]) if dec_b else 0.0

        evals_a = getattr(agente_a, 'metricas', None)
        evals_b = getattr(agente_b, 'metricas', None)
        n_evals_a = np.mean([m['evaluaciones'] for m in evals_a]) if evals_a else 0.0
        n_evals_b = np.mean([m['evaluaciones'] for m in evals_b]) if evals_b else 0.0

        # Muestrear valor de evaluación a mitad de partida (ronda 5 del jugador 0)
        valor_mitad_a = None
        if evals_a:
            ronda_5_m = [m for m in evals_a if m.get('ronda') == 5]
            if ronda_5_m:
                valor_mitad_a = ronda_5_m[0].get('valor')

        resultados.append({
            'partida': i + 1,
            'semilla': semilla,
            'empieza': nombre_a if empieza == 0 else nombre_b,
            'agente_a': nombre_a,
            'agente_b': nombre_b,
            'puntaje_a': pts_a,
            'puntaje_b': pts_b,
            'diferencia': pts_a - pts_b,
            'ganador': ganador,
            'tiempo_decision_a': float(t_prom_a),
            'tiempo_decision_b': float(t_prom_b),
            'tiempo_total': float(t_total),
            'evals_prom_a': float(n_evals_a),
            'evals_prom_b': float(n_evals_b),
            'valor_mitad_a': valor_mitad_a,
        })

        if (i + 1) % 25 == 0 or (i + 1) == n_partidas:
            victorias_a_parc = sum(1 for x in resultados if x['ganador'] == nombre_a)
            victorias_b_parc = sum(1 for x in resultados if x['ganador'] == nombre_b)
            empates_parc = sum(1 for x in resultados if x['ganador'] == "Empate")
            print(f"Progreso: {i+1}/{n_partidas} | Victorias {nombre_a}: {victorias_a_parc} | Victorias {nombre_b}: {victorias_b_parc} | Empates: {empates_parc}")

    return resultados


def analizar_estadisticas(resultados, nombre_a, nombre_b):
    """Realiza el análisis estadístico formal riguroso."""
    n = len(resultados)
    victorias_a = sum(1 for r in resultados if r['ganador'] == nombre_a)
    victorias_b = sum(1 for r in resultados if r['ganador'] == nombre_b)
    empates = sum(1 for r in resultados if r['ganador'] == "Empate")

    # Win-rate de A y B
    win_rate_a = victorias_a / n
    win_rate_b = victorias_b / n
    ic_inf_a, ic_sup_a = intervalo_wilson(victorias_a, n)
    ic_inf_b, ic_sup_b = intervalo_wilson(victorias_b, n)

    # Test binomial de dos colas (H0: p = 0.5 sobre partidas con ganador definido)
    partidas_decisivas = victorias_a + victorias_b
    if partidas_decisivas > 0:
        res_binom = stats.binomtest(victorias_a, partidas_decisivas, p=0.5, alternative='two-sided')
        p_valor_binom = float(res_binom.pvalue)
    else:
        p_valor_binom = 1.0

    # Chi-cuadrado de bondad de ajuste contra distribución esperada 50-50 sobre partidas decisivas
    obs = [victorias_a, victorias_b]
    total_obs = sum(obs)
    if total_obs > 0:
        exp = [total_obs / 2.0, total_obs / 2.0]
        chi2_stat, p_valor_chi2 = stats.chisquare(obs, f_exp=exp)
    else:
        chi2_stat, p_valor_chi2 = 0.0, 1.0

    # Estadísticas de puntajes
    puntos_a = [r['puntaje_a'] for r in resultados]
    puntos_b = [r['puntaje_b'] for r in resultados]
    media_a, std_a = float(np.mean(puntos_a)), float(np.std(puntos_a, ddof=1))
    media_b, std_b = float(np.mean(puntos_b)), float(np.std(puntos_b, ddof=1))

    # Test t pareado para diferencia de puntajes
    t_stat, p_valor_t = stats.ttest_rel(puntos_a, puntos_b)

    # Bootstrap de diferencia de medias (A - B)
    diff_media, ic_boot_inf, ic_boot_sup = bootstrap_diferencia_medias(puntos_a, puntos_b)

    # Correlación de Pearson y Spearman entre valor estimado a mitad de juego y diferencia final
    valores_mitad = [r['valor_mitad_a'] for r in resultados if r['valor_mitad_a'] is not None]
    dif_finales = [r['diferencia'] for r in resultados if r['valor_mitad_a'] is not None]

    if len(valores_mitad) >= 10:
        r_pearson, p_pearson = stats.pearsonr(valores_mitad, dif_finales)
        r_spearman, p_spearman = stats.spearmanr(valores_mitad, dif_finales)
    else:
        r_pearson, p_pearson = 0.0, 1.0
        r_spearman, p_spearman = 0.0, 1.0

    # Tiempos promedio de decisión
    t_prom_a = float(np.mean([r['tiempo_decision_a'] for r in resultados]))
    t_prom_b = float(np.mean([r['tiempo_decision_b'] for r in resultados]))

    analisis = {
        'enfrentamiento': f"{nombre_a} vs {nombre_b}",
        'total_partidas': n,
        'victorias_a': victorias_a,
        'victorias_b': victorias_b,
        'empates': empates,
        'win_rate_a': float(win_rate_a),
        'win_rate_b': float(win_rate_b),
        'ic_wilson_95_a': [float(ic_inf_a), float(ic_sup_a)],
        'ic_wilson_95_b': [float(ic_inf_b), float(ic_sup_b)],
        'test_binomial_p_valor': float(p_valor_binom),
        'chi2_stat': float(chi2_stat),
        'chi2_p_valor': float(p_valor_chi2),
        'puntaje_medio_a': media_a,
        'puntaje_std_a': std_a,
        'puntaje_medio_b': media_b,
        'puntaje_std_b': std_b,
        'diferencia_media_puntaje_a_menos_b': diff_media,
        'ic_bootstrap_95_diferencia': [ic_boot_inf, ic_boot_sup],
        't_student_stat': float(t_stat),
        't_student_p_valor': float(p_valor_t),
        'correlacion_pearson_mitad_final': float(r_pearson),
        'pearson_p_valor': float(p_pearson),
        'correlacion_spearman_mitad_final': float(r_spearman),
        'spearman_p_valor': float(p_spearman),
        'tiempo_promedio_decision_a_ms': t_prom_a * 1000,
        'tiempo_promedio_decision_b_ms': t_prom_b * 1000,
    }
    return analisis


def experimento_eficiencia(n_estados=50, semilla=42):
    """
    Evalúa el impacto de la memoización, poda y profundidad en tiempos y llamadas.
    Toma n_estados aleatorios de decisión y ejecuta las diferentes configuraciones.
    """
    print(f"\n{'='*60}")
    print(f"Iniciando Experimento de Eficiencia (Memoización, Poda y Profundidad)")
    print(f"{'='*60}")

    rng = random.Random(semilla)
    estados = []
    # Generar estados de prueba variados
    for ronda in [1, 3, 5, 7, 9]:
        usadas_j = set(random.sample(CATEGORIAS, ronda))
        usadas_o = set(random.sample(CATEGORIAS, ronda))
        for r_restantes in [3, 2, 1]:
            dados = normalizar([rng.randint(1, 6) for _ in range(N_DADOS)])
            tablero = {
                'dados': dados,
                'tiradas_restantes': r_restantes,
                'puntajes': [ronda * 15, ronda * 14],
                'usadas': [usadas_j, usadas_o],
                'ronda': ronda * 2,
            }
            estados.append(vista_para(tablero, 0))
            if len(estados) >= n_estados:
                break
        if len(estados) >= n_estados:
            break

    configuraciones = [
        ("Mejorado_Completo", {'usar_memo': True, 'usar_poda': True, 'profundidad': None}),
        ("Sin_Poda", {'usar_memo': True, 'usar_poda': False, 'profundidad': None}),
        ("Sin_Memo_Prof1", {'usar_memo': False, 'usar_poda': True, 'profundidad': 1}),
        ("Con_Memo_Prof1", {'usar_memo': True, 'usar_poda': True, 'profundidad': 1}),
        ("Con_Memo_Prof2", {'usar_memo': True, 'usar_poda': True, 'profundidad': 2}),
    ]

    resultados_eficiencia = []

    for nombre_cfg, params in configuraciones:
        agente = AgenteCachoMejorado(**params)
        tiempos = []
        evals = []
        nodos_max = []
        nodos_azar = []
        cortes = []

        for st in estados:
            t0 = perf_counter()
            agente.elegir_accion(st)
            t_ms = (perf_counter() - t0) * 1000
            m = agente.metricas[-1]

            tiempos.append(t_ms)
            evals.append(m['evaluaciones'])
            nodos_max.append(m['nodos_max'])
            nodos_azar.append(m['nodos_azar'])
            cortes.append(m['cortes'])

        res = {
            'configuracion': nombre_cfg,
            'tiempo_medio_ms': float(np.mean(tiempos)),
            'tiempo_std_ms': float(np.std(tiempos)),
            'evaluaciones_medio': float(np.mean(evals)),
            'nodos_max_medio': float(np.mean(nodos_max)),
            'nodos_azar_medio': float(np.mean(nodos_azar)),
            'cortes_medio': float(np.mean(cortes)),
        }
        resultados_eficiencia.append(res)
        print(f"Config: {nombre_cfg:<18} | Tiempo: {res['tiempo_medio_ms']:6.2f} ms | Evals: {res['evaluaciones_medio']:7.1f} | Cortes: {res['cortes_medio']:5.1f}")

    return resultados_eficiencia


def extraer_decisiones_divergentes(n_casos=5, semilla=2026):
    """Encuentra ejemplos representativos de jugadas donde Mejorada y Base divergen."""
    rng = random.Random(semilla)
    casos = []
    
    agente_mejorado = AgenteCachoMejorado()
    agente_base = AgenteCachoBase()

    manos_clave = [
        # (dados, tiradas_restantes, usadas_j, descripcion)
        ((2, 3, 3, 5, 6), 2, set(), "Par de 3 con 2 tiradas restantes"),
        ((1, 2, 3, 4, 6), 1, {'escalera'}, "Casi escalera con 'escalera' ya usada"),
        ((6, 6, 6, 2, 3), 2, set(), "Trío de 6 al inicio de turno"),
        ((1, 1, 1, 1, 5), 1, set(), "Poker servido con 1 tirada restante"),
        ((5, 5, 5, 5, 5), 3, set(), "Grande servida"),
    ]

    for dados, r, usadas, desc in manos_clave:
        tablero = {
            'dados': dados,
            'tiradas_restantes': r,
            'puntajes': [30, 30],
            'usadas': [usadas, set()],
            'ronda': len(usadas) * 2,
        }
        estado = vista_para(tablero, 0)
        
        acc_mejorada = agente_mejorado.elegir_accion(estado)
        val_mejorada = agente_mejorado.ultima_valoracion.get(acc_mejorada, 0.0)
        
        acc_base = agente_base.elegir_accion(estado)

        casos.append({
            'escenario': desc,
            'dados': list(dados),
            'tiradas_restantes': r,
            'usadas': list(usadas),
            'decision_mejorada': str(acc_mejorada),
            'valor_esperado_mejorada': float(val_mejorada) if val_mejorada is not None else 0.0,
            'decision_base': str(acc_base),
        })

    return casos


def main():
    print("Iniciando suite de evaluación rigurosa para Cacho...")

    # Crear directorios de salida
    ruta_base = os.path.abspath(os.path.join(directorio_actual, "..", "..", ".."))
    dir_datos = os.path.join(ruta_base, "datos")
    os.makedirs(dir_datos, exist_ok=True)

    # 1. Torneo 1: Base vs Mejorada (100 partidas)
    res_base_vs_mejorada = ejecutar_torneo(
        creador_a=lambda: AgenteCachoBase(nombre="Base"),
        creador_b=lambda: AgenteCachoMejorado(nombre="Mejorada"),
        nombre_a="Base",
        nombre_b="Mejorada",
        n_partidas=100,
        semilla_base=1000
    )
    analisis_1 = analizar_estadisticas(res_base_vs_mejorada, "Base", "Mejorada")

    # 2. Torneo 2: Aislamiento de componentes: Mejorado(FuncionBase) vs Mejorado(FuncionMejorada)
    res_aislamiento = ejecutar_torneo(
        creador_a=lambda: AgenteCachoMejorado(nombre="Búsqueda_Nueva_Funcion_Base", evaluador=FuncionEvaluacionBase()),
        creador_b=lambda: AgenteCachoMejorado(nombre="Búsqueda_Nueva_Funcion_Mejorada", evaluador=FuncionEvaluacionMejorada()),
        nombre_a="Mej_FuncBase",
        nombre_b="Mej_FuncMejorada",
        n_partidas=100,
        semilla_base=2000
    )
    analisis_2 = analizar_estadisticas(res_aislamiento, "Mej_FuncBase", "Mej_FuncMejorada")

    # 3. Experimento de Eficiencia
    res_eficiencia = experimento_eficiencia(n_estados=60)

    # 4. Análisis de decisiones cualitativas
    casos_decisiones = extraer_decisiones_divergentes()

    # Guardar CSV de resultados (formato exacto especificado en el PDF)
    # Formato PDF: agente_a,agente_b,puntaje_a,puntaje_b,version_funcion,tiempo_decision_promedio
    ruta_csv_principal = os.path.join(dir_datos, "resultados_cacho.csv")
    with open(ruta_csv_principal, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "agente_a", "agente_b", "puntaje_a", "puntaje_b", "version_funcion",
            "tiempo_decision_promedio", "semilla", "empieza", "ganador", "diferencia_puntaje"
        ])
        for r in res_base_vs_mejorada:
            writer.writerow([
                r['agente_a'], r['agente_b'], r['puntaje_a'], r['puntaje_b'], "base_vs_mejorada",
                f"{r['tiempo_decision_b']:.5f}", r['semilla'], r['empieza'], r['ganador'], r['diferencia']
            ])
        for r in res_aislamiento:
            writer.writerow([
                r['agente_a'], r['agente_b'], r['puntaje_a'], r['puntaje_b'], "aislamiento_evaluador",
                f"{r['tiempo_decision_b']:.5f}", r['semilla'], r['empieza'], r['ganador'], r['diferencia']
            ])

    print(f"\n[+] Resultados principales guardados en: {ruta_csv_principal}")

    # Guardar CSV de eficiencia
    ruta_csv_eficiencia = os.path.join(dir_datos, "eficiencia_cacho.csv")
    with open(ruta_csv_eficiencia, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "configuracion", "tiempo_medio_ms", "tiempo_std_ms",
            "evaluaciones_medio", "nodos_max_medio", "nodos_azar_medio", "cortes_medio"
        ])
        for r in res_eficiencia:
            writer.writerow([
                r['configuracion'], f"{r['tiempo_medio_ms']:.3f}", f"{r['tiempo_std_ms']:.3f}",
                f"{r['evaluaciones_medio']:.1f}", f"{r['nodos_max_medio']:.1f}",
                f"{r['nodos_azar_medio']:.1f}", f"{r['cortes_medio']:.1f}"
            ])
    print(f"[+] Resultados de eficiencia guardados en: {ruta_csv_eficiencia}")

    # Guardar JSON con el análisis estadístico consolidado
    ruta_json_stats = os.path.join(dir_datos, "analisis_estadistico_cacho.json")
    datos_consolidados = {
        'torneo_base_vs_mejorada': analisis_1,
        'torneo_aislamiento_evaluacion': analisis_2,
        'eficiencia': res_eficiencia,
        'casos_decisiones': casos_decisiones,
    }
    with open(ruta_json_stats, 'w', encoding='utf-8') as f:
        json.dump(datos_consolidados, f, indent=2, ensure_ascii=False)
    print(f"[+] Análisis estadístico completo guardado en: {ruta_json_stats}")

    # Imprimir resumen de resultados
    print("\n" + "="*60)
    print("RESUMEN ESTADÍSTICO - TORNEO 1: BASE vs MEJORADA")
    print("="*60)
    print(f"Victorias Base: {analisis_1['victorias_a']} | Victorias Mejorada: {analisis_1['victorias_b']} | Empates: {analisis_1['empates']}")
    print(f"Win-Rate Mejorada: {analisis_1['win_rate_b'] * 100:.1f}%")
    print(f"Intervalo de Wilson 95% (Mejorada): [{analisis_1['ic_wilson_95_b'][0]*100:.1f}%, {analisis_1['ic_wilson_95_b'][1]*100:.1f}%]")
    print(f"Test Binomial p-valor: {analisis_1['test_binomial_p_valor']:.6e} (Significativo: {analisis_1['test_binomial_p_valor'] < 0.05})")
    print(f"Puntaje Medio Base: {analisis_1['puntaje_medio_a']:.2f} ± {analisis_1['puntaje_std_a']:.2f}")
    print(f"Puntaje Medio Mejorada: {analisis_1['puntaje_medio_b']:.2f} ± {analisis_1['puntaje_std_b']:.2f}")
    print(f"Diferencia Media (Mejorada - Base): {-analisis_1['diferencia_media_puntaje_a_menos_b']:.2f} pts")

    print("\n" + "="*60)
    print("RESUMEN ESTADÍSTICO - TORNEO 2: MEJORADA(BASE) vs MEJORADA(MEJORADA)")
    print("="*60)
    print(f"Victorias FuncBase: {analisis_2['victorias_a']} | Victorias FuncMejorada: {analisis_2['victorias_b']} | Empates: {analisis_2['empates']}")
    print(f"Win-Rate FuncMejorada: {analisis_2['win_rate_b'] * 100:.1f}%")
    print(f"Intervalo de Wilson 95% (FuncMejorada): [{analisis_2['ic_wilson_95_b'][0]*100:.1f}%, {analisis_2['ic_wilson_95_b'][1]*100:.1f}%]")
    print(f"Test Binomial p-valor: {analisis_2['test_binomial_p_valor']:.6e} (Significativo: {analisis_2['test_binomial_p_valor'] < 0.05})")
    print(f"Puntaje Medio FuncBase: {analisis_2['puntaje_medio_a']:.2f} ± {analisis_2['puntaje_std_a']:.2f}")
    print(f"Puntaje Medio FuncMejorada: {analisis_2['puntaje_medio_b']:.2f} ± {analisis_2['puntaje_std_b']:.2f}")
    print(f"Diferencia Media (FuncMejorada - FuncBase): {-analisis_2['diferencia_media_puntaje_a_menos_b']:.2f} pts")
    print(f"Correlación Pearson (Valor mitad vs Diferencia final): r = {analisis_2['correlacion_pearson_mitad_final']:.4f} (p = {analisis_2['pearson_p_valor']:.4e})")


if __name__ == "__main__":
    main()
