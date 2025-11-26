-- =============================================
-- Sistema de Gestión de Equipos de TI - Universidad
-- Base de Datos MySQL
-- =============================================

CREATE DATABASE IF NOT EXISTS it_management;
USE it_management;

-- =============================================
-- TABLA DE USUARIOS Y AUTENTICACIÓN
-- =============================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'technician', 'viewer') NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- TABLA DE PROVEEDORES
-- =============================================
CREATE TABLE IF NOT EXISTS providers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    ruc VARCHAR(20) UNIQUE,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    website VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    INDEX idx_name (name),
    INDEX idx_ruc (ruc),
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- TABLA DE CONTRATOS CON PROVEEDORES
-- =============================================
CREATE TABLE IF NOT EXISTS contracts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider_id INT NOT NULL,
    contract_number VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    amount DECIMAL(12, 2),
    status ENUM('active', 'expired', 'terminated') DEFAULT 'active',
    attachment_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_provider (provider_id),
    INDEX idx_status (status),
    FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- TABLA DE CATEGORÍAS DE EQUIPOS
-- =============================================
CREATE TABLE IF NOT EXISTS equipment_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- TABLA DE UBICACIONES
-- =============================================
CREATE TABLE IF NOT EXISTS locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    building VARCHAR(100) NOT NULL,
    floor VARCHAR(50),
    room VARCHAR(50),
    department VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_building (building),
    INDEX idx_department (department)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- TABLA DE EQUIPOS
-- =============================================
CREATE TABLE IF NOT EXISTS equipment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_code VARCHAR(50) UNIQUE NOT NULL,
    serial_number VARCHAR(100),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INT,
    brand VARCHAR(100),
    model VARCHAR(100),
    purchase_date DATE,
    purchase_price DECIMAL(12, 2),
    provider_id INT,
    warranty_months INT DEFAULT 12,
    warranty_end_date DATE,
    status ENUM('operational', 'in_maintenance', 'broken', 'retired', 'in_storage') DEFAULT 'operational',
    current_location_id INT,
    assigned_to VARCHAR(100),
    specifications JSON,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    INDEX idx_asset_code (asset_code),
    INDEX idx_serial (serial_number),
    INDEX idx_status (status),
    INDEX idx_category (category_id),
    INDEX idx_location (current_location_id),
    FOREIGN KEY (category_id) REFERENCES equipment_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE SET NULL,
    FOREIGN KEY (current_location_id) REFERENCES locations(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- TABLA DE HISTORIAL DE UBICACIONES
-- =============================================
CREATE TABLE IF NOT EXISTS equipment_location_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id INT NOT NULL,
    location_id INT NOT NULL,
    assigned_to VARCHAR(100),
    move_date DATE NOT NULL,
    reason TEXT,
    moved_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_equipment (equipment_id),
    INDEX idx_location (location_id),
    INDEX idx_move_date (move_date),
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE CASCADE,
    FOREIGN KEY (moved_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- TABLA DE TIPOS DE MANTENIMIENTO
-- =============================================
CREATE TABLE IF NOT EXISTS maintenance_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- TABLA DE MANTENIMIENTOS
-- =============================================
CREATE TABLE IF NOT EXISTS maintenance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id INT NOT NULL,
    maintenance_type_id INT,
    type ENUM('preventive', 'corrective') NOT NULL,
    scheduled_date DATE,
    performed_date DATE,
    technician VARCHAR(100),
    provider_id INT,
    description TEXT NOT NULL,
    diagnosis TEXT,
    solution TEXT,
    cost DECIMAL(10, 2),
    status ENUM('scheduled', 'in_progress', 'completed', 'cancelled') DEFAULT 'scheduled',
    next_maintenance_date DATE,
    attachments JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    INDEX idx_equipment (equipment_id),
    INDEX idx_type (type),
    INDEX idx_status (status),
    INDEX idx_scheduled_date (scheduled_date),
    INDEX idx_performed_date (performed_date),
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE,
    FOREIGN KEY (maintenance_type_id) REFERENCES maintenance_types(id) ON DELETE SET NULL,
    FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- TABLA DE PARTES/REPUESTOS USADOS
-- =============================================
CREATE TABLE IF NOT EXISTS maintenance_parts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maintenance_id INT NOT NULL,
    part_name VARCHAR(200) NOT NULL,
    quantity INT DEFAULT 1,
    unit_cost DECIMAL(10, 2),
    total_cost DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_maintenance (maintenance_id),
    FOREIGN KEY (maintenance_id) REFERENCES maintenance(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- TABLA DE ALERTAS Y NOTIFICACIONES
-- =============================================
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id INT,
    alert_type ENUM('maintenance_due', 'warranty_expiring', 'equipment_old', 'custom') NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    is_read BOOLEAN DEFAULT FALSE,
    assigned_to INT,
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_equipment (equipment_id),
    INDEX idx_type (alert_type),
    INDEX idx_assigned (assigned_to),
    INDEX idx_is_read (is_read),
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- TABLA DE LOGS DE AUDITORÍA
-- =============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id INT,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_action (action),
    INDEX idx_table (table_name),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- DATOS INICIALES
-- =============================================

-- Usuario administrador por defecto (password: admin123)
INSERT INTO users (username, email, password_hash, full_name, role) VALUES
('admin', 'admin@universidad.edu', 'admin123', 'Administrador del Sistema', 'admin'),
('tecnico1', 'tecnico1@universidad.edu', 'admin123', 'Juan Pérez', 'technician'),
('viewer1', 'viewer1@universidad.edu', 'admin123', 'María González', 'viewer');

-- Categorías de equipos
INSERT INTO equipment_categories (name, description) VALUES
('Computadoras de Escritorio', 'PCs de escritorio para uso administrativo y académico'),
('Laptops', 'Computadoras portátiles'),
('Servidores', 'Servidores físicos y virtuales'),
('Equipos de Red', 'Routers, switches, access points'),
('Impresoras', 'Impresoras y multifuncionales'),
('Proyectores', 'Proyectores multimedia'),
('UPS', 'Sistemas de alimentación ininterrumpida'),
('Monitores', 'Pantallas y monitores');

-- Ubicaciones
INSERT INTO locations (building, floor, room, department) VALUES
('Edificio Central', 'Piso 1', 'Sala 101', 'Administración'),
('Edificio Central', 'Piso 2', 'Sala 201', 'Sistemas'),
('Edificio Académico A', 'Piso 1', 'Lab 101', 'Laboratorio de Cómputo 1'),
('Edificio Académico A', 'Piso 2', 'Lab 201', 'Laboratorio de Cómputo 2'),
('Edificio Académico B', 'Piso 1', 'Sala 105', 'Biblioteca'),
('Edificio de Ingeniería', 'Piso 3', 'Sala 301', 'Departamento de Sistemas');

-- Tipos de mantenimiento
INSERT INTO maintenance_types (name, description) VALUES
('Limpieza General', 'Limpieza interna y externa del equipo'),
('Actualización de Software', 'Actualización de sistema operativo y aplicaciones'),
('Reemplazo de Pasta Térmica', 'Cambio de pasta térmica en procesadores'),
('Revisión de Hardware', 'Inspección general de componentes'),
('Calibración', 'Calibración de equipos especializados'),
('Backup', 'Respaldo de información');

-- Proveedores de ejemplo
INSERT INTO providers (name, ruc, contact_person, phone, email) VALUES
('TechSupply S.A.', '20123456789', 'Carlos Rodríguez', '01-2345678', 'ventas@techsupply.com'),
('CompuWorld', '20987654321', 'Ana Martínez', '01-8765432', 'contacto@compuworld.com'),
('IT Solutions', '20456789123', 'Pedro Sánchez', '01-4567891', 'info@itsolutions.com');

-- =============================================
-- EQUIPOS DE EJEMPLO
-- =============================================

-- Computadoras de Escritorio
INSERT INTO equipment (asset_code, serial_number, name, description, category_id, brand, model, purchase_date, purchase_price, provider_id, warranty_months, warranty_end_date, status, current_location_id, assigned_to, created_by) VALUES
('PC-2024-001', 'DL-SN-2024-0001', 'Dell OptiPlex 7090', 'Computadora de escritorio para administración', 1, 'Dell', 'OptiPlex 7090', '2024-01-15', 3500.00, 1, 36, '2027-01-15', 'operational', 1, 'María Torres', 1),
('PC-2024-002', 'HP-SN-2024-0002', 'HP ProDesk 600 G6', 'PC para uso en laboratorio de cómputo', 1, 'HP', 'ProDesk 600 G6', '2024-02-10', 3200.00, 2, 24, '2026-02-10', 'operational', 3, NULL, 1),
('PC-2024-003', 'DL-SN-2024-0003', 'Dell OptiPlex 5090', 'Computadora para departamento de sistemas', 1, 'Dell', 'OptiPlex 5090', '2024-03-05', 2800.00, 1, 24, '2026-03-05', 'operational', 2, 'Pedro Ramírez', 1),
('PC-2023-015', 'HP-SN-2023-0015', 'HP Elite 800 G9', 'PC de alto rendimiento para ingeniería', 1, 'HP', 'Elite 800 G9', '2023-06-20', 4200.00, 2, 36, '2026-06-20', 'operational', 6, 'Carlos Méndez', 1),
('PC-2023-020', 'DL-SN-2023-0020', 'Dell Precision 3660', 'Workstation para diseño gráfico', 1, 'Dell', 'Precision 3660', '2023-08-12', 5500.00, 1, 36, '2026-08-12', 'in_maintenance', 4, 'Laura Vega', 1),

-- Laptops
('LT-2024-001', 'LN-SN-2024-0001', 'Lenovo ThinkPad T14', 'Laptop para personal administrativo', 2, 'Lenovo', 'ThinkPad T14 Gen 3', '2024-01-20', 4500.00, 3, 24, '2026-01-20', 'operational', 1, 'Ana Morales', 1),
('LT-2024-002', 'DL-SN-2024-0002', 'Dell Latitude 5430', 'Laptop para soporte técnico', 2, 'Dell', 'Latitude 5430', '2024-02-15', 4000.00, 1, 24, '2026-02-15', 'operational', 2, 'Juan Pérez', 1),
('LT-2023-010', 'HP-SN-2023-0010', 'HP EliteBook 840', 'Laptop ejecutiva para dirección', 2, 'HP', 'EliteBook 840 G9', '2023-05-10', 5200.00, 2, 36, '2026-05-10', 'operational', 1, 'Director General', 1),
('LT-2023-025', 'AS-SN-2023-0025', 'ASUS VivoBook Pro', 'Laptop para docentes', 2, 'ASUS', 'VivoBook Pro 15', '2023-09-18', 3800.00, 3, 24, '2025-09-18', 'broken', 5, NULL, 1),

-- Servidores
('SRV-2023-001', 'DL-SRV-2023-001', 'Dell PowerEdge R740', 'Servidor principal de base de datos', 3, 'Dell', 'PowerEdge R740', '2023-03-15', 18500.00, 1, 60, '2028-03-15', 'operational', 2, NULL, 1),
('SRV-2023-002', 'HP-SRV-2023-002', 'HP ProLiant DL380 Gen10', 'Servidor de aplicaciones web', 3, 'HP', 'ProLiant DL380 Gen10', '2023-04-20', 16000.00, 2, 60, '2028-04-20', 'operational', 2, NULL, 1),
('SRV-2024-001', 'DL-SRV-2024-001', 'Dell PowerEdge R650', 'Servidor de respaldo y storage', 3, 'Dell', 'PowerEdge R650', '2024-01-10', 22000.00, 1, 60, '2029-01-10', 'operational', 2, NULL, 1),

-- Equipos de Red
('NET-2024-001', 'CS-RT-2024-001', 'Cisco Catalyst 9300', 'Switch core principal', 4, 'Cisco', 'Catalyst 9300-48P', '2024-01-05', 8500.00, 3, 60, '2029-01-05', 'operational', 2, NULL, 1),
('NET-2024-002', 'UB-AP-2024-002', 'Ubiquiti UniFi AP', 'Access Point para edificio central', 4, 'Ubiquiti', 'UniFi AP AC Pro', '2024-02-01', 850.00, 3, 24, '2026-02-01', 'operational', 1, NULL, 1),
('NET-2023-015', 'CS-RT-2023-015', 'Cisco ISR 4321', 'Router principal de internet', 4, 'Cisco', 'ISR 4321', '2023-07-10', 5200.00, 3, 36, '2026-07-10', 'operational', 2, NULL, 1),

-- Impresoras
('PRT-2024-001', 'HP-PRT-2024-001', 'HP LaserJet Pro M404dn', 'Impresora láser monocromática', 5, 'HP', 'LaserJet Pro M404dn', '2024-01-25', 1200.00, 2, 12, '2025-01-25', 'operational', 1, NULL, 1),
('PRT-2024-002', 'CN-PRT-2024-002', 'Canon imageRUNNER 2625i', 'Multifuncional para departamento', 5, 'Canon', 'imageRUNNER 2625i', '2024-02-20', 3500.00, 2, 12, '2025-02-20', 'operational', 6, NULL, 1),
('PRT-2023-008', 'HP-PRT-2023-008', 'HP OfficeJet Pro 9025', 'Impresora multifuncional a color', 5, 'HP', 'OfficeJet Pro 9025', '2023-04-15', 1800.00, 2, 12, '2024-04-15', 'in_maintenance', 3, NULL, 1),

-- Proyectores
('PRJ-2024-001', 'EP-PRJ-2024-001', 'Epson PowerLite 2250U', 'Proyector WUXGA para aula', 6, 'Epson', 'PowerLite 2250U', '2024-01-15', 4200.00, 3, 36, '2027-01-15', 'operational', 3, NULL, 1),
('PRJ-2023-005', 'BQ-PRJ-2023-005', 'BenQ MW560', 'Proyector WXGA para conferencias', 6, 'BenQ', 'MW560', '2023-05-20', 2800.00, 3, 24, '2025-05-20', 'operational', 4, NULL, 1),
('PRJ-2023-012', 'EP-PRJ-2023-012', 'Epson EB-2250U', 'Proyector para auditorio', 6, 'Epson', 'EB-2250U', '2023-09-10', 5500.00, 3, 36, '2026-09-10', 'operational', 5, NULL, 1),

-- UPS
('UPS-2024-001', 'APC-UPS-2024-001', 'APC Smart-UPS 3000VA', 'UPS para servidor principal', 7, 'APC', 'SMT3000RMI2U', '2024-01-08', 2500.00, 1, 24, '2026-01-08', 'operational', 2, NULL, 1),
('UPS-2024-002', 'APC-UPS-2024-002', 'APC Back-UPS Pro 1500VA', 'UPS para equipos de red', 7, 'APC', 'BR1500G', '2024-02-05', 800.00, 1, 24, '2026-02-05', 'operational', 2, NULL, 1),
('UPS-2023-010', 'CM-UPS-2023-010', 'Cyberpower CP1500PFCLCD', 'UPS para laboratorio', 7, 'CyberPower', 'CP1500PFCLCD', '2023-06-15', 950.00, 3, 24, '2025-06-15', 'operational', 3, NULL, 1),

-- Monitores
('MON-2024-001', 'DL-MON-2024-001', 'Dell UltraSharp U2722DE', 'Monitor 27 pulgadas QHD', 8, 'Dell', 'UltraSharp U2722DE', '2024-01-20', 1200.00, 1, 36, '2027-01-20', 'operational', 1, 'María Torres', 1),
('MON-2024-002', 'LG-MON-2024-002', 'LG 27UP850-W', 'Monitor 4K UHD para diseño', 8, 'LG', '27UP850-W', '2024-02-10', 1500.00, 2, 36, '2027-02-10', 'operational', 4, 'Laura Vega', 1),
('MON-2023-015', 'SM-MON-2023-015', 'Samsung S27A600U', 'Monitor 27 pulgadas para oficina', 8, 'Samsung', 'S27A600U', '2023-07-08', 850.00, 2, 36, '2026-07-08', 'operational', 6, 'Carlos Méndez', 1);

-- =============================================
-- MANTENIMIENTOS DE EJEMPLO
-- =============================================

-- Mantenimientos Preventivos Completados
INSERT INTO maintenance (equipment_id, maintenance_type_id, type, scheduled_date, performed_date, technician, provider_id, description, diagnosis, solution, cost, status, next_maintenance_date, created_by) VALUES
(1, 1, 'preventive', '2024-03-15', '2024-03-15', 'Juan Pérez', NULL, 'Limpieza general y actualización de software', 'Equipo con acumulación moderada de polvo, software desactualizado', 'Se realizó limpieza interna y externa, actualización de Windows 11 y Office 365', 0.00, 'completed', '2024-09-15', 1),
(2, 4, 'preventive', '2024-04-10', '2024-04-12', 'Juan Pérez', NULL, 'Revisión general de hardware y limpieza', 'Equipo en buen estado general, ventiladores funcionando correctamente', 'Limpieza interna, verificación de componentes, actualización de drivers', 0.00, 'completed', '2024-10-10', 1),
(10, 1, 'preventive', '2024-02-20', '2024-02-20', 'TechSupply', 1, 'Mantenimiento preventivo de servidor principal', 'Servidor operando normalmente, temperatura estable', 'Limpieza de componentes, actualización de firmware, verificación de RAID', 850.00, 'completed', '2024-08-20', 1),
(11, 1, 'preventive', '2024-03-01', '2024-03-01', 'TechSupply', 1, 'Mantenimiento preventivo servidor de aplicaciones', 'Servidor en óptimas condiciones, sin alertas de hardware', 'Limpieza general, actualización de sistema operativo, respaldo de configuración', 800.00, 'completed', '2024-09-01', 1),
(16, 2, 'preventive', '2024-04-05', '2024-04-05', 'Juan Pérez', NULL, 'Actualización de firmware y limpieza de impresora', 'Impresora con firmware desactualizado, requiere limpieza de rodillos', 'Actualización de firmware a versión más reciente, limpieza de rodillos y cabezales', 0.00, 'completed', '2024-07-05', 1),

-- Mantenimientos Correctivos Completados
(5, NULL, 'corrective', NULL, '2024-04-18', 'IT Solutions', 3, 'Equipo no enciende, posible falla de fuente de poder', 'Fuente de poder dañada, sin voltaje de salida', 'Reemplazo de fuente de poder, pruebas de POST exitosas, equipo operativo', 450.00, 'completed', NULL, 1),
(9, NULL, 'corrective', NULL, '2024-04-20', 'CompuWorld', 2, 'Pantalla no enciende, equipo hace 3 beeps al iniciar', 'Memoria RAM defectuosa en slot 2', 'Reemplazo de módulo de memoria RAM de 16GB, pruebas de estabilidad exitosas', 320.00, 'completed', NULL, 1),
(18, NULL, 'corrective', NULL, '2024-04-15', 'Juan Pérez', NULL, 'Impresora presenta atascos constantes de papel', 'Rodillos de alimentación desgastados, bandeja desalineada', 'Reemplazo de kit de rodillos, ajuste de bandeja, calibración', 180.00, 'completed', NULL, 1),

-- Mantenimientos en Progreso
(3, 3, 'preventive', '2024-05-10', NULL, 'Juan Pérez', NULL, 'Reemplazo de pasta térmica preventivo', NULL, NULL, NULL, 'in_progress', NULL, 1),
(12, 4, 'preventive', '2024-05-15', NULL, 'IT Solutions', 3, 'Revisión y mantenimiento de switch core', NULL, NULL, 650.00, 'in_progress', NULL, 1),

-- Mantenimientos Programados
(6, 1, 'preventive', '2024-06-01', NULL, NULL, NULL, 'Limpieza general y actualización de software programada', NULL, NULL, NULL, 'scheduled', NULL, 1),
(7, 1, 'preventive', '2024-06-05', NULL, NULL, NULL, 'Mantenimiento preventivo programado', NULL, NULL, NULL, 'scheduled', NULL, 1),
(8, 2, 'preventive', '2024-06-10', NULL, NULL, NULL, 'Actualización de software y backup de datos', NULL, NULL, NULL, 'scheduled', NULL, 1),
(13, 1, 'preventive', '2024-06-15', NULL, 'IT Solutions', 3, 'Mantenimiento preventivo de access point', NULL, NULL, 250.00, 'scheduled', NULL, 1),
(14, 1, 'preventive', '2024-06-20', NULL, 'IT Solutions', 3, 'Mantenimiento preventivo de router principal', NULL, NULL, 400.00, 'scheduled', NULL, 1),
(19, 1, 'preventive', '2024-06-25', NULL, NULL, NULL, 'Limpieza y calibración de proyector', NULL, NULL, NULL, 'scheduled', NULL, 1),
(22, 1, 'preventive', '2024-07-01', NULL, NULL, NULL, 'Prueba de carga y verificación de UPS', NULL, NULL, NULL, 'scheduled', NULL, 1);

-- =============================================
-- PARTES Y REPUESTOS UTILIZADOS
-- =============================================

INSERT INTO maintenance_parts (maintenance_id, part_name, quantity, unit_cost, total_cost) VALUES
-- Partes para mantenimiento correctivo del equipo 5 (fuente de poder)
(6, 'Fuente de poder EVGA 650W 80+ Gold', 1, 450.00, 450.00),

-- Partes para mantenimiento correctivo del equipo 9 (memoria RAM)
(7, 'Memoria RAM DDR4 16GB 3200MHz Kingston', 1, 320.00, 320.00),

-- Partes para mantenimiento correctivo de impresora
(8, 'Kit de rodillos HP OfficeJet Pro', 1, 120.00, 120.00),
(8, 'Pasta térmica Arctic MX-4', 1, 15.00, 15.00),
(8, 'Isopropanol 99% (botella)', 1, 25.00, 25.00),
(8, 'Pads de limpieza', 2, 10.00, 20.00);

-- =============================================
-- HISTORIAL DE UBICACIONES
-- =============================================

INSERT INTO equipment_location_history (equipment_id, location_id, assigned_to, move_date, reason, moved_by) VALUES
(1, 1, 'María Torres', '2024-01-15', 'Asignación inicial del equipo', 1),
(5, 4, 'Laura Vega', '2023-08-12', 'Asignación inicial del equipo', 1),
(5, 2, NULL, '2024-04-18', 'Movido a soporte técnico para reparación', 2),
(5, 4, 'Laura Vega', '2024-04-19', 'Equipo reparado, devuelto a ubicación original', 2),
(9, 5, NULL, '2023-09-18', 'Asignación inicial a biblioteca', 1),
(9, 2, NULL, '2024-04-20', 'Movido a soporte para diagnóstico y reparación', 2);
