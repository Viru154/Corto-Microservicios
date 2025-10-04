-- Sucursales Guatemala
INSERT INTO sucursales (nombre, ciudad, direccion, numero_salas, capacidad_total, pais) VALUES
('Cinépolis Oakland Mall', 'Guatemala', 'Diagonal 6 13-01 zona 10', 8, 1200, 'GT'),
('Cinemark Miraflores', 'Guatemala', '21 avenida 4-32 zona 11', 6, 900, 'GT'),
('Cinépolis Pradera', 'Guatemala', 'Calz. Aguilar Batres 34-70 zona 12', 5, 750, 'GT'),
('Cinépolis Cayalá', 'Guatemala', '16 calle 8-44 zona 16', 10, 1500, 'GT'),
('Cinemark Tikal Futura', 'Guatemala', 'Calz. Roosevelt 22-43 zona 11', 7, 1050, 'GT');

-- Salas para cada sucursal (ejemplo con sucursal 1)
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
WHERE s.sucursal_id <= 5;
