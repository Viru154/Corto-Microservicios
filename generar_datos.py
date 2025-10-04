"""
Generador de Datos Masivos - Sistema de Cines Distribuido
Ajustado al schema real de la base de datos
Genera datos para Data Warehouse con volumen realista
"""

import random
from datetime import datetime, timedelta, time
from faker import Faker
import os

# Configuración
Faker.seed(42)
random.seed(42)

# ============================================
# CONFIGURACIÓN
# ============================================
CONFIG = {
    'AÑOS_HISTORICO': 3,
    'NUM_PELICULAS': 80,
    'NUM_CLIENTES_GT': 4000,
    'NUM_CLIENTES_SV': 3000,
    'FUNCIONES_POR_DIA_GT': 50,  # ~36,500 funciones en 3 años
    'FUNCIONES_POR_DIA_SV': 40,  # ~29,200 funciones en 3 años
    'TASA_OCUPACION_PROMEDIO': 0.50,
    'BATCH_SIZE': 500  # Registros por INSERT
}

# ============================================
# DATOS MAESTROS
# ============================================
GENEROS = ['Acción', 'Comedia', 'Drama', 'Terror', 'Ciencia Ficción', 'Animación', 
           'Thriller', 'Romance', 'Aventura', 'Suspenso']

CLASIFICACIONES = ['G', 'PG', 'PG-13', 'R']

DIRECTORES = [
    'Christopher Nolan', 'Greta Gerwig', 'Denis Villeneuve', 
    'James Cameron', 'Steven Spielberg', 'Martin Scorsese',
    'Quentin Tarantino', 'Ridley Scott'
]

NOMBRES_GT = ['Juan', 'María', 'Carlos', 'Ana', 'José', 'Carmen', 'Luis', 'Sofía']
APELLIDOS_GT = ['García', 'Rodríguez', 'López', 'Martínez', 'González', 'Pérez']

NOMBRES_SV = ['Roberto', 'Claudia', 'Fernando', 'Patricia', 'Ricardo', 'Gabriela']
APELLIDOS_SV = ['Flores', 'Torres', 'Morales', 'Castillo', 'Rivas', 'Méndez']

# IDs de sucursales creadas previamente
SUCURSALES_GT = [1, 2, 3, 4, 5]
SUCURSALES_SV = [1, 2, 3, 4]

# Estructura de salas por sucursal (capacidades típicas)
SALAS_POR_SUCURSAL = {
    'capacidades': [80, 150, 150, 150, 150, 150, 200],
    'tipos': ['VIP', 'STANDARD', 'STANDARD', 'STANDARD', 'STANDARD', 'STANDARD', 'IMAX']
}

# ============================================
# GENERADOR DE PELÍCULAS
# ============================================
def generar_peliculas(num, pais='GT'):
    fake = Faker('es_ES')
    peliculas = []
    
    precios_gt = [35.00, 40.00, 45.00, 50.00]
    precios_sv = [4.50, 5.00, 5.50, 6.00]
    precios = precios_gt if pais == 'GT' else precios_sv
    
    for i in range(num):
        titulo = fake.catch_phrase()[:50]
        fecha_estreno = datetime.now() - timedelta(days=random.randint(30, 730))
        
        pelicula = {
            'titulo': titulo,
            'genero': random.choice(GENEROS),
            'duracion_minutos': random.randint(90, 180),
            'clasificacion': random.choice(CLASIFICACIONES),
            'director': random.choice(DIRECTORES),
            'fecha_estreno': fecha_estreno.strftime('%Y-%m-%d'),
            'precio_base': random.choice(precios),
            'es_3d': random.choice([True, False]),
            'activa': True,
            'pais': pais
        }
        peliculas.append(pelicula)
    
    return peliculas

# ============================================
# GENERADOR DE CLIENTES
# ============================================
def generar_clientes(num, pais='GT'):
    clientes = []
    
    nombres = NOMBRES_GT if pais == 'GT' else NOMBRES_SV
    apellidos = APELLIDOS_GT if pais == 'GT' else APELLIDOS_SV
    
    tipos = ['REGULAR'] * 80 + ['VIP'] * 15 + ['CORPORATIVO'] * 5
    
    for i in range(num):
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        fecha_nac = datetime.now() - timedelta(days=random.randint(6570, 25550))
        
        cliente = {
            'nombre': nombre,
            'apellido': apellido,
            'email': f"{nombre.lower()}.{apellido.lower()}{i+1}@email.com",
            'telefono': f"{random.randint(5500, 7800)}-{random.randint(1000, 9999)}",
            'fecha_nacimiento': fecha_nac.strftime('%Y-%m-%d'),
            'tipo_cliente': random.choice(tipos),
            'pais': pais
        }
        clientes.append(cliente)
    
    return clientes

# ============================================
# GENERADOR DE FUNCIONES Y VENTAS
# ============================================
def generar_funciones_ventas(num_peliculas, num_clientes, sucursales, pais='GT'):
    funciones = []
    ventas = []
    
    funciones_por_dia = CONFIG['FUNCIONES_POR_DIA_GT'] if pais == 'GT' else CONFIG['FUNCIONES_POR_DIA_SV']
    
    fecha_inicio = datetime.now() - timedelta(days=365 * CONFIG['AÑOS_HISTORICO'])
    fecha_fin = datetime.now()
    dias_totales = (fecha_fin - fecha_inicio).days
    
    horarios = [time(14, 0), time(16, 30), time(19, 0), time(21, 30)]
    
    print(f"\nGenerando funciones y ventas para {pais}...")
    print(f"Período: {dias_totales} días")
    
    funcion_counter = 0
    venta_counter = 0
    
    for dia in range(dias_totales):
        fecha_actual = fecha_inicio + timedelta(days=dia)
        
        if dia % 100 == 0:
            print(f"  Día {dia}/{dias_totales} - Funciones: {funcion_counter}, Ventas: {venta_counter}")
        
        es_fin_semana = fecha_actual.weekday() >= 5
        num_funciones = int(funciones_por_dia * (1.3 if es_fin_semana else 1.0))
        
        for _ in range(num_funciones):
            # Seleccionar película, sucursal y sala aleatorias
            pelicula_id = random.randint(1, num_peliculas)
            sucursal_id = random.choice(sucursales)
            
            # Generar sala_id basado en estructura típica
            # Cada sucursal tiene entre 5-8 salas
            num_salas_sucursal = random.randint(5, 8)
            sala_local = random.randint(1, num_salas_sucursal)
            
            # Calcular sala_id global (asumiendo estructura secuencial)
            # Esto es una aproximación - en realidad deberías consultar la BD
            sala_id = (sucursal_id - 1) * 8 + sala_local
            
            hora = random.choice(horarios)
            
            # Tipo de sala según número
            if sala_local == 1:
                tipo_sala = 'IMAX'
                capacidad = 200
            elif sala_local == num_salas_sucursal:
                tipo_sala = 'VIP'
                capacidad = 80
            else:
                tipo_sala = 'STANDARD'
                capacidad = 150
            
            # Precio base (obtener de peliculas[pelicula_id])
            # Simplificación: usar precio promedio
            precio_base = 45.00 if pais == 'GT' else 5.50
            
            multiplicador = {'IMAX': 1.5, 'VIP': 1.3, 'STANDARD': 1.0}[tipo_sala]
            precio_boleto = round(precio_base * multiplicador, 2)
            
            # Calcular ocupación
            ocupacion = CONFIG['TASA_OCUPACION_PROMEDIO']
            if es_fin_semana:
                ocupacion *= 1.3
            if hora >= time(19, 0):
                ocupacion *= 1.2
            
            ocupacion = min(ocupacion, 0.95)
            ocupacion_real = ocupacion * random.uniform(0.7, 1.2)
            ocupacion_real = max(0.05, min(0.98, ocupacion_real))
            
            boletos_vendidos = int(capacidad * ocupacion_real)
            
            # Crear función
            funcion = {
                'pelicula_id': pelicula_id,
                'sala_id': sala_id,
                'sucursal_id': sucursal_id,
                'fecha_funcion': fecha_actual.strftime('%Y-%m-%d'),
                'hora_funcion': hora.strftime('%H:%M'),
                'precio_boleto': precio_boleto,
                'boletos_disponibles': capacidad - boletos_vendidos,
                'boletos_vendidos': boletos_vendidos,
                'estado': 'FINALIZADA' if fecha_actual < datetime.now() - timedelta(days=1) else 'PROGRAMADA'
            }
            funciones.append(funcion)
            funcion_counter += 1
            
            # Generar ventas para esta función
            boletos_restantes = boletos_vendidos
            while boletos_restantes > 0:
                cantidad = min(random.choice([1, 2, 2, 3, 4]), boletos_restantes)
                cliente_id = random.randint(1, num_clientes) if random.random() > 0.2 else None
                
                venta = {
                    'funcion_id': funcion_counter,
                    'cliente_id': cliente_id if cliente_id else 'NULL',
                    'cantidad_boletos': cantidad,
                    'precio_unitario': precio_boleto,
                    'total': round(precio_boleto * cantidad, 2),
                    'metodo_pago': random.choice(['TARJETA', 'TARJETA', 'EFECTIVO', 'TRANSFERENCIA']),
                    'tipo_venta': random.choice(['ONLINE', 'ONLINE', 'TAQUILLA']),
                    'fecha_venta': (fecha_actual - timedelta(hours=random.randint(0, 48))).strftime('%Y-%m-%d %H:%M:%S'),
                    'pais': pais
                }
                ventas.append(venta)
                venta_counter += 1
                boletos_restantes -= cantidad
    
    print(f"✅ Total generado: {len(funciones):,} funciones y {len(ventas):,} ventas")
    return funciones, ventas

# ============================================
# GENERADOR SQL
# ============================================
def generar_sql_batch(tabla, registros, batch_size=500):
    """Genera INSERTs en lotes para mejor performance"""
    if not registros:
        return ""
    
    columnas = list(registros[0].keys())
    sql_parts = [f"-- Tabla: {tabla}\n-- Total registros: {len(registros):,}\n"]
    
    for i in range(0, len(registros), batch_size):
        batch = registros[i:i + batch_size]
        
        valores = []
        for reg in batch:
            vals = []
            for col in columnas:
                val = reg[col]
                if val == 'NULL' or val is None:
                    vals.append('NULL')
                elif isinstance(val, bool):
                    vals.append('TRUE' if val else 'FALSE')
                elif isinstance(val, (int, float)):
                    vals.append(str(val))
                else:
                    # Escapar comillas
                    val_esc = str(val).replace("'", "''")
                    vals.append(f"'{val_esc}'")
            valores.append(f"({', '.join(vals)})")
        
        sql_parts.append(f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES\n")
        sql_parts.append(',\n'.join(valores))
        sql_parts.append(';\n\n')
    
    return ''.join(sql_parts)

# ============================================
# MAIN
# ============================================
def generar_datos_pais(pais='GT'):
    print(f"\n{'='*70}")
    print(f"GENERANDO DATOS PARA {pais}")
    print(f"{'='*70}")
    
    sucursales = SUCURSALES_GT if pais == 'GT' else SUCURSALES_SV
    num_clientes = CONFIG['NUM_CLIENTES_GT'] if pais == 'GT' else CONFIG['NUM_CLIENTES_SV']
    
    # 1. Películas
    print("\n[1/4] Generando películas...")
    peliculas = generar_peliculas(CONFIG['NUM_PELICULAS'], pais)
    
    # 2. Clientes
    print(f"[2/4] Generando {num_clientes:,} clientes...")
    clientes = generar_clientes(num_clientes, pais)
    
    # 3. Funciones y Ventas
    print(f"[3/4] Generando funciones y ventas (esto tomará tiempo)...")
    funciones, ventas = generar_funciones_ventas(
        CONFIG['NUM_PELICULAS'], 
        num_clientes, 
        sucursales, 
        pais
    )
    
    # 4. Guardar SQL
    print(f"[4/4] Generando archivos SQL...")
    
    directorio = f"databases/{pais.lower()}/"
    os.makedirs(directorio, exist_ok=True)
    
    # Películas
    with open(f"{directorio}03_peliculas.sql", 'w', encoding='utf-8') as f:
        f.write(generar_sql_batch('peliculas', peliculas, CONFIG['BATCH_SIZE']))
    
    # Clientes
    with open(f"{directorio}04_clientes.sql", 'w', encoding='utf-8') as f:
        f.write(generar_sql_batch('clientes', clientes, CONFIG['BATCH_SIZE']))
    
    # Funciones
    with open(f"{directorio}05_funciones.sql", 'w', encoding='utf-8') as f:
        f.write(generar_sql_batch('funciones', funciones, CONFIG['BATCH_SIZE']))
    
    # Ventas (archivo más grande, usar batches más pequeños)
    with open(f"{directorio}06_ventas.sql", 'w', encoding='utf-8') as f:
        f.write(generar_sql_batch('ventas', ventas, 300))
    
    print(f"\n✅ Archivos generados en: {directorio}")
    print(f"   📄 03_peliculas.sql: {len(peliculas):,} registros")
    print(f"   📄 04_clientes.sql: {len(clientes):,} registros")
    print(f"   📄 05_funciones.sql: {len(funciones):,} registros")
    print(f"   📄 06_ventas.sql: {len(ventas):,} registros")
    
    return {
        'peliculas': len(peliculas),
        'clientes': len(clientes),
        'funciones': len(funciones),
        'ventas': len(ventas)
    }

# ============================================
# EJECUCIÓN
# ============================================
if __name__ == '__main__':
    print("\n" + "="*70)
    print("GENERADOR DE DATOS MASIVOS - SISTEMA DE CINES DISTRIBUIDO")
    print("="*70)
    print("\n📊 Configuración:")
    print(f"   Años histórico: {CONFIG['AÑOS_HISTORICO']}")
    print(f"   Películas: {CONFIG['NUM_PELICULAS']} por país")
    print(f"   Clientes GT: {CONFIG['NUM_CLIENTES_GT']:,}")
    print(f"   Clientes SV: {CONFIG['NUM_CLIENTES_SV']:,}")
    print(f"   Funciones/día GT: {CONFIG['FUNCIONES_POR_DIA_GT']}")
    print(f"   Funciones/día SV: {CONFIG['FUNCIONES_POR_DIA_SV']}")
    print(f"   Ocupación promedio: {CONFIG['TASA_OCUPACION_PROMEDIO']*100:.0f}%")
    
    print("\n⚠️  Este proceso puede tardar 2-5 minutos.")
    print("    Se generarán aproximadamente:")
    dias = 365 * CONFIG['AÑOS_HISTORICO']
    est_func_gt = CONFIG['FUNCIONES_POR_DIA_GT'] * dias
    est_func_sv = CONFIG['FUNCIONES_POR_DIA_SV'] * dias
    est_ventas = int((est_func_gt + est_func_sv) * 150 * 0.5)
    print(f"    - ~{est_func_gt:,} funciones GT")
    print(f"    - ~{est_func_sv:,} funciones SV")
    print(f"    - ~{est_ventas:,} ventas totales")
    
    input("\n▶️  Presiona ENTER para iniciar...")
    
    inicio = datetime.now()
    
    # Guatemala
    stats_gt = generar_datos_pais('GT')
    
    # El Salvador
    stats_sv = generar_datos_pais('SV')
    
    tiempo_total = (datetime.now() - inicio).total_seconds()
    
    # Resumen
    print("\n" + "="*70)
    print("✅ GENERACIÓN COMPLETADA")
    print("="*70)
    
    total_registros = sum(stats_gt.values()) + sum(stats_sv.values())
    print(f"\nTotal de registros generados: {total_registros:,}")
    print(f"  Guatemala: {sum(stats_gt.values()):,}")
    print(f"    - Películas: {stats_gt['peliculas']:,}")
    print(f"    - Clientes: {stats_gt['clientes']:,}")
    print(f"    - Funciones: {stats_gt['funciones']:,}")
    print(f"    - Ventas: {stats_gt['ventas']:,}")
    print(f"\n  El Salvador: {sum(stats_sv.values()):,}")
    print(f"    - Películas: {stats_sv['peliculas']:,}")
    print(f"    - Clientes: {stats_sv['clientes']:,}")
    print(f"    - Funciones: {stats_sv['funciones']:,}")
    print(f"    - Ventas: {stats_sv['ventas']:,}")
    
    print(f"\n⏱️  Tiempo de generación: {tiempo_total:.1f} segundos")
    
    print("\n📋 Pasos siguientes:")
    print("   1. Cargar datos a Guatemala:")
    print("      docker exec -i cine-db-guatemala psql -U cine_admin -d cine_gt < databases/guatemala/03_peliculas.sql")
    print("      docker exec -i cine-db-guatemala psql -U cine_admin -d cine_gt < databases/guatemala/04_clientes.sql")
    print("      docker exec -i cine-db-guatemala psql -U cine_admin -d cine_gt < databases/guatemala/05_funciones.sql")
    print("      docker exec -i cine-db-guatemala psql -U cine_admin -d cine_gt < databases/guatemala/06_ventas.sql")
    print("\n   2. Cargar datos a El Salvador:")
    print("      docker exec -i cine-db-elsalvador psql -U cine_admin -d cine_sv < databases/elsalvador/03_peliculas.sql")
    print("      docker exec -i cine-db-elsalvador psql -U cine_admin -d cine_sv < databases/elsalvador/04_clientes.sql")
    print("      docker exec -i cine-db-elsalvador psql -U cine_admin -d cine_sv < databases/elsalvador/05_funciones.sql")
    print("      docker exec -i cine-db-elsalvador psql -U cine_admin -d cine_sv < databases/elsalvador/06_ventas.sql")
    print("="*70 + "\n")