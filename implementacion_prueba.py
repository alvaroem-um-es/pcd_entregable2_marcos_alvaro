
# importacion de librerias necesarias
from abc import ABC, abstractmethod
import time
import random
import numpy as np


# R1: patron singleton
class SistemaIoT:
    _instancia = None
    def __init__(self):

        # asegurarse de que la inicializacion solo se realiza una vez
        if not hasattr(self, 'inicializado'):
            self.datos_temperatura = []  
            self.inicializado = True  

    @classmethod
    def obtener_instancia(cls):
        if cls._instancia is None:
            cls._instancia = cls()
        return cls._instancia

    def recibir_temperatura(self, marca_temporal, temperatura):
        try:
            self.datos_temperatura.append((marca_temporal, temperatura))
            self.manejar_nueva_temperatura(marca_temporal, temperatura)
        except Exception as e:
            print("Error al recibir temperatura:", e)

    def manejar_nueva_temperatura(self, marca_temporal, temperatura):
        try:
            # verificar si la temperatura actual esta por encima del umbral
            umbral = 35 
            if temperatura > umbral:
                print(f"Alerta: La temperatura ha superado el umbral de {umbral}°C. Temperatura actual: {temperatura}°C")

            datos_recientes = list(filter(lambda x: marca_temporal - x[0] <= 30, self.datos_temperatura))
            if datos_recientes and (max(datos_recientes, key=lambda x: x[1])[1] - min(datos_recientes, key=lambda x: x[1])[1] > 10):
                print("Alerta: La temperatura ha aumentado más de 10 grados centígrados en los últimos 30 segundos.")

        except Exception as e:
            print("Error al manejar nueva temperatura:", e)
            
    def obtener_datos_singleton(self):
        return self.datos_temperatura

# R2: patron observer
# clase observable (sujeto)
class Observable:
    def __init__(self):
        self._observadores = []

    def registrar_observador(self, observador):
        self._observadores.append(observador)

    def remover_observador(self, observador):
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar_observadores(self, datos):
        for observador in self._observadores:
            observador.actualizar(datos)

# clase observador
class Observador(ABC):
    @abstractmethod
    def actualizar(self, datos):
        pass

# definicion del observador
class SensorDeTemperatura(Observador):
    def __init__(self, nombre):
        self.nombre = nombre

    def actualizar(self, datos):
        try:
            marca_temporal, temperatura = datos
            print(f"{self.nombre} ha recibido datos de temperatura: {temperatura}°C en el momento {marca_temporal}")
        except Exception as e:
            print(f"Error en {self.nombre} al actualizar datos de temperatura:", e)


# R3: cadena de responsabilidad
class PasoCadenaResponsabilidad(ABC):
    def __init__(self, sucesor=None):
        self.sucesor = sucesor
    
    @abstractmethod
    def manejar(self, datos):
        pass

class ComprobarUmbral(PasoCadenaResponsabilidad):
    def __init__(self, umbral, sucesor=None):
        super().__init__(sucesor)
        self.umbral = umbral

    def manejar(self, datos):
        # temperatura actual
        temperatura_actual = datos[-1][1]
        if temperatura_actual > self.umbral:
            print(f"Alerta: La temperatura actual está por encima del umbral de {self.umbral}°C")

        # llamar al siguiente paso en la cadena de responsabilidad
        if self.sucesor:
            self.sucesor.manejar(datos)

class ComprobarAumentoTemperatura(PasoCadenaResponsabilidad):
    def __init__(self, sucesor=None):
        super().__init__(sucesor)
        self.alerta_disparada = False  # Controlar si la alerta ya se ha disparado

    def manejar(self, datos):
        # datos de los ultimos 30 segundos
        datos_recientes = [x for x in datos if datos[-1][0] - x[0] <= 30]

        if len(datos_recientes) > 0:
            max_temp = max(datos_recientes, key=lambda x: x[1])[1]
            min_temp = min(datos_recientes, key=lambda x: x[1])[1]

            # verificar si la temperatura ha aumentado mas de 10 grados
            if max_temp - min_temp > 10:
                if not self.alerta_disparada:
                    print("Alerta: La temperatura ha aumentado más de 10 grados en los últimos 30 segundos")
                    self.alerta_disparada = True
            else:
                self.alerta_disparada = False

        # llamar al siguiente paso en la cadena de responsabilidad
        if self.sucesor:
            self.sucesor.manejar(datos)

class CalcularEstadisticos(PasoCadenaResponsabilidad):
    def manejar(self, datos, estrategia):

        # filtra las temperaturas de los ultimos 60 segundos
        datos_recientes = [x for x in datos if datos[0][0] - x[0] <= 60]
        
        contexto = ContextoEstadisticas()

        contexto.establecer_estrategia(estrategia)
        contexto.ejecutar_estrategia(datos_recientes)

        # llamar al siguiente paso en la cadena de responsabilidad
        if self.sucesor:
            self.sucesor.manejar(datos)

# Creando la cadena de responsabilidad
def crear_cadena_responsabilidad(umbral):
    paso3 = ComprobarAumentoTemperatura()
    paso2 = ComprobarUmbral(umbral, sucesor=paso3)
    paso1 = CalcularEstadisticos(sucesor=paso2)

    return paso1


# R4: estrategias
class EstrategiaEstadisticas(ABC):
    @abstractmethod
    def calcular_estadisticas(self, datos):
        pass

# media y desviación típica
class EstrategiaMediaDesviacionEstandar(EstrategiaEstadisticas):
    def calcular_estadisticas(self, datos):
        try:
            if datos:
                temperaturas = list(map(lambda x: x[1], datos))
                media = sum(temperaturas) / len(temperaturas)
                desviacion_tipica = np.std(temperaturas)
                print(f"Media: {media:.2f}, Desviación Típica: {desviacion_tipica:.2f}")
        except Exception as e:
            print("Error en EstrategiaMediaDesviacionEstandar:", e)

# cuantiles
class EstrategiaCuantiles(EstrategiaEstadisticas):
    def calcular_estadisticas(self, datos):
        try:
            if datos:
                temperaturas = list(map(lambda x: x[1], datos))
                q1 = np.percentile(temperaturas, 25)
                q3 = np.percentile(temperaturas, 75)
                print(f"Cuantiles 25 y 75: {q1:.2f}, {q3:.2f}")
        except Exception as e:
            print("Error en EstrategiaCuantiles:", e)

# maximo y minimo
class EstrategiaMaxMin(EstrategiaEstadisticas):
    def calcular_estadisticas(self, datos):
        try:
            if datos:
                temperaturas = list(map(lambda x: x[1], datos))
                maximo = max(temperaturas)
                minimo = min(temperaturas)
                print(f"Máximo: {maximo:.2f}, Mínimo: {minimo:.2f}")
        except Exception as e:
            print("Error en EstrategiaMaxMin:", e)

# clase ContextoEstadisticas
class ContextoEstadisticas:
    def __init__(self):
        self.estrategia_actual = None

    def establecer_estrategia(self, estrategia):
        self.estrategia_actual = estrategia

    def ejecutar_estrategia(self, datos):
        if self.estrategia_actual:
            self.estrategia_actual.calcular_estadisticas(datos)
        else:
            print("No se ha establecido una estrategia")


def main():
    system = SistemaIoT()

    contexto = ContextoEstadisticas()

    # cambiar entre EstrategiaMaxMin, EstrategiaCuantiles y EstrategiaMediaDesviacionEstandar
    estrategia = EstrategiaMediaDesviacionEstandar()
    contexto.establecer_estrategia(estrategia)

    umbral = 35  
    cadena_responsabilidad = crear_cadena_responsabilidad(umbral)

    try:
        while True:
            marca_temporal = int(time.time())
            temperatura = random.uniform(20, 40)

            system.recibir_temperatura(marca_temporal, temperatura)

            datos_temperatura = system.datos_temperatura[-60:]  # ultimos 60 segundos
            cadena_responsabilidad.manejar(datos_temperatura, estrategia)

            time.sleep(5)
    except KeyboardInterrupt:
        print("\nFinalizando el programa...")

if __name__ == "__main__":
    main()