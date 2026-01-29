from app import app, db, Tarjeta, Producto

with app.app_context():
    print("Actualizando tarjetas existentes con producto_id...")
    
    tarjetas = Tarjeta.query.all()
    actualizadas = 0
    
    for tarjeta in tarjetas:
        if tarjeta.producto_id is None and tarjeta.nombre:
            # Intentar buscar el producto por nombre o SKU
            # El nombre generalmente contiene el título o SKU
            partes = tarjeta.nombre.split()
            if partes:
                # Buscar por SKU (primera palabra suele ser el SKU)
                producto = Producto.query.filter(
                    db.or_(
                        Producto.sku == partes[0],
                        Producto.titulo.like(f'%{tarjeta.nombre}%')
                    )
                ).first()
                
                if producto:
                    tarjeta.producto_id = producto.id
                    tarjeta.imagen = producto.imagen or tarjeta.imagen
                    actualizadas += 1
                    print(f"  Actualizada tarjeta {tarjeta.id}: {tarjeta.nombre} -> Producto ID {producto.id}")
    
    db.session.commit()
    
    print(f"\n✓ Proceso completado:")
    print(f"  Total tarjetas: {len(tarjetas)}")
    print(f"  Actualizadas: {actualizadas}")
    print(f"  Sin actualizar: {len(tarjetas) - actualizadas}")
