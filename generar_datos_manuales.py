from app import app, db, Producto, DatosManuales
import random
from datetime import datetime, timedelta

# Lista de fabricantes posibles
FABRICANTES = [
    'SVAN', 'ASPES', 'WONDER', 'HYUNDAI', 'NILSON', 'FAGOR',
    'LG', 'Samsung', 'Bosch', 'Siemens', 'Whirlpool', 'Candy'
]

with app.app_context():
    # Obtener todos los productos
    productos = Producto.query.all()
    
    print(f"Generando datos manuales para {len(productos)} productos...")
    
    agregados = 0
    actualizados = 0
    
    for producto in productos:
        if not producto.sku:
            continue
            
        # Verificar si ya existe
        datos = DatosManuales.query.filter_by(sku=producto.sku).first()
        
        if not datos:
            # Generar fecha aleatoria en los últimos 6 meses
            dias_atras = random.randint(1, 180)
            fecha = datetime.now() - timedelta(days=dias_atras)
            fecha_str = fecha.strftime("%d/%m/%Y")
            
            # Generar precio aleatorio entre 50 y 2000 euros
            pvp = round(random.uniform(50, 2000), 2)
            
            # Crear nuevo registro
            datos = DatosManuales(
                sku=producto.sku,
                unidades_vendidas=random.randint(0, 500),
                pvp=pvp,
                inventario=random.randint(0, 100),
                fecha_entrada=fecha_str,
                unidades_entrada=random.randint(10, 200),
                fabricante=random.choice(FABRICANTES)
            )
            db.session.add(datos)
            agregados += 1
        else:
            actualizados += 1
        
        # Commit cada 100 registros
        if (agregados + actualizados) % 100 == 0:
            db.session.commit()
            print(f"Procesados {agregados + actualizados} productos...")
    
    # Commit final
    db.session.commit()
    
    print(f"\n✓ Proceso completado:")
    print(f"  - Nuevos registros: {agregados}")
    print(f"  - Registros existentes: {actualizados}")
    print(f"  - Total: {agregados + actualizados}")
    
    # Mostrar algunos ejemplos
    print("\nEjemplos de datos generados:")
    ejemplos = DatosManuales.query.limit(5).all()
    for ej in ejemplos:
        print(f"  SKU: {ej.sku}")
        print(f"    - Unidades vendidas: {ej.unidades_vendidas}")
        print(f"    - PVP: {ej.pvp}€")
        print(f"    - Inventario: {ej.inventario}")
        print(f"    - Fecha entrada: {ej.fecha_entrada}")
        print(f"    - Unidades entrada: {ej.unidades_entrada}")
        print(f"    - Fabricante: {ej.fabricante}")
        print()
