import threading
import time
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta

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
    # Validar que las cantidades sean números
    if not all(isinstance(cantidad, int) for cantidad in [num_comanda, barbacoa, quesadilla, bebida, consome]):
        print("Error: Las cantidades deben ser números enteros.")
        return

    # Realizar la conexión a la base de datos
    tiempo_pedido = obtener_tiempo_total({
        "barbacoa": barbacoa,
        "quesadilla": quesadilla,
        "bebida": bebida,
        "consome": consome
    })
    
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
        "completado": False if "completado" not in locals() else completado,
        "tiempo_pedido": tiempo_pedido
    }

    result = comandas_collection.insert_one(comanda)
    print(f"Hilo {hilo_id}: Comanda insertada con ID: {result.inserted_id}")
    print(f"El tiempo estimado de preparación para la Comanda {num_comanda} es de {tiempo_pedido} segundos.")
    # Cerrar la conexión
    client.close()


def mostrar_datos_filtradas(opcion_filtrado):
    # Realizar la conexión a la base de datos
    client = MongoClient("mongodb+srv://danielxp:maspormasDF1@cluster0.glu8e4r.mongodb.net/?retryWrites=true&w=majority")
    db = client["danielxp88"]
    comandas_collection = db["comandas"]

    # Consultar y mostrar los datos de la colección "comandas" según la opción de filtrado
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
        print("Consomé:", comanda["consome"])
        tiempo_pedido = comanda.get("tiempo_pedido", None)
        if tiempo_pedido is not None:
            print(f"Tiempo estimado de preparación: {tiempo_pedido} segundos")
        # Verificar si 'completado' está presente en el documento
        completado = comanda.get("completado")
        if completado is not None:
            print("Completado:", completado)
        else:
            print("Completado: N/A")

        print("")

    # Cerrar la conexión
    client.close()

def mostrar_comandas_pendientes():
    # Realizar la conexión a la base de datos
    client = MongoClient("mongodb+srv://danielxp:maspormasDF1@cluster0.glu8e4r.mongodb.net/?retryWrites=true&w=majority")
    db = client["danielxp88"]
    comandas_collection = db["comandas"]

    # Buscar y mostrar los datos de las comandas pendientes
    print("-------------------------------------------------")
    print("Comandas Pendientes:")
    comandas_pendientes = comandas_collection.find({"$or": [{"completado": False}, {"completado": {"$exists": False}}]})

    hilos = []  # Lista para almacenar los hilos creados

    for comanda in comandas_pendientes:
        num_comanda = comanda["num_comanda"]
        completado = comanda.get("completado", "N/A")
        tiempo_pedido = comanda.get("tiempo_pedido", "N/A")

        print("Número de Comanda:", num_comanda)
        print("Completado:", completado)
        print("Tiempo estimado de preparación:", tiempo_pedido, "segundos")
        print("")

        # Crear un hilo para mostrar el progreso de la comanda
        hilo_progreso = threading.Thread(target=mostrar_progreso_comanda, args=(num_comanda,))
        hilos.append(hilo_progreso)

    # Iniciar todos los hilos antes de esperar a que terminen
    for hilo in hilos:
        hilo.start()

    # Esperar a que todos los hilos terminen
    for hilo in hilos:
        hilo.join()

    # Cerrar la conexión
    client.close()
# Definir un Lock global para sincronizar el acceso al archivo
archivo_lock = threading.Lock()

def escribir_archivo_txt(num_comanda, completado, tiempo_pedido, detalles):
    # Nombre del archivo único para todos los registros
    nombre_archivo = "registros_comandas.txt"
    
    # Bloquear para garantizar escritura segura en el archivo
    with archivo_lock:
        with open(nombre_archivo, "a") as archivo:  # Modo "a" para agregar contenido al archivo
            archivo.write(f"Número de Comanda: {num_comanda}\n")
            archivo.write(f"Completado: {completado}\n")
            archivo.write(f"Tiempo estimado de preparación: {tiempo_pedido} segundos\n")
            archivo.write("\nDetalles de la Comanda:\n")
            for comida, cantidad in detalles.items():
                archivo.write(f"{comida.capitalize()}: {cantidad}\n")
            archivo.write("\n" + "-"*40 + "\n")  # Separador entre comandas
    
    print(f"Comanda {num_comanda} - Información guardada en {nombre_archivo}")

def mostrar_progreso_comanda(num_comanda):
    # Realizar la conexión a la base de datos
    client = MongoClient("mongodb+srv://danielxp:maspormasDF1@cluster0.glu8e4r.mongodb.net/?retryWrites=true&w=majority")
    db = client["danielxp88"]
    comandas_collection = db["comandas"]

    # Mostrar el progreso de la comanda en tiempo real
    while True:
        comanda = comandas_collection.find_one({"num_comanda": num_comanda})
        if comanda:
            completado = comanda.get("completado", False)
            tiempo_pedido = comanda.get("tiempo_pedido", 0)
            detalles = {
                "barbacoa": comanda.get("barbacoa", 0),
                "quesadilla": comanda.get("quesadilla", 0),
                "bebida": comanda.get("bebida", 0),
                "consome": comanda.get("consome", 0),
            }

            print(f"Comanda {num_comanda} - Completado: {completado}, Tiempo restante: {tiempo_pedido} segundos")

            if completado or tiempo_pedido <= 0:
                break  # Salir del bucle si la comanda ha sido completada o el tiempo restante es menor o igual a cero

            # Simular intervalo de ejecución (quantum de 2 segundos)
            time.sleep(2)

            # Restar tiempo_pedido en la base de datos
            comandas_collection.update_one({"num_comanda": num_comanda}, {"$inc": {"tiempo_pedido": -2}})

    # Actualizar "completado" en la base de datos cuando la comanda ha terminado
    comandas_collection.update_one({"num_comanda": num_comanda}, {"$set": {"completado": True}})

    # Escribir información en archivo txt
    escribir_archivo_txt(num_comanda, True, tiempo_pedido, detalles)

    # Cerrar la conexión
    client.close()



def mostrar_datos():
    # Realizar la conexión a la base de datos
    client = MongoClient("mongodb+srv://danielxp:maspormasDF1@cluster0.glu8e4r.mongodb.net/?retryWrites=true&w=majority")
    db = client["danielxp88"]
    comandas_collection = db["comandas"]

    # Mostrar las opciones 
    print("-------------------------------------------------")
    print("1. Mostrar todas las comandas")
    print("2. Mostrar comandas completadas")
    print("3. Mostrar comandas no completadas")

    opcion_filtrado = input("Seleccione una opción: ")

    # Consultar y mostrar los datos según la opción
    mostrar_datos_filtradas(opcion_filtrado)


def borrar_datos():
    # Realizar la conexión a la base de datos
    client = MongoClient("mongodb+srv://danielxp:maspormasDF1@cluster0.glu8e4r.mongodb.net/?retryWrites=true&w=majority")
    db = client["danielxp88"]
    comandas_collection = db["comandas"]

    # Consultar y mostrar los datos de la colección "comandas"
    print("-------------------------------------------------")
    num_comanda = input("¿Qué número de comanda quieres borrar?: ")
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

    # Mostrar las comandas y solicitar el número de comanda a actualizar
    print("-------------------------------------------------")
    print("Comandas en la base de datos:")
    for comanda in comandas_collection.find():
        print("ID:", comanda["_id"])
        print("Número de Comanda:", comanda["num_comanda"])

        # Verificar si 'completado' está presente en el documento
        completado = comanda.get("completado")
        if completado is not None:
            print("Completado:", completado)
        else:
            print("Completado: N/A")

        print("")

    num_comanda = input("Ingrese número de comanda a actualizar: ")

    # Actualizar el campo "completado" de la comanda seleccionada
    comanda = comandas_collection.find_one({"num_comanda": int(num_comanda)})
    if comanda:
        completado = comanda.get("completado")
        if completado is not None:
            comandas_collection.update_one({"num_comanda": int(num_comanda)}, {"$set": {"completado": not completado}})
            print("Estado: Actualizado")
        else:
            print("No se encontró el campo 'completado' en la comanda.")
    else:
        print("No se encontró la comanda con el número proporcionado.")

    # Cerrar la conexión
    client.close()


def menu():
    while True:
        print("Menú de opciones:")
        print("1. Agregar Comanda")
        print("2. Borrar Comanda")
        print("3. Consultar Comandas")
        print("4. Actualizar Estado de Comanda")
        print("5. Preparar pedidos")
        print("6. Salir")

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
            mostrar_comandas_pendientes()
        elif opcion == "6":
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
    while True:
        cantidad = input(f"Ingrese la cantidad de {opcion}: ")
        
        try:
            cantidad = int(cantidad)
            if cantidad >= 0:
                return cantidad
            else:
                print("Por favor, ingrese un número mayor o igual a 0.")
        except ValueError:
            print("Por favor, ingrese un número válido.")

if __name__ == "__main__":
    menu()