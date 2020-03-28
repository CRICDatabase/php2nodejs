"""
Read the database from the PHP version and migrate the data to the Node.js version
"""
import sys

import json
import pymysql
import requests

# Function to log requests to Node.js REST API
def print_url(r, *args, **kwargs):
    print(r.url)

# API Key
headers = {
    'token_autenticacao': 'bac8db9147ac80b4ba8a05bb0de7c4fd'
}

# Open database connection
db = pymysql.connect(
    "0.0.0.0",
    "root",
    "123.456",
    "cric_ufop"
)

# prepare a cursor object using cursor() method
cursor = db.cursor()
cursor_aux = db.cursor()

# Migrate table usuarios
#
# Example of data in the PHP version
# {
#     id: 1,
#     nome: 'Name',
#     sobrenome: 'Name',
#     email: 'name.name@mail.com',
#     senha: 'password',
#     ativo: 1,
#     nivel: 10,
#     api_key: 'apiapiapi123456',
#     updated_at: 2018-05-20T00:37:59.000Z,
#     created_at: 2018-09-30T22:56:08.000Z
# }
cursor.execute("SELECT * FROM usuarios")
data = cursor.fetchone()
while(data is not None):
    # Need cythopatologist otherwise can't add information
    # response = requests.post(
    #     'http://localhost:3000/api/v1/usuarios-administrador',
    #     headers=headers,
    #     json={
    #             "primeiro_nome": data[1],
    #             "ultimo_nome": data[2],
    #             "email": data[3],
    #             "senha": data[4],
    #             "ativo": 1,
    #             "api_key": '123.456.789.0',
    #             "nivel_acesso": 'TOTAL',
    #         },
    #     hooks={'response': print_url}
    # )
    response = requests.post(
        'http://localhost:3000/api/v1/usuarios-citopatologista',
        headers=headers,
        json={
                "primeiro_nome": data[1],
                "ultimo_nome": data[2],
                "email": data[3],
                "senha": data[4],
                "ativo": 1,
                "codigo_crc": 'fake',
            },
        hooks={'response': print_url}
    )

    if response.status_code == 201:
        print("Added {}".format(response.json()))
    elif response.status_code == 403:
        print("Invalid request {}".format(data))
    elif response.status_code == 409:
        print("Information already exist {}".format(data))
    else:
        print("Failed with {} to add {}\t\n{}".format(
            response.status_code,
            data,
            response.json())
        )

    response = requests.post(
        'http://localhost:3000/api/v1/usuarios/analista/{}'.format(
            1
        ),
        headers=headers,
        hooks={'response': print_url}
    )

    if response.status_code == 201:
        print("Added {}".format(response.json()))
    elif response.status_code == 403:
        print("Invalid request {}".format(data))
    elif response.status_code == 409:
        print("Information already exist {}".format(data))
    else:
        print("Failed with {} to add {}\t\n{}".format(
            response.status_code,
            data,
            response.json())
        )

    data = cursor.fetchone()
    break

# Migrate table imagem
#
# Example of data in the PHP version
# {
#     id: 1,
#     nome: 'be340ee72689dfe3f8dc9c24de6127f4.jpg',
#     identificacao: 'LSIL',
#     timestamp: 2015-09-21T12:29:42.000Z,
#     excluido: 0,
#     id_lamina: '',
#     aprovado_classificacao: 1,
#     lamina: '2564',
#     ano: '14'
# }
cursor.execute("SELECT * FROM imagem")
data = cursor.fetchone()
while(data is not None):
    print(data)
    response = requests.post(
        'http://localhost:3000/api/v1/imagens',
        headers=headers,
        # Note, the json parameter is ignored if either data or files is passed.
        data={
                "id_usuario": 1,
                "id_lesao": 1,
                "codigo_lamina": 'old',
                "dt_aquisicao": '2020-01-01',
            },
        files={
            'file': open('1.jpg', 'rb')
        },
        hooks={'response': print_url}
    )

    if response.status_code == 201:
        print("Added {}".format(response.json()))
    elif response.status_code == 403:
        print("Invalid request {}".format(data))
    elif response.status_code == 409:
        print("Information already exist {}".format(data))
    else:
        print("Failed with {} to add {}\t\n{}".format(
            response.status_code,
            data,
            response.json())
        )

    # Read next line of database query
    data = cursor.fetchone()

    break

# Migrate table imagem_nucleos
#
# Example of data in the PHP version
# {
#     id: 1225,
#     id_imagem: 1,
#     x: 153,
#     y: 134,
#     id_imagem_tipo: 0,
#     id_usuario: 14,
#     timestamp: '2020-01-01',
#     excluido: 0,
# }
cursor.execute("SELECT * FROM  imagem_nucleos WHERE id_imagem = 1 AND id_usuario = 14 AND excluido =0")
data = cursor.fetchone()
while(data is not None):
    print(data)

    response = requests.post(
        'http://localhost:3000/api/v1/imagens/{}/classificacao-celula/{}'.format(
            1,
            1
        ),
        headers=headers,
        json={
            "id_lesao": 2,
            "coord_centro_nucleo_x": data[2],
            "coord_centro_nucleo_y": data[3],
            "alturaCanvas": 1388,  # Provided by Mariana
            "larguraCanvas": 1040,  # Provided by Mariana
    	    "alturaOriginalImg": 1388,  # Provided by Mariana
    	    "larguraOriginalImg": 1388  # Provided by Mariana
        },
        hooks={'response': print_url}
    )

    if response.status_code == 201:
        print("Added {}".format(response.json()))
    elif response.status_code == 403:
        print("Invalid request {}".format(data))
    elif response.status_code == 409:
        print("Information already exist {}".format(data))
    else:
        print("Failed with {} to add {}".format(
            response.status_code,
            data)
        )

    # Read next line of database query
    data = cursor.fetchone()

    break

# Migrate table imagem_tipo
#
# Example of data in the PHP version
# {
#     id: ,
#     tipo: ,
#     excluido: 0,
# }

# Migrate table imagem_segmentos
#
# Example of data in the PHP version
# {
#     id: ,
#     id_imagem: ,
#     id_imagem_tipo: ,
#     id_usuario: ,
#     timestamp: '2020-01-01',
#     excluido: 0,
# }

# Migrate table coordenadas_segmento
#
# Example of data in the PHP version
# {
#     id: ,
#     id_segmento: ,
#     x: ,
#     y: ,
# }

# Migrate table coordenadas_nucleo
#
# Example of data in the PHP version
# {
#     id: ,
#     id_segmento: ,
#     x: ,
#     y: ,
# }

# Migrate table exame
# Migrate table exame_imagens
# Migrate table exame_marcacoes
# Migrate table exame_marcacoes_has_opcoes
# Migrate table exame_opcoes
# Migrate table exame_resposta
# Migrate table exercicios
# Migrate table exercicios_imagens
# Migrate table exercicios_resposta
# Migrate table exercicios_sessao_interativa
# Migrate table sessao_interativa

# disconnect from server
db.close()