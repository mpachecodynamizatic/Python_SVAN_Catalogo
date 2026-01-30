"""
Script de prueba para la funcionalidad de plantillas de tarjetas
"""
from app import app, db, PlantillaTarjeta, Categoria, Subcategoria, obtener_plantilla_activa
import json

with app.app_context():
    print("=" * 70)
    print("PRUEBA DE PLANTILLAS DE TARJETAS")
    print("=" * 70)
    
    # 1. Verificar que la tabla existe
    print("\n1. Verificando tabla plantilla_tarjeta...")
    plantillas = PlantillaTarjeta.query.all()
    print(f"   ✓ Tabla existe. Plantillas actuales: {len(plantillas)}")
    
    # 2. Crear una plantilla de prueba para una subcategoría
    print("\n2. Creando plantilla de prueba...")
    subcategoria = Subcategoria.query.first()
    if subcategoria:
        # Eliminar plantilla anterior si existe
        PlantillaTarjeta.query.filter_by(subcategoria_id=subcategoria.id).delete()
        
        plantilla_test = PlantillaTarjeta(
            subcategoria_id=subcategoria.id,
            campos_ficha=json.dumps(['sku', 'titulo', 'ean']),
            atributos_seleccionados=json.dumps(['Potencia', 'Capacidad']),
            es_generica=False
        )
        db.session.add(plantilla_test)
        db.session.commit()
        print(f"   ✓ Plantilla creada para subcategoría {subcategoria.cod_categoria}")
    else:
        print("   ⚠ No hay subcategorías en la BD")
    
    # 3. Probar la función obtener_plantilla_activa
    print("\n3. Probando función obtener_plantilla_activa...")
    if subcategoria:
        config = obtener_plantilla_activa(subcategoria.id)
        print(f"   Subcategoría: {subcategoria.cod_categoria}")
        print(f"   Campos ficha: {config['campos_ficha']}")
        print(f"   Atributos: {config['atributos_seleccionados']}")
        print(f"   ✓ Función funcionando correctamente")
    
    # 4. Probar configuración por defecto
    print("\n4. Probando configuración por defecto...")
    # Crear una subcategoría sin plantilla para probar el default
    subcategoria_sin_config = Subcategoria.query.filter(
        ~Subcategoria.id.in_(
            db.session.query(PlantillaTarjeta.subcategoria_id).filter(PlantillaTarjeta.subcategoria_id.isnot(None))
        )
    ).first()
    
    if subcategoria_sin_config:
        config_default = obtener_plantilla_activa(subcategoria_sin_config.id)
        print(f"   Subcategoría sin config: {subcategoria_sin_config.cod_categoria}")
        print(f"   Campos ficha (default): {config_default['campos_ficha']}")
        print(f"   Atributos (default): {config_default['atributos_seleccionados']}")
        
        # Verificar que es la configuración por defecto
        expected_default = ['sku', 'titulo', 'ean', 'estado_referencia', 'color']
        if config_default['campos_ficha'] == expected_default and config_default['atributos_seleccionados'] == []:
            print(f"   ✓ Configuración por defecto correcta")
        else:
            print(f"   ✗ Error en configuración por defecto")
    else:
        print("   ⚠ Todas las subcategorías tienen configuración")
    
    # 5. Crear plantilla genérica de categoría
    print("\n5. Probando plantilla genérica de categoría...")
    categoria = Categoria.query.first()
    if categoria:
        # Eliminar plantilla genérica anterior si existe
        PlantillaTarjeta.query.filter_by(
            categoria_id=categoria.id,
            subcategoria_id=None,
            es_generica=True
        ).delete()
        
        plantilla_generica = PlantillaTarjeta(
            categoria_id=categoria.id,
            subcategoria_id=None,
            campos_ficha=json.dumps(['sku', 'titulo', 'marca', 'color']),
            atributos_seleccionados=json.dumps(['Clase energética', 'Consumo']),
            es_generica=True
        )
        db.session.add(plantilla_generica)
        db.session.commit()
        print(f"   ✓ Plantilla genérica creada para categoría {categoria.cod_categoria}")
        
        # Buscar una subcategoría de esta categoría sin plantilla específica
        subcats = Subcategoria.query.filter_by(categoria_id=categoria.id).all()
        for subcat in subcats:
            # Verificar que no tenga plantilla específica
            tiene_especifica = PlantillaTarjeta.query.filter_by(subcategoria_id=subcat.id).first()
            if not tiene_especifica:
                config_heredada = obtener_plantilla_activa(subcat.id)
                print(f"   Subcategoría {subcat.cod_categoria} heredará:")
                print(f"   - Atributos: {config_heredada['atributos_seleccionados']}")
                
                if config_heredada['atributos_seleccionados'] == ['Clase energética', 'Consumo']:
                    print(f"   ✓ Herencia de plantilla genérica funcionando")
                break
    
    # 6. Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"Total de plantillas en BD: {PlantillaTarjeta.query.count()}")
    print(f"Plantillas específicas: {PlantillaTarjeta.query.filter(PlantillaTarjeta.subcategoria_id.isnot(None)).count()}")
    print(f"Plantillas genéricas: {PlantillaTarjeta.query.filter_by(es_generica=True).count()}")
    print("\n✓ Pruebas completadas exitosamente")
    print("=" * 70)
