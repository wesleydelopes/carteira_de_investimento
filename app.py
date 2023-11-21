import requests
import pandas as pd
from datetime import datetime
import sqlite3

ALPHA_VANTAGE_API_KEY = "SuaChaveDeAPI"  # Substitua com sua chave de API do Alpha Vantage

def criar_tabela_carteira():
    conn = sqlite3.connect("Carteira.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Carteira (
            Simbolo TEXT PRIMARY KEY,
            Nome TEXT,
            Quantidade INTEGER,
            ValorInvestido REAL
        )
    ''')

    conn.commit()
    conn.close()

def adicionar_a_carteira(simbolo, quantidade, valor_investido):
    conn = sqlite3.connect("Carteira.db")
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO Carteira (Simbolo, Quantidade, ValorInvestido)
        VALUES (?, ?, ?)
    ''', (simbolo, quantidade, valor_investido))

    conn.commit()
    conn.close()

def calcular_valor_investido_total():
    conn = sqlite3.connect("Carteira.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT Quantidade, ValorInvestido
        FROM Carteira
    ''')

    rows = cursor.fetchall()
    conn.close()

    valor_total = sum(quantidade * valor_investido for quantidade, valor_investido in rows)
    return valor_total

def atualizar_cotacoes_acoes():
    try:
        simbolos_acoes = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA']

        cotacoes_acoes = {}

        for simbolo in simbolos_acoes:
            requisicao = requests.get(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={simbolo}&apikey={ALPHA_VANTAGE_API_KEY}")
            requisicao_dic = requisicao.json()

            if 'Global Quote' in requisicao_dic:
                cotacao = float(requisicao_dic['Global Quote']['05. price'])
                cotacoes_acoes[simbolo] = cotacao

        tabela_acoes = pd.DataFrame.from_dict(cotacoes_acoes, orient='index', columns=['Cotação'])
        tabela_acoes['Data Última Atualização'] = datetime.now()
        tabela_acoes.to_excel("Cotacoes_Acoes.xlsx", index=True)

        return cotacoes_acoes
    except Exception as e:
        print(f"Erro ao atualizar cotações de ações: {e}")
        return None

def mostrar_cotacoes_acoes():
    cotacoes_acoes = atualizar_cotacoes_acoes()
    if cotacoes_acoes:
        for simbolo, valor in cotacoes_acoes.items():
            print(f'{simbolo}: R${valor:.2f}')

def adicionar_a_carteira_interativa():
    criar_tabela_carteira()

    simbolo = input("Digite o símbolo da ação que deseja adicionar à carteira: ")
    quantidade = float(input("Digite a quantidade de ações: "))

    cotacoes_acoes = atualizar_cotacoes_acoes()

    if simbolo in cotacoes_acoes:
        valor_investido = cotacoes_acoes[simbolo] * quantidade
        adicionar_a_carteira(simbolo, quantidade, valor_investido)
        print(f"Ação {simbolo} adicionada à carteira com sucesso.")
    else:
        print(f"Não foi possível obter a cotação da ação {simbolo}.")

def mostrar_valor_investido_total():
    valor_total = calcular_valor_investido_total()
    print(f"O valor total investido na carteira é R${valor_total:.2f}")

# Exemplo de utilização
mostrar_cotacoes_acoes()
adicionar_a_carteira_interativa()
mostrar_valor_investido_total()
