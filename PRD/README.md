Configuração Inicial do Ambiente Python
=======================================

Este projeto utiliza um ambiente virtual para manter as dependências isoladas e organizadas.

Passo 1: Criar o ambiente virtual
---------------------------------
No diretório do projeto, execute:
    python -m venv .venv

Passo 2: Ativar o ambiente
--------------------------
Windows (PowerShell):
    .venv\Scripts\Activate

Linux/MacOS (bash/zsh):
    source .venv/bin/activate

Passo 3: Instalar dependências
------------------------------
Com o ambiente ativo, instale as bibliotecas listadas em requirements.txt:
    pip install -r requirements.txt

Passo 4: Conferir pacotes instalados
------------------------------------
    pip list

Exemplo de requirements.txt
---------------------------
requests==2.31.0
flask==3.0.0
pandas==2.2.2
pytest==8.0.0
black==24.3.0

Resultado
---------
- Ambiente isolado criado em .venv
- Dependências controladas via requirements.txt
- Fácil replicação em qualquer máquina: basta ativar o venv e rodar "pip install -r requirements.txt"
