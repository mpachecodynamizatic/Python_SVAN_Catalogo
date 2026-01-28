from app import app, Producto, Atributo
import csv

with app.app_context():
    print("=" * 50)
    print("VERIFICANDO VINCULACIÓN PRODUCTOS-ATRIBUTOS")
    print("=" * 50)
    
    # Verificar id_csv en productos
    print("\nPrimeros 5 productos:")
    productos = Producto.query.limit(5).all()
    for p in productos:
        print(f"ID: {p.id:4d} | SKU: {p.sku:15s} | id_csv: {p.id_csv}")
    
    # Verificar ProductoId en CSV de atributos
    print("\nPrimeros 5 registros del CSV de atributos:")
    with open('producto_atributos_PIM.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for i, row in enumerate(reader):
            if i >= 5:
                break
            producto_id_csv = row.get('ProductoId')
            producto_db = Producto.query.filter_by(id_csv=int(producto_id_csv)).first()
            if producto_db:
                print(f"ProductoId CSV: {producto_id_csv} -> Producto DB: ID={producto_db.id}, SKU={producto_db.sku}")
            else:
                print(f"ProductoId CSV: {producto_id_csv} -> NO ENCONTRADO en DB")
    
    # Verificar qué productos tienen atributos
    print("\nProductos con más atributos:")
    from sqlalchemy import func
    resultados = db.session.query(
        Producto.id, Producto.sku, Producto.id_csv, func.count(Atributo.id).label('num_atributos')
    ).join(Atributo, Producto.id == Atributo.producto_id).group_by(Producto.id).order_by(func.count(Atributo.id).desc()).limit(5).all()
    
    for r in resultados:
        print(f"Producto ID: {r.id:4d} | SKU: {r.sku:15s} | id_csv: {r.id_csv:6d} | Atributos: {r.num_atributos}")
