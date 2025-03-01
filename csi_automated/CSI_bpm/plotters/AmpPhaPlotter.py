import math
import numpy as np
import matplotlib.pyplot as plt

#from analysis.dataAnalysis import Analyzing#julio

'''
Amplitude and Phase plotter
---------------------------

Plot Amplitude and Phase of CSI samples
and update the plots in the same window.

Initiate Plotter with bandwidth, and
call update with CSI value.
'''

__all__ = [
    'Plotter'
]

class Plotter():
    def __init__(self, bandwidth, nsamples):
        self.bandwidth = bandwidth

        nsub = int(bandwidth * 3.2)
        self.x_amp = np.arange(-1 * nsub/2, nsub/2)
        self.x_pha = np.arange(-1 * nsub/2, nsub/2)

        #self.x_amp2 = np.arange(30)#julio

        self.fig, axs = plt.subplots(2)

        self.ax_amp = axs[0]
        self.ax_pha = axs[1]
        #self.ax_amp2 = axs[2]#julio

        self.fig.suptitle('Nexmon CSI Explorer')

        #analisis = Analyzing(nsub, nsamples)#julio

        #joao comment plot 1
        #plt.ion()
        #plt.show() 
    
    def update(self, csi, nsamples):

        #print("numero de smaples: ", nsamples)#julio
        #self.ax_amp.clear()
        #self.ax_pha.clear()

        # These are also cleared with clear()
        self.ax_amp.set_ylabel('Amplitude')
        self.ax_pha.set_ylabel('Phase')
        self.ax_pha.set_xlabel('Subcarrier')

        try:
            self.ax_amp.plot(self.x_amp, np.abs(csi))
            self.ax_pha.plot(self.x_pha, np.angle(csi, deg=True))

        except ValueError as err:
            print(
                f'A ValueError occurred. Is the bandwidth {self.bandwidth} MHz correct?\nError: ', err
            )
            exit(-1)
        plt.draw()
        plt.pause(0.001)
    '''
    def update_time(self, csi, nsamples):

        #print("numero de smaples: ", nsamples)#julio
        #self.ax_amp.clear()
        #self.ax_pha.clear()

        # These are also cleared with clear()
        #self.ax_amp.set_ylabel('Amplitude')
        self.ax_amp2.set_ylabel('Amplitude')#julio
        #self.ax_pha.set_ylabel('Phase')
        self.ax_pha.set_xlabel('Subcarrier')

        try:
            self.ax_amp2.plot(self.x_amp2, np.abs(csi[128:158])) #julio adiciono 10log(x) logaritmo
            #print("subportadora: ", self.x_amp[7], "amplitud: ", np.abs(csi[7]))#julio
            #print("\n")#julio
            #self.ax_pha.plot(self.x_pha, np.angle(csi, deg=True))

        except ValueError as err:
            print(
                f'A ValueError occurred. Is the bandwidth {self.bandwidth} MHz correct?\nError 2: ', err
            )
            exit(-1)
        plt.draw()
        plt.pause(0.001)
    '''
    def __del__(self):
        pass
