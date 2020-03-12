
# coding: utf-8

# In[ ]:


#Agradecimientos a Agustín Corbat por ayudarnos muchísimo con el código
import nidaqmx
from nidaqmx import stream_readers, stream_writers
from scipy import signal
import time
import numpy as np
import matplotlib.pyplot as plt
from simple_pid import PID

'''El código es el mismo que el de DAQ modificado para que envíe y reciba sólo una señal
y agregando el PID. Para entender mejor la comunicación con la DAQ correr el archivo "DAQ.py"'''

#Settear los parámetros del PID Kp, Ki, Kd y setpoint el valor que se desea obtener
pid = PID(Kp,Ki,Kd, setpoint= )
y = np.zeros(1)
inicial = -0.625 #valor inicial del PID 

controles = []
tensiones = []
with nidaqmx.Task() as task_o:
    test_Task = nidaqmx.Task()
    '''para generar'''
    task_o.ao_channels.add_ao_voltage_chan('Dev8/ao0')
    test_Writer = stream_writers.AnalogSingleChannelWriter(task_o.out_stream, auto_start=True) 
    tension = inicial
    test_Writer.write_one_sample(tension)
    time.sleep(1)
    
    with nidaqmx.Task() as task_i:
        '''para leer'''
        task_i.ai_channels.add_ai_voltage_chan('Dev8/ai1')
        test_Reader = stream_readers.AnalogSingleChannelReader(task_i.in_stream)
        '''comienza el PID:'''
        try:
            while True:
                # read from DAQ
                y = test_Reader.read_one_sample()
                
                # compute new ouput from the PID according to the systems current value
                correccion = pid(y)
#                correccion = -0.001
                
                # feed the PID output to the system 
                tension -= correccion
                tension = np.clip(tension, -9, 9) #tension, min_valor, max_valor
                
                # Set actuator value
                test_Writer.write_one_sample(tension)
                
                print(tension)
                controles.append(tension)
                tensiones.append(y)
                
        except KeyboardInterrupt:
            pass
        
'''
En el caso de realizar el experimento de espectroscopía láser de gas de rubidio:
Originalmente no se tenía el valor inicial, correspondiente al valor que se debía alimentar el
experimento (en voltaje) para que se reproduzca una transición fija, conocida y querida.
La forma de encontrarlo fue tomar un valor inicial bruto, en nuestro caso -0.8, y luego en vez
de tomar las correcciones del PID se tomó una corrección fija de 0.001, razón por la cual está con #
Por tanto esto reproducía un barrido a pasos de 0.001.
A la salida obtuvimos una señal DAVS. Se reconoció la segunda transición y se contó cuantos pasos
fueron necesarios hasta ese valor. Así, la alimentación correspondiente se encontraría a cantidad_pasos*0.001 
de la señal original (o sea 0.8)
En nuestro caso, la segunda transición se encontró a 1750 puntos, por lo tanto el valor inicial
era -0.8 + 1750*0.001=-0.625
Con este valor (-0.625V) fue posible localizar el láser en la 2da transición
'''

