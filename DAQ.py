
# coding: utf-8

# In[ ]:


#Agradecimientos a Agustín Corbat por ayudarnos muchísimo con el código
import nidaqmx
from nidaqmx import stream_readers, stream_writers
from scipy import signal
import time
import numpy as np
import matplotlib.pyplot as plt

#%%
'''Primero se encuentra a qué número de device corresponde'''
def check_device():
    import nidaqmx.system
    system = nidaqmx.system.System.local()
    for dev in system.devices:
        print(dev)

#$$
'''Comienza la conexión con la placa:'''

cantidad_puntos=10000
samples = signal.triang(cantidad_puntos)*0.7-0.85 #armo una señal triangular de altura 0.7 y le resto valores como offset

x=np.zeros(10000)
'''
El problema de la placa es que no le gusta realizar dos tasks al mismo tiempo, entonces
se abre una comunicación donde continuamente se envía una señal (output) y se abre otra sobre 
la misma donde se va recolectando información (input)
'''
with nidaqmx.Task() as task_o: #abro comunicación
    test_Task = nidaqmx.Task()
    '''para generar'''
    task_o.ao_channels.add_ao_voltage_chan('Dev8/ao0') #le avisa qué canal será el que envíe la señal
                                        #El número de Dev corresponde al hallado con la función anterior check_device
    task_o.timing.cfg_samp_clk_timing(rate=223000, sample_mode= nidaqmx.constants.AcquisitionType.CONTINUOUS) #Rate opcional, máximo 2500000
    #Sets the source of the Sample Clock, the rate of the Sample Clock, and the number of samples to acquire or generate. (p.232)
    test_Writer = stream_writers.AnalogSingleChannelWriter(task_o.out_stream, auto_start=True) 
    test_Writer.write_many_sample(samples) #envía la señal triangular
    time.sleep(1)        
    
    with nidaqmx.Task() as task_i:
        '''para leer'''
        task_i.ai_channels.add_ai_voltage_chan('Dev8/ai1') #le avisa qué canal será el que reciba la señal
        task_i.timing.cfg_samp_clk_timing(rate=223000, sample_mode= nidaqmx.constants.AcquisitionType.CONTINUOUS)
        #Sets the source of the Sample Clock, the rate of the Sample Clock, and the number of samples to acquire or generate. (p.232)
        test_Reader = stream_readers.AnalogSingleChannelReader(task_i.in_stream)
#        time.sleep(2)
        test_Reader.read_many_sample(x, number_of_samples_per_channel=10000) #lee y guarda 10000 puntos en x
    

