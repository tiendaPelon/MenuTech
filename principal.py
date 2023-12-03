import threading
from pymongo import MongoClient
from bson import ObjectId

def escribir_base_de_datos(hilo_id, num_comanda, barbacoa, quesadilla, bebida, consome):
    # Realizar la conexión a la base de datos
    client = MongoClient("mongodb+srv://danielxp:maspormasDF1@cluster0.glu8e4r.mongodb.net/?retryWrites=true&w=majority")
    db = client["danielxp88"]
    comandas_collection = db["comandas"]

    # Insertar el valor en la base de datos
    comanda = {
        "num_comanda": num_comanda,
        "barbacoa": barbacoa,
        "quesadilla": quesadilla,
        "bebida": bebida,
        "consome": consome,
        "completado": False  
    }
    result = comandas_collection.insert_one(comanda)
    print(f"Hilo {hilo_id}: Comanda insertada con ID: {result.inserted_id}")

    # Cerrar la conexión
    client.close()

def mostrar_datos():
    # Realizar la conexión a la base de datos
    client = MongoClient("mongodb+srv://danielxp:maspormasDF1@cluster0.glu8e4r.mongodb.net/?retryWrites=true&w=majority")
    db = client["danielxp88"]
    comandas_collection = db["comandas"]

    # Consultar y mostrar los datos de la colección "comandas"
    print("-----------------")
    print("Datos en la base de datos:")
    for comanda in comandas_collection.find():
        print("ID:", comanda["_id"])
        print("Número de Comanda:", comanda["num_comanda"])
        print("Barbacoa:", comanda["barbacoa"])
        print("Quesadilla:", comanda["quesadilla"])
        print("Bebida:", comanda["bebida"])
        print("Consomé:", comanda["consome"])

        # Verificar si 'completado' está presente 
        completado = comanda.get("completado")
        if completado is not None:
            print("Completado:", completado)
        else:
            print("Completado: N/A")

        print("")

    # Cerrar la conexión
    client.close()


def borrar_datos():
    # Realizar la conexión a la base de datos
    client = MongoClient("mongodb+srv://danielxp:maspormasDF1@cluster0.glu8e4r.mongodb.net/?retryWrites=true&w=majority")
    db = client["danielxp88"]
    comandas_collection = db["comandas"]

    # Consultar y mostrar los datos de la colección "comandas"
    print("-----------------")
    num_comanda = input("¿Cuál número de comanda quieres borrar?: ")
    bus = {'num_comanda': int(num_comanda)}
    comandas_collection.delete_one(bus)
    print("Registro borrado")

    # Cerrar la conexión
    client.close()

def actualizar_completado():
    # Realizar la conexión a la base de datos
    client = MongoClient("mongodb+srv://danielxp:maspormasDF1@cluster0.glu8e4r.mongodb.net/?retryWrites=true&w=majority")
    db = client["danielxp88"]
    comandas_collection = db["comandas"]

    # Mostrar las comandas y solicitar el ID de la comanda a actualizar
    print("-----------------")
    print("Comandas en la base de datos:")
    for comanda in comandas_collection.find():
        print("ID:", comanda["_id"])
        print("Número de Comanda:", comanda["num_comanda"])

        # Verificar si se encuentra 'completado' 
        completado = comanda.get("completado")
        if completado is not None:
            print("Completado:", completado)
        else:
            print("Completado: N/A")

        print("")

    comanda_id = input("Ingrese el ID de la comanda que desea actualizar: ")
    completado = input("¿La comanda está completada? (Sí/No): ").lower() == "sí"

    # Actualizar el campo "completado" de la comanda seleccionada
    comandas_collection.update_one({"_id": ObjectId(comanda_id)}, {"$set": {"completado": completado}})
    print("Se ha actualizado")

    # Cerrar la conexión
    client.close()


def menu():
    while True:
        print("Menú de opciones:")
        print("1. Agregar Comanda")
        print("2. Borrar Comanda")
        print("3. Consultar Comandas")
        print("4. Actualizar Estado de Comanda")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            # Generar automáticamente el número de comanda incremental
            hilo = threading.Thread(target=escribir_base_de_datos, args=(threading.current_thread().name, obtener_numero_comanda(), obtener_opcion("barbacoa"), obtener_opcion("quesadilla"), obtener_opcion("bebida"), obtener_opcion("consome")), name=f'HiloAgregarComanda')
            hilo.start()
            hilo.join()
        elif opcion == "2":
            hilo = threading.Thread(target=borrar_datos, name=f'HiloBorrarComanda')
            hilo.start()
            hilo.join()
        elif opcion == "3":
            hilo = threading.Thread(target=mostrar_datos, name=f'HiloConsultarComandas')
            hilo.start()
            hilo.join()
        elif opcion == "4":
            hilo = threading.Thread(target=actualizar_completado, name=f'HiloActualizarComanda')
            hilo.start()
            hilo.join()
        elif opcion == "5":
            print("¡Gracias por utilizarlo, adiós:)!")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

def obtener_numero_comanda():
    # Obtener el último número de comanda registrado y generar el siguiente
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
    # Solicitar la cantidad de la opcion
    cantidad = input(f"Ingrese la cantidad de {opcion}: ")
    return int(cantidad)

if __name__ == "__main__":
    menu()
