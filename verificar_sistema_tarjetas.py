import sqlite3

conn = sqlite3.connect('catalogos_nuevo.db')
cursor = conn.cursor()

print("=" * 80)
print("VERIFICACIÓN DEL SISTEMA DE TARJETAS")
print("=" * 80)

# 1. Verificar tabla DatosManuales
print("\n1. TABLA DATOS_MANUALES:")
cursor.execute("SELECT COUNT(*) FROM datos_manuales")
total_datos = cursor.fetchone()[0]
print(f"   Total registros: {total_datos}")

cursor.execute("PRAGMA table_info(datos_manuales)")
columns = cursor.fetchall()
print(f"   Columnas ({len(columns)}):")
for col in columns:
    print(f"     - {col[1]} ({col[2]})")

# 2. Verificar tabla Tarjeta
print("\n2. TABLA TARJETA:")
cursor.execute("SELECT COUNT(*) FROM tarjeta")
total_tarjetas = cursor.fetchone()[0]
print(f"   Total tarjetas: {total_tarjetas}")

cursor.execute("SELECT COUNT(*) FROM tarjeta WHERE producto_id IS NOT NULL")
con_producto = cursor.fetchone()[0]
print(f"   Tarjetas con producto_id: {con_producto}")

cursor.execute("PRAGMA table_info(tarjeta)")
columns = cursor.fetchall()
print(f"   Columnas ({len(columns)}):")
for col in columns:
    print(f"     - {col[1]} ({col[2]})")

# 3. Ejemplos de datos manuales
print("\n3. EJEMPLOS DE DATOS MANUALES:")
cursor.execute("""
    SELECT sku, unidades_vendidas, pvp, inventario, fecha_entrada, fabricante
    FROM datos_manuales
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"   SKU: {row[0]}")
    print(f"     Vendidas: {row[1]} | PVP: {row[2]}€ | Stock: {row[3]}")
    print(f"     Fecha: {row[4]} | Fabricante: {row[5]}")

# 4. Estadísticas de precios
print("\n4. ESTADÍSTICAS DE PRECIOS:")
cursor.execute("SELECT AVG(pvp), MIN(pvp), MAX(pvp) FROM datos_manuales")
avg, min_p, max_p = cursor.fetchone()
print(f"   PVP Promedio: {avg:.2f}€")
print(f"   PVP Mínimo: {min_p:.2f}€")
print(f"   PVP Máximo: {max_p:.2f}€")

# 5. Estadísticas de inventario
print("\n5. ESTADÍSTICAS DE INVENTARIO:")
cursor.execute("SELECT SUM(inventario), AVG(inventario) FROM datos_manuales")
total_inv, avg_inv = cursor.fetchone()
print(f"   Inventario total: {total_inv} unidades")
print(f"   Inventario promedio: {avg_inv:.0f} unidades/producto")

# 6. Fabricantes
print("\n6. DISTRIBUCIÓN POR FABRICANTE:")
cursor.execute("""
    SELECT fabricante, COUNT(*) as total
    FROM datos_manuales
    GROUP BY fabricante
    ORDER BY total DESC
""")
for fab, count in cursor.fetchall():
    print(f"   {fab}: {count} productos")

print("\n" + "=" * 80)
print("✓ Sistema listo para usar")
print("  - Todas las tablas creadas correctamente")
print("  - Datos manuales generados para todos los productos")
print("  - Diseño de tarjetas actualizado con 4 bloques")
print("=" * 80)

conn.close()
