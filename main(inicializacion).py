class Inodo:
    tipo = '0'
    tamano = 0
    tabla = [0,0,0,0,0]
    permisos = ['R','W','E']
    dueno = ''
    dummy = ['A'] * 35

bootBlock = []

lil = ['10','X','X','X','X','X','X','X','X','X']#sizeof < 1K o count < 10

lbl = ['X','X','X','X','X','X','X','X','X','X']#sizeof < 1K o count < 10

li = []#numero de inodos para 1M son 960

directorio_raiz = {'.':'3','..':'3'}

usuario='H'


if __name__ == '__main__':
    print(lil.count('X'))
    for number in range(4,961):
        crearVariable = 'Inodo_'+str(number)
        crearVariable=Inodo()
        crearVariable.dueno=usuario
        li.append(crearVariable)
        
    counter = 0
    for number in range(0,957):
        if li[number].tipo == '0':
            lil[9-counter]=(number+4)
            counter+=1
            if counter == 10:
                break
    print(lil)
        #print(li[number].tipo)
        #if li[inode].tipo =='0':
         #   print(inode)
    #print(li[49].dummy)
    #print(type(crearVariable))
    #Inodo_1
    
