from app import app, db, Producto
import os
import csv

def importar_productos_test(filepath):
    marca_map = {
        'ASPES': 'AS', 'Aspes': 'AS',
        'WONDER': 'WD', 'Wonder': 'WD',
        'SVAN': 'SV', 'Svan': 'SV',
        'HYUNDAI': 'HY', 'Hyundai': 'HY',
        'NILSON': 'NL', 'Nilson': 'NL',
        'FAGOR': 'FR', 'Fagor': 'FR'
    }
    
    importados = 0
    omitidos = 0
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:  # utf-8-sig elimina el BOM
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            marca_original = row.get('Marca', '').strip()
            if marca_original in marca_map:
                try:
                    id_csv = int(row.get('id', 0))
                    if Producto.query.filter_by(id_csv=id_csv).first():
                        omitidos += 1
                        continue
                        
                    producto = Producto(
                        id_csv=id_csv,
                        marca=marca_map[marca_original],
                        producto_id=row.get('ProductoId', '').strip(),
                        sku=row.get('Sku', '').strip(),
                        ean=row.get('Ean', '').strip(),
                        descripcion=row.get('Descripcion', '').strip(),
                        titulo=row.get('Titulo', '').strip(),
                        descripcion_larga=row.get('DescripcionLarga', '').strip(),
                        estado_referencia=row.get('EstadoReferencia', '').strip(),
                        clasificacion=row.get('Clasificacion', '').strip(),
                        color=row.get('Color', '').strip(),
                        dimensiones=row.get('Dimensiones', '').strip()
                    )
                    db.session.add(producto)
                    importados += 1
                except Exception as e:
                    print(f"Error importando producto: {e}")
                    continue
            else:
                omitidos += 1
    
    db.session.commit()
    return importados, omitidos

with app.app_context():
    # Verificar productos antes
    antes = Producto.query.count()
    print(f'Productos antes: {antes}')
    
    # Importar
    filepath = 'producto_general_PIM.csv'
    if os.path.exists(filepath):
        try:
            importados, omitidos = importar_productos_test(filepath)
            despues = Producto.query.count()
            print(f'Productos despues: {despues}')
            print(f'Importados: {importados}')
            print(f'Omitidos: {omitidos} (duplicados o marcas no incluidas)')
            
            # Mostrar algunos productos
            productos = Producto.query.limit(5).all()
            print('\nPrimeros 5 productos:')
            for p in productos:
                titulo_corto = p.titulo[:50] if p.titulo else "N/A"
                print(f'  ID: {p.id}, CSV_ID: {p.id_csv}, Marca: {p.marca}, SKU: {p.sku}')
                print(f'    Titulo: {titulo_corto}...')
        except Exception as e:
            print(f'Error: {e}')
            import traceback
            traceback.print_exc()
    else:
        print('Archivo CSV no encontrado')
