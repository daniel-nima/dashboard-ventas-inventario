"""
Genera un dataset sintético pero realista de ventas e inventario
para un pequeño negocio de abarrotes en Lima.

Salida:
  data/productos.csv  -> catálogo con precio, costo, stock actual y mínimo
  data/ventas.csv     -> transacciones diarias de ~12 meses

Uso:
  python src/generar_datos.py
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)  # reproducible

# ----------------------------------------------------------------------
# 1) Catálogo de productos
# ----------------------------------------------------------------------
CATALOGO = {
    "Abarrotes": ["Arroz 1kg", "Azúcar 1kg", "Aceite 1L", "Fideos 500g",
                  "Lentejas 500g", "Atún lata", "Sal 1kg", "Harina 1kg"],
    "Bebidas":   ["Gaseosa 1.5L", "Agua 625ml", "Jugo 1L", "Cerveza 630ml",
                  "Energizante 300ml", "Té helado 500ml"],
    "Lácteos":   ["Leche 1L", "Yogurt 1L", "Queso 500g", "Mantequilla 200g",
                  "Huevos x12"],
    "Limpieza":  ["Detergente 1kg", "Lejía 1L", "Jabón barra", "Papel higiénico x4",
                  "Lavavajilla 500ml"],
    "Snacks":    ["Galletas pack", "Papas fritas", "Chocolate barra",
                  "Chicles", "Maní 100g", "Caramelos bolsa"],
}

rows = []
pid = 1
for categoria, productos in CATALOGO.items():
    for nombre in productos:
        costo = round(float(RNG.uniform(1.5, 22.0)), 2)
        margen = float(RNG.uniform(0.18, 0.45))          # 18% a 45%
        precio = round(costo * (1 + margen), 2)
        stock_min = int(RNG.integers(10, 40))
        stock_actual = int(RNG.integers(0, 120))
        rows.append({
            "producto_id": pid,
            "nombre": nombre,
            "categoria": categoria,
            "costo_unitario": costo,
            "precio_unitario": precio,
            "stock_actual": stock_actual,
            "stock_minimo": stock_min,
        })
        pid += 1

productos = pd.DataFrame(rows)
productos.to_csv("data/productos.csv", index=False)

# ----------------------------------------------------------------------
# 2) Transacciones de ventas (~12 meses)
# ----------------------------------------------------------------------
fechas = pd.date_range("2025-09-01", "2026-08-31", freq="D")
canales = ["Tienda", "Online", "Mayorista"]
canal_p = [0.62, 0.20, 0.18]

# popularidad por producto (algunos se venden mucho más que otros)
popularidad = RNG.uniform(0.4, 3.0, size=len(productos))
popularidad = popularidad / popularidad.sum()

ventas = []
vid = 1
for fecha in fechas:
    # estacionalidad: más ventas en diciembre y fines de semana
    factor_mes = 1.35 if fecha.month == 12 else (1.15 if fecha.month in (1, 7) else 1.0)
    factor_dia = 1.25 if fecha.weekday() >= 5 else 1.0
    n_tx = int(RNG.poisson(22 * factor_mes * factor_dia))
    prods = RNG.choice(productos["producto_id"].values, size=n_tx, p=popularidad)
    for producto_id in prods:
        cantidad = int(RNG.integers(1, 8))
        canal = RNG.choice(canales, p=canal_p)
        ventas.append({
            "venta_id": vid,
            "fecha": fecha.date().isoformat(),
            "producto_id": int(producto_id),
            "cantidad": cantidad,
            "canal": canal,
        })
        vid += 1

ventas = pd.DataFrame(ventas)
ventas.to_csv("data/ventas.csv", index=False)

print(f"productos.csv -> {len(productos)} filas")
print(f"ventas.csv    -> {len(ventas)} filas ({fechas.min().date()} a {fechas.max().date()})")
