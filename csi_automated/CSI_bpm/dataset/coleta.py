import config
from analysis.dataAnalysis import analyze
import decoders.interleaved as decoder
from plotters.AmpPhaPlotter import Plotter
import os
import time
from datetime import datetime
import csv


def append_number_to_csv(file_name, number, timestamp):

    readable_timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')

    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([readable_timestamp, number])

def append_timestamps_to_csv(file_name, timestamp):


    for i in range(500):
        readable_timestamp = datetime.fromtimestamp(timestamp[i]).strftime('%Y-%m-%d %H:%M:%S.%f')

        with open(file_name, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([i, readable_timestamp])


def process_pcap_file(pcap_filename, caminho, sequence, window_size, lowfreq, highfreq, peak, begin, end, limiar,fs):

    #pcap_filepath = '../Scan'
   
    if '.pcap' not in pcap_filename:
        pcap_filename += '.pcap'
    pcap_filepath = '/'.join([caminho, pcap_filename])    
    try:
        samples = decoder.read_pcap(pcap_filepath)
    except FileNotFoundError:
        print(f'File {pcap_filepath} not found.')
        exit(-1)
    
    csi_data = samples.get_pd_csi()
    timestamps = samples.timestamps
    timestamp = timestamps[end]

    data = analyze(csi_data[begin:end], sequence, window_size, lowfreq, highfreq, peak, limiar,fs, timestamp)

    # append_number_to_csv('bpm_time.csv', data, timestamp)
    # append_timestamps_to_csv('bpm_time_samples.csv',  timestamps)


    return data

    

    #function to check if next file exists. Wait until 15 seconds
def check_next_file(file_name, path):
    limit = 0
    while(limit <= 500):
        if '.pcap' not in file_name:
            file_name += '.pcap'
        pcap_filepath = '/'.join([path, file_name])   
        try:
            with open(pcap_filepath, 'r') as f:
                limit = 0
                return True
        except IOError:
            print("Waiting 0.25 seconds to receive next file")
            time.sleep(0.5)
            limit += 1
    print(limit)
    print("Timeout")
    return False



#function to check if file has the ammount of samples. Wait until 3 seconds
def check_ammount_samples(pcap_filename, path):
    limit = 0
    while(limit <= 300):
        if '.pcap' not in pcap_filename:
            pcap_filename += '.pcap'
        pcap_filepath = '/'.join([path, pcap_filename])    
        try:
            pcap_filesize = os.stat(pcap_filepath).st_size
            with open(pcap_filepath, 'rb') as pcapfile:
                fc = pcapfile.read()
                bandwidth = decoder.__find_bandwidth(
                    # 32-36 is where the incl_len
                    # bytes for the first frame are
                    # located.
                    # https://wiki.wireshark.org/Development/LibpcapFileFormat/
                    fc[32:36]
                )
            # Number of OFDM sub-carriers
            nsub = int(bandwidth * 3.2)
            samples = decoder.__find_nsamples_max(pcap_filesize, nsub)
            if samples == 500:
                return True
            else:
                print('Waiting 0.25 seconds to receive all samples', limit)
                time.sleep(0.25)
                limit += 1

        except FileNotFoundError:
            print(f'File {pcap_filepath} not found.')
            exit(-1)
        
    print("Timeout, not enough samples")
    return False


