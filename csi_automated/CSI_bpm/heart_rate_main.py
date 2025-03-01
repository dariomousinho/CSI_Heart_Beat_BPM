import subprocess
import os
import time

def run_script(script_name):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    result = subprocess.run(["sudo", "python3", script_path], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

if __name__ == "__main__":
    
    # Executa base_csi_bpm.py
    run_script('base_csi_bpm.py')
    
    # Aguardar 3 segundos antes de executar capturar.py
    print("Aguardando 3 segundos antes de executar capturar.py...")
    time.sleep(3)
    
    # Executa capturar.py
    run_script(os.path.join('..', 'captura', 'capturar.py'))
    
    
