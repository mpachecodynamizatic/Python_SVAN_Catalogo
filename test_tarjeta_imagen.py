# Script de prueba para verificar la generación de tarjetas como imágenes
from app import app, Producto, Tarjeta, DatosManuales, db, renderizar_tarjeta_como_imagen
import os

with app.app_context():
    # Buscar una tarjeta de ejemplo
    tarjeta = Tarjeta.query.filter(Tarjeta.producto_id.isnot(None)).first()
    
    if tarjeta and tarjeta.producto:
        producto = tarjeta.producto
        print(f"Probando con producto: {producto.sku} - {producto.titulo}")
        
        # Buscar datos manuales
        dm = DatosManuales.query.filter_by(sku=producto.sku).first()
        
        # Generar imagen
        img_buffer = renderizar_tarjeta_como_imagen(producto, dm)
        
        if img_buffer:
            # Guardar imagen para verificar
            with open('test_tarjeta.png', 'wb') as f:
                f.write(img_buffer.getvalue())
            print("✓ Imagen generada exitosamente: test_tarjeta.png")
        else:
            print("✗ Error al generar la imagen")
    else:
        print("No se encontró ninguna tarjeta con producto asociado")
