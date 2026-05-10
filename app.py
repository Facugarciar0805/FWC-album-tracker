import streamlit as st
import streamlit.components.v1 as components
import json
import os

# ── Configuración de la página ──────────────────────────────────────────────
st.set_page_config(
    page_title="Álbum Mundial - Figuritas",
    page_icon="⚽",
    layout="wide",
)

# ── Autenticación ─────────────────────────────────────────────────────────────
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

JSON_PATH = "datos.json"

# ── Carga / guardado de datos ─────────────────────────────────────────────────

def cargar_datos() -> dict:
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    st.error("No se encontró datos.json. Asegurate de que el archivo esté en el proyecto.")
    st.stop()

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

def numeros_faltantes(pais):
    return [str(i + 1) for i, tiene in enumerate(datos[pais]) if not tiene]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
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
tengo   = total_tengo()
posible = total_posible()
pct     = int(tengo / posible * 100) if posible else 0

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

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
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

    t = tengo_pais(pais_sel)
    f = faltan_pais(pais_sel)
    st.markdown(f"**{pais_sel}:** {t}/20 — faltan {f}")
    st.progress(t / 20)

# ── TABLA PRINCIPAL ───────────────────────────────────────────────────────────
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

# Construir filas
filas_html = ""
for pais in paises_filtrados:
    f = faltan_pais(pais)
    t = tengo_pais(pais)

    if f == 0:
        badge_class = "faltan-0"
        faltantes_str = '<span style="color:#4ade80; font-weight:600;">¡Completo! 🎉</span>'
    else:
        if f <= 5:
            badge_class = "faltan-low"
        elif f <= 10:
            badge_class = "faltan-mid"
        else:
            badge_class = "faltan-hi"

        nums = numeros_faltantes(pais)
        faltantes_str = " ".join(
            f'<span class="num-badge">{n}</span>' for n in nums
        )

    filas_html += f"""
    <tr>
      <td class="pais-col">{pais}</td>
      <td class="tengo-col"><strong style="color:#4ade80">{t}</strong> / 20</td>
      <td class="faltan-col"><span class="faltan-badge {badge_class}">{f}</span></td>
      <td class="nums-col">{faltantes_str}</td>
    </tr>
    """

tabla_html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  body {{ margin:0; padding:0; background:transparent; font-family:sans-serif; color:#e2e8f0; }}
  .fig-table {{ border-collapse:collapse; width:100%; font-size:13px; }}
  .fig-table th {{
      background:#1e3a5f; color:white; padding:8px 10px;
      text-align:left; font-weight:600; position:sticky; top:0; z-index:1;
  }}
  .fig-table th.tengo-col, .fig-table th.faltan-col {{ text-align:center; }}
  .fig-table td {{ padding:6px 10px; border-bottom:1px solid #1e293b; vertical-align:middle; }}
  .fig-table tr:nth-child(even) td {{ background:#0f1923; }}
  .fig-table tr:nth-child(odd)  td {{ background:#111827; }}
  .fig-table tr:hover td {{ background:#1a2a3a !important; }}

  .pais-col   {{ min-width:150px; font-weight:600; }}
  .tengo-col  {{ text-align:center; width:80px; }}
  .faltan-col {{ text-align:center; width:70px; }}

  .faltan-badge {{ display:inline-block; padding:2px 8px; border-radius:10px; font-size:12px; font-weight:700; }}
  .faltan-0   {{ background:#14532d; color:#4ade80; }}
  .faltan-low {{ background:#1e3a5f; color:#60a5fa; }}
  .faltan-mid {{ background:#422006; color:#fb923c; }}
  .faltan-hi  {{ background:#450a0a; color:#f87171; }}

  .num-badge {{
      display:inline-block;
      background:#1e293b;
      color:#cbd5e1;
      border:1px solid #334155;
      border-radius:5px;
      padding:1px 6px;
      margin:2px 1px;
      font-size:12px;
      font-weight:600;
  }}
</style>
</head>
<body>
<div style="overflow-x:auto; overflow-y:auto;">
<table class="fig-table">
  <thead>
    <tr>
      <th class="pais-col">País</th>
      <th class="tengo-col">Tengo</th>
      <th class="faltan-col">Faltan</th>
      <th>Números que faltan</th>
    </tr>
  </thead>
  <tbody>
    {filas_html}
  </tbody>
</table>
</div>
</body>
</html>"""

components.html(tabla_html, height=700, scrolling=True)