import subprocess
import re
import csv

class WifiMacScanner:
    def get_wifi_scan_results(self):
        try:
            # Ativando a interface
            subprocess.run(["sudo", "ip" ,"link", "set", "wlan0", "up"], check=True)
            result = subprocess.run(
                ["sudo", "iw", "wlan0", "scan"],  # Usando o comando 'iw scan'
                capture_output=True,
                text=True,
                check=True
            )

            scan_lines  = result.stdout.splitlines()
            
            with open("wifi_scan_debug.txt", "w") as debug_file:
                debug_file.write("\n".join(scan_lines))
            
            return scan_lines
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar o comando: {e}")
            return []
        
    def parse_scan_results(self, scan_results):
        networks = []
        current_network = {}
        in_ht_operation = False
        
        for line in scan_results:
            line = line.strip()
            
            # Start of a new network
            if line.startswith("BSS ") and line.count(":") > 2:
                if current_network:
                    networks.append(current_network)
                    
                current_network = {"Channel": "Unknown"}  # Initialize with default channel value
                in_ht_operation = False


                address = re.search(r"BSS ([\da-fA-F:]+)", line)
                if address:
                    current_network["Address"] = address.group(1)
                    print(f"DEBUG: Found BSS -> {current_network['Address']}")  # Debug print

            
            # SSID information
            elif "SSID:" in line:
                ssid_match = re.search(r'SSID: (.+)', line)
                if ssid_match:
                    raw_ssid = ssid_match.group(1)
                    # Check if SSID is hidden (contains null bytes)
                    if "\\x00" in raw_ssid or raw_ssid.strip() == "":
                        current_network["SSID"] = "<Hidden>"
                    else:
                        current_network["SSID"] = raw_ssid
                    print(f"DEBUG: Processing SSID -> {current_network['SSID']}")  # Debug print
    
    
            # Frequency information
            elif "freq:" in line:
                freq_match = re.search(r"freq: (\d+)", line)
                if freq_match:
                    current_network["Frequency"] = freq_match.group(1)
            
            # Signal strength
            elif "signal:" in line:
                signal_match = re.search(r"signal: ([-\d.]+) dBm", line)
                if signal_match:
                    current_network["Signal"] = float(signal_match.group(1))
            
            elif "HT operation:" in line:
                in_ht_operation = True  # Enable flag to track HT operation block
                print(f"DEBUG: [{current_network.get('SSID', 'Unknown SSID')}] Entering HT operation block")

            elif in_ht_operation and "primary channel:" in line:
                channel = re.search(r"\* primary channel: (\d+)", line)
                if channel:
                    current_network["Channel"] = channel.group(1)
                    print(f"DEBUG: [{current_network.get('SSID', 'Unknown SSID')}] Extracted primary channel -> {channel.group(1)}")

                    in_ht_operation = False  # Reset flag after finding the primary channel

            elif line and not line.startswith(" ") and in_ht_operation:
                in_ht_operation = False

            elif "DS Parameter set:" in line:
                channel = re.search(r"DS Parameter set: channel (\d+)", line)
                if channel:
                    current_network["Channel"] = channel.group(1)
                print(f"DEBUG: [{current_network.get('SSID', 'Unknown SSID')}] Extracted DS Parameter set channel -> {channel.group(1)}")
            

            # Primary channel - now looking for the exact pattern with asterisk and indentation
            
            # Bandwidth information from VHT operation
            elif "* channel width:" in line:
                width_match = re.search(r"\* channel width: (\d+)", line)
                if width_match:
                    width_value = width_match.group(1)
                    if width_value == "1":
                        current_network["Bandwidth"] = "80 MHz"
                    elif width_value == "2":
                        current_network["Bandwidth"] = "160 MHz"
                    else:
                        current_network["Bandwidth"] = "20/40 MHz"
        
        # Add the last network if it exists
        if current_network:
            networks.append(current_network)
        
        return networks

    def show_networks(self):
        scan_results = self.get_wifi_scan_results()
        return self.parse_scan_results(scan_results)

    # Classificar as redes pela intensidade do sinal (dBm)
    def show_by_signal(self):
        scan_results = self.get_wifi_scan_results()
        networks = self.parse_scan_results(scan_results)
        sorted_networks = sorted(networks, key=lambda x: x.get("Signal", -100), reverse=True)
        return sorted_networks

    # Salvar dados em formato CSV
    def save_to_csv(self, filename="configurações_disponiveis.csv"):
        networks = self.show_networks()
        try:
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Escrevendo o cabeçalho
                writer.writerow(["SSID", "Endereço MAC", "Canal", "Frequência", "Sinal", "Largura de Banda"])
                
                # Escrevendo os dados das redes
                for network in networks:
                    writer.writerow([
                        network.get('SSID', 'N/A'),
                        network.get('Address', 'N/A'),
                        network.get('Channel', 'N/A'),
                        network.get('Frequency', 'N/A'),
                        network.get('Signal', 'N/A'),
                        network.get('Bandwidth', 'N/A')
                    ])
            print(f"Configurações salvas em: {filename}")
        except IOError as e:
            print(f"Erro ao salvar o arquivo: {e}")