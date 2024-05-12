import pytest
import time 
from implementacion_prueba import *

#Prueba para verificar si se establece correctamente una estrategia en el sistema
def test_establecer_estrategia():
    sistema = Sistema.get_instancia()
    estrategia = Estrategia1()
    sistema.establecer_estrategia(estrategia)
    assert sistema._estrategia == estrategia

#Prueba para verificar si se genera un error al establecer una estrategia no válida en el sistema
def test_establecer_estrategia_error():
    sistema = Sistema.get_instancia()
    with pytest.raises(ErrorEstrategia):
        sistema.establecer_estrategia("Estrategia No Válida")

#Prueba para verificar si se genera un error al establecer una temperatura no válida en el sensor
def test_establecer_temperatura_error():
    sensor = Sensor("Sensor 1")
    with pytest.raises(ErrorTemperatura):
        sensor.establecer_temp(("10:00:00", "30"))

#Prueba para verificar si se registra correctamente una temperatura en el sensor 
def test_temperatura_valida():
    sensor = Sensor("Sensor 1")
    temperatura = (time.strftime("%H:%M:%S"), 30)
    sensor.establecer_temp(temperatura)
    assert sensor.temperatura == temperatura

#Prueba para verificar si se registra correctamente un observador en el sensor
def test_registro_observador():
    sensor = Sensor("Sensor 1")
    sistema = Sistema.get_instancia()
    sensor.registro(sistema)
    assert sistema in sensor._observers

#Prueba para verificar si se maneja correctamente un error al registrar un observador no válido en el sensor
def test_registro_observador_error():
    sensor = Sensor("Sensor 1")
    with pytest.raises(ErrorObservador):
        sensor.registro("No es un observador válido")

#Prueba para verificar si se elimina correctamente un observador del sensor
def test_borrado_observador():
    sensor = Sensor("Sensor 1")
    sistema = Sistema.get_instancia()
    sensor.registro(sistema)
    sensor.borrado(sistema)
    assert sistema not in sensor._observers

#Prueba para verificar si se maneja correctamente un error al intentar eliminar un observador no registrado del sensor
def test_borrado_observador_error():
    sensor = Sensor("Sensor 1")
    sistema = Sistema.get_instancia()
    with pytest.raises(ErrorObservador):
        sensor.borrado(sistema)

#Prueba para verificar si se notifica correctamente a los observadores sobre cambios de temperatura
def test_notificacion_observadores(capfd):
    sensor = Sensor("Sensor 1")
    sistema = Sistema.get_instancia()
    sensor.registro(sistema)
    temperatura = ("10:00:00", 30)
    sensor.establecer_temp(temperatura)
    out, _ = capfd.readouterr()
    assert f"Timestamp: {temperatura[0]}, Temp: {temperatura[1]}" in out

#Pruebas para verificar si los cálculos se realizan correctamente
def test_calculo_estadisticas_estrategia1():
    estrategia = Estrategia1()
    temperaturas = [25, 28, 30, 32, 29, 27, 31, 26, 28, 30, 33, 35]
    estrategia.algoritmo(temperaturas)  

def test_calculo_estadisticas_estrategia2():
    estrategia = Estrategia2()
    temperaturas = [25, 28, 30, 32, 29, 27, 31, 26, 28, 30, 33, 35]
    estrategia.algoritmo(temperaturas)

def test_calculo_estadisticas_estrategia3():
    estrategia = Estrategia3()
    temperaturas = [25, 28, 30, 32, 29, 27, 31, 26, 28, 30, 33, 35]
    estrategia.algoritmo(temperaturas)
