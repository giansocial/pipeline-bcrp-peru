INSERT INTO dim_categoria (nombre, descripcion) VALUES
    ('Cambiario', 'Tipo de cambio y mercado cambiario'),
    ('Precios', 'Indices de precios al consumidor e inflacion'),
    ('Monetario', 'Credito, liquidez y agregados monetarios'),
    ('Tasas de interes', 'Tasas activas y pasivas del sistema financiero')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO dim_serie (codigo_bcrp, nombre, categoria, unidad, decimales) VALUES
    ('PN01234PM', 'Tipo de cambio promedio del periodo - venta', 'Cambiario', 'Soles por dolar', 3),
    ('PN38705PM', 'Indice de precios al consumidor de Lima Metropolitana', 'Precios', 'Indice Dic.2021=100', 2),
    ('PN00015MM', 'Credito al sector privado - moneda nacional', 'Monetario', 'Millones de soles', 0),
    ('PN00069MM', 'Credito al sector privado - moneda extranjera', 'Monetario', 'Millones de dolares', 0),
    ('PN00072MM', 'Liquidez del sistema financiero', 'Monetario', 'Millones de soles', 0),
    ('PN07819NM', 'Tasa de interes activa promedio - moneda nacional', 'Tasas de interes', 'Porcentaje', 2),
    ('PN07804NM', 'Tasa de interes pasiva promedio - moneda nacional', 'Tasas de interes', 'Porcentaje', 2)
ON CONFLICT (codigo_bcrp) DO NOTHING;
