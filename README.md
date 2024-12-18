# Dependências
O programa precisa das bibliotecas listadas em requirements.txt. Para instalá-las, execute `pip install -r requirements.txt`
Também é necessária uma versão do Python igual ou superior à 1.13.1 (O recurso de encerrar uma Queue multithread só foi inserido nesta versão).

# Como executar
Execute o script principal com o comando `python main.py 0 output.json log.log`, no qual o primeiro argumento indica o número de praias a serem analisadas; o segundo, o nome do arquivo de saída; o terceiro, o nome do arquivo onde salvar logs.

# Cache
O arquivo https:.tar.xz contém uma cache compactada. Ela pode ser descompactada e utilizada para rodar rapidamente o script.
