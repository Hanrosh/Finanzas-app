import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Sistema Financiero Inteligente", layout="wide", page_icon="💰")

# --- 1. BARRA LATERAL (CONFIGURACIÓN) ---
st.sidebar.header("🛠️ Configuración")
fecha_inicio = st.sidebar.date_input("Fecha Inicio", date.today())
capital_inicial = st.sidebar.number_input("Capital Inicial ($)", value=0, step=1000)

st.sidebar.markdown("---")
st.sidebar.subheader("📝 Tus Datos")

# Datos de ejemplo (para que no inicie vacío)
data_ingresos = pd.DataFrame([
    {"Concepto": "Nómina", "Monto": 15000, "Frecuencia": "Quincenal", "Dia": 15},
    {"Concepto": "Ventas Extra", "Monto": 2000, "Frecuencia": "Mensual", "Dia": 5}
])

data_gastos = pd.DataFrame([
    {"Concepto": "Renta", "Monto": 4500, "Frecuencia": "Mensual", "Dia": 1},
    {"Concepto": "Supermercado", "Monto": 2500, "Frecuencia": "Semanal", "Dia": 0},
    {"Concepto": "Netflix", "Monto": 200, "Frecuencia": "Mensual", "Dia": 10}
])

data_deudas = pd.DataFrame([
    {"Concepto": "Tarjeta Crédito", "Saldo_Total": 15000, "Pago_Mensual": 3000, "Dia_Pago": 5},
    {"Concepto": "Préstamo Auto", "Saldo_Total": 80000, "Pago_Mensual": 5000, "Dia_Pago": 20}
])

# Tablas editables
st.sidebar.write("Ingresos")
df_ingresos = st.sidebar.data_editor(data_ingresos, num_rows="dynamic")
st.sidebar.write("Gastos")
df_gastos = st.sidebar.data_editor(data_gastos, num_rows="dynamic")
st.sidebar.write("Deudas (Debt Terminator 🤖)")
df_deudas = st.sidebar.data_editor(data_deudas, num_rows="dynamic")

# --- 2. EL MOTOR (LÓGICA MATEMÁTICA) ---
def generar_proyeccion(fecha_ini, saldo_ini, df_ing, df_gas, df_deu):
    fechas = [fecha_ini + timedelta(weeks=i) for i in range(53)]
    plan = []
    saldo_actual = saldo_ini
    
    # Copia de saldos para ir restando (Lógica Smart)
    saldos_deudas = df_deu["Saldo_Total"].tolist() if not df_deu.empty else []
    
    for i in range(52):
        semana_inicio = fechas[i]
        semana_fin = fechas[i+1] - timedelta(days=1)
        
        ingreso_sem = 0
        gasto_sem = 0
        deuda_sem = 0
        
        # Calcular Ingresos
        for _, row in df_ing.iterrows():
            toca = False
            try:
                if row["Frecuencia"] == "Semanal": toca = True
                elif row["Frecuencia"] == "Quincenal":
                    if (semana_inicio.day <= 15 and semana_fin.day >= 15) or (semana_inicio.month != semana_fin.month): toca = True
                elif row["Frecuencia"] == "Mensual":
                    fecha_pago = date(semana_inicio.year, semana_inicio.month, int(row["Dia"]))
                    if semana_inicio <= fecha_pago <= semana_fin: toca = True
            except: pass
            if toca: ingreso_sem += row["Monto"]
            
        # Calcular Gastos
        for _, row in df_gas.iterrows():
            toca = False
            try:
                if row["Frecuencia"] == "Semanal": toca = True
                elif row["Frecuencia"] == "Quincenal":
                    if (semana_inicio.day <= 15 and semana_fin.day >= 15) or (semana_inicio.month != semana_fin.month): toca = True
                elif row["Frecuencia"] == "Mensual":
                    fecha_pago = date(semana_inicio.year, semana_inicio.month, int(row["Dia"]))
                    if semana_inicio <= fecha_pago <= semana_fin: toca = True
            except: pass
            if toca: gasto_sem += row["Monto"]
            
        # Calcular Deudas (LÓGICA INTELIGENTE)
        for idx, row in df_deu.iterrows():
            if idx < len(saldos_deudas) and saldos_deudas[idx] > 0: # Solo si hay saldo vivo
                toca = False
                try:
                    fecha_pago = date(semana_inicio.year, semana_inicio.month, int(row["Dia_Pago"]))
                    if semana_inicio <= fecha_pago <= semana_fin: toca = True
                except: pass
                
                if toca:
                    pago = row["Pago_Mensual"]
                    if saldos_deudas[idx] < pago: pago = saldos_deudas[idx]
                    deuda_sem += pago
                    saldos_deudas[idx] -= pago

        flujo = ingreso_sem - gasto_sem - deuda_sem
        saldo_actual += flujo
        
        plan.append({
            "Semana": f"S{i+1}",
            "Fecha": semana_inicio.strftime("%d-%b"),
            "Ingresos": ingreso_sem,
            "Gastos": gasto_sem,
            "Deudas": deuda_sem,
            "Flujo Neto": flujo,
            "Saldo Acumulado": saldo_actual
        })
        
    return pd.DataFrame(plan)

# Ejecutar motor
df_plan = generar_proyeccion(fecha_inicio, capital_inicial, df_ingresos, df_gastos, df_deudas)

# --- 3. DASHBOARD ---
st.title("📊 Tablero Financiero 360°")

saldo_hoy = df_plan.iloc[0]["Saldo Acumulado"]
minimo_anual = df_plan["Saldo Acumulado"].min()
total_deuda_orig = df_deudas["Saldo_Total"].sum() if not df_deudas.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Saldo Proyectado (Semana 1)", f"${saldo_hoy:,.0f}")
col2.metric("Punto Más Bajo del Año", f"${minimo_anual:,.0f}", delta_color="off")
col3.metric("Deuda Total Inicial", f"${total_deuda_orig:,.0f}", delta_color="inverse")
col4.metric("Capital Inicial", f"${capital_inicial:,.0f}")

if minimo_anual < 0:
    st.error(f"🚨 ALERTA: Tu saldo será negativo (${minimo_anual:,.0f}) en algún momento. ¡Revisa tus gastos!")
else:
    st.success("✅ PLAN SALUDABLE: Tu saldo se mantiene positivo todo el año.")

c1, c2 = st.columns([2, 1])
with c1:
    st.subheader("📈 La Línea de la Vida")
    fig_line = px.line(df_plan, x="Semana", y="Saldo Acumulado", markers=True, title="Evolución de tu Dinero")
    fig_line.add_hline(y=0, line_dash="dash", line_color="red")
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("🍰 ¿A dónde va el dinero?")
    total_g = df_plan["Gastos"].sum()
    total_d = df_plan["Deudas"].sum()
    fig_pie = px.pie(names=["Gastos", "Deudas"], values=[total_g, total_d], color_discrete_sequence=["#f1c40f", "#e74c3c"])
    st.plotly_chart(fig_pie, use_container_width=True)

with st.expander("📅 Ver Master Plan Detallado (Tabla)"):
    st.dataframe(df_plan, use_container_width=True)