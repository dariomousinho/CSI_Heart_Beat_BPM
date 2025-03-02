import fnmatch
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.fftpack import fft
from scipy.signal import butter, lfilter
from hampel import hampel
from sklearn.decomposition import PCA
from scipy.fft import fft, fftfreq
#from interfaceHeartRate import InterfaceHeartRate
from time import time
from datetime import datetime;
from pytz import timezone
import json
from os.path import dirname, join
import pickle
import os
from scipy.ndimage import median_filter


def variance_pca(series, sequence): ## sequence é as posições, de 1 ao 17

	current_dir = dirname(__file__)
	file_path = join(current_dir, "pca_variance.json")

	pca = PCA()
	principal_components = pca.fit_transform(series)

	explained_variance = pca.explained_variance_ratio_

	with open(file_path, 'r') as arquivo:
		dados = json.load(arquivo)

	dados[str(sequence)].append(explained_variance[0])

	with open(file_path, 'w') as arquivo:
		json.dump(dados, arquivo)
	
	

def iq_samples_abs(series):
	abs_series = {}
	for key in series.keys():
		for i in range(len(series[key])):
			valor = np.abs(series[key][i])
			if valor == 0:
				valor = -1 * 100
			else:
				valor = 20 * np.log10(valor)
			if key in abs_series:
				abs_series[key] = np.append(abs_series[key], valor)
			else:
				abs_series[key] = np.array(valor)

	abs_series = pd.DataFrame(abs_series)

	return abs_series

def iq_samples_abs_teste(series):
    abs_series = {}
    for key in series.keys():
        # Verificar se a chave existe no DataFrame
        if key in series.columns:
            abs_values = []
            for i in range(len(series[key])):
                try:
                    valor = np.abs(series[key][i])
                    if valor == 0:
                        valor = -1 * 100
                    else:
                        valor = 20 * np.log10(valor)
                    abs_values.append(valor)
                except (KeyError, IndexError) as e:
                    # Caso o índice ou a chave seja inválido, ignora
                    print(f"Erro ao acessar índice {i} na chave '{key}': {e}")
                    abs_values.append(np.nan)  # Usa NaN para valores inválidos
            abs_series[key] = abs_values
        else:
            print(f"Chave '{key}' não encontrada no DataFrame")
    # Converter em DataFrame para manter consistência
    abs_series = pd.DataFrame(abs_series)

    # Remover colunas ou linhas que contenham apenas NaN
    abs_series.dropna(axis=1, how='all', inplace=True)
    abs_series.dropna(axis=0, how='all', inplace=True)

    return abs_series

def hampel_filter(series):
	filtered = {}
	for key in series.keys():
		filtered[key] = hampel(series[key], window_size=31, n=3, imputation=True)
	filtered = pd.DataFrame(filtered)
	return filtered

def moving_avg_filter(series, window_size):
	moving_avg = {}

	for key in series.keys():                 #window=10 ###############################################################
		moving_avg[key] = series[key].rolling(window=window_size, min_periods=1, center=True).mean()
									
	moving_avg = pd.DataFrame(moving_avg)
	return moving_avg

def band_pass_filter(series, lowfreq, highfreq, fs= 43.47):
	t = 1.0 / fs
	lowcut = lowfreq
	highcut = highfreq
	#lowcut = 1.5
	#highcut = 3.67
	n = len(series)
	b, a = butter(5, [lowcut / (fs / 2), highcut / (fs / 2)], 'band', analog=False, output='ba')

	bandpass_samples_filter = {}
	for key in series.keys():
		bandpass_samples_filter[key] = lfilter(b, a, series[key])

	bandpass_samples_filter = pd.DataFrame(bandpass_samples_filter)

	return bandpass_samples_filter

def csi_pca(series):
	series = series.reset_index()
	for subcarrier in series.keys():
		for sample in range(len(series[subcarrier])):
			if np.isnan(series[subcarrier][sample]) or np.isinf(series[subcarrier][sample]):
				series[subcarrier][sample] = 0

	pca = PCA(n_components=1)
	series.columns = series.columns.astype(str)
	principal_components = pca.fit_transform(series)

	principal_components = pd.DataFrame(data=principal_components, columns=['PCA'])


	return principal_components
	
def heart_beat(n, xf, yf, highfreq, lowfreq):
	frequencias = []
	amplitudes = []
	i = 0
	sizeXf = len(xf)

	for i in range(sizeXf):
		if xf[i] > lowfreq and xf[i] < highfreq:
		#if xf[i] > 1.5 and xf[i] < 3.67:
			frequencias.append(xf[i])
			amplitudes.append(np.abs(yf[i]))

	amplitudes, frequencias = zip(*sorted(zip(amplitudes, frequencias)))

	j = len(frequencias) - 1
	frequenciasMax = []
	amplitudesMax = []

	for i in range(n):
		if j <= -1:
			break
		frequenciasMax.append(frequencias[j])
		amplitudesMax.append(amplitudes[j])	
		j-=1
	frequenciasMax, amplitudesMax = zip(*sorted(zip(frequenciasMax, amplitudesMax)))

	if j == -1:
		mediaFrequencia = sum(frequenciasMax) / len(frequenciasMax)
	else:
		mediaFrequencia = sum(frequenciasMax) / n
	bpm = round(mediaFrequencia * 60)

	#plot(frequenciasMax, amplitudesMax)

	#InterfaceHeartRate.show_heart_rate(bpm)
	#timestamp = time()
	#dt = datetime.fromtimestamp(timestamp, tz = timezone("America/Sao_Paulo"))
	#timestamp_bpm = dt.strftime("%d/%m/%Y %H:%M:%S")

	#arqSaida = open("batimentos.txt","a+")
	#arqSaida.write(str(bpm) + ' ' + str(timestamp_bpm) + '\n')
	#arqSaida.close()
	return bpm

def heart_beat_filtering(n, xf, yf, highfreq, lowfreq, limiar, timestamp, sequence):
	"""
	Calcula o BPM com base nas frequências e amplitudes filtradas.

	:param n: Número de picos a considerar.
	:param xf: Frequências da FFT.
	:param yf: Amplitudes da FFT.
	:param highfreq: Frequência superior do intervalo de interesse.
	:param lowfreq: Frequência inferior do intervalo de interesse.
	:param k: Fator para ajuste do limiar baseado no desvio padrão (default: 1.5).
	:return: BPM calculado.
	"""
	frequencias_amplitudes = []

	# Filtrar frequências dentro do intervalo esperado
	for i in range(len(xf)):
		if lowfreq <= xf[i] <= highfreq:
			frequencias_amplitudes.append([xf[i], np.abs(yf[i])])

	# Lista somente com as amplitudes

	amplitudes = []
	for fa in frequencias_amplitudes:
		amplitudes.append(fa[1])

	mean_amp = np.mean(amplitudes)
	std_amp = np.std(amplitudes)

	upper_limit = mean_amp + limiar * std_amp

	frequencias_amplitudes_filtradas  = []

	for freq, amp in frequencias_amplitudes:
		if  amp >= upper_limit:
			frequencias_amplitudes_filtradas.append([freq, amp])

	sorted_data = sorted(frequencias_amplitudes_filtradas, key=lambda x: x[1], reverse=True)

	top_frequencies_amplitudes = sorted_data[:n]

	top_frequencies = []
	top_amplitudes = []
	for freq, amp in top_frequencies_amplitudes:
		top_frequencies.append(freq)
		top_amplitudes.append(amp)

	
	
	print("Frequências (Filtradas):", [fa[0] for fa in frequencias_amplitudes_filtradas])
	print("Amplitudes (Filtradas):", [fa[1] for fa in frequencias_amplitudes_filtradas])
	print("Top Frequências:", top_frequencies)
	print("Top Amplitudes:", top_amplitudes)



	# plot_frequencies_comparison(
	# 	[fa[0] for fa in frequencias_amplitudes],  # Frequências originais [Só intervalo correto]
    # 	[fa[1] for fa in frequencias_amplitudes],
	# 	[f[0] for f in frequencias_amplitudes_filtradas],  # Frequências filtradas
	# 	[f[1] for f in frequencias_amplitudes_filtradas],
	# 	top_frequencies,
	# 	top_amplitudes,
	# 	upper_limit,
	# 	mean_value=mean_amp,
	# 	time=timestamp,
	# 	sequence=sequence

	# )

	# Calcular a média das frequências selecionadas
	if len(top_frequencies) > 0:
		media_frequencia = np.mean(top_frequencies)
	else:
		# Caso não haja picos válidos, retorne um BPM padrão ou 0
		media_frequencia = 0

	bpm = round(media_frequencia * 60)  # Converter para BPM
	return bpm
		

def plot_frequencies_comparison(
	original_frequencies,
	original_amplitudes,
	filtered_frequencies,
	filtered_amplitudes,
	top_frequencies,
	top_amplitudes,
	upper_limit=None,
	mean_value=None,
	title="Comparação de Frequências e Amplitudes",
	time=None,
	sequence=None
	):
	"""
	Plota a comparação das frequências e amplitudes antes e depois do filtro,
	destacando os picos selecionados.

	:param original_frequencies: Frequências antes do filtro.
	:param original_amplitudes: Amplitudes antes do filtro.
	:param filtered_frequencies: Frequências após o filtro.
	:param filtered_amplitudes: Amplitudes após o filtro.
	:param top_frequencies: Frequências dos picos selecionados.
	:param top_amplitudes: Amplitudes dos picos selecionados.
	:param title: Título do gráfico.
	"""
	plt.figure(figsize=(12, 6))

	# Plotar dados originais
	plt.plot(original_frequencies, original_amplitudes, 'o--', color='gray', label='Original', alpha=0.7)

	# Plotar dados filtrados
	plt.plot(filtered_frequencies, filtered_amplitudes, 'o-', color='blue', label='Filtrado', alpha=0.9)

	# Plotar os picos
	plt.scatter(top_frequencies, top_amplitudes, label="Top Picos", color="red", zorder=5)

	# Adicionar texto para os picos
	for freq, amp in zip(top_frequencies, top_amplitudes):
		plt.text(freq, amp, f"{freq:.2f} Hz", fontsize=9, color="red")

	
	if upper_limit is not None:
		plt.axhline(y=upper_limit, color='orange', linestyle='--', linewidth=1.5, label='Limiar Superior')

	if mean_value is not None:
		plt.axhline(y=mean_value, color='purple', linestyle='-', linewidth=1.5, label='Média')

	plt.title(title)
	plt.xlabel("Frequência (Hz)")
	plt.ylabel("Amplitude")
	plt.legend()
	plt.grid(True)

	readable_timestamp = str(datetime.fromtimestamp(time).strftime('%Y-%m-%d_%H-%M-%S.%f'))
	file_name = f"arq{sequence}_{readable_timestamp}.png"
	output_file = os.path.join("plot_sitting", file_name)

	plt.savefig(output_file, format='png', dpi=300)
	plt.close()  # Fecha o gráfico para liberar memória

def csi_fft(series, peak, highfreq, lowfreq,limiar, timestamp, sequence):
	yf = fft(series)
	xf = fftfreq(yf.size, 0.023)

	return heart_beat_filtering(peak, xf, yf, highfreq, lowfreq,limiar, timestamp,sequence)
	
# def plot(x,y):
# 	f, ax = plt.subplots()
# 	plt.plot(x, color = 'green')
# 	ax.set(xlabel='Frequencias', ylabel='dB', title='Frequencias Máximas a cada 20 segundos')
# 	plt.show()

def plot(series, title):
	f, ax = plt.subplots()
	plt.plot(series)
	ax.set(xlabel='Amostras', ylabel='Amplitude', title=title)
	plt.show()

def plot_band_pass_frequency(series, fs, title="After Band Pass Filter - Frequency Domain"):
    """
    Plota o gráfico do sinal filtrado no domínio da frequência.

    :param series: DataFrame com os sinais filtrados (uma coluna por subportadora).
    :param fs: Frequência de amostragem do sinal (Hz).
    :param title: Título do gráfico.
    """
    # Calcula a FFT para cada subportadora
    fft_results = []
    freqs = fftfreq(series.shape[0], d=1/fs)  # Frequências associadas à FFT

    for col in series.columns:
        fft_result = fft(series[col].to_numpy())
        fft_results.append(np.abs(fft_result))

    # Converte os resultados em um array numpy
    fft_results = np.array(fft_results)

    # Plota o gráfico
    plt.figure(figsize=(10, 6))
    for i in range(fft_results.shape[0]):
        plt.plot(freqs[:len(freqs)//2], fft_results[i][:len(freqs)//2])

    plt.title(title)
    plt.xlabel("Frequência (Hz)")
    plt.ylabel("Amplitude")
    plt.xlim(0, 4)  # Define um limite até 4 Hz para foco em frequências cardíacas
    plt.grid()
    plt.show()

def mediana_filter(series, size):
    return median_filter(series, 15)


def analyze(csi, sequence, window_size=3, lowfreq=1, highfreq=2.5, peak=4, limiar=1.5, fs=43.47, timestamp=None):
	

	
	series = moving_avg_filter(csi, window_size)
	# plot_band_pass_frequency(series,fs=43.47, title="After Moving Average Filter")

	series = band_pass_filter(series, lowfreq, highfreq,fs )
	# plot_band_pass_frequency(series,fs=43.47, title="Após Filtro Passa Banda")

	
	# series_abs = iq_samples_abs(series)
	# plot(series_abs, "All subcarrier's magnitude")

	series_abs = csi_pca(series)
	# plot(series_abs, "Após PCA")


	x = series_abs['PCA'].to_numpy()
	bpm = csi_fft(x, peak, highfreq, lowfreq, limiar, timestamp, sequence)
	# plot(bpm, "FFT")


	return bpm


def get_sampling_rate(pcap_file, sampling_rates_df): #Não utilizada
	
    rate_row = sampling_rates_df.loc[sampling_rates_df['File'] == pcap_file]
    if not rate_row.empty:
        return rate_row.iloc[0]['Sampling Rate (Hz)']
    else:
        raise ValueError(f"Taxa de amostragem não encontrada para o arquivo {pcap_file}")