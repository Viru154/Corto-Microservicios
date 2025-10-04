-- Sucursales El Salvador (Basado en ubicaciones reales)
INSERT INTO sucursales (nombre, ciudad, direccion, numero_salas, capacidad_total, pais) VALUES
('Cinépolis Multiplaza', 'Antiguo Cuscatlán', 'Calle El Mirador y Autopista Sur, Antiguo Cuscatlán', 10, 1500, 'SV'),
('Cinépolis Galerías', 'San Salvador', 'Paseo General Escalón 3700, San Salvador', 8, 1200, 'SV'),
('Cinépolis La Gran Vía', 'Antiguo Cuscatlán', 'Carretera a Santa Tecla, Antiguo Cuscatlán', 9, 1350, 'SV'),
('Cinemark Plaza Mundo', 'Soyapango', 'Bulevar del Ejército, Soyapango', 7, 1050, 'SV');

-- Salas para cada sucursal El Salvador
INSERT INTO salas (sucursal_id, numero_sala, capacidad, tipo_sala) 
SELECT s.sucursal_id, gs.numero, gs.capacidad, gs.tipo
FROM sucursales s
CROSS JOIN (
    VALUES 
    (1, 200, 'IMAX'),
    (2, 150, 'STANDARD'),
    (3, 150, 'STANDARD'),
    (4, 150, 'STANDARD'),
    (5, 150, 'STANDARD'),
    (6, 150, 'STANDARD'),
    (7, 150, 'STANDARD'),
    (8, 80, 'VIP')
) AS gs(numero, capacidad, tipo)
WHERE s.pais = 'SV';

