import heapq

# 1. BASE DE CONOCIMIENTO
servicios_ocana = {
    "Ruta Juan XXIII": [
        ("Terminal Santa Clara", 0),
        ("Hospital Emiro", 4),
        ("Juan XXIII", 7),
        ("Centro", 11),
        ("UFPSO", 18)
    ],

    "Ruta Nueva España": [
        ("Terminal Santa Clara", 0),
        ("Hospital Emiro", 4),
        ("Nueva España", 12),
        ("Centro", 15),
        ("UFPSO", 18)
    ],

    "Ruta Cristo Rey": [
        ("Terminal Santa Clara", 0),
        ("Hospital Emiro", 4),
        ("Cristo Rey", 8),
        ("Centro", 12),
        ("UFPSO", 19)
    ],

    "Ruta Circunvalar": [
        ("Terminal Santa Clara", 0),
        ("Hospital Emiro", 4),
        ("Centro", 7),
        ("Circunvalar", 12),
        ("UFPSO", 16),
        ("Batallón Santander", 19),
        ("La Ermita", 22)
    ],

    "Ruta El Llano": [
        ("Terminal Santa Clara", 0),
        ("Hospital Emiro", 4),
        ("El Llano", 7),
        ("Centro", 10),
        ("UFPSO", 17)
    ],

    "Ruta El Bambo": [
        ("Terminal Santa Clara", 0),
        ("Hospital Emiro", 4),
        ("Centro", 7),
        ("El Bambo", 11),
        ("UFPSO", 15),
        ("Batallón Santander", 18),
        ("La Ermita", 21)
    ],

    "Ruta Aguas Claras": [
        ("Terminal Santa Clara", 0),
        ("Hospital Emiro", 4),
        ("Centro", 7),
        ("Aguas Claras", 13)
    ]
}

# 2. CONSTRUCCIÓN DEL GRAFO (OPTIMIZADO)
def construir_grafo(servicios):
    grafo = {}
    for ruta, paradas in servicios.items():
        for i in range(len(paradas) - 1):
            est_a, tiempo_a = paradas[i]
            est_b, tiempo_b = paradas[i + 1]
            t = tiempo_b - tiempo_a

            grafo.setdefault(est_a, []).append({'dest': est_b, 't': t, 'ruta': ruta})
            grafo.setdefault(est_b, []).append({'dest': est_a, 't': t, 'ruta': ruta})
    return grafo

# Se construye UNA sola vez
grafo_global = construir_grafo(servicios_ocana)

# 3. HEURÍSTICA
heuristica_base = {
    'Terminal Santa Clara': 0,
    'Hospital Emiro': 1,
    'Juan XXIII': 2,
    'Nueva España': 2,
    'El Llano': 2,
    'Centro': 3,
    'Cristo Rey': 4,
    'Aguas Claras': 4,
    'Circunvalar': 5,
    'El Bambo': 5,
    'UFPSO': 6,
    'Batallón Santander': 7,
    'La Ermita': 8
}

def heuristica(nodo, destino):
    if nodo == destino:
        return 0
    valor_nodo = heuristica_base.get(nodo, 0)
    valor_destino = heuristica_base.get(destino, 0)
    return abs(valor_nodo - valor_destino)



# 4. REGLAS DEL SISTEMA.
def aplicar_reglas(nodo_actual, vecino, costo_tramo, ruta_actual, nueva_ruta):

    # Regla 1: Penalización por transbordo
    if ruta_actual and ruta_actual != nueva_ruta:
        costo_tramo += 5

    # Regla 2: Estaciones congestionadas
    estaciones_congestionadas = ["Hospital Emiro", "Centro"]
    if vecino in estaciones_congestionadas:
        costo_tramo += 3

    # Regla 3: tramos largos
    if costo_tramo > 15:
        costo_tramo += 2

    return costo_tramo


# 5. ALGORITMO
def sistema_experto_transporte(inicio, fin):

    frontera = [(heuristica(inicio, fin), 0, inicio, [(inicio, None)], None)]
    visitados = {}

    while frontera:
        f, g, actual, camino, ruta_actual = heapq.heappop(frontera)
        estado_actual = (actual, ruta_actual)

        if actual == fin:
            return camino, g

        if estado_actual in visitados and visitados[estado_actual] <= g:
            continue
        visitados[estado_actual] = g

        for conexion in grafo_global.get(actual, []):
            vecino = conexion['dest']
            costo_tramo = conexion['t']

            costo_tramo = aplicar_reglas(
                actual,
                vecino,
                costo_tramo,
                ruta_actual,
                conexion['ruta']
            )

            nuevo_g = g + costo_tramo
            nuevo_f = nuevo_g + heuristica(vecino, fin)

            heapq.heappush(
                frontera,
                (
                    nuevo_f,
                    nuevo_g,
                    vecino,
                    camino + [(vecino, conexion['ruta'])],
                    conexion['ruta']
                )
            )

    return None, 0


def detectar_transbordos(ruta):
    transbordos = []

    for i in range(1, len(ruta) - 1):
        estacion_actual, servicio_actual = ruta[i]
        _, servicio_siguiente = ruta[i + 1]

        if servicio_actual and servicio_siguiente and servicio_actual != servicio_siguiente:
            transbordos.append((estacion_actual, servicio_actual, servicio_siguiente))

    return transbordos


# 6. INTERFAZ
def menu():
    print("="*60)
    print("   SISTEMA EXPERTO DE RUTAS - OCAÑA (A*)   ")
    print("="*60)

    estaciones = sorted(grafo_global.keys())
    print("\nEstaciones disponibles:")
    for e in estaciones:
        print("-", e)

    orig = input("\nIngrese ORIGEN: ").strip()
    dest = input("Ingrese DESTINO: ").strip()

    if orig not in estaciones or dest not in estaciones:
        print("\n Error: estación no válida.")
        return

    ruta, tiempo = sistema_experto_transporte(orig, dest)

    if ruta:
        print("\n RUTA ÓPTIMA ENCONTRADA:\n")

        for i in range(len(ruta)):
            estacion, servicio = ruta[i]
            if i == 0:
                print(f" {estacion} (Inicio)")
            else:
                print(f"  └──[{servicio}]→ {estacion}")

        transbordos = detectar_transbordos(ruta)

        if transbordos:
            print("\n Transbordos realizados:")
            for estacion, ruta_origen, ruta_destino in transbordos:
                print(f"- En {estacion}: cambiar de [{ruta_origen}] a [{ruta_destino}]")
        else:
            print("\n No se realizaron transbordos.")

        print(f"\n Tiempo total estimado: {tiempo} minutos")

    else:
        print("\n No se encontró ruta.")


if __name__ == "__main__":
    menu()
