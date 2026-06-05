# Sistema de Convalidación de Estudios
## UNIACC · Escuela de Psicología

---

## Requisitos

- Python 3.9 o superior
- API Key de Anthropic (https://console.anthropic.com)
- Conexión a internet (para la IA)

---

## Instalación

### Mac / Linux

1. Descomprime la carpeta en tu escritorio (o donde prefieras).
2. Abre la Terminal.
3. Navega a la carpeta:
   ```
   cd ~/Desktop/convalidacion_app
   ```
4. Dale permisos al lanzador:
   ```
   chmod +x iniciar.sh
   ```
5. Ejecútalo:
   ```
   ./iniciar.sh
   ```

### Windows

1. Descomprime la carpeta en tu escritorio.
2. Doble clic en `iniciar.bat`.
3. Si aparece advertencia de seguridad, haz clic en "Ejecutar de todas formas".

---

## Primera vez

Al iniciar, el sistema pedirá tu **API Key de Anthropic** si no está configurada.

Puedes configurarla permanentemente como variable de entorno:
- **Mac/Linux:** Agrega `export ANTHROPIC_API_KEY=sk-ant-...` a tu `~/.zshrc` o `~/.bashrc`
- **Windows:** Panel de Control → Variables de entorno → Nueva: `ANTHROPIC_API_KEY`

---

## Uso del sistema

### Etapa 1 — Certificado académico

1. Arrastra o selecciona el PDF del certificado de notas del estudiante.
2. La IA extrae automáticamente:
   - **Nombre, RUT, carrera e institución** del estudiante
   - **Todas las asignaturas** con código, semestre y nota
3. Revisa y corrige si algún dato no es correcto.

### Etapa 2 — Contraste con programas

1. Ingresa la **ruta a la carpeta** donde están los PDFs de los programas del estudiante:
   - Mac: `/Users/tu_usuario/Desktop/programas_alumno`
   - Windows: `C:\Users\tu_usuario\Desktop\programas_alumno`
2. El sistema:
   - Si encuentra el programa en la carpeta → lee el contenido y contrasta temáticamente
   - Si no encuentra el programa → hace estimación por nombre de asignatura
   - Si la institución tiene historial → aplica equivalencias ya registradas automáticamente
3. Se muestran los resultados con porcentaje de coincidencia.
4. Solo pasan asignaturas con **≥70% de coincidencia** y **nota ≥4.5**.

### Acta de Validación

- Se genera en el formato oficial del Acta de Validación UNIACC 2025.
- Usa el botón **Imprimir** para obtener el PDF final (Ctrl+P / Cmd+P).
- Guarda el proceso en el **Histórico**.

### Histórico

- Todos los procesos guardados se almacenan en `data/historico.json`.
- El sistema construye automáticamente una **base de equivalencias por institución**.
- La próxima vez que llegue un estudiante de la misma universidad, las equivalencias se aplican sin necesidad de subir programas.

---

## Estructura de carpetas

```
convalidacion_app/
├── app.py              ← Servidor principal
├── requirements.txt    ← Dependencias Python
├── iniciar.sh          ← Lanzador Mac/Linux
├── iniciar.bat         ← Lanzador Windows
├── templates/
│   └── index.html      ← Interfaz de la app
└── data/
    └── historico.json  ← Base de datos de procesos (se crea automáticamente)
```

---

## Configuración avanzada

En la sección **Configuración** dentro de la app puedes ajustar:
- Carpeta predeterminada de programas UNIACC (base fija de 50 programas)
- Porcentaje mínimo de coincidencia (por defecto 70%)
- Nota mínima de aprobación (por defecto 4.5)

---

## Soporte

App desarrollada para la Dirección de Procesos Académicos y Titulación.
Escuela de Psicología UNIACC · 2025
