"""
Read the database from the PHP version and migrate the data to the Node.js version
"""
import pymysql
import json
import requests

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

# Migrate users
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
# cursor.execute("SELECT * FROM usuarios")

# data = cursor.fetchone()
# while(data is not None):
#     response = requests.post(
#         'http://localhost:3000/api/v1/usuarios-administrador',
#         headers=headers,
#         json={
#                 "primeiro_nome": data[1],
#                 "ultimo_nome": data[2],
#                 "email": data[3],
#                 "senha": data[4],
#                 "ativo": 1,
#                 "api_key": '123.456.789.0',
#                 "nivel_acesso": 'TOTAL',
#             },
#     )

#     if response.status_code == 201:
#         print("Added {}".format(response.json()))
#     else:
#         print("Failed with {} to add {}\t\n{}".format(
#             response.status_code,
#             data,
#             response.json())
#         )
        

#     response = requests.post(
#         'http://localhost:3000/api/api/v1/usuarios-citopatologista',
#         headers=headers,
#         json={
#                 "primeiro_nome": data[1],
#                 "ultimo_nome": data[2],
#                 "email": data[3],
#                 "senha": data[4],
#                 "ativo": 1,
#                 "codigo_crc": 'fake',
#             },
#     )

#     if response.status_code == 201:
#         print("Added {}".format(response.json()))
#     else:
#         print("Failed with {}".format(
#             response.status_code
#         ))

#     # Read next line of database query
#     data = cursor.fetchone()

# Add lesion
# response = requests.post(
#     'http://localhost:3000/api/v1/imagens-lesoes/{}'.format(9),
#     headers=headers,
#     json=[
#             {
#                 "nome": "LSIL",
#                 "detalhes": "",
#             },
#         ],
# )

# if response.status_code != 201:
#     print("Added {}".format(response.json()))
# else:
#     print("Failed with {} to add lesion\t\n{}".format(
#         response.status_code,
#         response.json())
#     )
    

# Migrate images
# {
#     id: 1,
#     nome: 'be340ee72689dfe3f8dc9c24de6127f4.jpg',
#     identificacao: 'LSIL',
#     timestamp: 2015-09-21T12:29:42.000Z,
#     excluido: 0,
#     id_lamina: '',
#     aprovado_classificacao: 1,
#     lamina: '2564 ',
#     ano: '14'
# }
#
# Example of data in the PHP version
cursor.execute("SELECT * FROM imagem")

data = cursor.fetchone()
while(data is not None):
    response = requests.post(
        'http://localhost:3000/api/v1/imagens',
        headers=headers,
        # Note, the json parameter is ignored if either data or files is passed.
        data={
                "id_usuario": 8,
                "id_lesao": 1,
                "codigo_lamina": 'old',
                "dt_aquisicao": '2020-01-01',
            },
        files={
            'file': open('example0001.jpg', 'rb')
        }
    )

    if response.status_code == 201:
        print("Added {}".format(response.json()))
    else:
        print("Failed with {} to add {}\t\n{}".format(
            response.status_code,
            data,
            response.json())
        )

    # Read next line of database query
    data = cursor.fetchone()

    break


# disconnect from server
db.close()