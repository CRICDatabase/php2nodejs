"""
Read the database from the PHP version and migrate the data to the Node.js version
"""
import sys
import argparse

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

def add_users():
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
    user_id = 2
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
                    "senha": "123.456",  # FIXME must be data[4]
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
                user_id
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

        user_id = user_id + 1
        data = cursor.fetchone()

def add_images():
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
    cursor.execute("SELECT * FROM imagem WHERE excluido =0")
    data = cursor.fetchone()
    while(data is not None):
        print(data)

        if data[0] > 470:
            break

        try:
            if data[2] == "ASC-US":
                injury = 2
            elif data[2] == "LSIL":
                injury = 3
            elif data[2] == "ASC-H":
                injury = 4
            elif data[2] == "HSIL":
                injury = 5
            elif data[2] == "Carcinoma":
                injury = 6
            else:
                injury = 7
        except:
            injury = 7

        try:
            if len(data[8]) == 2:
                year = "20{}".format(data[8])
            elif len(data[8]) == 4:
                year = data[8]
            else:
                year = "2020"
        except:
            year = "2020"

        response = requests.post(
            'http://localhost:3000/api/v1/imagens',
            headers=headers,
            # Note, the json parameter is ignored if either data or files is passed.
            data={
                    "id_usuario": 1,  # Use special user for migration
                    "id_lesao": injury,
                    "codigo_lamina": data[7],
                    "dt_aquisicao": '{}-01-01'.format(year),
                },
            files={
                'file': open('images/{}'.format(data[1]), 'rb')
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

def add_classification():
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
    imagens = requests.get(
        'http://localhost:3000/api/v1/imagens/listar/{}'.format(
            1  # Use special user for migration
        ),
        headers=headers,
        hooks={'response': print_url}
    )

    for imagem in imagens.json():
        print(imagem)

        #cursor.execute("SELECT * FROM  imagem_nucleos WHERE id_imagem = 1 AND id_usuario = 14 AND excluido =0")
        cursor.execute("""SELECT * FROM imagem_nucleos """
            """WHERE id_imagem = {} AND """
            """id_usuario = 15 AND """
            """excluido = 0""".format(
                imagem["id"]
        ))
        data = cursor.fetchone()
        while(data is not None):
            print(data)

            # Mapping from php/src/intra/nucleos_imagem.php
            # <select id="nucleoTipo" onchange="mudaTipo(this.value);">
            # <option value="0">Normal</option>
            # <option value="1">ASC-US</option>
            # <option value="2">LSIL</option>
            # <option value="3">ASC-H</option>
            # <option value="4">HSIL</option>
            # <option value="5">Carcinoma</option>
            # </select>
            try:
                if data[4] == 0:  # "Normal"
                    injury = 1
                if data[4] == 1:  # "ASC-US"
                    injury = 2
                elif data[4] == 2:  # "LSIL"
                    injury = 3
                elif data[4] == 3:  # "ASC-H"
                    injury = 4
                elif data[4] == 4:  # "HSIL"
                    injury = 5
                elif data[4] == 5:  # "Carcinoma"
                    injury = 6
                else:
                    injury = 7
            except:
                injury = 7

            response = requests.post(
                'http://localhost:3000/api/v1/imagens/{}/classificacao-celula/{}'.format(
                    imagem["id"],  # id_imagem
                    15  # Mari, Ale e Claudia
                ),
                headers=headers,
                json={
                    "id_lesao": injury,
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
                print("Invalid request {}".format(response.request.body))
            elif response.status_code == 409:
                print("Information already exist {}".format(response.request.body))
            else:
                print("Failed with {} to add {}".format(
                    response.status_code,
                    response.request.body)
                )

            break
            # Read next line of database query
            data = cursor.fetchone()

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate data to new schema.')
    parser.add_argument(
        '--all',
        action='store_true',
        help='Migrate all the information'
    )
    parser.add_argument(
        '--users',
        action='store_true',
        help='Migrate users information'
    )
    parser.add_argument(
        '--images',
        action='store_true',
        help='Migrate images information'
    )
    parser.add_argument(
        '--classification',
        action='store_true',
        help='Migrate cell classification information'
    )
    args = parser.parse_args()

    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    cursor_aux = db.cursor()

    if args.users or args.all:
        add_users()
    if args.images or args.all:
        add_images()
    if args.classification or args.all:
        add_classification()

    # disconnect from server
    db.close()