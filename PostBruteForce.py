import requests,sys, codecs, signal, os
from datetime import datetime
from pwn import *
from alive_progress import alive_bar

## VARIABLES GLOBALES
grafico = "\n |\/\/\/|  \n |      |  \n |      |  \n | (o)(o)  \n C      _) \n  | ,___|       ¡Multiplicate por cero!\n  |   /    \n /____\    \n/      \ \n"
ayuda = "Metodo de utilzación: python3 PostBruteForce.py \n                      --url [url] -f [output]\n                      -u [nombre de usuario] -U [wordlist de usuarios] \n                      -p [password] -P [wordlist de passwords]"
dataFalsa = {}
data = {}
url = ""
username = ""
userlist = ""
password = ""
passlist = ""
outputPath = ""
now = str(datetime.now())

    
# METODO INFO, PROCESA ARGUMENTOS
def info():
    
    global url 
    global username 
    global userlist 
    global password 
    global passlist 
    global outputPath

    print(grafico)
    print("Script de fuerza bruta por metodo POST")
    print("\n")
    
    #Minimo para funcionar
    
    if len(sys.argv) < 3:
        
        print(ayuda)        
        sys.exit(1)
        
    #Proceso de los argumentos
    
    for x in range(len(sys.argv)):
        if sys.argv[x] == "-h":
            print(ayuda)
        if sys.argv[x] == "--url":
            url = sys.argv[x+1]
        if sys.argv[x] == "-u":
            username = sys.argv[x+1]
        if sys.argv[x] == "-U":
            userlist = sys.argv[x+1]
        if sys.argv[x] == "-p":
            password = sys.argv[x+1]
        if sys.argv[x] == "-P":
            passlist = sys.argv[x+1]
            
        if sys.argv[x] == "-f":
            outputPath = sys.argv[x+1]

            
            
    #Print de los parametros
    
    print ("-----\n> Url: ["+url+"]") 
    print ("> Username: ["+username+"]")
    print ("> Wordlist de usuarios: ["+userlist+"]")
    print ("> Password: ["+password+"]")
    print ("> Wordlist de passwords: ["+passlist+"]")
    print ("> Path del output: ["+outputPath+"]\n-----")
    
    #Caso de url vacia
    
    if url == "":
        print("La url no puede estar vacia")
        print("\n"+ayuda+"\n")
        sys.exit(1)
    
    #Casos contemplados:
    # Se usan username y userlist o password y passlist a la vez
    # Falta un user o un password
    # Se mete un user y un pass individual
    # No existe la worlist
    
    while True:
        if username != "" and passlist != "" and password == "" and userlist == "":
            if os.path.exists(passlist):
                break
            else:
                print("La worlist no existe")
                
        if username == "" and passlist == "" and password != "" and userlist != "":
            if os.path.exists(userlist):
                break
            else:
                print("La wordlist no existe")
        
        if username == "" and passlist != "" and password == "" and userlist != "":
            if os.path.exists(userlist) and os.path.exists(passlist):
                break
            else:
                print("Las wordlists no existen")
        
        print ("\nError en los argumentos\n")
        print("\n"+ayuda+"\n")
        sys.exit(1)
        
        
#Handler para usar CTRL-C

def handler(signum, frame):
    sys.exit(0)

#Check de la url mandando un post y esperando respuesta
def checkUrl():
    try:
        p = log.progress('Probando URL: '+url)
        requests.post(url, timeout=2)
        p = log.success("Hay conexion con la url: "+url)
        return(1)
    except:
        print("No hay conexión con la url, terminando el script.")
        sys.exit(0)
        
#Crea el diccionario a partir de los parametros introducidos, siempre habra username y password nombrados de diferente forma, que serán la ubicacion de los payloads
#Añade los parametros POST necesarios y su valor de forma iterativa al diccionario

def createData():
    while True:
        while True:
            print("\nEjemplo de parametros POST- [username='user'&password='pass'&Login=Login] ")
            numParams = input("\nNumero de parametros POST: \n")
            numParams = int(numParams)
            if numParams >= 2:
                break
            print("ERROR: minimo debe haber dos parametros\n")
            
        #PARAMETROS PARA USER Y PASS
        
        print("---------")
        userParam = input("Nombre del parametro de usuario:\n")
        print("---------")
        passParam = input("Nombre del parametro de contraseña\n")
        data[userParam[:-1]] = ""
        data[passParam[:-1]] = ""
        print("---------")
        print("Parametros extra = "+str(numParams-2))
        print("---------")
        
        #PARAMETROS ADICIONALES
        
        for x in range(numParams-2):
            extraParam = input("Nombre del parametro adicional: \n")
            print("---------")
            extraParamValue = input("Valor del parametro adicional: \n")
            print("---------")
            data[extraParam[:-1]] = extraParamValue[:-1]
            
        print ("PETICIÓN POST:")
        print (data)
        print("---------")
        
        # COMPROBACIÓN DE QUE LOS PARAMETROS ESTEN CORRECTOS, DEFAULT YES
        
        select = input("Es correcta la estructura de la petición POST?      [Y][n]")
        select = select[:-1]
        if select == "N" or select == "n":
            data.clear()
            print("\n")
        else:
            return(1)
        

    

def busquedaDoble():
    
    #Busqueda con doble wordlist, en user y password
    
    #Guarda el numero de lineas de los diccionarios y abre la wordlist de users
    
    with codecs.open(passlist, "r", encoding="ascii", errors="ignore") as fp:
        linesPassword = len(fp.readlines())
    with codecs.open(userlist, "r", encoding="ascii", errors="ignore") as fp:
        linesUser = len(fp.readlines())
        
    fileuser = codecs.open(userlist, "r", encoding="ascii", errors="ignore")
    output = ""
    
    
    #Checkea la longitud de la respuesta de un intento erroneo de login
    
    reqCheck = requests.post(url, data=data, timeout=1)
    reqText = reqCheck.content
    lenCheck = len(reqText)

    #Inicio de los bucles anidados
    
    p = log.progress('Buscando combinaciones')
    
    with alive_bar(linesUser*linesPassword, force_tty=True, title="Progress", ctrl_c=True) as bar:
        
        for user in fileuser.readlines():
            user = user.strip()
            filepass = codecs.open(passlist, "r", encoding="ascii", errors="ignore")
            
            for password in filepass.readlines():
                password = password.strip()
                p.status("User: ["+user+ "] Password: ["+ password+"]")
                count = 0
                
                #Introduce user y password por iteracion
        
                for n in data:
                    if count==0:
                        data.update({n:user})
                    if count==1:
                        data.update({n:password})
                        break
                    count = count+1
                
                #Intenta hacer la request con los parametros y compara la longitud con la erronea
                try:
                    req = requests.post(url, data=data, timeout=1)
                    txt = req.content
                    lenReq = len(txt)
                    if lenReq > lenCheck or lenReq < lenCheck:
                        output = output + now[:-7]+"\nHit en la url: "+url+"\n[ + ] User: "+user+ " Password: "+ password+"\n"
                        print("[ + ] User: "+user+ " Password: "+ password)
                except:
                    pass
                bar()
            filepass.close()
            
        
        fileuser.close()
        
    outputFile = codecs.open(outputPath, "a", encoding="ascii", errors="ignore")
    outputFile.write(output)
    outputFile.write("\n")
    outputFile.close()
    return(1)

def busquedaPass():
    
    #Busqueda por contraseña
    
    #Guarda el numero de lineas del diccionario de password y abre el archivo 
    
    with codecs.open(passlist, "r", encoding="ascii", errors="ignore") as fp:
        linesPassword = len(fp.readlines())

    filepass = codecs.open(passlist, "r", encoding="ascii", errors="ignore")
    output = ""
    
    #Checkea la longitud de la respuesta de un intento erroneo de login
    
    
    reqCheck = requests.post(url, data=data, timeout=1)
    reqCheck = reqCheck.text
    lenCheck = len(reqCheck)
    
    
    #Inicio del bucle
    
    p = log.progress('Buscando combinaciones')
    with alive_bar(linesPassword, force_tty=True, title="Progress", ctrl_c=True) as bar:
        
        for password in filepass.readlines():
            password = password.strip()
            p.status("User: ["+username+ "] Password: ["+ password+"]")
            count = 0
            
            #Introduce user hardcoded y password por iteracion
            
            for n in data:
                if count==0:
                    data.update({n:username})
                if count==1:
                    data.update({n:password})
                    break
                count= count+1
                
            #Intenta hacer la request con los parametros y compara la longitud con la erronea

            try:
                
                req = requests.post(url, data=data, timeout=1)
                txt = req.text
                lenReq = len(txt)
                if lenReq > lenCheck or lenReq < lenCheck:
                    output = output + now[:-7]+"\nHit en la url: "+url+"\n[ + ] User: "+username+ " Password: "+ password+"\n"
                    print("[ + ] User: "+username+ " Password: "+ password)
            except:
                pass
            bar()
        filepass.close()
    outputFile = codecs.open(outputPath, "a", encoding="ascii", errors="ignore")
    outputFile.write(output)
    outputFile.write("\n")
    outputFile.close()
    return(1)
    
def busquedaUser():
    
    #Busqueda por usuario
    
    #Guarda el numero de lineas del diccionario de usuario y abre el archivo 
    
    
    with codecs.open(userlist, "r", encoding="ascii", errors="ignore") as fp:
        linesUser = len(fp.readlines())

    fileuser = codecs.open(userlist, "r", encoding="ascii", errors="ignore")
    output = ""
    
    #Checkea la longitud de la respuesta de un intento erroneo de login
    
    reqCheck = requests.post(url, data=data, timeout=1)
    reqCheck = reqCheck.text
    lenCheck = len(reqCheck)
    
    #Inicio del bucle
    
    p = log.progress('Buscando combinaciones')
    with alive_bar(linesUser, force_tty=True, title="Progress", ctrl_c=True) as bar:
        
        for user in fileuser.readlines():
            user = user.strip()
            p.status("User: ["+user+ "] Password: ["+ password+"]")
            count = 0
            
            #Introduce password harcoded y user por iteracion
            
            for n in data:
                if count==0:
                    data.update({n:user})
                if count==1:
                    data.update({n:password})
                    break
                count= count+1
                
            #Intenta hacer la request con los parametros y compara la longitud con la erronea
        
            try:
                req = requests.post(url, data=data, timeout=1)
                txt = req.text
                lenReq = len(txt)
                if lenReq > lenCheck or lenReq < lenCheck:
                    output = output + now[:-7]+"\nHit en la url: "+url+"\n[ + ] User: "+username+ " Password: "+ password+"\n"
                    print("[ + ] User: "+user+ " Password: "+ password)
            except:
                pass
            bar()
        fileuser.close()
        
    outputFile = codecs.open(outputPath, "a", encoding="ascii", errors="ignore")
    outputFile.write(output)
    outputFile.write("\n")
    outputFile.close()
    return(1)

if __name__ == '__main__':
    
    signal.signal(signal.SIGINT, handler)
    
    
    info()
    checkUrl()
    createData()
    

    if username != "" and passlist != "" and password == "" and userlist == "":
        busquedaPass()
    if username == "" and passlist == "" and password != "" and userlist != "":
        busquedaUser()
    if username == "" and passlist != "" and password == "" and userlist != "":
        busquedaDoble()
    
    sys.exit(1)
        
        


