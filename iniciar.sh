#!/bin/bash
# ============================================================
#  Sistema de Convalidación UNIACC — Lanzador
# ============================================================

cd "$(dirname "$0")"

if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 no encontrado. Instálalo desde https://www.python.org"
  exit 1
fi

echo "📦 Instalando dependencias base..."
pip3 install flask anthropic --quiet

# Preguntar proveedor si no hay config
if [ ! -f "data/config.json" ]; then
  echo ""
  echo "¿Qué proveedor de IA usarás?"
  echo "  1) Anthropic Claude (recomendado)"
  echo "  2) OpenAI GPT-4o"
  echo "  3) Google Gemini (tiene capa gratuita)"
  read -p "Elige [1-3]: " PROV
  case $PROV in
    2) pip3 install openai --quiet ;;
    3) pip3 install google-generativeai --quiet ;;
    *) ;;
  esac
fi

echo ""
echo "🚀 Iniciando servidor..."
echo "   Abre tu navegador en: http://localhost:5050"
echo "   (Configura tu API Key en la sección ⚙️ Configuración)"
echo ""

sleep 1.5 && open "http://localhost:5050" 2>/dev/null || \
  xdg-open "http://localhost:5050" 2>/dev/null &

python3 app.py
