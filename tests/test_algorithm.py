import pytest
from app.services.recommendation_service import (
    calcular_perfil,
    definir_pesos,
    similitud,
    calcular_compatibilidad,
    quick_sort,
    recomendar_profesor
)
from unittest.mock import MagicMock

# ─── HELPERS ───

def make_student(edad=20, promedio=3.5, trabaja=False, recien_graduado=False,
                 disciplina=3, madurez_emocional=3, modalidad="presencial"):
    s = MagicMock()
    s.edad = edad
    s.promedio = promedio
    s.trabaja = trabaja
    s.recien_graduado = recien_graduado
    s.disciplina = disciplina
    s.madurez_emocional = madurez_emocional
    s.modalidad.value = modalidad
    return s

def make_teacher(rigurosidad=3, flexibilidad=3, carga_tareas=3,
                 estilo=1, exp_jovenes=3, exp_adultos=3, id=1, nombre="Profesor Test"):
    t = MagicMock()
    t.id = id
    t.nombre = nombre
    t.rigurosidad = rigurosidad
    t.flexibilidad = flexibilidad
    t.carga_tareas = carga_tareas
    t.estilo = estilo
    t.exp_jovenes = exp_jovenes
    t.exp_adultos = exp_adultos
    return t


# ─── TEST 1: calcular_perfil ───

def test_calcular_perfil_promedios_correctos():
    students = [
        make_student(edad=18, promedio=3.0, trabaja=True,  recien_graduado=True),
        make_student(edad=22, promedio=4.0, trabaja=False, recien_graduado=False),
        make_student(edad=20, promedio=3.5, trabaja=True,  recien_graduado=False),
    ]
    perfil = calcular_perfil(students)

    assert perfil["edad_prom"] == 20.0
    assert perfil["promedio_prom"] == round((3.0 + 4.0 + 3.5) / 3, 2)
    assert perfil["pct_trabaja"] == round(2/3 * 100, 2)
    assert perfil["pct_recien_grad"] == round(1/3 * 100, 2)
    assert perfil["total_estudiantes"] == 3

def test_calcular_perfil_grupo_vacio():
    with pytest.raises(ValueError, match="no tiene estudiantes"):
        calcular_perfil([])

def test_calcular_perfil_todos_trabajan():
    students = [make_student(trabaja=True) for _ in range(5)]
    perfil = calcular_perfil(students)
    assert perfil["pct_trabaja"] == 100.0

def test_calcular_perfil_modalidad_predominante():
    students = [
        make_student(modalidad="presencial"),
        make_student(modalidad="presencial"),
        make_student(modalidad="virtual"),
    ]
    perfil = calcular_perfil(students)
    assert perfil["modalidad_pred"] == "presencial"


# ─── TEST 2: definir_pesos ───

def test_pesos_suman_uno_grupo_base():
    perfil = {
        "edad_prom": 24, "promedio_prom": 3.5,
        "pct_trabaja": 30, "pct_recien_grad": 20
    }
    pesos = definir_pesos(perfil)
    assert abs(sum(pesos.values()) - 1.0) < 0.001

def test_pesos_grupo_joven():
    perfil = {
        "edad_prom": 18, "promedio_prom": 3.5,
        "pct_trabaja": 5, "pct_recien_grad": 75
    }
    pesos = definir_pesos(perfil)
    assert pesos["rigurosidad"] == 0.30
    assert pesos["exp_jovenes"] == 0.25
    assert pesos["flexibilidad"] == 0.10
    assert pesos["exp_adultos"] == 0.05

def test_pesos_adulto_trabajador():
    perfil = {
        "edad_prom": 30, "promedio_prom": 3.5,
        "pct_trabaja": 70, "pct_recien_grad": 5
    }
    pesos = definir_pesos(perfil)
    assert pesos["flexibilidad"] == 0.30
    assert pesos["exp_adultos"] == 0.25
    assert pesos["exp_jovenes"] == 0.05

def test_pesos_bajo_rendimiento():
    perfil = {
        "edad_prom": 22, "promedio_prom": 2.8,
        "pct_trabaja": 20, "pct_recien_grad": 10
    }
    pesos = definir_pesos(perfil)
    assert pesos["estilo"] == 0.25
    assert pesos["flexibilidad"] == 0.25
    assert pesos["rigurosidad"] == 0.10

def test_pesos_alto_rendimiento():
    perfil = {
        "edad_prom": 22, "promedio_prom": 4.5,
        "pct_trabaja": 10, "pct_recien_grad": 10
    }
    pesos = definir_pesos(perfil)
    assert pesos["rigurosidad"] == 0.30
    assert pesos["carga_tareas"] == 0.25


# ─── TEST 3: similitud ───

def test_similitud_valores_iguales():
    assert similitud(3, 3) == 1.0

def test_similitud_diferencia_maxima():
    # Entre 1 y 5 la diferencia máxima es 4 → similitud = 0
    assert similitud(1, 5) == 0.0
    assert similitud(5, 1) == 0.0

def test_similitud_siempre_entre_0_y_1():
    for v_actual in range(1, 6):
        for v_esperado in range(1, 6):
            resultado = similitud(v_actual, v_esperado)
            assert 0.0 <= resultado <= 1.0

def test_similitud_simetrica():
    assert similitud(2, 4) == similitud(4, 2)


# ─── TEST 4: calcular_compatibilidad ───

def test_puntaje_siempre_entre_0_y_1():
    perfil = {
        "madurez_prom": 3, "pct_trabaja": 50,
        "edad_prom": 20, "pct_recien_grad": 40
    }
    pesos = {
        "rigurosidad": 0.20, "flexibilidad": 0.20,
        "carga_tareas": 0.15, "estilo": 0.15,
        "exp_jovenes": 0.15, "exp_adultos": 0.15
    }
    for r in range(1, 6):
        for f in range(1, 6):
            teacher = make_teacher(rigurosidad=r, flexibilidad=f)
            c = calcular_compatibilidad(teacher, perfil, pesos)
            assert 0.0 <= c <= 1.0

def test_profesor_perfecto_obtiene_puntaje_alto():
    # Grupo joven → necesita rigurosidad 5, exp_jovenes 5
    perfil = {
        "madurez_prom": 1, "pct_trabaja": 0,
        "edad_prom": 18, "pct_recien_grad": 80
    }
    pesos = {
        "rigurosidad": 0.30, "exp_jovenes": 0.25,
        "flexibilidad": 0.10, "carga_tareas": 0.15,
        "estilo": 0.15, "exp_adultos": 0.05
    }
    profesor_ideal = make_teacher(rigurosidad=5, exp_jovenes=5, estilo=1)
    profesor_malo  = make_teacher(rigurosidad=1, exp_jovenes=1, estilo=3)

    assert calcular_compatibilidad(profesor_ideal, perfil, pesos) > \
           calcular_compatibilidad(profesor_malo, perfil, pesos)


# ─── TEST 5: quick_sort ───

def test_quick_sort_orden_descendente():
    items = [
        {"teacher_id": 1, "nombre": "A", "puntaje": 0.5},
        {"teacher_id": 2, "nombre": "B", "puntaje": 0.9},
        {"teacher_id": 3, "nombre": "C", "puntaje": 0.3},
        {"teacher_id": 4, "nombre": "D", "puntaje": 0.7},
    ]
    resultado = quick_sort(items, key="puntaje")
    puntajes = [r["puntaje"] for r in resultado]
    assert puntajes == sorted(puntajes, reverse=True)

def test_quick_sort_un_elemento():
    items = [{"teacher_id": 1, "nombre": "A", "puntaje": 0.8}]
    assert quick_sort(items, key="puntaje") == items

def test_quick_sort_lista_vacia():
    assert quick_sort([], key="puntaje") == []

def test_quick_sort_puntajes_iguales():
    items = [
        {"teacher_id": i, "nombre": f"P{i}", "puntaje": 0.5}
        for i in range(5)
    ]
    resultado = quick_sort(items, key="puntaje")
    assert len(resultado) == 5


# ─── TEST 6: recomendar_profesor ───

def test_recomendacion_retorna_estructura_correcta():
    students = [make_student() for _ in range(10)]
    teachers = [make_teacher(id=i, nombre=f"Profesor {i}") for i in range(1, 6)]

    resultado = recomendar_profesor(students, teachers)

    assert "recomendado" in resultado
    assert "top3" in resultado
    assert "scores" in resultado
    assert "perfil_grupo" in resultado
    assert "pesos_usados" in resultado
    assert "justificacion" in resultado

def test_recomendacion_top3_maximo_3():
    students = [make_student() for _ in range(5)]
    teachers = [make_teacher(id=i) for i in range(1, 4)]  # solo 3 profesores

    resultado = recomendar_profesor(students, teachers)
    assert len(resultado["top3"]) <= 3

def test_recomendacion_sin_profesores_lanza_error():
    students = [make_student() for _ in range(5)]
    with pytest.raises(ValueError, match="No hay profesores"):
        recomendar_profesor(students, [])

def test_recomendacion_scores_ordenados_descendente():
    students = [make_student() for _ in range(10)]
    teachers = [make_teacher(id=i) for i in range(1, 8)]

    resultado = recomendar_profesor(students, teachers)
    puntajes = [s["puntaje"] for s in resultado["scores"]]
    assert puntajes == sorted(puntajes, reverse=True)

def test_recomendado_es_el_primero_del_ranking():
    students = [make_student() for _ in range(10)]
    teachers = [make_teacher(id=i) for i in range(1, 6)]

    resultado = recomendar_profesor(students, teachers)
    assert resultado["recomendado"]["puntaje"] == resultado["scores"][0]["puntaje"]