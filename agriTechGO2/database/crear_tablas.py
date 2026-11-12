import sys
from pathlib import Path

# Permite importar conexion.py desde la raíz del proyecto.
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from conexion import obtener_conexion


TABLAS = [
    (
        "perfiles",
        """
        CREATE TABLE IF NOT EXISTS perfiles (
            usuario_id INT PRIMARY KEY,
            telefono VARCHAR(25) DEFAULT '',
            municipio VARCHAR(80) DEFAULT '',
            vereda VARCHAR(100) DEFAULT '',
            descripcion TEXT,
            foto MEDIUMBLOB,
            FOREIGN KEY (usuario_id)
                REFERENCES usuarios(id)
        )
        """
    ),
    (
        "fincas",
        """
        CREATE TABLE IF NOT EXISTS fincas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            agricultor_id INT NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            municipio VARCHAR(80) DEFAULT '',
            vereda VARCHAR(100) DEFAULT '',
            descripcion TEXT,
            activa BOOLEAN NOT NULL DEFAULT TRUE,
            UNIQUE KEY uq_finca_agricultor (
                agricultor_id, nombre
            ),
            FOREIGN KEY (agricultor_id)
                REFERENCES usuarios(id)
        )
        """
    ),
    (
        "cosechas",
        """
        CREATE TABLE IF NOT EXISTS cosechas (
            id CHAR(32) PRIMARY KEY,
            finca_id INT NOT NULL,
            producto VARCHAR(80) NOT NULL,
            calidad VARCHAR(80) NOT NULL DEFAULT 'No aplica',
            unidad ENUM('kg', 'arroba', 'unidad') NOT NULL,
            cantidad DECIMAL(12,3) NOT NULL,
            precio DECIMAL(14,2) NOT NULL,
            fecha DATE NOT NULL,
            foto MEDIUMBLOB,
            activa BOOLEAN NOT NULL DEFAULT TRUE,
            creado_en TIMESTAMP NOT NULL
                DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (finca_id)
                REFERENCES fincas(id)
        )
        """
    ),
    (
        "pedidos",
        """
        CREATE TABLE IF NOT EXISTS pedidos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            comprador_id INT NOT NULL,
            cosecha_id CHAR(32) NOT NULL,
            cantidad DECIMAL(12,3) NOT NULL,
            precio_unitario DECIMAL(14,2) NOT NULL,
            unidad ENUM('kg', 'arroba', 'unidad') NOT NULL,
            estado ENUM(
                'pendiente',
                'aceptado',
                'rechazado',
                'entregado',
                'cancelado'
            ) NOT NULL DEFAULT 'pendiente',
            observaciones VARCHAR(500),
            creado_en TIMESTAMP NOT NULL
                DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (comprador_id)
                REFERENCES usuarios(id),
            FOREIGN KEY (cosecha_id)
                REFERENCES cosechas(id)
        )
        """
    ),
    (
        "pagos",
        """
        CREATE TABLE IF NOT EXISTS pagos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pedido_id INT NOT NULL,
            monto DECIMAL(14,2) NOT NULL,
            estado ENUM(
                'pendiente',
                'confirmado',
                'rechazado'
            ) NOT NULL DEFAULT 'pendiente',
            referencia VARCHAR(150),
            es_simulado BOOLEAN NOT NULL DEFAULT TRUE,
            creado_en TIMESTAMP NOT NULL
                DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pedido_id)
                REFERENCES pedidos(id)
        )
        """
    ),
    (
        "proyectos",
        """
        CREATE TABLE IF NOT EXISTS proyectos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            finca_id INT NOT NULL,
            titulo VARCHAR(150) NOT NULL,
            descripcion TEXT,
            meta DECIMAL(14,2) NOT NULL,
            rentabilidad_estimada DECIMAL(7,4)
                NOT NULL DEFAULT 0,
            riesgo ENUM('Bajo', 'Medio', 'Alto')
                NOT NULL DEFAULT 'Medio',
            avance DECIMAL(5,4) NOT NULL DEFAULT 0,
            porcentaje_ventas DECIMAL(5,4)
                NOT NULL DEFAULT 0,
            estado ENUM(
                'borrador',
                'abierto',
                'financiado',
                'cerrado'
            ) NOT NULL DEFAULT 'borrador',
            es_simulado BOOLEAN NOT NULL DEFAULT TRUE,
            creado_en TIMESTAMP NOT NULL
                DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (finca_id)
                REFERENCES fincas(id)
        )
        """
    ),
    (
        "inversiones",
        """
        CREATE TABLE IF NOT EXISTS inversiones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            inversionista_id INT NOT NULL,
            proyecto_id INT NOT NULL,
            monto DECIMAL(14,2) NOT NULL,
            rentabilidad_estimada DECIMAL(7,4)
                NOT NULL DEFAULT 0,
            estado ENUM(
                'activa',
                'cancelada',
                'finalizada'
            ) NOT NULL DEFAULT 'activa',
            es_simulada BOOLEAN NOT NULL DEFAULT TRUE,
            creado_en TIMESTAMP NOT NULL
                DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (inversionista_id)
                REFERENCES usuarios(id),
            FOREIGN KEY (proyecto_id)
                REFERENCES proyectos(id)
        )
        """
    ),
    (
        "seguimientos",
        """
        CREATE TABLE IF NOT EXISTS seguimientos (
            inversionista_id INT NOT NULL,
            finca_id INT NOT NULL,
            PRIMARY KEY (inversionista_id, finca_id),
            FOREIGN KEY (inversionista_id)
                REFERENCES usuarios(id),
            FOREIGN KEY (finca_id)
                REFERENCES fincas(id)
        )
        """
    ),
    (
        "wallets",
        """
        CREATE TABLE IF NOT EXISTS wallets (
            usuario_id INT PRIMARY KEY,
            saldo DECIMAL(14,2) NOT NULL DEFAULT 0,
            es_simulada BOOLEAN NOT NULL DEFAULT TRUE,
            FOREIGN KEY (usuario_id)
                REFERENCES usuarios(id)
        )
        """
    ),
    (
        "movimientos_wallet",
        """
        CREATE TABLE IF NOT EXISTS movimientos_wallet (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            inversion_id INT,
            tipo ENUM(
                'recarga',
                'retiro',
                'inversion',
                'devolucion'
            ) NOT NULL,
            monto DECIMAL(14,2) NOT NULL,
            detalle VARCHAR(255) NOT NULL,
            creado_en TIMESTAMP NOT NULL
                DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id)
                REFERENCES wallets(usuario_id),
            FOREIGN KEY (inversion_id)
                REFERENCES inversiones(id)
        )
        """
    ),
]


def preparar_usuarios(cursor):
    """Crea o adapta la tabla de usuarios enviada por el equipo."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) DEFAULT NULL,
            correo VARCHAR(100) UNIQUE NOT NULL,
            rol VARCHAR(50) NOT NULL DEFAULT 'pendiente',
            password_hash VARCHAR(255) DEFAULT NULL,
            activo BOOLEAN NOT NULL DEFAULT TRUE,
            creado_en TIMESTAMP NOT NULL
                DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Revisamos qué columnas existen antes de agregar otras.
    cursor.execute("SHOW COLUMNS FROM usuarios")
    columnas = {fila[0] for fila in cursor.fetchall()}

    if "password_hash" not in columnas:
        cursor.execute("""
            ALTER TABLE usuarios
            ADD COLUMN password_hash VARCHAR(255) DEFAULT NULL
        """)

    if "activo" not in columnas:
        cursor.execute("""
            ALTER TABLE usuarios
            ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE
        """)

    if "creado_en" not in columnas:
        cursor.execute("""
            ALTER TABLE usuarios
            ADD COLUMN creado_en TIMESTAMP NOT NULL
                DEFAULT CURRENT_TIMESTAMP
        """)

    # El formulario inicial ya no necesita pedir el nombre.
    cursor.execute("""
        ALTER TABLE usuarios
        MODIFY COLUMN nombre VARCHAR(100) NULL DEFAULT NULL
    """)

    # Conserva los roles existentes y define uno para nuevas cuentas.
    cursor.execute("""
        ALTER TABLE usuarios
        MODIFY COLUMN rol VARCHAR(50) NOT NULL DEFAULT 'pendiente'
    """)


def crear_tablas():
    """Prepara la estructura utilizando la conexión a TiDB Cloud."""
    conexion = None
    cursor = None
    etapa = "abrir la conexión"

    try:
        conexion = obtener_conexion()

        if conexion is None:
            raise RuntimeError(
                "obtener_conexion() no devolvió una conexión."
            )

        cursor = conexion.cursor()

        etapa = "seleccionar la base de datos"
        cursor.execute("CREATE DATABASE IF NOT EXISTS agritechgo")
        cursor.execute("USE agritechgo")

        # Las claves foráneas deben estar habilitadas.
        cursor.execute("SET SESSION foreign_key_checks = 1")

        etapa = "preparar usuarios"
        preparar_usuarios(cursor)
        print("OK: usuarios preparada.")

        for nombre, sentencia in TABLAS:
            etapa = f"crear o comprobar {nombre}"
            cursor.execute(sentencia)
            print(f"OK: tabla {nombre} disponible.")

        etapa = "comprobar el resultado"
        cursor.execute("SHOW TABLES")
        tablas = [fila[0] for fila in cursor.fetchall()]

        print("\nTablas encontradas:")
        for nombre in tablas:
            print(f" - {nombre}")

        print("\nEstructura preparada correctamente.")

    except Exception as error:
        print(f"\nError al {etapa}: {error}")
        print(
            "El proceso se detuvo. Las tablas creadas antes "
            "del error pueden permanecer en la base."
        )
        raise

    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            if conexion is not None:
                conexion.close()


if __name__ == "__main__":
    crear_tablas()