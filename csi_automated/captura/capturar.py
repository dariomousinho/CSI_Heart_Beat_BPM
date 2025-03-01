import sys
import os
import subprocess
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mac_identify')))
from mac import WifiMacScanner

class CaptureWifiPcaps:

    def __init__(self):
        scanner = WifiMacScanner()
        networks_rank = scanner.show_by_signal()  # Classificar pela intensidade do sinal
        # Encontrar a rede com maior sinal e frequência de 5.0 GHz
        strongest_network = None
        for network in networks_rank:
            if 'Frequency' in network and 'Signal' in network:
                if '5' == network['Frequency'][0] and '<Hidden>' != network['SSID']:  # Frequência de 5 GHz
                    strongest_network = network
                    break

        print("Redes Wi-Fi disponíveis:")
        for network in networks_rank:
            # Checar se a chave SSID e outras chaves existem
            if 'SSID' in network and 'Address' in network and 'Frequency' in network:
                signal = network.get('Signal', 'N/A')
                channel = network.get('Channel', 'N/A')
                bandwidth = network.get('Bandwidth', 'N/A')
                
                print(f"SSID: {network['SSID']}, Endereço: {network['Address']}, Sinal: {signal} dBm, Canal: {channel}, Frequência: {network['Frequency']}, Largura de Banda: {bandwidth}")
        
        print("\nRede Wi-Fi mais forte:")
        if strongest_network:
            print(f"SSID: {strongest_network.get('SSID', 'N/A')}, Endereço: {strongest_network.get('Address', 'N/A')}, Sinal: {strongest_network.get('Signal', 'N/A')} dBm, Canal: {strongest_network.get('Channel', 'N/A')}, Frequência: {strongest_network.get('Frequency', 'N/A')}, Largura de Banda: {strongest_network.get('Bandwidth', 'N/A')}")
            self.execute_capturar_script(strongest_network.get("Address", ""), strongest_network.get("Channel", ""))
        else:
            print("Nenhuma rede Wi-Fi encontrada.")
            
    def execute_capturar_script(self, mac_address, channel):
        """Executa o script capturar.sh com os parâmetros especificados."""
        try:
            time.sleep(10)
            result = subprocess.run(
                ["sudo", "bash", "capturar.sh", "80", channel, mac_address], 
                capture_output=True, 
                text=True, 
                check=True
            )
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar o script: {e}")

    
if __name__ == "__main__":
    CaptureWifiPcaps()
