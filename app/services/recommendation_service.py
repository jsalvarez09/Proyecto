from statistics import mode
from app.models.student import Student
from app.models.teacher import Teacher

# ─── PASO 1: CALCULAR PERFIL COLECTIVO ───

def calcular_perfil(students: list[Student]) -> dict:
    n = len(students)
    if n == 0:
        raise ValueError("El grupo no tiene estudiantes")

    edad_prom = sum(s.edad for s in students) / n
    promedio_prom = sum(float(s.promedio) for s in students) / n
    pct_trabaja = sum(1 for s in students if s.trabaja) / n * 100
    pct_recien_grad = sum(1 for s in students if s.recien_graduado) / n * 100
    disciplina_prom = sum(s.disciplina for s in students) / n
    madurez_prom = sum(s.madurez_emocional for s in students) / n
    modalidad_pred = mode(s.modalidad.value for s in students)

    return {
        "edad_prom": round(edad_prom, 2),
        "promedio_prom": round(promedio_prom, 2),
        "pct_trabaja": round(pct_trabaja, 2),
        "pct_recien_grad": round(pct_recien_grad, 2),
        "disciplina_prom": round(disciplina_prom, 2),
        "madurez_prom": round(madurez_prom, 2),
        "modalidad_pred": modalidad_pred,
        "total_estudiantes": n
    }


# ─── PASO 2: PESOS DINÁMICOS ───

def definir_pesos(perfil: dict) -> dict:
    pesos = {
        "rigurosidad": 0.20,
        "flexibilidad": 0.20,
        "carga_tareas": 0.15,
        "estilo": 0.15,
        "exp_jovenes": 0.15,
        "exp_adultos": 0.15
    }

    if perfil["edad_prom"] < 20 and perfil["pct_recien_grad"] > 50:
        # Grupo joven sin experiencia
        pesos["rigurosidad"] = 0.30
        pesos["exp_jovenes"] = 0.25
        pesos["flexibilidad"] = 0.10
        pesos["carga_tareas"] = 0.15
        pesos["estilo"] = 0.15
        pesos["exp_adultos"] = 0.05

    elif perfil["pct_trabaja"] > 60 or perfil["edad_prom"] > 28:
        # Grupo adulto trabajador
        pesos["flexibilidad"] = 0.30
        pesos["exp_adultos"] = 0.25
        pesos["carga_tareas"] = 0.20
        pesos["rigurosidad"] = 0.15
        pesos["estilo"] = 0.05
        pesos["exp_jovenes"] = 0.05

    elif perfil["promedio_prom"] < 3.2:
        # Grupo de bajo rendimiento
        pesos["estilo"] = 0.25
        pesos["flexibilidad"] = 0.25
        pesos["rigurosidad"] = 0.10
        pesos["carga_tareas"] = 0.15
        pesos["exp_jovenes"] = 0.15
        pesos["exp_adultos"] = 0.10

    elif perfil["promedio_prom"] > 4.0:
        # Grupo de alto rendimiento
        pesos["rigurosidad"] = 0.30
        pesos["carga_tareas"] = 0.25
        pesos["flexibilidad"] = 0.15
        pesos["estilo"] = 0.10
        pesos["exp_jovenes"] = 0.10
        pesos["exp_adultos"] = 0.10

    return pesos


# ─── PASO 3: FUNCIÓN DE SIMILITUD ───

def similitud(valor_actual: float, valor_esperado: float) -> float:
    diferencia = abs(valor_actual - valor_esperado)
    return round(1 - (diferencia / 4), 4)


# ─── PASO 4: CALCULAR COMPATIBILIDAD ───

def calcular_compatibilidad(teacher: Teacher, perfil: dict, pesos: dict) -> float:
    puntaje = 0.0

    # Rigurosidad esperada: grupo poco maduro necesita más estructura
    rig_esperada = 5 - (perfil["madurez_prom"] - 1)
    puntaje += pesos["rigurosidad"] * similitud(teacher.rigurosidad, rig_esperada)

    # Flexibilidad esperada: mayor si trabajan
    flex_esperada = 1 + (perfil["pct_trabaja"] / 100) * 4
    puntaje += pesos["flexibilidad"] * similitud(teacher.flexibilidad, flex_esperada)

    # Carga de tareas: menor carga si trabajan mucho
    carga_esperada = 5 - (perfil["pct_trabaja"] / 100) * 4
    puntaje += pesos["carga_tareas"] * similitud(teacher.carga_tareas, carga_esperada)

    # Estilo: grupo joven prefiere amigable (1), adulto prefiere neutro (2)
    estilo_esperado = 1 if perfil["edad_prom"] < 22 else 2
    puntaje += pesos["estilo"] * similitud(teacher.estilo, estilo_esperado)

    # Experiencia con jóvenes
    exp_jov_esperada = 5 if perfil["pct_recien_grad"] > 40 else 3
    puntaje += pesos["exp_jovenes"] * similitud(teacher.exp_jovenes, exp_jov_esperada)

    # Experiencia con adultos
    exp_adu_esperada = 5 if perfil["pct_trabaja"] > 50 else 3
    puntaje += pesos["exp_adultos"] * similitud(teacher.exp_adultos, exp_adu_esperada)

    return round(puntaje, 4)


# ─── PASO 5: QUICK SORT ───

def quick_sort(items: list, key: str) -> list:
    if len(items) <= 1:
        return items

    pivot = items[len(items) // 2][key]
    left = [x for x in items if x[key] > pivot]   # descendente
    middle = [x for x in items if x[key] == pivot]
    right = [x for x in items if x[key] < pivot]

    return quick_sort(left, key) + middle + quick_sort(right, key)


# ─── PASO 6: GENERAR JUSTIFICACIÓN ───

def generar_justificacion(teacher: Teacher, perfil: dict, pesos: dict) -> str:
    # Detectar perfil activo
    if perfil["edad_prom"] < 20 and perfil["pct_recien_grad"] > 50:
        perfil_nombre = "Grupo joven sin experiencia universitaria"
    elif perfil["pct_trabaja"] > 60 or perfil["edad_prom"] > 28:
        perfil_nombre = "Grupo adulto trabajador"
    elif perfil["promedio_prom"] < 3.2:
        perfil_nombre = "Grupo de bajo rendimiento académico"
    elif perfil["promedio_prom"] > 4.0:
        perfil_nombre = "Grupo de alto rendimiento académico"
    else:
        perfil_nombre = "Grupo mixto equilibrado"

    # Criterio con mayor peso
    criterio_principal = max(pesos, key=pesos.get)
    nombres_criterios = {
        "rigurosidad": "rigurosidad académica",
        "flexibilidad": "flexibilidad pedagógica",
        "carga_tareas": "carga de tareas moderada",
        "estilo": "estilo de enseñanza",
        "exp_jovenes": "experiencia con grupos jóvenes",
        "exp_adultos": "experiencia con grupos adultos"
    }

    return (
        f"El profesor {teacher.nombre} fue recomendado para el perfil '{perfil_nombre}'. "
        f"El grupo tiene una edad promedio de {perfil['edad_prom']} años, "
        f"un promedio académico de {perfil['promedio_prom']}, "
        f"un {perfil['pct_trabaja']}% de estudiantes que trabajan "
        f"y un {perfil['pct_recien_grad']}% de recién graduados. "
        f"El criterio determinante fue '{nombres_criterios[criterio_principal]}' "
        f"con un peso de {round(pesos[criterio_principal] * 100)}% en la evaluación."
    )


# ─── FUNCIÓN PRINCIPAL ───

def recomendar_profesor(students: list[Student], teachers: list[Teacher]) -> dict:
    if not teachers:
        raise ValueError("No hay profesores disponibles")

    # 1. Perfil colectivo
    perfil = calcular_perfil(students)

    # 2. Pesos dinámicos
    pesos = definir_pesos(perfil)

    # 3. Calcular puntaje para cada profesor
    scores = []
    for teacher in teachers:
        puntaje = calcular_compatibilidad(teacher, perfil, pesos)
        scores.append({
            "teacher_id": teacher.id,
            "nombre": teacher.nombre,
            "puntaje": puntaje
        })

    # 4. Ordenar con Quick Sort descendente
    scores_ordenados = quick_sort(scores, key="puntaje")

    # 5. Profesor recomendado y top 3
    top3 = scores_ordenados[:3]
    recomendado_id = scores_ordenados[0]["teacher_id"]
    recomendado = next(t for t in teachers if t.id == recomendado_id)

    # 6. Justificación
    justificacion = generar_justificacion(recomendado, perfil, pesos)

    return {
        "recomendado": scores_ordenados[0],
        "top3": top3,
        "scores": scores_ordenados,
        "perfil_grupo": perfil,
        "pesos_usados": pesos,
        "justificacion": justificacion
    }