# CSI-Based Heart Rate Monitoring System 📡

Este repositório contém um sistema de monitoramento de batimentos cardíacos baseado em **Wi-Fi Channel State Information (CSI)**, desenvolvido para rodar em **Raspberry Pi** utilizando o firmware **Nexmon**. O sistema coleta pacotes Wi-Fi, processa os sinais CSI e estima os batimentos cardíacos de forma **não intrusiva**.

📌 **Destaques do Projeto**:
- **Autônomo**: Funciona de forma independente, sem dispositivos adicionais.
- **Precisão aprimorada**: Utiliza filtros, PCA e FFT para estimativa de BPM.
- **Não invasivo**: Monitoramento sem necessidade de sensores de contato.

---

## 📁 **Estrutura do Projeto**
O projeto está organizado nos seguintes módulos:

<img width="1280" alt="Image" src="https://github.com/user-attachments/assets/f9234427-f1d5-41a5-a8bd-69aed6e2fc54" />

---

## 📌 **Módulos Principais**
1. Captura – Captura pacotes CSI do Wi-Fi e armazena os arquivos .pcap.
2. CSI_bpm – Processa os pacotes coletados e estima a frequência cardíaca (BPM).
3. Mac_identify – Realiza a varredura de redes Wi-Fi e identifica a melhor rede disponível.

O fluxo de dados ocorre da seguinte maneira:

Mac_identify faz a varredura e seleciona a rede Wi-Fi ideal.
Captura inicia a coleta de pacotes e os salva como .pcap.
CSI_bpm processa os pacotes, filtra os sinais e estima a frequência cardíaca.

---

## 📌 **Pré-requisitos**
Antes de instalar e executar o sistema, é necessário garantir os seguintes requisitos:

**Hardware Necessário**:
- **Raspberry Pi 4B (Foi utilizado o 8GB RAM)**
- **Fonte de energia compatível com Raspberry Pi**
- **Rede Wi-Fi 5 GHz disponível** *(não precisa da senha, apenas o sinal)*

**Software Necessário**:
- **Kernel 5.10.92 do Raspberry Pi OS** *(vamos mostrar como instalar)*
- **Firmware Nexmon** *(vamos instalar nesta configuração)*
- **Python e suas dependências**



---

## :wrench: **Instalação e Configuração**
1️⃣ **Instalar o Raspberry Pi OS**

O sistema foi testado no Kernel 5.10.92 do Raspberry Pi OS.
Baixe a imagem do sistema operacional:
🔗 [Raspberry Pi OS 5.10.92](https://downloads.raspberrypi.org/raspios_full_armhf/images/raspios_full_armhf-2022-01-28/)

Grave a imagem no cartão SD usando o BalenaEtcher:
🔗 [Download do BalenaEtcher](https://etcher.balena.io/)

Após inicializar o Raspberry Pi com essa imagem, **nunca execute** o comando _**apt upgrade**_, pois o Nexmon só tem suporte até a versão 5.10, rodar o comando fará com que saia da versão desejada. 

Então, instale os pacotes necessários:

```bash
sudo apt install git python3 python3-pip
```

Verifique a versão do Python:

```bash
python3 --version
```

Se a versão for menor que 3.10, atualize:

```bash
sudo apt install python3.10
```

2️⃣ **Instalação do Firmware Nexmon**

Nesta etapa, siga o tutorial oficial do Firmware 🔗 [Getting started Nexmon](https://github.com/nexmonster/nexmon_csi/tree/pi-5.10.92?tab=readme-ov-file#getting-started)

--- 

## ▶️ **Execução do Sistema**

Após configurar o ambiente, use o script _**run_both_scripts.sh**_ para iniciar a captura e o processamento.

1️⃣ **Dê permissão de execução ao script:**

```bash
chmod +x run_both_scripts.sh
```

2️⃣ **Execute o sistema com sudo:**
```bash
sudo ./run_both_scripts.sh
```

📌 **O que esse script faz?**

1. Realiza instalação das dependências (bibliotecas) utilizadas no sistema;
1. Inicia a varredura da rede (mac_identify);
1. Captura pacotes Wi-Fi (captura);
1. Processa os sinais CSI e exibe os batimentos cardíacos (CSI_bpm).

🔍 _Observação: O uso de sudo é necessário para acessar a interface de rede Wi-Fi._
