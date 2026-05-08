import streamlit as st
import streamlit.components.v1 as components
import json
import csv
import os

# ── Configuración de la página ──────────────────────────────────────────────
st.set_page_config(
    page_title="Álbum Mundial - Figuritas",
    page_icon="⚽",
    layout="wide",
)

password = os.environ.get("APP_PASSWORD", "")

if password:
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        ingresada = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if ingresada == password:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
        st.stop()



CSV_PATH = "figuritas.csv"
JSON_PATH = "datos.json"

# ── Carga / inicialización de datos ─────────────────────────────────────────

def cargar_desde_csv() -> dict:
    """Lee el CSV original y devuelve un dict {pais: [bool x 20]}."""
    datos = {}
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # saltar encabezado
        for fila in reader:
            if not fila or not fila[0].strip():
                continue
            pais = fila[0].strip()
            if pais.upper() == "TOTAL":
                continue
            figuritas = []
            for i in range(1, 21):
                val = fila[i].strip().lower() if i < len(fila) else ""
                figuritas.append(val == "x")
            datos[pais] = figuritas
    return datos


def cargar_datos() -> dict:
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    datos = cargar_desde_csv()
    guardar_datos(datos)
    return datos


def guardar_datos(datos: dict):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


# ── Session state ────────────────────────────────────────────────────────────
if "datos" not in st.session_state:
    st.session_state.datos = cargar_datos()

datos = st.session_state.datos
paises = list(datos.keys())

# ── Helpers ──────────────────────────────────────────────────────────────────
def total_tengo():
    return sum(sum(v) for v in datos.values())

def total_posible():
    return sum(len(v) for v in datos.values())

def faltan_pais(pais):
    return datos[pais].count(False)

def tengo_pais(pais):
    return datos[pais].count(True)

# ── CSS custom ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Tabla */
    .fig-table { border-collapse: collapse; width: 100%; font-size: 13px; }
    .fig-table th {
        background: #1e3a5f;
        color: white;
        padding: 6px 4px;
        text-align: center;
        font-weight: 600;
        position: sticky;
        top: 0;
    }
    .fig-table th.pais-col { text-align: left; padding-left: 10px; min-width: 140px; }
    .fig-table td { padding: 4px 3px; text-align: center; border-bottom: 1px solid #2a2a2a; }
    .fig-table td.pais-col { text-align: left; padding-left: 10px; font-weight: 500; }
    .fig-table tr:hover td { background: #1a2a3a !important; }

    /* Celdas figuritas */
    .tengo  { color: #4ade80; font-size: 15px; }
    .falta  { color: #374151; font-size: 12px; }

    /* Columna Faltan */
    .faltan-badge {
        display: inline-block;
        padding: 1px 7px;
        border-radius: 10px;
        font-size: 12px;
        font-weight: 700;
    }
    .faltan-0  { background:#14532d; color:#4ade80; }
    .faltan-low { background:#1e3a5f; color:#60a5fa; }
    .faltan-mid { background:#422006; color:#fb923c; }
    .faltan-hi  { background:#450a0a; color:#f87171; }

    /* Fila alternada */
    .fig-table tr:nth-child(even) td { background: #0f1923; }
    .fig-table tr:nth-child(odd)  td { background: #111827; }

    /* Header totales */
    .totales-box {
        background: linear-gradient(135deg, #1e3a5f, #0f2840);
        border: 1px solid #2563eb;
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .metric-big { font-size: 2rem; font-weight: 800; color: #60a5fa; }
    .metric-label { font-size: 0.85rem; color: #94a3b8; margin-top: 2px; }

    /* Progress bar custom */
    .prog-container { flex: 1; }
    .prog-bar-bg {
        background: #1e293b;
        border-radius: 8px;
        height: 18px;
        overflow: hidden;
        margin-top: 6px;
    }
    .prog-bar-fill {
        height: 100%;
        border-radius: 8px;
        background: linear-gradient(90deg, #2563eb, #4ade80);
        transition: width 0.4s ease;
    }
    .prog-label { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ───────────────────────────────────────────────────────────────────
tengo = total_tengo()
posible = total_posible()
pct = int(tengo / posible * 100) if posible else 0

st.markdown("## ⚽ Álbum del Mundial — Seguimiento de Figuritas")

col_m1, col_m2, col_prog = st.columns([1, 1, 4])
with col_m1:
    st.metric("Tengo", f"{tengo}")
with col_m2:
    st.metric("Faltan", f"{posible - tengo}")
with col_prog:
    st.markdown(f"""
    <div style="margin-top:8px;">
      <div style="font-size:0.85rem; color:#94a3b8;">Progreso total</div>
      <div class="prog-bar-bg">
        <div class="prog-bar-fill" style="width:{pct}%"></div>
      </div>
      <div class="prog-label">{tengo} de {posible} figuritas ({pct}%)</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── SIDEBAR: agregar figurita ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎴 Registrar figurita")
    pais_sel = st.selectbox("País", paises, key="sb_pais")
    num_sel  = st.number_input("Número", min_value=1, max_value=20, value=1, step=1, key="sb_num")

    idx = int(num_sel) - 1
    estado_actual = datos[pais_sel][idx]

    if estado_actual:
        st.success(f"✅ Ya tenés la {pais_sel} #{num_sel}")
    else:
        st.warning(f"❌ Te falta la {pais_sel} #{num_sel}")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✅ La tengo", use_container_width=True, type="primary"):
            datos[pais_sel][idx] = True
            guardar_datos(datos)
            st.rerun()
    with col_b:
        if st.button("❌ No la tengo", use_container_width=True):
            datos[pais_sel][idx] = False
            guardar_datos(datos)
            st.rerun()

    st.divider()

    # Mini estadísticas del país seleccionado
    t = tengo_pais(pais_sel)
    f = faltan_pais(pais_sel)
    st.markdown(f"**{pais_sel}:** {t}/20 — faltan {f}")
    st.progress(t / 20)

# ── TABLA PRINCIPAL ──────────────────────────────────────────────────────────

# Filtros rápidos encima de la tabla
col_f1, col_f2 = st.columns([2, 1])
with col_f1:
    buscar = st.text_input("🔍 Buscar país", placeholder="ej: Argentina")
with col_f2:
    filtro = st.selectbox("Mostrar", ["Todos", "Con figuritas faltantes", "Completos"])

paises_filtrados = paises
if buscar:
    paises_filtrados = [p for p in paises_filtrados if buscar.lower() in p.lower()]
if filtro == "Con figuritas faltantes":
    paises_filtrados = [p for p in paises_filtrados if faltan_pais(p) > 0]
elif filtro == "Completos":
    paises_filtrados = [p for p in paises_filtrados if faltan_pais(p) == 0]

# Construir HTML de la tabla
numeros_header = "".join(f"<th>{i}</th>" for i in range(1, 21))
html = f"""
<div style="overflow-x:auto; overflow-y:auto; max-height:70vh;">
<table class="fig-table">
  <thead>
    <tr>
      <th class="pais-col">País</th>
      {numeros_header}
      <th>Tengo</th>
      <th>Faltan</th>
    </tr>
  </thead>
  <tbody>
"""

for pais in paises_filtrados:
    figs = datos[pais]
    celdas = ""
    for i, tiene in enumerate(figs):
        if tiene:
            celdas += '<td><span class="tengo">✅</span></td>'
        else:
            celdas += f'<td><span class="falta" title="Falta #{i+1}">·</span></td>'

    f = faltan_pais(pais)
    t = tengo_pais(pais)
    if f == 0:
        badge_class = "faltan-0"
    elif f <= 5:
        badge_class = "faltan-low"
    elif f <= 10:
        badge_class = "faltan-mid"
    else:
        badge_class = "faltan-hi"

    html += f"""
    <tr>
      <td class="pais-col">{pais}</td>
      {celdas}
      <td><strong style="color:#4ade80">{t}</strong></td>
      <td><span class="faltan-badge {badge_class}">{f}</span></td>
    </tr>
    """

html += "</tbody></table></div>"

# Embeber CSS dentro del componente para evitar que Streamlit escape el HTML
tabla_html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  body {{ margin:0; padding:0; background:transparent; font-family:sans-serif; color:#e2e8f0; }}
  .fig-table {{ border-collapse:collapse; width:100%; font-size:13px; }}
  .fig-table th {{
      background:#1e3a5f; color:white; padding:6px 4px;
      text-align:center; font-weight:600; position:sticky; top:0; z-index:1;
  }}
  .fig-table th.pais-col {{ text-align:left; padding-left:10px; min-width:150px; }}
  .fig-table td {{ padding:4px 3px; text-align:center; border-bottom:1px solid #2a2a2a; }}
  .fig-table td.pais-col {{ text-align:left; padding-left:10px; font-weight:500; }}
  .fig-table tr:hover td {{ background:#1a2a3a !important; }}
  .fig-table tr:nth-child(even) td {{ background:#0f1923; }}
  .fig-table tr:nth-child(odd)  td {{ background:#111827; }}
  .tengo  {{ color:#4ade80; font-size:15px; }}
  .falta  {{ color:#374151; font-size:12px; }}
  .faltan-badge {{ display:inline-block; padding:1px 7px; border-radius:10px; font-size:12px; font-weight:700; }}
  .faltan-0   {{ background:#14532d; color:#4ade80; }}
  .faltan-low {{ background:#1e3a5f; color:#60a5fa; }}
  .faltan-mid {{ background:#422006; color:#fb923c; }}
  .faltan-hi  {{ background:#450a0a; color:#f87171; }}
  .wrap {{ overflow-x:auto; overflow-y:auto; }}
</style>
</head>
<body>
<div class="wrap">{html}</div>
</body>
</html>"""

components.html(tabla_html, height=700, scrolling=True)