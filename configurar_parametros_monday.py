#!/usr/bin/env python3
"""Configura el "Parameter" (prefill por URL) de cada pregunta del form de Monday.

Uso (Mac / Linux):
    export MONDAY_TOKEN="tu_token"            # no lo escribas en este archivo
    python3 configurar_parametros_monday.py <URL o token del form>            # solo muestra el plan
    python3 configurar_parametros_monday.py <URL o token del form> --aplicar  # aplica los cambios

No necesita librerías extra ni otros archivos.
"""
import json, os, re, sys, unicodedata, urllib.request, pathlib

API = "https://api.monday.com/v2"

# Nombres de parámetro (si hay config.json en la carpeta, se usan los de ahí)
PARAMS = {
    "solicita": "solicita",
    "correo": "correo",
    "account_manager": "account_manager",
    "cuenta": "cuenta",
    "campana": "campana",
    "geo": "geo",
    "presupuesto": "presupuesto",
    "cpm": "cpm",
    "esp_calendario": "esp_calendario",
    "direccion": "direccion",
    "propuesta": "propuesta",
    "estrategia": "Source",
    "prioridad": "prioridad",
    "tipo_solicitud": "tipo_solicitud",
    "notas": "comentarios",
    "cpm_especial": "cpm_especial",
    "calendario": "calendario"
}

# Título de la pregunta en el form -> clave en config.json "params"
TITULOS = {
    "quien solicita": "solicita",
    "correo electronico": "correo",
    "account manager": "account_manager",
    "cuenta": "cuenta",
    "nombre de campana": "campana",
    "geolocalizacion de campana": "geo",
    "presupuesto": "presupuesto",
    "cpm especial": "cpm_especial",
    "cual": "cpm",
    "calendario": "calendario",
    "especificaciones calendario": "esp_calendario",
    "direccion comercial": "direccion",
    "tu propuesta es": "propuesta",
    "prioridad": "prioridad",
    "tipo de solicitud": "tipo_solicitud",
    "estrategia": "estrategia",
    "notificacion al planner": "notas",
}
# Preguntas que se revisan a mano (el formato del valor por URL no está documentado)
REVISAR = {}
# Opciones que usa la herramienta en cada lista (deben coincidir con el form)
LISTAS = {
    "direccion": [
        "Eduardo Gomez",
        "Antonio Rivera",
        "Irasema Vargas",
        "Begoña Casto",
        "Maria Fernanda Herrera",
        "Gabriel Contreras"
    ],
    "propuesta": [
        "Digital",
        "Multi",
        "Regional",
        "Mid Market"
    ],
    "prioridad": [
        "Alta",
        "Media",
        "Baja"
    ],
    "tipo_solicitud": [
        "VIX (AAEE o Pauta)",
        "Pauta O&O",
        "AAEE Digitales",
        "VoBo de Pauta"
    ],
    "cpm_especial": [
        "Si",
        "No",
        "Código 8 / Plan 99",
        "CPM en USD"
    ]
}


def simple(s):
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]+", "", s.lower()).strip()


def gql(token, query, variables=None):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": token, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if out.get("errors"):
        raise RuntimeError(json.dumps(out["errors"], ensure_ascii=False, indent=2))
    return out["data"]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    aplicar = "--aplicar" in sys.argv
    forzar = "--forzar" in sys.argv
    token = os.environ.get("MONDAY_TOKEN")
    if not token:
        sys.exit('Falta el token. Corre primero: export MONDAY_TOKEN="tu_token"')
    if not args:
        sys.exit('Falta la URL del form. Ej.: python3 configurar_parametros_monday.py "https://forms.monday.com/forms/xxxx?r=use1"')
    url = args[0].strip()
    if "wkf.ms" in url:
        sys.exit("Es un link corto (wkf.ms). Ábrelo en el navegador y copia la URL completa (forms.monday.com/forms/...).")
    m = re.search(r"/forms/([A-Za-z0-9]+)", url)
    form_token = m.group(1) if m else url
    print(f"Token del form: {form_token}")
    cfg = pathlib.Path(__file__).with_name("config.json")
    params = dict(PARAMS)
    if cfg.exists():
        params.update(json.loads(cfg.read_text(encoding="utf-8")).get("params", {}))
        print("Usando nombres de parámetro de config.json")

    Q = """query($t: String!) { form(formToken: $t) { title questions {
        id title type %s settings { prefill { enabled source lookup } } } } }"""
    try:
        data = gql(token, Q % "options { label }", {"t": form_token})
    except RuntimeError:
        data = gql(token, Q % "", {"t": form_token})
    form = data["form"]
    print(f'Form: {form["title"]}\n')
    plan = []
    avisos = []
    for q in form["questions"]:
        key = TITULOS.get(simple(q["title"]))
        pf = (q.get("settings") or {}).get("prefill") or {}
        actual = f'{pf.get("source")}:{pf.get("lookup")}' if pf.get("enabled") else "sin prefill"
        if key:
            want = params.get(key, key)
            ok = pf.get("enabled") and pf.get("source") == "QueryParam" and pf.get("lookup") == want
            if pf.get("enabled") and not ok and not forzar:
                print(f'  =   {q["title"]:<32} [{q["type"]}]  {actual}  (ya tiene parámetro: se respeta)')
            else:
                print(f'  {"OK " if ok else "-> "} {q["title"]:<32} [{q["type"]}]  {actual}  =>  {want}')
                if not ok:
                    plan.append((q, want))
            if key in LISTAS and q.get("options") is not None:
                form_ops = [o.get("label") for o in q["options"] or []]
                faltan = [o for o in LISTAS[key] if o not in form_ops]
                if faltan:
                    avisos.append(f'{q["title"]}: la herramienta usa {faltan}, el form tiene {form_ops}')
        elif simple(q["title"]) in REVISAR:
            print(f'  ?   {q["title"]:<32} [{q["type"]}]  {actual}  ({REVISAR[simple(q["title"])]})')
        else:
            print(f'  ·   {q["title"]:<32} [{q["type"]}]  {actual}  (no se toca)')

    if avisos:
        print("\nOpciones que no coinciden (el prefill de esas listas fallaría):")
        for a in avisos:
            print("  ! " + a)
    if not plan:
        print("\nTodo está configurado.")
        return
    if not aplicar:
        print(f"\n{len(plan)} pregunta(s) por configurar. Vuelve a correr con --aplicar para hacer los cambios.")
        return
    print()
    for q, want in plan:
        try:
            gql(token, """mutation($t: String!, $id: String!, $q: UpdateQuestionInput!) {
                update_form_question(formToken: $t, questionId: $id, question: $q) { id } }""",
                {"t": form_token, "id": q["id"], "q": {"type": q["type"],
                 "settings": {"prefill": {"enabled": True, "source": "QueryParam", "lookup": want}}}})
            print(f'  listo  {q["title"]}  =>  {want}')
        except Exception as e:
            print(f'  ERROR  {q["title"]}: {e}')


if __name__ == "__main__":
    main()
