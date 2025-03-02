import threading
import time
import os
import dataset.coleta as dataset
import pandas as pd
import numpy as np
from interfaceHeartRate import InterfaceHeartRate
import warnings

warnings.filterwarnings("ignore", category=np.ComplexWarning)

# Configuração global para parâmetros
window_size = 6             # valor padrão para window_size
lowfreq = 0.8               # valor padrão para lowfreq
highfreq = 3.3              # valor padrão para highfreq
peak = 3                    # valor padrão para peak
sliding_window = 250        # valor padrão para sliding_window
total_samples = 500         # valor padrão para total_samples
amount_windows = 7          # valor padrão para amount_windows
limiar = 0.8              # valor padrão para limiar



fs = 43.47



def get_sampling_rate(pcap_file, sampling_rates_df):
    rate_row = sampling_rates_df.loc[sampling_rates_df['File'] == pcap_file]
    if not rate_row.empty:
        return rate_row.iloc[0]['Sampling Rate (Hz)']
    else:
        raise ValueError(f"Taxa de amostragem não encontrada para o arquivo {pcap_file}")

# Função de processamento dos arquivos com parâmetros
def process_files(interface):
    path = "../captura/Scan"  # Caminho dos scans

    

    #Excluir texto no bmp_time.csv
    with open('bpm_time.csv', 'w') as f:
        f.write("")
        f.close()


    print("########## CSI EXPLORER Begins ##########")

    quantidade = 0
    sequence = 1
    while sequence < 2000 and quantidade < 2000:
        params = interface.get_params()
        if params:
            set_params(params['window_size'], params['lowfreq'], params['highfreq'], params['peak'])

        file = 'arq' + str(sequence)
        file_exists = dataset.check_next_file(file, path)

        print('Processando arquivo: ', file)
        # fs = get_sampling_rate(file + '.pcap', sampling_rates_df)

        if file_exists:
            samples_ammount_achieved = dataset.check_ammount_samples(file, path)
            if samples_ammount_achieved:
                step = (total_samples - sliding_window ) // (amount_windows - 1)

                for i in range(amount_windows):
                    start = i * step
                    end = start + sliding_window

                    # print(f"Processando janela {i+1} de {amount_windows} - {start} a {end} - taxrate: {fs} Hz")
                    bpm = dataset.process_pcap_file(file, path, sequence, window_size, lowfreq, highfreq, peak, start, end, limiar, fs)


                    interface.root.after(0, interface.show_heart_rate, round(bpm))

                
                quantidade += 1  # Incrementa a quantidade de processados
            print()
        else:
            break
        sequence += 1

    print("########## CSI EXPLORER Ends ##########")

# Função para inicializar parâmetros
def set_params(w_size, l_freq, h_freq, p, lim):
    global window_size, lowfreq, highfreq, peak, limiar
    window_size = w_size
    lowfreq = l_freq
    highfreq = h_freq
    peak = p
    limiar = lim

    print(f"Parâmetros definidos: window_size={window_size}, lowfreq={lowfreq}, highfreq={highfreq}, peak={peak}, sliding_window={sliding_window}, total_samples={total_samples}, limiar={limiar}")

if __name__ == "__main__":
    # Inicializar a interface
    interface = InterfaceHeartRate()

    processing_thread = threading.Thread(target=process_files, args=(interface,))
    processing_thread.start()
    # Iniciar o loop de eventos da interface gráfica
    interface.root.mainloop()

    