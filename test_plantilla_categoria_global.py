"""
Script de prueba para verificar que las plantillas genéricas de categoría
son independientes del catálogo.
"""

from app import app, db, PlantillaTarjeta, Categoria, Subcategoria
import json

def test_plantilla_categoria_independiente_catalogo():
    """
    Verifica que las plantillas genéricas de categoría se aplican
    independientemente del catálogo.
    """
    print("\n" + "="*70)
    print("TEST: Plantillas Genéricas de Categoría Independientes del Catálogo")
    print("="*70)
    
    with app.app_context():
        # Obtener todas las categorías
        categorias = Categoria.query.all()
        print(f"\n📋 Total de categorías en la BD: {len(categorias)}")
        
        # Buscar plantillas genéricas de categoría
        plantillas_genericas = PlantillaTarjeta.query.filter_by(
            catalogo_id=None,
            subcategoria_id=None,
            es_generica=True
        ).filter(PlantillaTarjeta.categoria_id.isnot(None)).all()
        
        print(f"\n✨ Plantillas genéricas de categoría encontradas: {len(plantillas_genericas)}")
        
        for plantilla in plantillas_genericas:
            categoria = Categoria.query.get(plantilla.categoria_id)
            print(f"\n  📁 Categoría: {categoria.descripcion} (Código: {categoria.cod_categoria})")
            print(f"     • ID Categoría: {categoria.id}")
            print(f"     • Catálogo ID: {plantilla.catalogo_id} (debe ser None)")
            print(f"     • Campos ficha: {json.loads(plantilla.campos_ficha)}")
            print(f"     • Atributos: {json.loads(plantilla.atributos_seleccionados)}")
            
            # Verificar que catalogo_id es None
            if plantilla.catalogo_id is None:
                print(f"     ✅ Correctamente configurada como independiente del catálogo")
            else:
                print(f"     ❌ ERROR: catalogo_id debería ser None")
            
            # Buscar subcategorías de esta categoría
            subcategorias = Subcategoria.query.filter_by(categoria_id=categoria.id).all()
            print(f"     • Subcategorías que heredan esta plantilla: {len(subcategorias)}")
            
            # Mostrar catálogos donde aparece esta categoría
            catalogos_unicos = set()
            for subcat in subcategorias:
                catalogos_unicos.add(subcat.categoria.catalogo_id)
            
            if catalogos_unicos:
                print(f"     • La categoría aparece en {len(catalogos_unicos)} catálogo(s) diferente(s)")
                print(f"       → Esta plantilla se aplicará en TODOS esos catálogos ✅")
        
        # Verificar que NO existen plantillas genéricas con catalogo_id específico
        plantillas_erroneas = PlantillaTarjeta.query.filter(
            PlantillaTarjeta.catalogo_id.isnot(None),
            PlantillaTarjeta.subcategoria_id.is_(None),
            PlantillaTarjeta.es_generica == True,
            PlantillaTarjeta.categoria_id.isnot(None)
        ).all()
        
        if plantillas_erroneas:
            print(f"\n❌ ADVERTENCIA: Se encontraron {len(plantillas_erroneas)} plantillas genéricas con catálogo específico")
            print("   Estas plantillas deberían tener catalogo_id=None para ser verdaderamente genéricas")
            for p in plantillas_erroneas:
                print(f"   - Plantilla ID {p.id}: categoria_id={p.categoria_id}, catalogo_id={p.catalogo_id}")
        else:
            print(f"\n✅ Verificación OK: No hay plantillas genéricas incorrectas con catalogo_id específico")
        
        print("\n" + "="*70)
        print("Prueba completada")
        print("="*70 + "\n")

if __name__ == '__main__':
    test_plantilla_categoria_independiente_catalogo()
