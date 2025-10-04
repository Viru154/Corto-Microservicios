const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Configuración de conexión al DW
const pool = new Pool({
    host: process.env.DB_DW_HOST,
    port: process.env.DB_DW_PORT,
    database: process.env.DB_DW_NAME,
    user: process.env.DB_DW_USER,
    password: process.env.DB_DW_PASSWORD
});

// Middleware
app.use(cors());
app.use(express.json());

// ============================================
// ENDPOINTS
// ============================================

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'OK', timestamp: new Date() });
});

// Obtener todas las películas
app.get('/api/peliculas', async (req, res) => {
    try {
        const result = await pool.query('SELECT * FROM dim_pelicula ORDER BY titulo');
        res.json({ success: true, data: result.rows, total: result.rowCount });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Resumen por país
app.get('/api/ventas/por-pais', async (req, res) => {
    try {
        const result = await pool.query(`
            SELECT 
                p.nombre as pais,
                COUNT(DISTINCT fv.pelicula_id) as peliculas_distintas,
                SUM(fv.cantidad_boletos) as total_boletos,
                SUM(fv.ingreso_total) as total_ingresos,
                ROUND(AVG(fv.precio_promedio), 2) as precio_promedio
            FROM fact_ventas fv
            JOIN dim_pais p ON fv.pais_id = p.pais_id
            GROUP BY p.nombre
            ORDER BY total_ingresos DESC
        `);
        res.json({ success: true, data: result.rows });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Top películas por ingresos
app.get('/api/peliculas/top/:limit', async (req, res) => {
    try {
        const limit = parseInt(req.params.limit) || 10;
        const result = await pool.query(`
            SELECT 
                p.titulo,
                p.genero,
                SUM(fv.cantidad_boletos) as total_boletos,
                SUM(fv.ingreso_total) as total_ingresos
            FROM fact_ventas fv
            JOIN dim_pelicula p ON fv.pelicula_id = p.pelicula_id
            GROUP BY p.pelicula_id, p.titulo, p.genero
            ORDER BY total_ingresos DESC
            LIMIT $1
        `, [limit]);
        res.json({ success: true, data: result.rows });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Ventas por mes
app.get('/api/ventas/por-mes', async (req, res) => {
    try {
        const result = await pool.query(`
            SELECT 
                t.anio,
                t.mes,
                p.nombre as pais,
                SUM(fv.cantidad_boletos) as total_boletos,
                SUM(fv.ingreso_total) as total_ingresos
            FROM fact_ventas fv
            JOIN dim_tiempo t ON fv.tiempo_id = t.tiempo_id
            JOIN dim_pais p ON fv.pais_id = p.pais_id
            GROUP BY t.anio, t.mes, p.nombre
            ORDER BY t.anio DESC, t.mes DESC, p.nombre
            LIMIT 24
        `);
        res.json({ success: true, data: result.rows });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Iniciar servidor
app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/health`);
});
