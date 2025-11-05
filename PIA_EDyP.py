import sqlite3
from sqlite3 import Error
from datetime import datetime
import random
import sys
import pandas as pd
import os

def crear_tablas():
    """Crea las tablas necesarias si no existen."""
    try:
        with sqlite3.connect("AFIS_UANL.db") as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Alumnos (
                    matricula INTEGER PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    carrera TEXT NOT NULL,
                    semestre INTEGER NOT NULL
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Actividades (
                    clave INTEGER PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    tipo_afi TEXT NOT NULL
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS RegistroAFI (
                    folio INTEGER PRIMARY KEY,
                    matricula INTEGER NOT NULL,
                    clave_actividad INTEGER NOT NULL,
                    fecha TIMESTAMP NOT NULL,
                    oficial INTEGER NOT NULL CHECK (oficial IN (0, 1)),
                    FOREIGN KEY (matricula) REFERENCES Alumnos(matricula),
                    FOREIGN KEY (clave_actividad) REFERENCES Actividades(clave)
                );
            """)

            print("Tablas creadas correctamente.")
    except Error as e:
        print(f"Error al crear tablas: {e}")

def registrar_alumno():
    """Registra un nuevo alumno."""
    while True:
        nombre = input("Nombre del alumno: ").strip()
        if not nombre or any(char.isdigit() for char in nombre):
            print("El nombre no puede estar vacío ni contener números.")
            continue
        break

    while True:
        carrera = input("Carrera: ").strip()
        if carrera.replace(" ", "").isalpha():
            break
        else:
            print("La carrera no puede contener números ni símbolos. Intenta nuevamente.")

    while True:
        try:
            semestre = int(input("Semestre actual (1-10): "))
            if 1 <= semestre <= 10:
                break
            else:
                print("El semestre debe estar entre 1 y 10.")
        except ValueError:
            print("Ingresa un número válido.")

    matricula = random.randint(1000000, 2999999)

    try:
        with sqlite3.connect("AFIS_UANL.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Alumnos (matricula, nombre, carrera, semestre)
                VALUES (?, ?, ?, ?)
            """, (matricula, nombre, carrera, semestre))
            conn.commit()
            print(f"Alumno registrado correctamente. Matrícula: {matricula}")
    except Error as e:
        print(f"Error al registrar alumno: {e}")

def registrar_actividad():
    """Registra una nueva AFI en el sistema."""
    while True:
        nombre = input("Nombre de la actividad AFI: ").strip()
        if not nombre or any(char.isdigit() for char in nombre):
            print("El nombre no puede estar vacío ni contener números.")
            continue
        break

    tipos_validos = [
        "Académicas",
        "Artísticas",
        "Culturales",
        "Deportivas",
        "Responsabilidad Social",
        "Innovación y Emprendimiento",
        "Investigación",
        "Idiomas"
    ]

    print("\nTipos válidos de AFI:")
    for i, tipo in enumerate(tipos_validos, start=1):
        print(f"{i}. {tipo}")

    try:
        opcion = int(input("\nSelecciona el número del tipo de AFI: "))
        if 1 <= opcion <= len(tipos_validos):
            tipo = tipos_validos[opcion - 1]
        else:
            print("Opción no válida.")
            return
    except ValueError:
        print("Ingresa un número válido.")
        return

    clave = random.randint(100, 999)
    try:
        with sqlite3.connect("AFIS_UANL.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Actividades (clave, nombre, tipo_afi)
                VALUES (?, ?, ?)
            """, (clave, nombre, tipo))
            conn.commit()
            print(f"Actividad '{nombre}' registrada correctamente. Clave: {clave}")
    except Error as e:
        print(f"Error al registrar actividad: {e}")

def registrar_participacion():
    """Registra participación y determina si cuenta como oficial o no."""
    try:
        matricula = int(input("Matrícula del alumno: "))
    except ValueError:
        print("Matrícula inválida.")
        return

    try:
        with sqlite3.connect("AFIS_UANL.db") as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM Alumnos WHERE matricula = ?", (matricula,))
            alumno = cursor.fetchone()
            if not alumno:
                print("Esa matrícula no existe. Inténtalo de nuevo.")
                return

            clave = int(input("Clave de la actividad: "))

            cursor.execute("SELECT tipo_afi FROM Actividades WHERE clave = ?", (clave,))
            actividad = cursor.fetchone()
            if not actividad:
                print("No existe una actividad con esa clave.")
                return

            tipo_afi = actividad[0]
            fecha = datetime.now()

            cursor.execute("""
                SELECT COUNT(*) FROM RegistroAFI r
                JOIN Actividades a ON r.clave_actividad = a.clave
                WHERE r.matricula = ? AND a.tipo_afi = ? AND r.oficial = 1
            """, (matricula, tipo_afi))
            cantidad = cursor.fetchone()[0]

            oficial = 1 if cantidad == 0 else 0

            cursor.execute("""
                INSERT INTO RegistroAFI (folio, matricula, clave_actividad, fecha, oficial)
                VALUES (?, ?, ?, ?, ?)
            """, (random.randint(1, 99999), matricula, clave, fecha, oficial))
            conn.commit()

            if oficial:
                print(f"Participación registrada con asistencia oficial ({tipo_afi}).")
            else:
                print(f"Participación registrada, pero NO con asistencia oficial (ya tenía una AFI de tipo {tipo_afi}).")

    except Error as e:
        print(f"Error al registrar participación: {e}")

def consultar_registros_alumno():
    """Consulta todas las AFI registradas de un alumno."""
    try:
        matricula = int(input("Matrícula del alumno: "))
    except ValueError:
        print("Matrícula inválida.")
        return

    try:
        with sqlite3.connect("AFIS_UANL.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.nombre, act.nombre, act.tipo_afi, r.fecha, r.oficial
                FROM RegistroAFI r
                JOIN Alumnos a ON r.matricula = a.matricula
                JOIN Actividades act ON r.clave_actividad = act.clave
                WHERE a.matricula = ?
            """, (matricula,))
            registros = cursor.fetchall()

            if registros:
                print("\nActividades registradas:")
                print("----------------------------------------------------")
                for nombre, actividad, tipo, fecha, oficial in registros:
                    estado = "Oficial" if oficial == 1 else "No oficial"
                    print(f"{actividad} ({tipo}) | {fecha[:16]} | {estado}")
                print("----------------------------------------------------")
            else:
                print("No hay registros para esa matrícula.")
    except Error as e:
        print(f"Error al consultar registros: {e}")

def eliminar_alumno():
    """Elimina un alumno y sus registros relacionados."""
    try:
        matricula = int(input("Matrícula del alumno a eliminar: "))
    except ValueError:
        print("Matrícula inválida.")
        return

    try:
        with sqlite3.connect("AFIS_UANL.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Alumnos WHERE matricula = ?", (matricula,))
            alumno = cursor.fetchone()
            if not alumno:
                print("No existe un alumno con esa matrícula.")
                return

            cursor.execute("DELETE FROM RegistroAFI WHERE matricula = ?", (matricula,))
            cursor.execute("DELETE FROM Alumnos WHERE matricula = ?", (matricula,))
            conn.commit()
            print("Alumno y registros asociados eliminados correctamente.")
    except Error as e:
        print(f" Error al eliminar alumno: {e}")

def exportar_excel():
    """Exporta toda la información a Excel."""
    try:
        with sqlite3.connect("AFIS_UANL.db") as conn:
            query = """
            SELECT 
                r.folio AS Folio,
                a.matricula AS Matricula,
                a.nombre AS Alumno,
                a.carrera AS Carrera,
                a.semestre AS Semestre,
                act.clave AS ClaveActividad,
                act.nombre AS Actividad,
                act.tipo_afi AS TipoAFI,
                r.fecha AS FechaRegistro,
                CASE r.oficial WHEN 1 THEN 'Sí' ELSE 'No' END AS AsistenciaOficial
            FROM RegistroAFI r
            JOIN Alumnos a ON r.matricula = a.matricula
            JOIN Actividades act ON r.clave_actividad = act.clave
            ORDER BY a.matricula, r.fecha;
            """

            df = pd.read_sql_query(query, conn)

            if df.empty:
                print("No hay registros para exportar.")
                return

            nombre_archivo = "Registro_AFIS_Exportado.xlsx"
            df.to_excel(nombre_archivo, index=False)
            print(f"Datos exportados correctamente a '{nombre_archivo}'.")

            if os.name == "nt":
                os.startfile(nombre_archivo)
    except Error as e:
        print(f"Error al exportar datos: {e}")
        
def eliminar_afi():
    try:
        clave = int(input("Clave de la AFI que deseas eliminar: "))
        with sqlite3.connect("AFIS_UANL.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM Actividades WHERE clave = ?", (clave,))
            afi = cursor.fetchone()
            if not afi:
                print("No existe una AFI con esa clave.")
                return

            cursor.execute("SELECT COUNT(*) FROM RegistroAFI WHERE clave_actividad = ?", (clave,))
            participaciones = cursor.fetchone()[0]

            if participaciones > 0:
                print(f"La AFI '{afi[0]}' tiene {participaciones} registro(s) de participación.")
                print("Si la eliminas, se borrarán TODOS esos registros permanentemente.")
                confirm = input("¿Estás completamente seguro de que deseas eliminar esta AFI? (s/n): ").strip().lower()
                if confirm != "s":
                    print("Operación cancelada.")
                    return

                cursor.execute("DELETE FROM RegistroAFI WHERE clave_actividad = ?", (clave,))
            else:
                confirm = input(f"¿Seguro que deseas eliminar la AFI '{afi[0]}'? (s/n): ").strip().lower()
                if confirm != "s":
                    print("Operación cancelada.")
                    return

            cursor.execute("DELETE FROM Actividades WHERE clave = ?", (clave,))
            conn.commit()
            print(f"AFI '{afi[0]}' eliminada correctamente junto con sus registros asociados (si los tenía).")

    except ValueError:
        print("Ingresa una clave válida (número).")
    except Error as e:
        print(f"Error al eliminar AFI: {e}")

def eliminar_registro_participacion():
    try:
        folio = int(input("Folio del registro de participación a eliminar: "))
        with sqlite3.connect("AFIS_UANL.db") as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT r.folio, a.nombre, act.nombre
                FROM RegistroAFI r
                JOIN Alumnos a ON r.matricula = a.matricula
                JOIN Actividades act ON r.clave_actividad = act.clave
                WHERE r.folio = ?
            """, (folio,))
            registro = cursor.fetchone()

            if not registro:
                print("No existe un registro con ese folio.")
                return

            print(f"Registro encontrado:\n Alumno: {registro[1]}\n Actividad: {registro[2]}")
            confirm = input("¿Deseas eliminar este registro? (s/n): ").strip().lower()
            if confirm != "s":
                print("Operación cancelada.")
                return

            cursor.execute("DELETE FROM RegistroAFI WHERE folio = ?", (folio,))
            conn.commit()
            print("Registro eliminado correctamente.")
            
    except ValueError:
        print("Ingresa un número válido para el folio.")
    except Error as e:
        print(f"Error al eliminar registro: {e}")

#MENU PRINCIPAL
def menu():
    """Menú principal."""
    while True:
        print("\n**** SISTEMA DE REGISTRO DE AFIS UANL ****")
        print("1. Registrar alumno")
        print("2. Registrar AFI")
        print("3. Registrar participación en afi")
        print("4. Consultar registro de un alumno")
        print("5. Eliminar alumno")
        print("6. Eiminar registro de participación de afi")
        print("7. Eliminar AFI")
        print("8. Exportar todos los registros a Excel")
        print("9. Salir")

        try:
            opcion = int(input("Selecciona una opción (1-9): "))
            if opcion == 1:
                registrar_alumno()
            elif opcion == 2:
                registrar_actividad()
            elif opcion == 3:
                registrar_participacion()
            elif opcion == 4:
                consultar_registros_alumno()
            elif opcion == 5:
                eliminar_alumno()
            elif opcion == 6:
                eliminar_registro_participacion()
            elif opcion == 7:
                eliminar_afi()
            elif opcion == 8:
                exportar_excel()
            elif opcion == 9:
                print("Saliendo del programa...")
                sys.exit()
            else:
                print("Opción no válida.")
        except ValueError:
            print("Por favor ingresa un número válido.")

if __name__ == "__main__":
    crear_tablas()
    menu()