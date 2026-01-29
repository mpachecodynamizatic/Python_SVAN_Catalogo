import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('catalogos_nuevo.db')
cursor = conn.cursor()

print("=" * 80)
print("VERIFICACIÓN DE MODELO DE DATOS - ATRIBUTOS")
print("=" * 80)

# 1. Verificar estructura de la tabla atributo
print("\n1. ESTRUCTURA DE LA TABLA ATRIBUTO:")
cursor.execute("PRAGMA table_info(atributo)")
columns = cursor.fetchall()
print(f"   Columnas en tabla atributo: {len(columns)}")
for col in columns:
    print(f"   - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")

# 2. Contar atributos con y sin SKU
print("\n2. ESTADÍSTICAS DE SKU EN ATRIBUTOS:")
cursor.execute("SELECT COUNT(*) FROM atributo WHERE sku IS NOT NULL")
con_sku = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM atributo WHERE sku IS NULL")
sin_sku = cursor.fetchone()[0]
total_atributos = con_sku + sin_sku

print(f"   Total atributos: {total_atributos}")
print(f"   Con SKU: {con_sku} ({(con_sku/total_atributos*100):.2f}%)")
print(f"   Sin SKU: {sin_sku} ({(sin_sku/total_atributos*100):.2f}%)")

# 3. Verificar coherencia entre atributo.sku y producto.sku
print("\n3. COHERENCIA DE DATOS:")
cursor.execute("""
    SELECT COUNT(*) 
    FROM atributo a
    JOIN producto p ON a.producto_id = p.id
    WHERE a.sku = p.sku
""")
coherentes = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) 
    FROM atributo a
    JOIN producto p ON a.producto_id = p.id
    WHERE a.sku IS NOT NULL AND a.sku != p.sku
""")
incoherentes = cursor.fetchone()[0]

print(f"   Atributos coherentes (sku coincide con producto): {coherentes}")
print(f"   Atributos incoherentes: {incoherentes}")

# 4. Ejemplos de atributos con SKU
print("\n4. EJEMPLOS DE ATRIBUTOS CON SKU:")
cursor.execute("""
    SELECT a.sku, a.atributo, a.valor, a.orden, p.titulo
    FROM atributo a
    JOIN producto p ON a.producto_id = p.id
    WHERE a.sku IS NOT NULL
    LIMIT 10
""")
ejemplos = cursor.fetchall()
for ej in ejemplos:
    print(f"   SKU: {ej[0]}, Atributo: {ej[1]}, Valor: {ej[2][:30]}..., Orden: {ej[3]}")

# 5. Verificar CSV esperado
print("\n5. COLUMNAS ESPERADAS EN CSV (producto_atributos_PIM.csv):")
print("   Columnas actuales necesarias:")
print("   - ProductoId (para relación con productos)")
print("   - SKU (NUEVO - para búsqueda directa y redundancia)")
print("   - Nombre (nombre del atributo)")
print("   - Valor (valor del atributo)")
print("   - OrdenEnGrupo (orden de visualización)")

print("\n6. RESUMEN:")
if sin_sku == 0:
    print("   ✓ Todos los atributos tienen SKU asignado")
else:
    print(f"   ⚠ Hay {sin_sku} atributos sin SKU")

if incoherentes == 0:
    print("   ✓ Todos los SKUs son coherentes con sus productos")
else:
    print(f"   ⚠ Hay {incoherentes} SKUs incoherentes")

print("\n" + "=" * 80)

conn.close()
