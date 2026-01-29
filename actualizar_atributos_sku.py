import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('catalogos_nuevo.db')
cursor = conn.cursor()

# Actualizar los SKUs de los atributos desde la tabla producto
cursor.execute("""
    UPDATE atributo 
    SET sku = (
        SELECT producto.sku 
        FROM producto 
        WHERE producto.id = atributo.producto_id
    )
    WHERE atributo.producto_id IS NOT NULL
""")

conn.commit()

# Verificar cuántos se actualizaron
cursor.execute("SELECT COUNT(*) FROM atributo WHERE sku IS NOT NULL")
count = cursor.fetchone()[0]
print(f"Actualizados {count} atributos con SKU")

# Mostrar algunos ejemplos
cursor.execute("SELECT sku, atributo, valor FROM atributo WHERE sku IS NOT NULL LIMIT 5")
print("\nPrimeros 5 atributos con SKU:")
for row in cursor.fetchall():
    print(f"  SKU: {row[0]}, Atributo: {row[1]}, Valor: {row[2]}")

conn.close()
