import sqlite3
import os

# Nome do banco de dados
nome_banco = "estabelecimentos_202411.db"

# Caminho do banco de dados
caminho_banco = os.path.join(os.path.dirname(__file__), nome_banco)

# Conectar ao banco de dados SQLite
conexao = sqlite3.connect(caminho_banco)

# Criar um cursor para executar comandos SQL
cursor = conexao.cursor()

# Query para filtrar valores da coluna CO_SERVICO e obter CO_UNIDADE
query = """
SELECT CO_UNIDADE 
FROM tabela_dados
WHERE CO_SERVICO IN (159, 152)
"""
cursor.execute(query)

# Armazenar os resultados em um array
resultado = cursor.fetchall()
array_co_unidade = [linha[0] for linha in resultado]

# Exibir o array resultante
print("Valores da coluna CO_UNIDADE correspondentes:")
print(array_co_unidade)
  
# Fechar a conexão
conexao.close()

# Conectar ou criar o banco de dados
conexao = sqlite3.connect("estab_202411_159_152.db")
cursor = conexao.cursor()

# Criar uma tabela para armazenar os valores do array
cursor.execute("""
CREATE TABLE IF NOT EXISTS serv159152 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    valor TEXT UNIQUE
)
""")

# Inserir os valores do array no banco de dados
for valor in array_co_unidade:
    cursor.execute("INSERT OR IGNORE INTO serv159152 (valor) VALUES (?)", (valor,))

# Salvar e fechar a conexão
conexao.commit()
conexao.close()

print("Array salvo no banco de dados SQLite 'estab_202411_159_152.db'")
