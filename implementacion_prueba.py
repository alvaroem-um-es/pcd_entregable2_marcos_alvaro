# -------------------------------------------------------------- #
#  Copyright (c) UMU Corporation. All rights reserved.
# ######################## PROGRAMACIÓN FUNCIONAL, OBJETOS Y PATRONES DE DISEÑO ####################### #
# ########################  ENTREGABLE 2  ####################### #


#### IMPLEMENTACIÓN CÓDIGO PARA ENTORNO IoT SENSOR DE TEMPERATURA EN INVERNADERO ####

# -------------------------------------------------------------- #

#### CLASES PARA LAS EXCEPCIONES  ####



from abc import ABC, abstractmethod
import time
import random
import functools
import numpy as np



class ErrorTemperatura(Exception):
    pass

class ErrorObservador(Exception):
    pass

class ErrorEstrategia(Exception):
    pass





# -------------------------------------------------------------- #

#### CLASES PARA LOS OBJETOS Y LOS PATRONES DE DISEÑO PERTENECIENTES AL ENUNCIADO CON SUS MÉTODOS CORRESPONDIENTES ####

# OBSERVER

class Observable:
    def __init__(self):
        self._observers = []

    def registro(self, observer):

        """
        Este método se utiliza para registrar un nuevo 
        observador en la lista de observadores.
        """
        
        if not isinstance(observer,Observer) :
            print("Sistema no es observador.")
            raise ErrorObservador
        self._observers.append(observer)

    def borrado(self, element):

        """
         Este método se utiliza para eliminar un 
         observador de la lista de observadores. 
        """

        if element not in self._observers :
            print("Observador no registrado.")
            raise ErrorObservador
        self._observers.remove(element)

    def notificacion(self, temperatura):

        """
         Este método se utiliza para notificar a todos los observadores
         registrados cuando se produce un evento de interés.
        """

        for element in self._observers:
            element.actualizar(temperatura)

class Observer(ABC):
    @abstractmethod
    def actualizar(self, temperatura):
        pass


class Sensor(Observable): 

    """
     Es una clase que hereda de Observable, lo que significa que es capaz de notificar 
     a otros objetos (observadores) sobre cambios en la temperatura. 
     Tiene un método establecer_temp(self, temperatura) que se utiliza para establecer 
     la temperatura actual del sensor. 
    
    """


    def __init__(self, name):
        super().__init__()
        self.temperatura = 0
        self.name = name

    def establecer_temp(self, temperatura):
        if not isinstance(temperatura[1],int) :
            print("La temperatura debe ser un número entero.")
            raise ErrorTemperatura
        self.temperatura = temperatura
        self.notificacion(self.temperatura)



class Sistema(Observer):

    """
     Es una clase que actúa como un observador. Implementa el método 
     actualizar(self, temperatura) definido en la clase Observer. Cuando se llama 
     a este método, imprime el tiempo y la temperatura recibida como argumento.
     Si se ha establecido una estrategia, crea instancias de Estadísticos, 
     UmbralTemperatura y AumentoTemperatura'
    """

    SingleInstance = None

    def __init__(self):
        self._name = "Sistema_funcional" 
        self._estrategia=None

    @classmethod
    def get_instancia(cls) :
        if not cls.SingleInstance :
            cls.SingleInstance = cls()
        return cls.SingleInstance
    
    def actualizar(self, temperatura): 
        print ("Timestamp: {}, Temp: {}".format(temperatura[0],temperatura[1]))
        if self._estrategia is not None:
            stats = Estadísticos()   
            stats.establecer_estrategia(self._estrategia)  
            umbral = UmbralTemperatura(stats)
            subida = AumentoTemperatura(umbral)
            t = temperatura[1]
            subida.solicitud(t)
        else:
            print("Error: No se ha establecido ninguna estrategia en el sistema.")


    def establecer_estrategia(self,estrategia) :
        if (isinstance(estrategia,Estrategia1)) or (isinstance(estrategia,Estrategia2)) or (isinstance(estrategia,Estrategia3)) :
            self._estrategia  = estrategia
        else :
            print("La estrategia elegida no consta.")
            raise ErrorEstrategia
        




# PATRÓN STRATEGY:
class Estrategia(ABC) :

    """
    El patrón Strategy se utiliza para definir diferentes estrategias 
    de cálculo de estadísticas sobre un conjunto de datos de temperatura.

    """

    def algoritmo(self,T) :
        pass



class Estrategia1(Estrategia):
    def algoritmo(self, T):
        media = np.mean(T)
        desviacion_tipica = np.std(T)
        print(f"\n\tCálculo de la media y desviación típica: \n\t|\tMedia: {round(media, 2)}\n\t|\tDesviación típica: {round(desviacion_tipica, 2)}\n")




class Estrategia2(Estrategia):
    def algoritmo(self, T):
        print("\tCómputo de cuantiles:\n")
        cuartiles = np.percentile(T, [25, 50, 75])
        cuartil1, cuartil2, cuartil3 = cuartiles
        print(f"\t\tCuartiles: {cuartil1}, {cuartil2}, {cuartil3}\n")



class Estrategia3(Estrategia):
    def algoritmo(self, T):
        maximo = max(T)
        minimo = min(T)
        print(f"\n\tValores máximos y mínimos en un periodo de 60 segundos: máximo:{maximo}, mínimo:{minimo}\n")





#CHAIN OF RESPONSABILITY
class Manejador(ABC) : 

    """
    Esta clase define la interfaz común para todos los manejadores en la cadena.
    El constructor toma un parámetro sucesor, que representa el próximo manejador en la cadena.
    El método solicitud es el método clave que maneja una solicitud (en este caso, la temperatura). 
    La implementación predeterminada en esta clase base no realiza ninguna acción y debe ser sobrescrita por las subclases.

    """

    def __init__(self,sucesor=None) :
        self.sucesor = sucesor

    def solicitud(self,temperatura) :
        pass



class Estadísticos(Manejador) :    
    def __init__(self,sucesor=None,estrategia=None,temperaturas_stats=[]) :
        super().__init__(sucesor)
        self.estrategia = estrategia
        self.temperaturas_stats = temperaturas_stats

    def establecer_estrategia(self,estrategia_concreta) :
        self.estrategia = estrategia_concreta  

    def solicitud(self,temperatura) :
        self.temperaturas_stats.append(temperatura)
        if len(self.temperaturas_stats) == 12:
            print(f"Cálculos de interés de las temperaturas registradas en el último minuto: ")
            self.estrategia.algoritmo(self.temperaturas_stats)
            self.temperaturas_stats.clear() 

        #Pasamos al siguiente a través de lo heredado de la interfaz de Manejador:
        if self.sucesor :
            self.sucesor.solicitud(temperatura)


class UmbralTemperatura(Manejador) :
    def __init__(self,sucesor=None,temperaturas_umbral = []) :
        super().__init__(sucesor)
        self.temperaturas_umbral = temperaturas_umbral

    def solicitud(self,temperatura) : 
        self.temperaturas_umbral.append(temperatura)

        if temperatura > 33 :
            print("Temperatura actual por encima de 33ºC") 

        #Pasamos al siguiente a través de lo heredado de la interfaz de Manejador:
        if self.sucesor :
            self.sucesor.solicitud(temperatura)


class AumentoTemperatura(Manejador) :
    def __init__(self,sucesor=None,temperaturas_aumento = []) :
        super().__init__(sucesor)
        self.temperaturas_aumento = temperaturas_aumento

    def solicitud(self,temperatura) :
        self.temperaturas_aumento.append(temperatura)
        if len(self.temperaturas_aumento) == 6:
            sub = list(filter(lambda x: x>10,self.temperaturas_aumento))
            if len(sub) > 0 :
                print("La temperatura ha aumentado más de 10 grados en los últimos 30 segundos.")
            self.temperaturas_aumento.clear() 
        
        #Pasamos al siguiente a través de lo heredado de la interfaz de Manejador:
        if self.sucesor :
            self.sucesor.solicitud(temperatura)




# -------------------------------------------------------------- #

#### INSTANCIAMIENTO DE LAS CLASES Y COMPROBACIÓN DE ERRORES ####


if __name__ == "__main__":

    sensor = Sensor("Sensor 1")
    
    sistema = Sistema.get_instancia()

    # Registro del sistema como observador del sensor
    sensor.registro(sistema)

    estrategia = Estrategia1()

    # Establecemos la estrategia en el sistema
    sistema.establecer_estrategia(estrategia)

    # Simulamos la generación de datos del sensor y su procesamiento por el sistema
    for _ in range(60):
        temperatura = (time.strftime("%H:%M:%S"), random.randint(20, 40))
        sensor.establecer_temp(temperatura)
        time.sleep(5)  

    # Prueba de error: Intentamos establecer una estrategia no válida en el sistema
    try:
        sistema.establecer_estrategia("Estrategia No Válida")
    except ErrorEstrategia:
        print("Error: La estrategia elegida no es válida.")

    # Prueba de error: Establecemos una temperatura no válida en el sensor
    try:
        sensor.establecer_temp(("10:00:00", "30")) 
    except ErrorTemperatura:
        print("Error: La temperatura debe ser un número entero.")




