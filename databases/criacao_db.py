import pandas as pd
import sqlite3
import os  # Importação do módulo para manipular caminhos e o sistema operacional

# Nome do arquivo CSV e o nome do banco de dados
arquivo_csv = "rlEstabServClass202411.csv"
nome_banco = "estabelecimentos_202411.db"

# Obter o caminho do arquivo CSV (na mesma pasta que o script teste.py)
caminho_csv = os.path.join(os.path.dirname(__file__), arquivo_csv)

# Obter o caminho do banco de dados
caminho_banco = os.path.join(os.path.dirname(__file__), nome_banco)

# Carregar o CSV em um DataFrame
df = pd.read_csv(
    caminho_csv,
    delimiter=";",
    encoding="ISO-8859-1",
    dtype={"CO_UNIDADE": "object", "CO_SERVICO": "int64", "CO_CLASSIFICACAO": "int64", "TP_CARACTERISTICA": "int64", "CO_CNPJCPF": "object", "CO_AMBULATORIAL": "int64", "CO_AMBULATORIAL_SUS": "int64", "CO_HOSPITALAR": "int64", "CO_HOSPITALAR_SUS": "int64", "CO_END_COMPL": "int64", "ST_ATIVO_SN": "object", "TO_CHAR(DT_ATUALIZACAO,'DD/MM/YYYY')": "object", "CO_USUARIO": "object"}
)  # Ajuste o delimitador conforme necessário

# Conectar ao banco de dados SQLite (cria o arquivo se ele não existir)
conexao = sqlite3.connect(caminho_banco)

# Exportar o DataFrame para o SQLite como uma tabela
df.to_sql("tabela_dados", conexao, if_exists="replace", index=False)

# Mostrar o esquema dos dados no banco
cursor = conexao.cursor()
cursor.execute("PRAGMA table_info(tabela_dados)")
schema = cursor.fetchall()

# Exibir o esquema dos dados
print("Esquema da tabela 'tabela_dados':")
for coluna in schema:
    print(f"Nome: {coluna[1]}, Tipo: {coluna[2]}")

# Fechar a conexão
conexao.close()
