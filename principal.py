import threading
from pymongo import MongoClient

tiempos_comida = {
    "barbacoa": 4,
    "quesadilla": 3,
    "bebida": 1,
    "consome": 2
}

def obtener_tiempo_total(orden):
    tiempo_total = 0
    for comida, cantidad in orden.items():
        tiempo_total += tiempos_comida[comida] * cantidad
    return tiempo_total

def escribir_base_de_datos(hilo_id, num_comanda, barbacoa, quesadilla, bebida, consome):
    tiempo_pedido = obtener_tiempo_total({
        "barbacoa": barbacoa,
        "quesadilla": quesadilla,
        "bebida": bebida,
        "consome": consome
    })

    client = MongoClient("mongodb+srv://danielxp:maspormasDF1@cluster0.glu8e4r.mongodb.net/?retryWrites=true&w=majority")
    db = client["danielxp88"]
    comandas_collection = db["comandas"]

    comanda = {
        "num_comanda": num_comanda,
        "barbacoa": barbacoa,
        "quesadilla": quesadilla,
        "bebida": bebida,
        "consome": consome,
        "tiempo_pedido": tiempo_pedido
    }
    result = comandas_collection.insert_one(comanda)
    print(f"Hilo {hilo_id}: Comanda insertada con ID: {result.inserted_id}")
    print(f"El tiempo estimado de preparación para la Comanda {num_comanda} es de {tiempo_pedido} segundos.")
    client.close()

def mostrar_datos_filtradas(opcion_filtrado):
    client = MongoClient("mongodb+srv://danielxp:maspormasDF1@cluster0.glu8e4r.mongodb.net/?retryWrites=true&w=majority")
    db = client["danielxp88"]
    comandas_collection = db["comandas"]

    print("-------------------------------------------------")
    print("Datos en la base de datos:")

    if opcion_filtrado == "1":
        comandas = comandas_collection.find()
    elif opcion_filtrado == "2":
        comandas = comandas_collection.find({"completado": True})
    elif opcion_filtrado == "3":
        comandas = comandas_collection.find({"$or": [{"completado": False}, {"completado": {"$exists": False}}]})
    else:
        print("Opción no válida.")
        client.close()
        return

    for comanda in comandas:
        print("ID:", comanda["_id"])
        print("Número de Comanda:", comanda["num_comanda"])
        print("Barbacoa:", comanda["barbacoa"])
        print("Quesadilla:", comanda["quesadilla"])
        print("Bebida:", comanda["bebida"])
        print("Consome:", comanda["consome"])
        print("")  # Agregar una línea en blanco entre registros

    client.close()

def mostrar_datos():
    print("-------------------------------------------------")
    print("1. Mostrar todas las comandas")
    print("2. Mostrar comandas completadas")
    print("3. Mostrar comandas no completadas")

    opcion_filtrado = input("Seleccione una opción: ")

    mostrar_datos_filtradas(opcion_filtrado)

def borrar_datos():
    client = MongoClient("mongodb+srv://danielxp:maspormasDF1@cluster0.glu8e4r.mongodb.net/?retryWrites=true&w=majority")
    db = client["danielxp88"]
    comandas_collection = db["comandas"]

    print("-----------------")
    print("Datos en la base de datos:")

    num_comanda = input("¿Qué número de comanda quieres borrar?: ")
    bus = {'num_comanda': int(num_comanda)}
    comandas_collection.delete_one(bus)
    print("Registro borrado")

    client.close()

def menu():
    while True:
        print("Menú de opciones:")
        print("1. Agregar Comanda")
        print("2. Borrar Comanda")
        print("3. Consultar Comandas")
        print("4. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            cant_barbacoa = obtener_opcion("barbacoa")
            cant_quesadilla = obtener_opcion("quesadilla")
            cant_bebida = obtener_opcion("bebida")
            cant_consome = obtener_opcion("consome")

            hilo = threading.Thread(target=escribir_base_de_datos, args=(
                threading.current_thread().name,
                obtener_numero_comanda(),
                cant_barbacoa,
                cant_quesadilla,
                cant_bebida,
                cant_consome
            ), name='HiloAgregarComanda')

            hilo.start()
            hilo.join()

        elif opcion == "2":
            hilo = threading.Thread(target=borrar_datos, name='HiloBorrarComanda')
            hilo.start()
            hilo.join()

        elif opcion == "3":
            hilo = threading.Thread(target=mostrar_datos, name='HiloConsultarComandas')
            hilo.start()
            hilo.join()

        elif opcion == "4":
            print("Saliendo del programa. ¡Hasta luego!")
            break

        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

# Funciones para obtener_numero_comanda y obtener_opcion se mantienen igual


def obtener_numero_comanda():
    client = MongoClient("mongodb+srv://danielxp:maspormasDF1@cluster0.glu8e4r.mongodb.net/?retryWrites=true&w=majority")
    db = client["danielxp88"]
    comandas_collection = db["comandas"]

    ultima_comanda = comandas_collection.find_one(sort=[("num_comanda", -1)])

    if ultima_comanda:
        numero_comanda = ultima_comanda["num_comanda"] + 1
    else:
        numero_comanda = 1

    client.close()
    return numero_comanda

def obtener_opcion(opcion):
    cantidad = input(f"Ingrese la cantidad de {opcion}: ")
    return int(cantidad)

if __name__ == "__main__":
    menu()
