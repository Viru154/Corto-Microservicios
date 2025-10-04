"""
ETL - Carga Data Warehouse desde bases operacionales
Extrae de GT y SV, transforma y carga al DW
"""

import psycopg2
from datetime import datetime

# Configuración de conexiones
DB_GT = {
    'host': 'localhost',
    'port': 5432,
    'database': 'cine_gt',
    'user': 'cine_admin',
    'password': 'cine_pass_2024'
}

DB_SV = {
    'host': 'localhost',
    'port': 5433,
    'database': 'cine_sv',
    'user': 'cine_admin',
    'password': 'cine_pass_2024'
}

DB_DW = {
    'host': 'localhost',
    'port': 5434,
    'database': 'cine_dw',
    'user': 'dw_admin',
    'password': 'dw_pass_2024'
}

def conectar(config):
    return psycopg2.connect(**config)

def cargar_peliculas(pais_code):
    """Extrae películas y carga a dim_pelicula"""
    config = DB_GT if pais_code == 'GT' else DB_SV
    
    conn_origen = conectar(config)
    conn_dw = conectar(DB_DW)
    
    cur_origen = conn_origen.cursor()
    cur_dw = conn_dw.cursor()
    
    print(f"  Extrayendo películas de {pais_code}...")
    
    cur_origen.execute("""
        SELECT titulo, genero, clasificacion, duracion_minutos
        FROM peliculas
    """)
    
    peliculas = cur_origen.fetchall()
    
    print(f"  Insertando {len(peliculas)} películas a dim_pelicula...")
    
    for p in peliculas:
        cur_dw.execute("""
            INSERT INTO dim_pelicula (titulo, genero, clasificacion, duracion_minutos)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, p)
    
    conn_dw.commit()
    cur_origen.close()
    cur_dw.close()
    conn_origen.close()
    conn_dw.close()
    
    print(f"  ✓ Películas de {pais_code} cargadas")

def cargar_sucursales(pais_code):
    """Extrae sucursales y carga a dim_sucursal"""
    config = DB_GT if pais_code == 'GT' else DB_SV
    pais_id = 1 if pais_code == 'GT' else 2
    
    conn_origen = conectar(config)
    conn_dw = conectar(DB_DW)
    
    cur_origen = conn_origen.cursor()
    cur_dw = conn_dw.cursor()
    
    print(f"  Extrayendo sucursales de {pais_code}...")
    
    cur_origen.execute("SELECT nombre, ciudad FROM sucursales")
    sucursales = cur_origen.fetchall()
    
    print(f"  Insertando {len(sucursales)} sucursales...")
    
    for s in sucursales:
        cur_dw.execute("""
            INSERT INTO dim_sucursal (pais_id, nombre, ciudad)
            VALUES (%s, %s, %s)
        """, (pais_id, s[0], s[1]))
    
    conn_dw.commit()
    cur_origen.close()
    cur_dw.close()
    conn_origen.close()
    conn_dw.close()
    
    print(f"  ✓ Sucursales de {pais_code} cargadas")

def cargar_ventas(pais_code):
    """Extrae ventas y carga a fact_ventas"""
    config = DB_GT if pais_code == 'GT' else DB_SV
    pais_id = 1 if pais_code == 'GT' else 2
    
    conn_origen = conectar(config)
    conn_dw = conectar(DB_DW)
    
    cur_origen = conn_origen.cursor()
    cur_dw = conn_dw.cursor()
    
    print(f"  Extrayendo ventas de {pais_code}...")
    
    # Query agregado por día/película/sucursal
    cur_origen.execute("""
        SELECT 
            DATE(v.fecha_venta) as fecha,
            f.pelicula_id,
            f.sucursal_id,
            SUM(v.cantidad_boletos) as total_boletos,
            SUM(v.total) as total_ingresos
        FROM ventas v
        JOIN funciones f ON v.funcion_id = f.funcion_id
        GROUP BY DATE(v.fecha_venta), f.pelicula_id, f.sucursal_id
        ORDER BY fecha
    """)
    
    ventas = cur_origen.fetchall()
    print(f"  Procesando {len(ventas)} registros agregados...")
    
    batch_size = 1000
    for i in range(0, len(ventas), batch_size):
        batch = ventas[i:i+batch_size]
        
        for v in batch:
            fecha, pelicula_id, sucursal_id, boletos, ingresos = v
            precio_prom = round(ingresos / boletos, 2) if boletos > 0 else 0
            
            # Obtener tiempo_id
            cur_dw.execute("SELECT tiempo_id FROM dim_tiempo WHERE fecha = %s", (fecha,))
            tiempo_row = cur_dw.fetchone()
            if not tiempo_row:
                continue
            tiempo_id = tiempo_row[0]
            
            cur_dw.execute("""
                INSERT INTO fact_ventas 
                (tiempo_id, pelicula_id, sucursal_id, pais_id, cantidad_boletos, ingreso_total, precio_promedio, fuente)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (tiempo_id, pelicula_id, sucursal_id, pais_id, boletos, ingresos, precio_prom, pais_code))
        
        conn_dw.commit()
        
        if (i + batch_size) % 10000 == 0:
            print(f"    Procesados {i + batch_size:,} registros...")
    
    cur_origen.close()
    cur_dw.close()
    conn_origen.close()
    conn_dw.close()
    
    print(f"  ✓ Ventas de {pais_code} cargadas")

def main():
    print("\n" + "="*60)
    print("ETL - CARGA DATA WAREHOUSE")
    print("="*60)
    
    inicio = datetime.now()
    
    # 1. Cargar dimensiones
    print("\n[1/3] Cargando dimensiones...")
    cargar_peliculas('GT')
    cargar_peliculas('SV')
    cargar_sucursales('GT')
    cargar_sucursales('SV')
    
    # 2. Cargar hechos
    print("\n[2/3] Cargando fact_ventas...")
    cargar_ventas('GT')
    cargar_ventas('SV')
    
    # 3. Verificar
    print("\n[3/3] Verificando carga...")
    conn_dw = conectar(DB_DW)
    cur = conn_dw.cursor()
    
    cur.execute("SELECT COUNT(*) FROM dim_pelicula")
    print(f"  dim_pelicula: {cur.fetchone()[0]:,} registros")
    
    cur.execute("SELECT COUNT(*) FROM dim_sucursal")
    print(f"  dim_sucursal: {cur.fetchone()[0]:,} registros")
    
    cur.execute("SELECT COUNT(*) FROM fact_ventas")
    print(f"  fact_ventas: {cur.fetchone()[0]:,} registros")
    
    cur.close()
    conn_dw.close()
    
    tiempo = (datetime.now() - inicio).total_seconds()
    
    print("\n" + "="*60)
    print(f"✓ ETL completado en {tiempo:.1f} segundos")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
