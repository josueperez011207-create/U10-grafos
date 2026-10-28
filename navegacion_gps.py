"""
Mini-Proyecto Unidad 10: Sistema de Navegación GPS

Modela ciudades (nodos) y autopistas (aristas ponderadas por tiempo en
minutos). Permite ver las ciudades, ver las rutas, agregar rutas nuevas
y consultar la ruta más rápida entre dos ciudades con el recorrido completo.

Los tiempos de las rutas precargadas son aproximados y solo sirven
como datos de ejemplo.
"""

import heapq
import unicodedata


class CiudadNoEncontradaError(Exception):
    """Se lanza cuando se busca una ciudad que no está en el mapa."""


def normalizar(texto):
    """
    Pasa el texto a minúsculas, sin tildes y sin espacios de más.
    Sirve para que 'León', 'leon' y '  LEON ' se traten como la misma ciudad.
    """
    descompuesto = unicodedata.normalize("NFD", texto)
    sin_tildes = "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")
    return " ".join(sin_tildes.lower().split())


def formatear_tiempo(minutos):
    """Convierte minutos a un texto legible: 45 min, 2 h, 1 h 15 min."""
    horas, resto = divmod(minutos, 60)
    if horas == 0:
        return f"{resto} min"
    if resto == 0:
        return f"{horas} h"
    return f"{horas} h {resto} min"


# ======================================================================
# GRAFO PONDERADO
# ======================================================================

class MapaGPS:
    """
    Grafo ponderado no dirigido con lista de adyacencia.

    adj = {ciudad: {ciudad_vecina: minutos}}
    Se usa un diccionario por ciudad para que, si se vuelve a agregar una
    ruta que ya existe, el tiempo se actualice en lugar de duplicarse.
    """

    def __init__(self):
        self.adj = {}
        self._indice = {}  # nombre normalizado -> nombre tal como se guardó

    # ---------------- ciudades ----------------

    def agregar_ciudad(self, nombre):
        """Agrega una ciudad (si no existe) y retorna su nombre guardado."""
        clave = normalizar(nombre)
        if not clave:
            raise ValueError("El nombre de la ciudad no puede estar vacío")

        if clave not in self._indice:
            nombre_limpio = " ".join(nombre.split())
            self._indice[clave] = nombre_limpio
            self.adj[nombre_limpio] = {}
        return self._indice[clave]

    def buscar_ciudad(self, nombre):
        """Retorna el nombre guardado de la ciudad o lanza error si no existe."""
        clave = normalizar(nombre)
        if not clave:
            raise ValueError("El nombre de la ciudad no puede estar vacío")
        if clave not in self._indice:
            raise CiudadNoEncontradaError(f"La ciudad '{nombre.strip()}' no existe en el mapa")
        return self._indice[clave]

    def listar_ciudades(self):
        """Retorna las ciudades en orden alfabético."""
        return sorted(self.adj, key=normalizar)

    # ---------------- rutas ----------------

    def agregar_ruta(self, origen, destino, minutos):
        """
        Agrega una autopista entre dos ciudades (en ambos sentidos).
        Si alguna ciudad no existe, se crea.
        Retorna el tiempo anterior si la ruta ya existía, o None si es nueva.
        """
        if isinstance(minutos, bool) or not isinstance(minutos, int):
            raise ValueError("El tiempo debe ser un número entero de minutos")
        if minutos <= 0:
            raise ValueError("El tiempo debe ser mayor que cero")
        if normalizar(origen) == normalizar(destino):
            raise ValueError("El origen y el destino no pueden ser la misma ciudad")

        a = self.agregar_ciudad(origen)
        b = self.agregar_ciudad(destino)

        anterior = self.adj[a].get(b)
        self.adj[a][b] = minutos
        self.adj[b][a] = minutos
        return anterior

    def tiempo_entre(self, a, b):
        """Tiempo de la autopista directa entre dos ciudades vecinas."""
        return self.adj[a][b]

    def listar_rutas(self):
        """Retorna una lista de (ciudad1, ciudad2, minutos) sin repetir."""
        rutas = []
        vistas = set()
        for a in self.listar_ciudades():
            for b, minutos in sorted(self.adj[a].items(), key=lambda x: normalizar(x[0])):
                par = frozenset((a, b))
                if par not in vistas:
                    vistas.add(par)
                    rutas.append((a, b, minutos))
        return rutas

    # ---------------- Dijkstra ----------------

    def ruta_mas_rapida(self, origen, destino):
        """
        Calcula la ruta más rápida entre dos ciudades con Dijkstra.

        Retorna (minutos, camino) donde camino es la lista completa de
        ciudades desde el origen hasta el destino.
        Si no existe ninguna ruta retorna (None, []).
        """
        origen = self.buscar_ciudad(origen)
        destino = self.buscar_ciudad(destino)

        infinito = float("inf")
        tiempos = {ciudad: infinito for ciudad in self.adj}
        previos = {}  # ciudad -> ciudad desde la que se llegó por el mejor camino
        tiempos[origen] = 0
        cola = [(0, origen)]  # (tiempo acumulado, ciudad)

        while cola:
            tiempo_actual, actual = heapq.heappop(cola)

            # Entrada vieja: ya se encontró un camino mejor a esta ciudad
            if tiempo_actual > tiempos[actual]:
                continue

            # Con pesos positivos, la primera vez que se saca el destino
            # de la cola ya es su distancia mínima
            if actual == destino:
                break

            for vecino, minutos in self.adj[actual].items():
                nuevo_tiempo = tiempo_actual + minutos
                if nuevo_tiempo < tiempos[vecino]:
                    tiempos[vecino] = nuevo_tiempo
                    previos[vecino] = actual
                    heapq.heappush(cola, (nuevo_tiempo, vecino))

        if tiempos[destino] == infinito:
            return None, []

        # Reconstrucción del camino: se camina hacia atrás con 'previos'
        camino = [destino]
        while camino[-1] != origen:
            camino.append(previos[camino[-1]])
        camino.reverse()

        return tiempos[destino], camino


# ======================================================================
# INTERFAZ DE CONSOLA
# ======================================================================

def crear_mapa_inicial():
    """Carga un mapa de ejemplo con ciudades de Nicaragua."""
    mapa = MapaGPS()
    rutas = [
        ("Managua", "Masaya", 30),
        ("Managua", "Granada", 50),
        ("Masaya", "Granada", 25),
        ("Granada", "Rivas", 70),
        ("Managua", "Rivas", 100),
        ("Managua", "León", 75),
        ("León", "Chinandega", 40),
        ("Managua", "Matagalpa", 120),
        ("Matagalpa", "Jinotega", 45),
        ("Matagalpa", "Estelí", 80),
        ("Managua", "Estelí", 150),
        ("Managua", "Juigalpa", 105),
    ]
    for origen, destino, minutos in rutas:
        mapa.agregar_ruta(origen, destino, minutos)
    return mapa


def mostrar_menu():
    print("\n" + "=" * 40)
    print("      SISTEMA DE NAVEGACIÓN GPS")
    print("=" * 40)
    print("1. Ver ciudades")
    print("2. Ver rutas (autopistas)")
    print("3. Agregar nueva ruta")
    print("4. Consultar ruta más rápida")
    print("5. Salir")


def opcion_ver_ciudades(mapa):
    ciudades = mapa.listar_ciudades()
    print(f"\nCiudades registradas ({len(ciudades)}):")
    for i, ciudad in enumerate(ciudades, start=1):
        print(f"  {i}. {ciudad}")


def opcion_ver_rutas(mapa):
    rutas = mapa.listar_rutas()
    if not rutas:
        print("\nTodavía no hay rutas registradas.")
        return

    print(f"\nRutas registradas ({len(rutas)}):")
    for a, b, minutos in rutas:
        print(f"  {a} <-> {b}: {formatear_tiempo(minutos)}")


def opcion_agregar_ruta(mapa):
    print("\n--- Agregar nueva ruta ---")
    print("(Si una ciudad no existe se crea automáticamente)")
    origen = input("Ciudad de origen: ")
    destino = input("Ciudad de destino: ")
    texto_tiempo = input("Tiempo en minutos: ").strip()

    try:
        minutos = int(texto_tiempo)
    except ValueError:
        raise ValueError("El tiempo debe ser un número entero de minutos")

    anterior = mapa.agregar_ruta(origen, destino, minutos)
    a = mapa.buscar_ciudad(origen)
    b = mapa.buscar_ciudad(destino)

    if anterior is None:
        print(f"\nRuta agregada: {a} <-> {b} ({formatear_tiempo(minutos)})")
    else:
        print(f"\nLa ruta ya existía. Tiempo actualizado de "
              f"{formatear_tiempo(anterior)} a {formatear_tiempo(minutos)}.")


def opcion_consultar_ruta(mapa):
    print("\n--- Consultar ruta más rápida ---")
    print("Ciudades disponibles: " + ", ".join(mapa.listar_ciudades()))
    origen = input("Ciudad de origen: ")
    destino = input("Ciudad de destino: ")

    minutos, camino = mapa.ruta_mas_rapida(origen, destino)

    if minutos is None:
        a = mapa.buscar_ciudad(origen)
        b = mapa.buscar_ciudad(destino)
        print(f"\nNo existe ninguna ruta entre {a} y {b}.")
        return

    if len(camino) == 1:
        print(f"\nYa estás en {camino[0]}. Tiempo: 0 min")
        return

    print("\nRuta más rápida: " + " -> ".join(camino))
    for a, b in zip(camino, camino[1:]):
        print(f"  {a} -> {b}: {formatear_tiempo(mapa.tiempo_entre(a, b))}")
    print(f"Tiempo total: {formatear_tiempo(minutos)}")


def main():
    mapa = crear_mapa_inicial()
    acciones = {
        "1": opcion_ver_ciudades,
        "2": opcion_ver_rutas,
        "3": opcion_agregar_ruta,
        "4": opcion_consultar_ruta,
    }

    while True:
        mostrar_menu()
        try:
            opcion = input("Elige una opción: ").strip()

            if opcion == "5":
                print("\n¡Buen viaje!")
                break

            accion = acciones.get(opcion)
            if accion is None:
                print("\nOpción no válida. Elige un número del 1 al 5.")
                continue

            accion(mapa)

        except (ValueError, CiudadNoEncontradaError) as error:
            print(f"\nError: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\n\nSaliendo del programa...")
            break


if __name__ == "__main__":
    main()
