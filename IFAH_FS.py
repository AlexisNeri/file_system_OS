import os
import csv


class Inodo:
    tipo = '0'
    tamano = 0
    tabla = [0, 0, 0, 0, 0]
    permisos = ['R', 'W', 'E']
    dueno = ''
    dummy = '0' * 35


carpeta_actual = 0
usuario = 'H'
ruta = "Usuario@" + usuario + ":~$"
tamanno_lil = 10
bloques_li = 60
total_inodos = 960
bloques_datablock = 961
disco = []
block_size = 1024
boot_block = '0' * block_size
lil = [0] * int(block_size / 4)
lbl = [0] * int(block_size / 4)
li = []
data_block = []
data_block2 = {}
inicio_datablock = 64
bloquesen_disco = 3


def inicializar():
    """
    Función implementada para llenar la Lista de Inodos, la función crea dos Inodos con información
    dummy (los primeros dos Inodos en Linux), después crea Inodos utilizables y los agrega a la lista.
    """

    # Fill first two inodes with dummy data
    for number in range(1, 3):
        crear_variable = 'Inodo_' + str(number)
        crear_variable = Inodo()
        crear_variable.tipo = ' '
        crear_variable.permisos = [' ', ' ', ' ']
        crear_variable.dueno = ' '
        li.append(crear_variable)
    # Initialize first usable Inode (3)
    crear_variable = 'Inodo_3'
    crear_variable = Inodo()
    crear_variable.tipo = 'D'
    crear_variable.permisos = [' ', ' ', ' ']
    crear_variable.tabla = [inicio_datablock, 0, 0, 0, 0]
    crear_variable.dueno = '_'
    li.append(crear_variable)
    # Fill the rest of the Inode List with newly created Inodes
    for number in range(4, total_inodos + 1):
        crear_variable = 'Inodo_' + str(number)
        crear_variable = Inodo()
        crear_variable.dueno = usuario
        li.append(crear_variable)


def llenar_lil():
    """
    Función
    implementada
    para
    llenar
    la
    Lista
    de
    Inodos
    Libres.Itera
    la
    lista
    de
    inodos
    basándose
    en
    el
    tamaño
    de
    la
    LIL, después
    agrega
    a
    LIL
    los
    Inodos
    cuyo
    tipo
    es ‘0’
    :return:
    """
    counter = 0
    # Iterate over the Inode list
    for number in range(0, total_inodos + 1):
        # Add free Inode to LIL
        if li[number].tipo == '0':
            lil[tamanno_lil - 1 - counter] = (number + 1)
            counter += 1
            # Stop when LIL is full
            if counter == tamanno_lil:
                break


def inicializar_disco():
    """
    Agrega todos los bloques de disco a la lista principal.
    """
    # Add every disc block to main disc space
    disco.append(boot_block)
    disco.append(lil)
    disco.append(lbl)
    disco.append(li)
    disco.append(data_block)


def inicializar_data_block():
    """
    Función implementada para inicializar root directory, y el resto
    de los bloques de datos con información vacía.
    """
    # Iterate from the start to the end of Data Block
    for number in range(int(inicio_datablock), 1025 - bloquesen_disco):
        # Initialize root directory
        if number == int(inicio_datablock):
            data_block.append({'.': li[2], '..': li[2]})
        # Initialize the rest of the blocks with empty data
        else:
            data_block.append('0' * 1024)


def bl_en_memoria(bloque_libre, primer_key):
    """
    Implementación para guardar los bloques libres excedentes de la LBL.
    """
    # Append free blocks to memory
    if primer_key in data_block2:
        data_block2[primer_key].append(bloque_libre)
    else:
        data_block2[primer_key] = [bloque_libre]


def llenar_lbl():
    """
    Función implementada para llenar la Lista de Bloques Libres, necesarios para el almacenamiento
    de los datos de las carpetas/archivos que se crean a lo largo de la ejecución.
    """
    counter = 0
    data_block_element = 0
    # Iterate all elements in Data Block
    for number in data_block:
        # Take element only if it is empty
        if number == '0' * 1024:
            # Append free blocks to memory based on size
            if counter < 256:
                lbl[256 - 1 - counter] = int(inicio_datablock + data_block_element)
                primer_key = int(inicio_datablock + data_block_element)
                counter += 1
            elif counter >= 256:
                if counter == 512:
                    counter = 256
                    primer_key = siguiente_key
                bl_en_memoria(int(inicio_datablock + data_block_element), primer_key)
                siguiente_key = int(inicio_datablock + data_block_element)
                counter += 1
        data_block_element += 1


def liberar_inodo(numero_inodo):
    """
    Función ejecutada al eliminar un archivo o carpeta, el Inodo correspondiente
    se agrega a la LIL con base en los elementos de la misma.
    """
    # Free inode after deleting file/folder
    if lil.count(0) == 256 - tamanno_lil:
        # Compare node with remember Inode when there is only one element
        if numero_inodo < lil[0]:
            lil[0] = numero_inodo
        else:
            pass
    # Place the released Inode in an empty space
    else:
        for number in range(0, tamanno_lil):
            if lil[number] == 0:
                lil[number] = numero_inodo
                break


def liberar_bloque(numero_bloque):
    """
    Implementación para agregar un bloque liberado a la LBL.
    Si no hay espacio disponible, se guarda en memoria para posteriormente ser guardado en disco.
    """
    key_allenar = 0
    # Check if LBL is full
    if lbl.count(0) == 0:
        for key, valor in data_block2.items():
            if valor == [0] * int(block_size / 4):
                key_allenar = key
            else:
                pass
        # Check if the block can be allocated in LBL
        if key_allenar != 0:
            data_block2.pop(key_allenar)
            data_block2[numero_bloque] = lbl[::-1]
            lbl[0] = numero_bloque
            for number in range(1, len(lbl)):
                lbl[number] = 0
        else:
            print("Sin memoria para guardar bloque liberado")
    # Add free block to LBL
    else:
        for number in range(0, 256):
            if lbl[number] == 0:
                lbl[number] = numero_bloque
                break


def tomar_inodo():
    """
    Función implementada para reservar un Inodo para su posterior asignación a un archivo/carpeta
    """
    # If there is only one Inode in LIL, fill it again.
    if lil.count(0) == 256 - 1:
        regresar = lil[0]
        llenar_lil()
        return regresar
    # When there is more than one element, iterate LIL to find the next Inode available
    else:
        for number in range(tamanno_lil - 1, -1, -1):
            if lil[number] != 0:
                regresar = lil[number]
                lil[number] = 0
                return regresar


def tomar_bloque():
    """
    Implementación para obtener un bloque disponible al momento de crear un archivo/carpeta.
    """
    # Check there is one element in LB
    if lbl.count(0) == 256 - 1:
        regresar = lbl[0]
        lista_temp = data_block2.get(regresar)
        if lista_temp != None:
            data_block2[regresar] = [0] * 256
            lista_temp = lista_temp[::-1]
            for number in range(256):
                lbl[number] = lista_temp[number]
            return regresar
        else:
            print("Ya no existen mas bloques de memoria disponibles")
            # Find the next free block in LBL
    else:
        for number in range(256 - 1, -1, -1):
            if lbl[number] != 0:
                regresar = lbl[number]
                lbl[number] = 0
                return regresar


def llenar_inodo(inodo, bloque, tipo, tamano):
    """
    Función implementada para llenar la información de un Inodo cuando se crea un archivo o carpeta.
    Toma como parámetros el tipo de archivo, tamaño, el Inodo a llenar y el bloque de datos que contiene.
    """
    # Ubicar el Inodo deseado y actualizar sus datos.
    li[inodo - 1].tipo = tipo
    li[inodo - 1].tamano = tamano
    # Actualizar los bloques de datos correspondientes al archivo
    for number in range(0, 5):
        li[inodo - 1].tabla[number] = bloque[number]


def borrar_archivo_carpeta():
    """
    Se encarga de eliminar un archivo o carpeta, invocando a las funciones necesarias
    para el manejo de Inodos, bloques y datos.
    """
    directorio_actual = data_block[carpeta_actual]
    nombre_archivo = input("Por favor, introduce el nombre del archivo o carpeta a borrar: \n\t")
    inodo_archivo = directorio_actual.get(nombre_archivo)
    # Check if file/folder exists
    if inodo_archivo is None:
        print('Archivo no encontrado')
    # Check user permissions
    else:
        # Update data in temporal Inode
        if inodo_archivo.dueno == usuario and inodo_archivo.permisos == ['R', 'W', 'E']:
            inodo_archivo.tipo = '0'
            inodo_archivo.tamano = 0
            numero_inodo = li.index(inodo_archivo) + 1
            # Free Inode
            liberar_inodo(numero_inodo)
            # Update Inode's table
            for number in range(len(inodo_archivo.tabla)):
                if inodo_archivo.tabla[number] != 0:
                    numero_bloque = inodo_archivo.tabla[number]
                    # Free block
                    liberar_bloque(numero_bloque)
                    inodo_archivo.tabla[number] = 0
                else:
                    break
            # Remove file/folder from current directory and update size
            directorio_actual.pop(nombre_archivo)
            inodo_carpeta_actual = directorio_actual.get('.')  # Se obtiene el inodo del directorio actual
            inodo_carpeta_actual.tamano = inodo_carpeta_actual.tamano - 16  # Se actualiza el tamaño de la carpeta


def crear_archivo_carpeta():
    """
    Implementación para crear un archivo o carpeta. En caso de ser archivo, toma datos del usuario para escribirlos en el archivo.
    Actualiza los bloques de datos con la información correspondiente.
    """
    bloque = [0, 0, 0, 0, 0]
    directorio_actual = data_block[carpeta_actual]
    crear = input("Que deseas crear:    1.Carpeta        2.Archivo\t\n")
    # Create folder
    if crear == "1":
        nombre = input("Introduce el nombre de la carpeta a crear\t\n")
        # Get free Inode
        inodo = tomar_inodo()
        inodo_real = inodo - 1
        # Get free Data Block ad update data
        bloque[0] = tomar_bloque()
        llenar_inodo(inodo, bloque, tipo='D', tamano=32)
        directorio_actual[nombre] = li[inodo_real]
        bloquea_cargar = bloque[0]
        data_block[bloquea_cargar - 64] = {'.': li[inodo_real], '..': directorio_actual.get('.')}
        directorio_actual = data_block[carpeta_actual]  # Se define el directorio Actual
        inodo_carpeta_actual = directorio_actual.get('.')  # Se obtiene el inodo del directorio actual
        inodo_carpeta_actual.tamano = inodo_carpeta_actual.tamano + 16
        # Se actualiza el tamaño de la carpeta
    # Create and initiailze new file
    elif crear == "2":
        informacion = input("A continuacion puede escribir la informacion de tu archivo:\n")
        nombre = input("Introduce el nombre del archivo a crear\t\n")
        inodo = tomar_inodo()
        inodo_real = inodo - 1
        # Calculate number of blocks based of input size
        if len(informacion) % 1024 == 0:
            iterar = int(len(informacion) / 1024)
        else:
            iterar = int(len(informacion) / 1024) + 1
        for number in range(0, iterar):
            bloque[number] = tomar_bloque()
        llenar_inodo(inodo, bloque, tipo='A', tamano=len(informacion))
        directorio_actual[nombre] = li[
            inodo_real]  # Se agrega al diccionario el nombre del nuevo archivo creado y si Inodo Asignado
        longitud = 1025  # Se define el tamaño maximo en que se dividira la informacion
        for number in range(0,
                            iterar):  # Se llenaran los distintos bloques que contienen toda la informacion del archivo
            bloquea_cargar = bloque[number]  # Se obtiene cada uno de los bloques
            data_block[bloquea_cargar - 64] = informacion[longitud * number:longitud * (
                        number + 1)]  # Se llena la informacion en cada uno de los bloques
        directorio_actual = data_block[carpeta_actual]  # Se define el directorio Actual
        inodo_carpeta_actual = directorio_actual.get('.')  # Se obtiene el inodo del directorio actual
        inodo_carpeta_actual.tamano = inodo_carpeta_actual.tamano + 16  # Se actualiza el tamaño de la carpeta
    else:
        print("Opcion no valida")


def listar_archivos():
    """
    Implementación para listar el contenido de la carpeta actual.
    """
    directorio_actual = data_block[carpeta_actual]
    print(ruta)
    # List all elements in current directory
    for key in directorio_actual:
        print(key)


def accesar_archivo_carpeta():
    """
    Implementación para navegar entre directorios y archivos.
    """
    global ruta
    global carpeta_actual
    directorio_actual = data_block[carpeta_actual]
    nombre_archivo = input("Introduce el nombre del archivo o carpeta a accesar\t\n")
    inodo_archivo = directorio_actual.get(nombre_archivo)
    # Check if file/folder exists
    if inodo_archivo is None:
        print('Archivo o carpeta no encontrado')
    else:
        # If navigating through folders, change current directory information
        if inodo_archivo.tipo == 'D':
            bloque_carpeta = inodo_archivo.tabla[0]
            carpeta_actual = bloque_carpeta - 64
            if nombre_archivo == '.':
                pass
            elif nombre_archivo == '..':
                hasta_aqui = ruta.rfind('/')
                ruta = ruta[0:hasta_aqui]
            else:
                ruta = ruta + "/" + nombre_archivo
        # If accessing files, print saved data
        elif inodo_archivo.tipo == 'A':
            info_concatenada = ""
            bloques_archivo = inodo_archivo.tabla
            # retrieve data from file
            for bloque in bloques_archivo:
                if bloque != 0:
                    info_archivo = data_block[bloque - 64]
                    info_concatenada = info_concatenada + info_archivo
                else:
                    break
            # Print file data
            print("*" * 80)
            print("La informacion del archivo " + nombre_archivo + " es la siguiente:")
            print("*" * 80)
            print()
            print(info_concatenada)
            print()
            print("*" * 80)
        else:
            print("El elemento al que se desea accesar no es un Archivo o carpeta")


def informacion_directorio():
    """
    Implementación para mostrar el contenido del directorio actual con la siguiente información: Nombre, Tipo, Tamaño, Tabla, Permisos, Dueño.
    """
    directorio_actual = data_block[carpeta_actual]
    print("*" * 80)
    print("La informacion de lo contenido en el directorio actual es la siguiente:")
    print("*" * 80)
    print()
    # Print formatted data
    for key, value in directorio_actual.items():
        print(key + "                    " + value.tipo + "    " + str(value.tamano) + "    " + str(
            value.tabla) + "    " + str(value.permisos) + "    " + value.dueno)
    print("*" * 80)


def copiar_archivo():
    """

    """
    directorio_actual = data_block[carpeta_actual]
    nombre_archivo = input("Introduce el nombre del archivo o carpeta a copiar\t\n")
    inodo_archivo = directorio_actual.get(nombre_archivo)
    # Check if file exists
    if inodo_archivo is None:
        print('Archivo no encontrado')
    else:
        # Verify that a file is going to be copied.
        if inodo_archivo.tipo == 'A':
            inodo = tomar_inodo()
            inodo_real = inodo - 1
            inodoa_copiar = li[inodo_real]
            # Update data in new retrieved Inode
            li[inodo_real].tipo = inodo_archivo.tipo
            li[inodo_real].tamano = inodo_archivo.tamano
            li[inodo_real].permisos = inodo_archivo.permisos
            li[inodo_real].dueno = inodo_archivo.dueno
            li[inodo_real].dummy = inodo_archivo.dummy
            # Copy file data to new file
            for number in range(0, 5):
                if inodo_archivo.tabla[number] != 0:
                    bloque_asignado = tomar_bloque()
                    li[inodo_real].tabla[number] = bloque_asignado
                    data_block[bloque_asignado - 64] = data_block[inodo_archivo.tabla[number] - 64]
                else:
                    li[inodo_real].tabla[number] = inodo_archivo.tabla[number]
            # Rename copied file
            nuevo_nombre = nombre_archivo + "-Copy"
            if nuevo_nombre in directorio_actual:
                nuevo_nombre = nuevo_nombre + "-Copy"
            # Update current directory information
            directorio_actual[nuevo_nombre] = li[
                inodo_real]  # Se agrega al directorio actual el nombre del nuevo archivo copiado y su Inodo Asignado
            directorio_actual = data_block[carpeta_actual]  # Se define el directorio Actual
            inodo_carpeta_actual = directorio_actual.get('.')  # Se obtiene el inodo del directorio actual
            inodo_carpeta_actual.tamano = inodo_carpeta_actual.tamano + 16  # Se actualiza el tamaño de la carpeta

        else:
            print("El elemento que se desea copiar no es un Archivo")


def write(disk_sector, iterable):
    if 'lbl' or 'db2' in disk_sector.lower():
        write_lbl_db2(disk_sector, iterable)
    elif 'li' in disk_sector.lower():
        write_li(iterable)
    elif 'db' in disk_sector.lower():
        write_db(iterable)
    else:
        print('Wrong disk sector, try again\n')


def write_lbl_db2(file, lbl_db2):
    int_list = []
    for element in lbl_db2:
        int_list.append(convert_int_to_string(element))
    write_to_csv(file, int_list)


def write_li(li):
    li_list = []
    for element in li:
        li_list.append(convert_dictionary_to_list(convert_object_to_dictionary(element)))
    write_to_csv('li', li_list)


def write_db(db):
    db_list = []
    for element in db:
        if is_a_dict(element):
            db_list.append(convert_dictionary_to_list(element))
        else:
            db_list.append(element)
    write_to_csv('db', db_list)


def write_to_csv(file_name, target_list):
    with open('{}.csv'.format(file_name), mode='w') as csv_file:
        writer = csv.writer(csv_file)
        for element in target_list:
            writer.writerow(element)


def convert_object_to_dictionary(this_object):
    return this_object.__dict__


def convert_dictionary_to_list(this_dictionary):
    my_object = list(this_dictionary.items())
    return my_object


def convert_int_to_string(int_value):
    my_string = str(int_value)
    return my_string


def is_a_dict(my_object):
    return type(my_object) is dict


if __name__ == '__main__':

    inicializar()
    llenar_lil()
    inicializar_data_block()
    llenar_lbl()
    inicializar_disco()

    ejecucion = True

    while ejecucion:
        listar_archivos()
        # Main menu
        opcion = input("Escoge una opcion del menu: \n\t\t\t\t\t1.Listar Directorio Actual    2.Crear    3. Borrar    "
                       "4.Acceder   5.Copiar Archivo    6.Salir\t\n")
        if opcion != '1' and opcion != '2' and opcion != '3' and opcion != '4' and opcion != '5' and opcion != '6':
            print("Opcion no valida")
            os.system("cls")
        else:
            if opcion == '1':
                informacion_directorio()
            if opcion == '2':
                crear_archivo_carpeta()
            if opcion == '3':
                borrar_archivo_carpeta()
            if opcion == '4':
                # os.system ("cls")
                accesar_archivo_carpeta()
            if opcion == '5':
                copiar_archivo()
            if opcion == '6':
                print('Saving LI\n')
                write('li', li)
                print('Saving LBL\n')
                write('lbl', lbl)
                print('Saving DB\n')
                write('db', data_block)
                print('Saving DB2\n')
                write('db2', data_block2)

                ejecucion = False
