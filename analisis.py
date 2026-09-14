"""
Análisis de ventas e inventario + generación de gráficos.

Lee:   data/productos.csv, data/ventas.csv
Genera: img/*.png  y  data/kpis_resumen.csv
Uso:   python src/analisis.py
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# ---------- estilo consistente ----------
AZUL   = "#1F4E79"
CELESTE= "#3C89C9"
VERDE  = "#2E8B7A"
AMBAR  = "#E0A100"
ROJO   = "#C0392B"
GRIS   = "#6B7280"
PALETA = [AZUL, CELESTE, VERDE, AMBAR, "#8E44AD"]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#E5E7EB",
    "grid.linewidth": 0.8,
    "figure.dpi": 120,
})
soles = FuncFormatter(lambda x, _: f"S/ {x:,.0f}")

# ---------- carga y modelo ----------
productos = pd.read_csv("data/productos.csv")
ventas = pd.read_csv("data/ventas.csv", parse_dates=["fecha"])

df = ventas.merge(productos, on="producto_id", how="left")
df["ingreso"] = df["cantidad"] * df["precio_unitario"]
df["costo"]   = df["cantidad"] * df["costo_unitario"]
df["margen"]  = df["ingreso"] - df["costo"]

# ---------- KPIs ----------
ingresos_total = df["ingreso"].sum()
unidades_total = int(df["cantidad"].sum())
margen_total   = df["margen"].sum()
ticket_prom    = df.groupby("venta_id")["ingreso"].sum().mean()
margen_pct     = margen_total / ingresos_total * 100

kpis = pd.DataFrame({
    "indicador": ["Ingresos totales (S/)", "Unidades vendidas",
                  "Margen bruto (S/)", "Margen bruto (%)", "Ticket promedio (S/)"],
    "valor": [round(ingresos_total, 2), unidades_total,
              round(margen_total, 2), round(margen_pct, 1), round(ticket_prom, 2)],
})
kpis.to_csv("data/kpis_resumen.csv", index=False)
print(kpis.to_string(index=False))

def guardar(fig, nombre):
    fig.tight_layout()
    fig.savefig(f"img/{nombre}", bbox_inches="tight")
    plt.close(fig)

# ---------- 1) Ingresos por mes ----------
mens = df.set_index("fecha").resample("MS")["ingreso"].sum()
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.plot(mens.index, mens.values, marker="o", color=AZUL, linewidth=2.4)
ax.fill_between(mens.index, mens.values, color=AZUL, alpha=0.08)
ax.set_title("Ingresos por mes")
ax.yaxis.set_major_formatter(soles)
ax.set_xlabel(""); ax.set_ylabel("")
guardar(fig, "01_ingresos_por_mes.png")

# ---------- 2) Top 10 productos por ingresos ----------
top = df.groupby("nombre")["ingreso"].sum().sort_values(ascending=True).tail(10)
fig, ax = plt.subplots(figsize=(9, 4.6))
ax.barh(top.index, top.values, color=CELESTE)
ax.set_title("Top 10 productos por ingresos")
ax.xaxis.set_major_formatter(soles)
ax.grid(axis="y", visible=False)
guardar(fig, "02_top_productos.png")

# ---------- 3) Ingresos por categoría ----------
cat = df.groupby("categoria")["ingreso"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.bar(cat.index, cat.values, color=PALETA[:len(cat)])
ax.set_title("Ingresos por categoría")
ax.yaxis.set_major_formatter(soles)
ax.grid(axis="x", visible=False)
guardar(fig, "03_ingresos_categoria.png")

# ---------- 4) Ventas por canal ----------
can = df.groupby("canal")["ingreso"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(6.5, 4.2))
ax.bar(can.index, can.values, color=[AZUL, CELESTE, VERDE])
for i, v in enumerate(can.values):
    ax.text(i, v, f" {v/ingresos_total*100:.0f}%", ha="center", va="bottom",
            fontweight="bold", color=GRIS)
ax.set_title("Ingresos por canal de venta")
ax.yaxis.set_major_formatter(soles)
ax.grid(axis="x", visible=False)
guardar(fig, "04_ventas_por_canal.png")

# ---------- 5) Margen bruto por categoría ----------
mcat = df.groupby("categoria")["margen"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.bar(mcat.index, mcat.values, color=VERDE)
ax.set_title("Margen bruto por categoría")
ax.yaxis.set_major_formatter(soles)
ax.grid(axis="x", visible=False)
guardar(fig, "05_margen_categoria.png")

# ---------- 6) Inventario: quiebres de stock ----------
inv = productos.copy()
inv["deficit"] = inv["stock_minimo"] - inv["stock_actual"]
quiebre = inv[inv["stock_actual"] < inv["stock_minimo"]].sort_values("deficit")
fig, ax = plt.subplots(figsize=(9, 4.6))
if len(quiebre):
    ax.barh(quiebre["nombre"], quiebre["stock_actual"], color=ROJO, label="Stock actual")
    ax.barh(quiebre["nombre"], quiebre["stock_minimo"], color="none",
            edgecolor=GRIS, linewidth=1.4, label="Stock mínimo")
    ax.legend(loc="lower right", frameon=False)
ax.set_title(f"Productos bajo stock mínimo (quiebre): {len(quiebre)}")
ax.grid(axis="y", visible=False)
guardar(fig, "06_quiebres_stock.png")

print(f"\nProductos en quiebre de stock: {len(quiebre)} de {len(productos)}")
print("Gráficos guardados en img/")
