from app import app, db, Catalogo, Categoria, Subcategoria, Ficha, Tarjeta, Producto

with app.app_context():
    print("=" * 60)
    print("VERIFICACIÓN DE DATOS PARA PDF")
    print("=" * 60)
    
    # Catálogos
    catalogos = Catalogo.query.count()
    print(f"\nCatálogos: {catalogos}")
    
    # Categorías
    categorias = Categoria.query.count()
    print(f"Categorías: {categorias}")
    
    # Subcategorías
    subcategorias = Subcategoria.query.count()
    print(f"Subcategorías: {subcategorias}")
    
    # Fichas
    fichas = Ficha.query.count()
    print(f"Fichas: {fichas}")
    
    # Tarjetas
    tarjetas = Tarjeta.query.count()
    print(f"Tarjetas: {tarjetas}")
    
    # Tarjetas con producto
    tarjetas_con_producto = Tarjeta.query.filter(Tarjeta.producto_id.isnot(None)).count()
    print(f"Tarjetas con producto asociado: {tarjetas_con_producto}")
    
    # Productos
    productos = Producto.query.count()
    print(f"Productos: {productos}")
    
    if subcategorias > 0:
        print("\n" + "-" * 60)
        print("SUBCATEGORÍAS DISPONIBLES (primeras 5):")
        print("-" * 60)
        subcat_list = Subcategoria.query.limit(5).all()
        for sc in subcat_list:
            num_fichas = Ficha.query.filter_by(subcategoria_id=sc.id).count()
            print(f"ID: {sc.id} | {sc.categoria.catalogo.codigo} - {sc.categoria.cod_categoria} - {sc.cod_categoria}")
            print(f"  -> {num_fichas} fichas")
            
            if num_fichas > 0:
                # Ver primera ficha
                primera_ficha = Ficha.query.filter_by(subcategoria_id=sc.id).first()
                num_tarjetas = Tarjeta.query.filter_by(ficha_id=primera_ficha.id).count()
                tarjetas_con_prod = Tarjeta.query.filter_by(ficha_id=primera_ficha.id).filter(Tarjeta.producto_id.isnot(None)).count()
                print(f"  -> Primera ficha tiene {num_tarjetas} tarjetas ({tarjetas_con_prod} con producto)")
    
    print("\n" + "=" * 60)
