import os
import re

# Lista de archivos template
templates = [
    'index.html',
    'productos.html',
    'productos_atributos.html',
    'fichas.html',
    'ver_producto.html',
    'atributos.html',
    'configurar.html',
    'categoria.html',
    'importar.html',
    'importar_progreso.html'
]

print("=" * 80)
print("VERIFICACIÓN DE ANCHO DE PANTALLAS")
print("=" * 80)

template_dir = 'templates'
updated = 0
not_updated = 0

for template in templates:
    filepath = os.path.join(template_dir, template)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Buscar si tiene container-fluid con width: 90%
        if 'container-fluid' in content and 'width: 90%' in content:
            print(f"✓ {template:<30} - Actualizado (90% ancho)")
            updated += 1
        elif 'container mt-5' in content:
            print(f"✗ {template:<30} - Pendiente (container limitado)")
            not_updated += 1
        else:
            print(f"? {template:<30} - Diferente estructura")
    else:
        print(f"✗ {template:<30} - No encontrado")

print("\n" + "=" * 80)
print(f"Resumen:")
print(f"  - Templates actualizados: {updated}")
print(f"  - Templates pendientes: {not_updated}")
print(f"  - Total verificados: {len(templates)}")
print("=" * 80)

if not_updated == 0:
    print("\n✓ ¡Todas las pantallas usan el 90% del ancho disponible!")
else:
    print(f"\n⚠ Hay {not_updated} pantallas que aún necesitan actualización")
