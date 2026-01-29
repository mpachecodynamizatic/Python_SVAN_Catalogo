import sqlite3

conn = sqlite3.connect('catalogos_nuevo.db')
cursor = conn.cursor()

# Actualizar productos con URL de imagen basada en SKU
cursor.execute('''
    UPDATE producto 
    SET imagen = 'https://pim.gruposvan.com/multimedia/' || sku || '/800x600_imagen_principal.png' 
    WHERE sku IS NOT NULL AND sku != ''
''')

conn.commit()
print(f'Actualizado {cursor.rowcount} productos con URL de imagen')

# Verificar algunos registros
cursor.execute('SELECT sku, imagen FROM producto LIMIT 5')
print('\nPrimeros 5 productos:')
for row in cursor.fetchall():
    print(f'  SKU: {row[0]}, Imagen: {row[1]}')

conn.close()
