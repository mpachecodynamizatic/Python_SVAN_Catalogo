from app import app, db, Producto, Atributo

with app.app_context():
    print("=" * 50)
    print("VERIFICACIÓN DE BASE DE DATOS")
    print("=" * 50)
    
    # Contar productos
    total_productos = Producto.query.count()
    print(f"\nTotal de productos: {total_productos}")
    
    # Contar atributos
    total_atributos = Atributo.query.count()
    print(f"Total de atributos: {total_atributos}")
    
    if total_productos > 0:
        print("\n" + "-" * 50)
        print("PRIMEROS 5 PRODUCTOS:")
        print("-" * 50)
        productos = Producto.query.limit(5).all()
        for p in productos:
            atrs = Atributo.query.filter_by(producto_id=p.id).count()
            print(f"ID: {p.id} | SKU: {p.sku} | Marca: {p.marca} | Atributos: {atrs}")
        
        # Verificar si hay atributos huérfanos (sin producto)
        print("\n" + "-" * 50)
        print("VERIFICANDO INTEGRIDAD:")
        print("-" * 50)
        atributos_sample = Atributo.query.limit(5).all()
        for atr in atributos_sample:
            prod = Producto.query.get(atr.producto_id)
            if prod:
                print(f"✓ Atributo ID {atr.id} -> Producto ID {atr.producto_id} ({prod.sku})")
            else:
                print(f"✗ Atributo ID {atr.id} -> Producto ID {atr.producto_id} (NO EXISTE)")
    
    print("\n" + "=" * 50)
