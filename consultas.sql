-- ======================================================================
--  Consultas SQL equivalentes al análisis (PostgreSQL / estándar)
--  Tablas: productos(producto_id, nombre, categoria, costo_unitario,
--                     precio_unitario, stock_actual, stock_minimo)
--          ventas(venta_id, fecha, producto_id, cantidad, canal)
-- ======================================================================

-- 1) KPIs generales -----------------------------------------------------
SELECT
    ROUND(SUM(v.cantidad * p.precio_unitario), 2)                        AS ingresos_totales,
    SUM(v.cantidad)                                                      AS unidades_vendidas,
    ROUND(SUM(v.cantidad * (p.precio_unitario - p.costo_unitario)), 2)   AS margen_bruto,
    ROUND(
        SUM(v.cantidad * (p.precio_unitario - p.costo_unitario))
      / SUM(v.cantidad * p.precio_unitario) * 100, 1)                    AS margen_pct
FROM ventas v
JOIN productos p ON p.producto_id = v.producto_id;

-- 2) Ingresos por mes ---------------------------------------------------
SELECT
    DATE_TRUNC('month', v.fecha)                       AS mes,
    ROUND(SUM(v.cantidad * p.precio_unitario), 2)      AS ingresos
FROM ventas v
JOIN productos p ON p.producto_id = v.producto_id
GROUP BY 1
ORDER BY 1;

-- 3) Top 10 productos por ingresos -------------------------------------
SELECT
    p.nombre,
    p.categoria,
    ROUND(SUM(v.cantidad * p.precio_unitario), 2)      AS ingresos
FROM ventas v
JOIN productos p ON p.producto_id = v.producto_id
GROUP BY p.nombre, p.categoria
ORDER BY ingresos DESC
LIMIT 10;

-- 4) Ingresos y margen por categoría -----------------------------------
SELECT
    p.categoria,
    ROUND(SUM(v.cantidad * p.precio_unitario), 2)                       AS ingresos,
    ROUND(SUM(v.cantidad * (p.precio_unitario - p.costo_unitario)), 2)  AS margen
FROM ventas v
JOIN productos p ON p.producto_id = v.producto_id
GROUP BY p.categoria
ORDER BY ingresos DESC;

-- 5) Participación por canal de venta ----------------------------------
SELECT
    v.canal,
    ROUND(SUM(v.cantidad * p.precio_unitario), 2)                       AS ingresos,
    ROUND(100.0 * SUM(v.cantidad * p.precio_unitario)
                / SUM(SUM(v.cantidad * p.precio_unitario)) OVER (), 1)  AS participacion_pct
FROM ventas v
JOIN productos p ON p.producto_id = v.producto_id
GROUP BY v.canal
ORDER BY ingresos DESC;

-- 6) Productos en quiebre de stock (stock actual < stock mínimo) -------
SELECT
    nombre,
    categoria,
    stock_actual,
    stock_minimo,
    (stock_minimo - stock_actual) AS deficit
FROM productos
WHERE stock_actual < stock_minimo
ORDER BY deficit DESC;
