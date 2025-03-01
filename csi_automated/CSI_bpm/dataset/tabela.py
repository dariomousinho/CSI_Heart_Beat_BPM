import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def batimentos(posicao, scan, bpm):
    
    #tabela = pd.read_csv('dataset\exemplo.csv')#index_col=0

    #tabela = pd.read_excel('exemplo.xlsx')
    
    data = {scan:[bpm]}
    
    data = pd.DataFrame(data)

    #data.to_csv('dataset\exemplo.csv')
    
    tabela = pd.concat([tabela, data])
    
    #tabela.to_csv('dataset\exemplo.csv')

    tabela.to_excel('exemplo.xlsx')
    
    
batimentos('wkej', "001", 72)
batimentos('wer', '001', 32)
batimentos('dwkn', '002', 23)