"""
Unidad 10: Grafos - Tarea
Estructura de Datos

Ejercicios:
  1. DFS iterativo
  2. Detección de ciclos en un grafo dirigido
  3. Red de tráfico (grafo ponderado) y camino de menor latencia
  4. Dijkstra devolviendo el camino exacto
  5. Grado de entrada y de salida de cada nodo
"""

import heapq
from collections import deque


class Grafo:
    def __init__(self, dirigido=False):
        """Inicializa un grafo con una lista de adyacencia (diccionario)."""
        self.adj = {}
        self.dirigido = dirigido

    def agregar_vertice(self, v):
        """Agrega un vértice al grafo."""
        if v not in self.adj:
            self.adj[v] = []

    def agregar_arista(self, u, v):
        """Agrega una arista entre u y v."""
        self.agregar_vertice(u)
        self.agregar_vertice(v)

        self.adj[u].append(v)
        if not self.dirigido:
            self.adj[v].append(u)

    def vecinos(self, v):
        """Retorna los vecinos de un vértice."""
        return self.adj.get(v, [])

    def bfs(self, inicio):
        """Recorrido en Anchura."""
        visitados = set()
        cola = deque([inicio])
        resultado = []

        visitados.add(inicio)

        while cola:
            actual = cola.popleft()
            resultado.append(actual)

            for vecino in self.vecinos(actual):
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.append(vecino)

        return resultado

    def dfs(self, inicio, visitados=None, resultado=None):
        """Recorrido en Profundidad (Recursivo)."""
        if visitados is None:
            visitados = set()
            resultado = []

        visitados.add(inicio)
        resultado.append(inicio)

        for vecino in self.vecinos(inicio):
            if vecino not in visitados:
                self.dfs(vecino, visitados, resultado)

        return resultado

    def mostrar(self):
        """Muestra el grafo."""
        for v, vecinos in self.adj.items():
            print(f"{v} -> {vecinos}")

    # ------------------------------------------------------------------
    # EJERCICIO 1: DFS iterativo
    # ------------------------------------------------------------------
    def dfs_iterativo(self, inicio):
        """
        Recorrido en profundidad usando una pila explícita (sin recursión).
        Devuelve el mismo orden que el DFS recursivo.
        """
        if inicio not in self.adj:
            raise ValueError(f"El vértice '{inicio}' no existe en el grafo")

        visitados = set()
        pila = [inicio]
        resultado = []

        while pila:
            actual = pila.pop()

            # Un vértice puede entrar a la pila más de una vez,
            # así que se revisa al sacarlo.
            if actual in visitados:
                continue

            visitados.add(actual)
            resultado.append(actual)

            # Se apilan en orden inverso para que el primer vecino
            # de la lista sea el primero en salir (igual que el recursivo).
            for vecino in reversed(self.vecinos(actual)):
                if vecino not in visitados:
                    pila.append(vecino)

        return resultado

    # ------------------------------------------------------------------
    # EJERCICIO 2: Detectar ciclos en un grafo dirigido
    # ------------------------------------------------------------------
    def tiene_ciclo(self):
        """
        Retorna True si el grafo dirigido tiene al menos un ciclo.

        Se usa DFS con tres colores:
          BLANCO = no visitado
          GRIS   = en el camino actual (todavía en la pila)
          NEGRO  = ya terminado por completo
        Si desde un vértice se llega a uno GRIS, hay una arista que
        regresa por el camino actual, o sea, un ciclo.
        """
        if not self.dirigido:
            raise ValueError("tiene_ciclo está pensado para grafos dirigidos")

        BLANCO, GRIS, NEGRO = 0, 1, 2
        color = {v: BLANCO for v in self.adj}

        # Se prueba desde cada vértice por si el grafo no es conexo
        for raiz in self.adj:
            if color[raiz] != BLANCO:
                continue

            color[raiz] = GRIS
            pila = [(raiz, iter(self.vecinos(raiz)))]

            while pila:
                nodo, iterador = pila[-1]

                for vecino in iterador:
                    if color[vecino] == GRIS:
                        return True  # arista de retorno -> ciclo
                    if color[vecino] == BLANCO:
                        color[vecino] = GRIS
                        pila.append((vecino, iter(self.vecinos(vecino))))
                        break  # se baja a explorar el vecino
                else:
                    # Ya no quedan vecinos por revisar: el nodo termina
                    color[nodo] = NEGRO
                    pila.pop()

        return False

    # ------------------------------------------------------------------
    # EJERCICIO 5: Grado de entrada y de salida
    # ------------------------------------------------------------------
    def grados(self):
        """
        Retorna un diccionario {vértice: (grado_entrada, grado_salida)}.
        En un grafo no dirigido ambos valores coinciden con el grado.
        """
        entrada = {v: 0 for v in self.adj}
        salida = {v: 0 for v in self.adj}

        for u in self.adj:
            for v in self.vecinos(u):
                salida[u] += 1
                entrada[v] += 1

        return {v: (entrada[v], salida[v]) for v in self.adj}

    def mostrar_grados(self):
        """Imprime el grado de entrada y de salida de cada vértice."""
        print(f"{'Vértice':<10}{'Entrada':>8}{'Salida':>8}")
        for v, (ent, sal) in self.grados().items():
            print(f"{str(v):<10}{ent:>8}{sal:>8}")


class GrafoPonderado(Grafo):
    def __init__(self, dirigido=False):
        super().__init__(dirigido)
        # adj: dict donde la clave es el vértice y el valor es una lista
        # de tuplas (vecino, peso)

    def agregar_arista(self, u, v, peso):
        if peso < 0:
            raise ValueError("Dijkstra no funciona con pesos negativos")

        self.agregar_vertice(u)
        self.agregar_vertice(v)

        self.adj[u].append((v, peso))
        if not self.dirigido:
            self.adj[v].append((u, peso))

    def vecinos(self, v):
        """Retorna los vecinos de un vértice sin el peso para compatibilidad."""
        return [vecino for vecino, peso in self.adj.get(v, [])]

    def mostrar(self):
        """Muestra el grafo con los pesos."""
        for v, vecinos in self.adj.items():
            print(f"{v} -> {vecinos}")

    def dijkstra(self, inicio):
        """
        Calcula el camino más corto desde 'inicio' a todos los demás vértices.
        """
        distancias = {v: float('infinity') for v in self.adj}
        distancias[inicio] = 0
        pq = [(0, inicio)]  # (distancia, vertice)

        while pq:
            dist_actual, actual = heapq.heappop(pq)

            if dist_actual > distancias[actual]:
                continue

            for vecino, peso in self.adj.get(actual, []):
                distancia = dist_actual + peso

                if distancia < distancias[vecino]:
                    distancias[vecino] = distancia
                    heapq.heappush(pq, (distancia, vecino))

        return distancias

    # ------------------------------------------------------------------
    # EJERCICIO 4: Dijkstra con reconstrucción del camino
    # ------------------------------------------------------------------
    def dijkstra_con_predecesores(self, inicio):
        """
        Igual que dijkstra(), pero además guarda de qué vértice se llegó
        a cada uno por su mejor camino. Retorna (distancias, previos).
        """
        if inicio not in self.adj:
            raise ValueError(f"El vértice '{inicio}' no existe en el grafo")

        distancias = {v: float('infinity') for v in self.adj}
        previos = {v: None for v in self.adj}
        distancias[inicio] = 0
        pq = [(0, inicio)]

        while pq:
            dist_actual, actual = heapq.heappop(pq)

            if dist_actual > distancias[actual]:
                continue

            for vecino, peso in self.adj.get(actual, []):
                distancia = dist_actual + peso

                if distancia < distancias[vecino]:
                    distancias[vecino] = distancia
                    previos[vecino] = actual
                    heapq.heappush(pq, (distancia, vecino))

        return distancias, previos

    def camino_mas_corto(self, inicio, destino):
        """
        Retorna (distancia, camino) donde camino es la lista exacta de
        nodos desde 'inicio' hasta 'destino'.
        Si no hay ruta posible retorna (infinito, []).
        """
        if destino not in self.adj:
            raise ValueError(f"El vértice '{destino}' no existe en el grafo")

        distancias, previos = self.dijkstra_con_predecesores(inicio)

        if distancias[destino] == float('infinity'):
            return float('infinity'), []

        # Se reconstruye desde el destino hacia atrás y luego se invierte
        camino = []
        actual = destino
        while actual is not None:
            camino.append(actual)
            actual = previos[actual]
        camino.reverse()

        return distancias[destino], camino


# ======================================================================
# DEMOSTRACIONES
# ======================================================================

def titulo(texto):
    print("\n" + "=" * 60)
    print(texto)
    print("=" * 60)


def ejercicio_1():
    titulo("EJERCICIO 1: DFS iterativo")

    g = Grafo()
    g.agregar_arista('A', 'B')
    g.agregar_arista('A', 'C')
    g.agregar_arista('B', 'D')
    g.agregar_arista('C', 'D')
    g.agregar_arista('D', 'E')

    recursivo = g.dfs('A')
    iterativo = g.dfs_iterativo('A')

    print("DFS recursivo :", recursivo)
    print("DFS iterativo :", iterativo)
    assert recursivo == iterativo

    # Vértice aislado
    g.agregar_vertice('Z')
    print("DFS desde Z   :", g.dfs_iterativo('Z'))
    assert g.dfs_iterativo('Z') == ['Z']

    # Vértice que no existe
    try:
        g.dfs_iterativo('X')
    except ValueError as e:
        print("Error esperado:", e)


def ejercicio_2():
    titulo("EJERCICIO 2: Detección de ciclos (grafo dirigido)")

    # Sin ciclos (DAG)
    dag = Grafo(dirigido=True)
    dag.agregar_arista('A', 'B')
    dag.agregar_arista('A', 'C')
    dag.agregar_arista('B', 'D')
    dag.agregar_arista('C', 'D')
    print("DAG (A->B, A->C, B->D, C->D) tiene ciclo:", dag.tiene_ciclo())
    assert dag.tiene_ciclo() is False

    # Con ciclo A -> B -> D -> A
    dag.agregar_arista('D', 'A')
    print("Se agrega D->A, tiene ciclo:", dag.tiene_ciclo())
    assert dag.tiene_ciclo() is True

    # Casos límite
    vacio = Grafo(dirigido=True)
    print("Grafo vacío tiene ciclo:", vacio.tiene_ciclo())
    assert vacio.tiene_ciclo() is False

    lazo = Grafo(dirigido=True)
    lazo.agregar_arista('X', 'X')
    print("Lazo X->X tiene ciclo:", lazo.tiene_ciclo())
    assert lazo.tiene_ciclo() is True

    # Grafo no conexo: el ciclo está en la segunda componente
    nc = Grafo(dirigido=True)
    nc.agregar_arista('A', 'B')
    nc.agregar_arista('M', 'N')
    nc.agregar_arista('N', 'M')
    print("No conexo, ciclo M<->N:", nc.tiene_ciclo())
    assert nc.tiene_ciclo() is True


def ejercicio_3():
    titulo("EJERCICIO 3: Red de tráfico - camino de menor latencia")

    # Los pesos son latencias en milisegundos
    red = GrafoPonderado()
    red.agregar_arista('Cliente', 'Router1', 5)
    red.agregar_arista('Cliente', 'Router2', 12)
    red.agregar_arista('Router1', 'Router2', 4)
    red.agregar_arista('Router1', 'Switch', 10)
    red.agregar_arista('Router2', 'Switch', 3)
    red.agregar_arista('Router2', 'Firewall', 8)
    red.agregar_arista('Firewall', 'Servidor', 3)
    red.agregar_arista('Switch', 'Servidor', 7)

    print("Red (vecino, latencia en ms):")
    red.mostrar()

    latencia, ruta = red.camino_mas_corto('Cliente', 'Servidor')
    print(f"\nMenor latencia Cliente -> Servidor: {latencia} ms")
    print("Ruta:", " -> ".join(ruta))
    assert latencia == 19
    assert ruta == ['Cliente', 'Router1', 'Router2', 'Switch', 'Servidor']

    print("\nLatencia mínima desde Cliente a todos los nodos:")
    for nodo, d in red.dijkstra('Cliente').items():
        print(f"  {nodo:<10} {d} ms")


def ejercicio_4():
    titulo("EJERCICIO 4: Dijkstra con camino exacto")

    # Grafo del Ejemplo 4 de la unidad
    gp = GrafoPonderado()
    gp.agregar_arista('A', 'B', 4)
    gp.agregar_arista('A', 'C', 2)
    gp.agregar_arista('C', 'B', 1)
    gp.agregar_arista('B', 'D', 5)

    print("Distancias desde A:", gp.dijkstra('A'))

    distancia, camino = gp.camino_mas_corto('A', 'D')
    print(f"A -> D: distancia {distancia}, camino {camino}")
    assert distancia == 8
    assert camino == ['A', 'C', 'B', 'D']

    # Origen = destino
    d, c = gp.camino_mas_corto('A', 'A')
    print(f"A -> A: distancia {d}, camino {c}")
    assert (d, c) == (0, ['A'])

    # Destino inalcanzable
    gp.agregar_vertice('Isla')
    d, c = gp.camino_mas_corto('A', 'Isla')
    print(f"A -> Isla: distancia {d}, camino {c}")
    assert c == []

    # Grafo dirigido: solo existe ruta en un sentido
    gd = GrafoPonderado(dirigido=True)
    gd.agregar_arista('P', 'Q', 3)
    print("Dirigido P -> Q:", gd.camino_mas_corto('P', 'Q'))
    print("Dirigido Q -> P:", gd.camino_mas_corto('Q', 'P'))

    # Peso negativo
    try:
        gp.agregar_arista('A', 'D', -1)
    except ValueError as e:
        print("Error esperado:", e)


def ejercicio_5():
    titulo("EJERCICIO 5: Grado de entrada y de salida")

    g = Grafo(dirigido=True)
    g.agregar_arista('A', 'B')
    g.agregar_arista('A', 'C')
    g.agregar_arista('B', 'C')
    g.agregar_arista('C', 'A')
    g.agregar_arista('C', 'D')

    g.mostrar()
    print()
    g.mostrar_grados()

    assert g.grados() == {
        'A': (1, 2),
        'B': (1, 1),
        'C': (2, 2),
        'D': (1, 0),
    }


if __name__ == "__main__":
    ejercicio_1()
    ejercicio_2()
    ejercicio_3()
    ejercicio_4()
    ejercicio_5()
    print("\nTodas las pruebas pasaron correctamente.")
