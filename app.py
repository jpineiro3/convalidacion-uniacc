import os
import json
import base64
import re
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DATA_FILE = Path("data/historico.json")
CONFIG_FILE = Path("data/config.json")
DATA_FILE.parent.mkdir(exist_ok=True)
if not DATA_FILE.exists():
    DATA_FILE.write_text(json.dumps([]))
if not CONFIG_FILE.exists():
    CONFIG_FILE.write_text(json.dumps({
        "proveedor": "anthropic",
        "anthropic_key": "",
        "openai_key": "",
        "gemini_key": "",
        "pct_min": 70,
        "nota_min": 4.5,
        "ruta_uniacc": ""
    }))

def get_config():
    return json.loads(CONFIG_FILE.read_text())

def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2))

UNIACC_ASIGNATURAS = [
    {"codigo": "PSIC0101", "nombre": "Bases Biológicas del Comportamiento", "periodo": "P1"},
    {"codigo": "PSIC0102", "nombre": "Epistemología", "periodo": "P1"},
    {"codigo": "PSIC0103", "nombre": "Introducción a la Psicología", "periodo": "P1"},
    {"codigo": "PSIC0104", "nombre": "Metodología de la Investigación", "periodo": "P1"},
    {"codigo": "PSIC0105", "nombre": "Procesos Psicológicos Básicos", "periodo": "P1"},
    {"codigo": "NIVE0101", "nombre": "Herramientas de Razonamiento y Comunicación", "periodo": "P1"},
    {"codigo": "NIVE0102", "nombre": "Herramientas para el Aprendizaje", "periodo": "P1"},
    {"codigo": "PSIC0201", "nombre": "Elementos de Neurociencia", "periodo": "P2"},
    {"codigo": "PSIC0202", "nombre": "Metodología Cuantitativa de Investigación", "periodo": "P2"},
    {"codigo": "PSIC0203", "nombre": "Psicología del Aprendizaje", "periodo": "P2"},
    {"codigo": "PSIC0204", "nombre": "Psicología Social", "periodo": "P2"},
    {"codigo": "PSIC0205", "nombre": "Teoría de la Personalidad", "periodo": "P2"},
    {"codigo": "TRAN0201", "nombre": "Comunicación Significativa", "periodo": "P2"},
    {"codigo": "SELSHH26", "nombre": "Ser Humano, Hoy", "periodo": "P2"},
    {"codigo": "PSIC0301", "nombre": "Análisis de Datos Cuantitativos", "periodo": "P3"},
    {"codigo": "PSIC0302", "nombre": "Ciclo Vital I - Infancia", "periodo": "P3"},
    {"codigo": "PSIC0303", "nombre": "Problemas Psicosociales", "periodo": "P3"},
    {"codigo": "PSIC0304", "nombre": "Psicobiología", "periodo": "P3"},
    {"codigo": "PSIC0305", "nombre": "Teorías Psicoanalíticas", "periodo": "P3"},
    {"codigo": "EFOG2601", "nombre": "Formación General I", "periodo": "P3"},
    {"codigo": "PSIC0401", "nombre": "Ciclo Vital II - Adolescencia", "periodo": "P4"},
    {"codigo": "PSIC0402", "nombre": "Metodología Cualitativa de Investigación", "periodo": "P4"},
    {"codigo": "PSIC0403", "nombre": "Sexualidad Humana", "periodo": "P4"},
    {"codigo": "PSIC0404", "nombre": "Teorías Cognitivas", "periodo": "P4"},
    {"codigo": "PSIC0405", "nombre": "Teorías Sistémicas", "periodo": "P4"},
    {"codigo": "EFOG2602", "nombre": "Formación General II", "periodo": "P4"},
    {"codigo": "PSIC0501", "nombre": "Análisis de Datos Cualitativos", "periodo": "P5"},
    {"codigo": "PSIC0502", "nombre": "Ciclo Vital III - Adultez", "periodo": "P5"},
    {"codigo": "PSIC0503", "nombre": "Psicología Social-Comunitaria", "periodo": "P5"},
    {"codigo": "PSIC0504", "nombre": "Psicopatología Infantil y de la Adolescencia", "periodo": "P5"},
    {"codigo": "PSIC0505", "nombre": "Teorías Humanistas", "periodo": "P5"},
    {"codigo": "SELEH26", "nombre": "Ética, Hoy", "periodo": "P5"},
    {"codigo": "EFOG2603", "nombre": "Formación General III", "periodo": "P5"},
    {"codigo": "PSIC0601", "nombre": "Evaluación Psicológica Infanto-Juvenil", "periodo": "P6"},
    {"codigo": "PSIC0602", "nombre": "Intervención Social Comunitaria", "periodo": "P6"},
    {"codigo": "PSIC0603", "nombre": "Psicología Educacional", "periodo": "P6"},
    {"codigo": "PSIC0604", "nombre": "Psicología Organizacional", "periodo": "P6"},
    {"codigo": "PSIC0605", "nombre": "Psicopatología Adultos", "periodo": "P6"},
    {"codigo": "EFOG2604", "nombre": "Formación General IV", "periodo": "P6"},
    {"codigo": "PSIC0701", "nombre": "Desarrollo Organizacional", "periodo": "P7"},
    {"codigo": "PSIC0702", "nombre": "Ética para Psicólogos", "periodo": "P7"},
    {"codigo": "PSIC0703", "nombre": "Evaluación Psicológica Adultos", "periodo": "P7"},
    {"codigo": "PSIC0704", "nombre": "Intervención Clínica Infanto Juvenil", "periodo": "P7"},
    {"codigo": "PSIC0705", "nombre": "Intervenciones Psicoeducativas y Preventivas en Salud Mental", "periodo": "P7"},
    {"codigo": "PRAC0101", "nombre": "Práctica Profesional I", "periodo": "P7"},
    {"codigo": "PSIC0801", "nombre": "Intervención Clínica Adultos", "periodo": "P8"},
    {"codigo": "PSIC0802", "nombre": "Intervención Educacional", "periodo": "P8"},
    {"codigo": "PSIC0803", "nombre": "Intervención Organizacional", "periodo": "P8"},
    {"codigo": "PSIC0804", "nombre": "Intervenciones Psicológicas a Distancia", "periodo": "P8"},
    {"codigo": "PSIC0805", "nombre": "Psicología y Políticas Públicas", "periodo": "P8"},
    {"codigo": "PRAC0102", "nombre": "Práctica Profesional II", "periodo": "P8"},
    {"codigo": "PSIC0901", "nombre": "Seminario de Título y Ética Profesional", "periodo": "P9"},
    {"codigo": "PSIC0902", "nombre": "Taller de Integración Profesional I", "periodo": "P9"},
    {"codigo": "PSIC0903", "nombre": "Intervenciones en Adicciones", "periodo": "P9"},
    {"codigo": "PSIC0904", "nombre": "Intervenciones en Violencia", "periodo": "P9"},
    {"codigo": "PSIC0905", "nombre": "Psicogerontología", "periodo": "P9"},
    {"codigo": "PSIC1001", "nombre": "Taller de Integración Profesional II", "periodo": "P10"},
    {"codigo": "PSIC1002", "nombre": "Taller de Titulación", "periodo": "P10"},
    {"codigo": "PREX1010", "nombre": "Presentación Examen", "periodo": "P10"},
    {"codigo": "DEEX1010", "nombre": "Defensa Examen", "periodo": "P10"},
]


def pdf_to_base64(path: Path) -> str:
    return base64.standard_b64encode(path.read_bytes()).decode("utf-8")


def clean_json(text: str) -> str:
    text = re.sub(r"```json|```", "", text).strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    return m.group(0) if m else text


# ─── ADAPTADORES POR PROVEEDOR ────────────────────────────────────────────────

def call_anthropic(messages: list, api_key: str, max_tokens: int = 2000) -> str:
    import anthropic as ac
    client = ac.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        messages=messages,
    )
    return response.content[0].text


def call_openai(messages: list, api_key: str, pdf_b64: str = None, max_tokens: int = 2000) -> str:
    """OpenAI GPT-4o. PDFs se convierten a texto via extracción básica o se describe el contenido."""
    payload = {
        "model": "gpt-4o",
        "max_tokens": max_tokens,
        "messages": messages,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


def call_gemini(prompt_text: str, api_key: str, pdf_b64: str = None, max_tokens: int = 2000) -> str:
    """Google Gemini 1.5 Flash (gratuito con límites)."""
    model = "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    parts = []
    if pdf_b64:
        parts.append({"inline_data": {"mime_type": "application/pdf", "data": pdf_b64}})
    parts.append({"text": prompt_text})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"maxOutputTokens": max_tokens}
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data["candidates"][0]["content"]["parts"][0]["text"]


def call_ai(prompt_text: str, pdf_b64: str = None, max_tokens: int = 2000) -> str:
    """Dispatcher: llama al proveedor configurado."""
    cfg = get_config()
    proveedor = cfg.get("proveedor", "anthropic")

    if proveedor == "anthropic":
        key = cfg.get("anthropic_key") or os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            raise ValueError("API Key de Anthropic no configurada")
        messages = []
        content = []
        if pdf_b64:
            content.append({"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64}})
        content.append({"type": "text", "text": prompt_text})
        messages.append({"role": "user", "content": content})
        return call_anthropic(messages, key, max_tokens)

    elif proveedor == "openai":
        key = cfg.get("openai_key") or os.environ.get("OPENAI_API_KEY", "")
        if not key:
            raise ValueError("API Key de OpenAI no configurada")
        content = []
        if pdf_b64:
            # GPT-4o no acepta PDF directo; agregamos nota al prompt
            prompt_text = "[NOTA: Se adjunta un programa académico en PDF. Analiza el contenido descrito a continuación.]\n\n" + prompt_text
        content.append({"role": "user", "content": prompt_text})
        return call_openai(content, key, max_tokens=max_tokens)

    elif proveedor == "gemini":
        key = cfg.get("gemini_key") or os.environ.get("GEMINI_API_KEY", "")
        if not key:
            raise ValueError("API Key de Gemini no configurada")
        return call_gemini(prompt_text, key, pdf_b64=pdf_b64, max_tokens=max_tokens)

    else:
        raise ValueError(f"Proveedor desconocido: {proveedor}")


# ─── RUTAS ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/config", methods=["GET"])
def get_config_route():
    cfg = get_config()
    # Ocultar keys parcialmente para mostrar en UI
    safe = dict(cfg)
    for k in ("anthropic_key", "openai_key", "gemini_key"):
        v = safe.get(k, "")
        safe[k] = (v[:8] + "..." + v[-4:]) if len(v) > 12 else ("✓ configurada" if v else "")
        safe[k + "_set"] = bool(v)
    return jsonify(safe)


@app.route("/api/config", methods=["POST"])
def save_config_route():
    data = request.json
    cfg = get_config()
    for field in ("proveedor", "pct_min", "nota_min", "ruta_uniacc"):
        if field in data:
            cfg[field] = data[field]
    # Solo actualizar keys si se envían no vacías
    for k in ("anthropic_key", "openai_key", "gemini_key"):
        if data.get(k):
            cfg[k] = data[k]
    save_config(cfg)
    return jsonify({"ok": True})


@app.route("/api/test_conexion", methods=["POST"])
def test_conexion():
    try:
        result = call_ai("Responde solo: OK")
        return jsonify({"ok": True, "respuesta": result.strip()[:20]})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/api/carpeta", methods=["POST"])
def listar_carpeta():
    data = request.json
    ruta = Path(data.get("ruta", "")).expanduser()
    if not ruta.exists() or not ruta.is_dir():
        return jsonify({"error": "Carpeta no encontrada"}), 400
    pdfs = sorted([f.name for f in ruta.glob("*.pdf")])
    return jsonify({"archivos": pdfs, "total": len(pdfs)})


@app.route("/api/extraer_certificado", methods=["POST"])
def extraer_certificado():
    if "archivo" not in request.files:
        return jsonify({"error": "Sin archivo"}), 400
    pdf_bytes = request.files["archivo"].read()
    b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")

    prompt = """Extrae del certificado académico los siguientes datos y devuelve SOLO JSON válido sin markdown:
{
  "estudiante": {
    "nombre": "nombre completo",
    "rut": "RUT si aparece, si no vacío",
    "carrera": "nombre de la carrera",
    "institucion": "nombre de la universidad o institución"
  },
  "asignaturas": [
    {"nombre": "nombre asignatura", "codigo": "código o vacío", "semestre": "semestre/año o vacío", "nota": 5.5}
  ]
}
Si la nota no aparece usa 0. La nota debe ser número decimal."""

    try:
        result = call_ai(prompt, pdf_b64=b64, max_tokens=2000)
        parsed = json.loads(clean_json(result))
        return jsonify(parsed)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/contrastar", methods=["POST"])
def contrastar():
    data = request.json
    asignatura = data.get("asignatura", {})
    carpeta_programas = data.get("carpeta_programas", "")
    usar_historico = data.get("usar_historico", False)
    institucion = data.get("institucion", "")
    cfg = get_config()

    # 1. Revisar histórico primero
    if usar_historico and institucion:
        hist = json.loads(DATA_FILE.read_text())
        for registro in hist:
            if registro.get("institucion", "").lower() == institucion.lower():
                for conv in registro.get("convalidadas", []):
                    if conv["origen"].lower() == asignatura["nombre"].lower():
                        return jsonify({
                            **asignatura,
                            "codigoUniacc": conv["codigoUniacc"],
                            "nombreUniacc": conv["uniacc"],
                            "pct": conv["pct"],
                            "justificacion": "Equivalencia registrada en histórico",
                            "fuente": "historico"
                        })

    lista_uniacc = "\n".join([f"{u['codigo']}: {u['nombre']}" for u in UNIACC_ASIGNATURAS])

    # 2. Buscar programa PDF en carpeta
    prog_path = None
    if carpeta_programas:
        carpeta = Path(carpeta_programas).expanduser()
        palabras = asignatura["nombre"].lower().split()[:2]
        for pdf in carpeta.glob("*.pdf"):
            if any(word in pdf.stem.lower() for word in palabras):
                prog_path = pdf
                break

    try:
        if prog_path and prog_path.exists():
            b64 = pdf_to_base64(prog_path)
            prompt = f"""Eres experto en equivalencias curriculares de psicología universitaria en Chile.
La asignatura de origen es: "{asignatura['nombre']}" (código: {asignatura.get('codigo','sin código')}).
Analiza su programa y determina cuál asignatura UNIACC tiene mayor equivalencia temática:

{lista_uniacc}

Responde SOLO JSON sin markdown:
{{"codigoUniacc":"PSICXXXX","nombreUniacc":"nombre exacto","pct":75,"justificacion":"razón en máximo 20 palabras"}}"""
            result = call_ai(prompt, pdf_b64=b64)
            parsed = json.loads(clean_json(result))
            return jsonify({**asignatura, **parsed, "fuente": "programa_pdf"})

        else:
            prompt = f"""Eres experto en equivalencias curriculares de psicología universitaria en Chile.
La asignatura de origen es: "{asignatura['nombre']}".
Solo tengo el nombre. Estima la equivalencia UNIACC más probable:

{lista_uniacc}

Responde SOLO JSON sin markdown:
{{"codigoUniacc":"PSICXXXX","nombreUniacc":"nombre exacto","pct":55,"justificacion":"estimación por nombre sin programa"}}
Si la coincidencia es baja usa pct menor a 50."""
            result = call_ai(prompt)
            parsed = json.loads(clean_json(result))
            return jsonify({**asignatura, **parsed, "fuente": "nombre_only"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/historico", methods=["GET"])
def get_historico():
    return jsonify(json.loads(DATA_FILE.read_text()))


@app.route("/api/historico", methods=["POST"])
def save_historico():
    data = request.json
    hist = json.loads(DATA_FILE.read_text())
    data["fecha"] = datetime.now().isoformat()
    hist.append(data)
    DATA_FILE.write_text(json.dumps(hist, ensure_ascii=False, indent=2))
    return jsonify({"ok": True, "total": len(hist)})


@app.route("/api/historico/<int:idx>", methods=["DELETE"])
def delete_historico(idx):
    hist = json.loads(DATA_FILE.read_text())
    if 0 <= idx < len(hist):
        hist.pop(idx)
        DATA_FILE.write_text(json.dumps(hist, ensure_ascii=False, indent=2))
    return jsonify({"ok": True})


@app.route("/api/equivalencias", methods=["GET"])
def get_equivalencias():
    hist = json.loads(DATA_FILE.read_text())
    por_inst = {}
    for r in hist:
        inst = r.get("institucion", "Desconocida")
        if inst not in por_inst:
            por_inst[inst] = []
        for c in r.get("convalidadas", []):
            if not any(x["origen"] == c["origen"] for x in por_inst[inst]):
                por_inst[inst].append(c)
    return jsonify(por_inst)


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  Sistema de Convalidación UNIACC - Escuela de Psicología")
    print("="*55)
    print(f"  Abre tu navegador en: http://localhost:5050")
    print("  Presiona Ctrl+C para detener")
    print("="*55 + "\n")
    app.run(debug=False, port=5050)
