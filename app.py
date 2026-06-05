import os, json, base64, re
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

_historico = []
_config = {
    "proveedor": os.environ.get("AI_PROVIDER", "anthropic"),
    "pct_min": 70,
    "nota_min": 4.5,
}

UNIACC_ASIGNATURAS = [
    {"codigo":"PSIC0101","nombre":"Bases Biológicas del Comportamiento","periodo":"P1"},
    {"codigo":"PSIC0102","nombre":"Epistemología","periodo":"P1"},
    {"codigo":"PSIC0103","nombre":"Introducción a la Psicología","periodo":"P1"},
    {"codigo":"PSIC0104","nombre":"Metodología de la Investigación","periodo":"P1"},
    {"codigo":"PSIC0105","nombre":"Procesos Psicológicos Básicos","periodo":"P1"},
    {"codigo":"NIVE0101","nombre":"Herramientas de Razonamiento y Comunicación","periodo":"P1"},
    {"codigo":"NIVE0102","nombre":"Herramientas para el Aprendizaje","periodo":"P1"},
    {"codigo":"PSIC0201","nombre":"Elementos de Neurociencia","periodo":"P2"},
    {"codigo":"PSIC0202","nombre":"Metodología Cuantitativa de Investigación","periodo":"P2"},
    {"codigo":"PSIC0203","nombre":"Psicología del Aprendizaje","periodo":"P2"},
    {"codigo":"PSIC0204","nombre":"Psicología Social","periodo":"P2"},
    {"codigo":"PSIC0205","nombre":"Teoría de la Personalidad","periodo":"P2"},
    {"codigo":"TRAN0201","nombre":"Comunicación Significativa","periodo":"P2"},
    {"codigo":"SELSHH26","nombre":"Ser Humano, Hoy","periodo":"P2"},
    {"codigo":"PSIC0301","nombre":"Análisis de Datos Cuantitativos","periodo":"P3"},
    {"codigo":"PSIC0302","nombre":"Ciclo Vital I - Infancia","periodo":"P3"},
    {"codigo":"PSIC0303","nombre":"Problemas Psicosociales","periodo":"P3"},
    {"codigo":"PSIC0304","nombre":"Psicobiología","periodo":"P3"},
    {"codigo":"PSIC0305","nombre":"Teorías Psicoanalíticas","periodo":"P3"},
    {"codigo":"EFOG2601","nombre":"Formación General I","periodo":"P3"},
    {"codigo":"PSIC0401","nombre":"Ciclo Vital II - Adolescencia","periodo":"P4"},
    {"codigo":"PSIC0402","nombre":"Metodología Cualitativa de Investigación","periodo":"P4"},
    {"codigo":"PSIC0403","nombre":"Sexualidad Humana","periodo":"P4"},
    {"codigo":"PSIC0404","nombre":"Teorías Cognitivas","periodo":"P4"},
    {"codigo":"PSIC0405","nombre":"Teorías Sistémicas","periodo":"P4"},
    {"codigo":"EFOG2602","nombre":"Formación General II","periodo":"P4"},
    {"codigo":"PSIC0501","nombre":"Análisis de Datos Cualitativos","periodo":"P5"},
    {"codigo":"PSIC0502","nombre":"Ciclo Vital III - Adultez","periodo":"P5"},
    {"codigo":"PSIC0503","nombre":"Psicología Social-Comunitaria","periodo":"P5"},
    {"codigo":"PSIC0504","nombre":"Psicopatología Infantil y de la Adolescencia","periodo":"P5"},
    {"codigo":"PSIC0505","nombre":"Teorías Humanistas","periodo":"P5"},
    {"codigo":"SELEH26","nombre":"Ética, Hoy","periodo":"P5"},
    {"codigo":"EFOG2603","nombre":"Formación General III","periodo":"P5"},
    {"codigo":"PSIC0601","nombre":"Evaluación Psicológica Infanto-Juvenil","periodo":"P6"},
    {"codigo":"PSIC0602","nombre":"Intervención Social Comunitaria","periodo":"P6"},
    {"codigo":"PSIC0603","nombre":"Psicología Educacional","periodo":"P6"},
    {"codigo":"PSIC0604","nombre":"Psicología Organizacional","periodo":"P6"},
    {"codigo":"PSIC0605","nombre":"Psicopatología Adultos","periodo":"P6"},
    {"codigo":"EFOG2604","nombre":"Formación General IV","periodo":"P6"},
    {"codigo":"PSIC0701","nombre":"Desarrollo Organizacional","periodo":"P7"},
    {"codigo":"PSIC0702","nombre":"Ética para Psicólogos","periodo":"P7"},
    {"codigo":"PSIC0703","nombre":"Evaluación Psicológica Adultos","periodo":"P7"},
    {"codigo":"PSIC0704","nombre":"Intervención Clínica Infanto Juvenil","periodo":"P7"},
    {"codigo":"PSIC0705","nombre":"Intervenciones Psicoeducativas y Preventivas en Salud Mental","periodo":"P7"},
    {"codigo":"PRAC0101","nombre":"Práctica Profesional I","periodo":"P7"},
    {"codigo":"PSIC0801","nombre":"Intervención Clínica Adultos","periodo":"P8"},
    {"codigo":"PSIC0802","nombre":"Intervención Educacional","periodo":"P8"},
    {"codigo":"PSIC0803","nombre":"Intervención Organizacional","periodo":"P8"},
    {"codigo":"PSIC0804","nombre":"Intervenciones Psicológicas a Distancia","periodo":"P8"},
    {"codigo":"PSIC0805","nombre":"Psicología y Políticas Públicas","periodo":"P8"},
    {"codigo":"PRAC0102","nombre":"Práctica Profesional II","periodo":"P8"},
    {"codigo":"PSIC0901","nombre":"Seminario de Título y Ética Profesional","periodo":"P9"},
    {"codigo":"PSIC0902","nombre":"Taller de Integración Profesional I","periodo":"P9"},
    {"codigo":"PSIC0903","nombre":"Intervenciones en Adicciones","periodo":"P9"},
    {"codigo":"PSIC0904","nombre":"Intervenciones en Violencia","periodo":"P9"},
    {"codigo":"PSIC0905","nombre":"Psicogerontología","periodo":"P9"},
    {"codigo":"PSIC1001","nombre":"Taller de Integración Profesional II","periodo":"P10"},
    {"codigo":"PSIC1002","nombre":"Taller de Titulación","periodo":"P10"},
    {"codigo":"PREX1010","nombre":"Presentación Examen","periodo":"P10"},
    {"codigo":"DEEX1010","nombre":"Defensa Examen","periodo":"P10"},
]

def clean_json(text):
    text = re.sub(r"```json|```", "", text).strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    return m.group(0) if m else text

def call_ai(prompt_text, pdf_b64=None, max_tokens=2000):
    proveedor = _config.get("proveedor", "anthropic")

    # ── ANTHROPIC ──────────────────────────────────────────────
    if proveedor == "anthropic":
        import anthropic as ac
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not key: raise ValueError("ANTHROPIC_API_KEY no configurada")
        client = ac.Anthropic(api_key=key)
        content = []
        if pdf_b64:
            content.append({"type":"document","source":{"type":"base64","media_type":"application/pdf","data":pdf_b64}})
        content.append({"type":"text","text":prompt_text})
        r = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            messages=[{"role":"user","content":content}]
        )
        return r.content[0].text

    # ── GEMINI ─────────────────────────────────────────────────
    elif proveedor == "gemini":
        import google.generativeai as genai
        key = os.environ.get("GEMINI_API_KEY", "")
        if not key: raise ValueError("GEMINI_API_KEY no configurada")
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        parts = []
        if pdf_b64:
            pdf_bytes = base64.b64decode(pdf_b64)
            parts.append({"mime_type": "application/pdf", "data": pdf_bytes})
        parts.append(prompt_text)
        response = model.generate_content(parts)
        return response.text

    # ── OPENAI ─────────────────────────────────────────────────
    elif proveedor == "openai":
        from openai import OpenAI
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key: raise ValueError("OPENAI_API_KEY no configurada")
        client = OpenAI(api_key=key)
        if pdf_b64:
            prompt_text = "[Programa académico adjunto — analiza su contenido]\n\n" + prompt_text
        r = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=max_tokens,
            messages=[{"role":"user","content":prompt_text}]
        )
        return r.choices[0].message.content

    raise ValueError(f"Proveedor no reconocido: {proveedor}")


# ── RUTAS ──────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify({
        "proveedor": _config["proveedor"],
        "pct_min": _config["pct_min"],
        "nota_min": _config["nota_min"],
        "anthropic_set": bool(os.environ.get("ANTHROPIC_API_KEY","")),
        "openai_set":    bool(os.environ.get("OPENAI_API_KEY","")),
        "gemini_set":    bool(os.environ.get("GEMINI_API_KEY","")),
    })

@app.route("/api/config", methods=["POST"])
def save_config():
    data = request.json
    for f in ("proveedor","pct_min","nota_min"):
        if f in data: _config[f] = data[f]
    return jsonify({"ok": True})

@app.route("/api/test_conexion", methods=["POST"])
def test_conexion():
    try:
        r = call_ai("Responde solo: OK")
        return jsonify({"ok": True, "respuesta": r.strip()[:30]})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@app.route("/api/extraer_certificado", methods=["POST"])
def extraer_certificado():
    if "archivo" not in request.files:
        return jsonify({"error":"Sin archivo"}), 400
    b64 = base64.standard_b64encode(request.files["archivo"].read()).decode()
    prompt = """Extrae del certificado académico los datos y devuelve SOLO JSON sin markdown:
{"estudiante":{"nombre":"","rut":"","carrera":"","institucion":""},
"asignaturas":[{"nombre":"","codigo":"","semestre":"","nota":5.5}]}
Si no hay nota usa 0. La nota debe ser número decimal."""
    try:
        return jsonify(json.loads(clean_json(call_ai(prompt, pdf_b64=b64, max_tokens=2000))))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/contrastar", methods=["POST"])
def contrastar():
    data = request.json
    asig = data.get("asignatura", {})
    institucion = data.get("institucion", "")
    pdf_b64 = data.get("programa_b64")

    # Revisar histórico primero
    if institucion:
        for reg in _historico:
            if reg.get("institucion","").lower() == institucion.lower():
                for conv in reg.get("convalidadas",[]):
                    if conv["origen"].lower() == asig["nombre"].lower():
                        return jsonify({**asig,
                            "codigoUniacc": conv["codigoUniacc"],
                            "nombreUniacc": conv["uniacc"],
                            "pct": conv["pct"],
                            "justificacion": "Equivalencia del histórico",
                            "fuente": "historico"})

    lista = "\n".join([f"{u['codigo']}: {u['nombre']}" for u in UNIACC_ASIGNATURAS])

    try:
        if pdf_b64:
            prompt = f"""Eres experto en equivalencias curriculares de psicología universitaria en Chile.
Asignatura origen: "{asig['nombre']}" (código: {asig.get('codigo','s/c')}).
Analiza el programa adjunto y determina la asignatura UNIACC más equivalente:
{lista}
Responde SOLO JSON sin markdown:
{{"codigoUniacc":"PSICXXXX","nombreUniacc":"nombre exacto","pct":75,"justificacion":"razón en 15 palabras"}}"""
            r = call_ai(prompt, pdf_b64=pdf_b64)
            fuente = "programa_pdf"
        else:
            prompt = f"""Eres experto en equivalencias curriculares de psicología universitaria en Chile.
Asignatura origen: "{asig['nombre']}". Solo tengo el nombre, sin programa.
Estima la equivalencia UNIACC más probable:
{lista}
Responde SOLO JSON sin markdown:
{{"codigoUniacc":"PSICXXXX","nombreUniacc":"nombre exacto","pct":55,"justificacion":"estimación por nombre sin programa"}}
Si la coincidencia es baja usa pct menor a 50."""
            r = call_ai(prompt)
            fuente = "nombre_only"

        parsed = json.loads(clean_json(r))
        return jsonify({**asig, **parsed, "fuente": fuente})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/historico", methods=["GET"])
def get_historico():
    return jsonify(_historico)

@app.route("/api/historico", methods=["POST"])
def save_historico():
    data = request.json
    data["fecha"] = datetime.now().isoformat()
    _historico.append(data)
    return jsonify({"ok": True, "total": len(_historico)})

@app.route("/api/historico/<int:idx>", methods=["DELETE"])
def delete_historico(idx):
    if 0 <= idx < len(_historico):
        _historico.pop(idx)
    return jsonify({"ok": True})

@app.route("/api/equivalencias", methods=["GET"])
def get_equivalencias():
    por_inst = {}
    for r in _historico:
        inst = r.get("institucion","Desconocida")
        if inst not in por_inst: por_inst[inst] = []
        for c in r.get("convalidadas",[]):
            if not any(x["origen"]==c["origen"] for x in por_inst[inst]):
                por_inst[inst].append(c)
    return jsonify(por_inst)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)
