import heapq

# 1. BASE DE CONOCIMIENTO
servicios_transmilenio = {
    'B12-G12': {
        'Portal Norte': 0, 'Calle 100': 15, 'Calle 72': 22, 'Ricaurte': 35, 'Sena': 42, 'Portal Sur': 55
    },
    'F23-J23': {
        'Portal Américas': 0, 'Madelena': 10, 'Ricaurte': 25, 'Jiménez': 35, 'Aguas': 40, 'Universidades': 42
    },
    'K43-G43': {
        'Portal Dorado': 0, 'Av. Rojas': 10, 'Ricaurte': 25, 'Sena': 32, 'Portal Sur': 45
    },
    'D20-H20': {
        'Portal 80': 0, 'Calle 72': 20, 'Calle 26': 32, 'Tercer Milenio': 40, 'Molinos': 55, 'Portal Usme': 65
    },
    'C15-H15': {
        'Portal Suba': 0, 'Calle 100': 20, 'Héroes': 30, 'Calle 26': 40, 'Tercer Milenio': 48, 'Portal Tunal': 60
    }
}

# 2. CONSTRUCCIÓN DEL GRAFO (OPTIMIZADO)
def construir_grafo(servicios):
    grafo = {}
    for ruta, paradas in servicios.items():
        estaciones = list(paradas.keys())
        for i in range(len(estaciones) - 1):
            est_a, est_b = estaciones[i], estaciones[i+1]
            t = paradas[est_b] - paradas[est_a]

            grafo.setdefault(est_a, []).append({'dest': est_b, 't': t, 'ruta': ruta})
            grafo.setdefault(est_b, []).append({'dest': est_a, 't': t, 'ruta': ruta})
    return grafo

# Se construye UNA sola vez
grafo_global = construir_grafo(servicios_transmilenio)

# 3. HEURÍSTICA
heuristica_base = {
    'Portal Norte': 50, 'Calle 100': 30, 'Calle 72': 18, 'Héroes': 20,
    'Portal Américas': 40, 'Madelena': 30, 'Ricaurte': 10, 'Jiménez': 0,
    'Aguas': 2, 'Universidades': 0, 'Portal Dorado': 35, 'Av. Rojas': 25,
    'Sena': 15, 'Portal Sur': 45, 'Portal 80': 40, 'Calle 26': 5,
    'Tercer Milenio': 5, 'Molinos': 35, 'Portal Usme': 50,
    'Portal Suba': 45, 'Portal Tunal': 45
}

def heuristica(nodo, destino):
    # Ajuste simple: evita sesgo fuerte
    if nodo == destino:
        return 0
    return heuristica_base.get(nodo, 20)



# 4. REGLAS DEL SISTEMA.
def aplicar_reglas(nodo_actual, vecino, costo_tramo, ruta_actual, nueva_ruta):

    # Regla 1: Penalización por transbordo
    if ruta_actual and ruta_actual != nueva_ruta:
        costo_tramo += 5

    # Regla 2: Estaciones congestionadas
    estaciones_congestionadas = ["Ricaurte", "Jiménez", "Calle 72", "Calle 100"]
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

        if actual == fin:
            return camino, g

        if actual in visitados and visitados[actual] <= g:
            continue
        visitados[actual] = g

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


# 6. INTERFAZ
def menu():
    print("="*60)
    print("   SISTEMA EXPERTO DE RUTAS - TRANSMILENIO (A*)   ")
    print("="*60)

    estaciones = sorted(heuristica_base.keys())
    print("\nEstaciones disponibles:")
    for e in estaciones:
        print("-", e)

    orig = input("\nIngrese ORIGEN: ").strip()
    dest = input("Ingrese DESTINO: ").strip()

    if orig not in estaciones or dest not in estaciones:
        print("\n❌ Error: estación no válida.")
        return

    ruta, tiempo = sistema_experto_transporte(orig, dest)

    if ruta:
        print("\n✅ RUTA ÓPTIMA ENCONTRADA:\n")

        for i in range(len(ruta)):
            estacion, servicio = ruta[i]
            if i == 0:
                print(f"📍 {estacion} (Inicio)")
            else:
                print(f"  └──[{servicio}]→ {estacion}")

        print(f"\n⏳ Tiempo total estimado: {tiempo} minutos")

    else:
        print("\n❌ No se encontró ruta.")


if __name__ == "__main__":
    menu()