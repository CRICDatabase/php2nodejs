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

# REST API
REST_API_URL = None
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
            '{}/api/v1/usuarios-citopatologista'.format(REST_API_URL),
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
            error_log.write("User: {}".format(data))
            raise Exception("Failed in user")
        elif response.status_code == 409:
            print("Information already exist {}".format(data))
        else:
            print("Failed with {} to add {}\t\n{}".format(
                response.status_code,
                data,
                response.json())
            )
            error_log.write("User: {}".format(data))
            raise Exception("Failed in user")

        response = requests.post(
            '{}/api/v1/usuarios/analista/{}'.format(
                REST_API_URL,
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
    cursor.execute(
        """SELECT * FROM imagem """
        """WHERE """
        """excluido = 0 """
        """AND """
        """aprovado_classificacao = 1"""
    )
    data = cursor.fetchone()
    while(data is not None):
        print(
            """Adding image {} ...""".format(
                data[1]
            )
        )

        if data[2].strip() == "Negativa":
            injury = 1
        if data[2].strip() == "ASC-US":
            injury = 2
        elif data[2].strip() == "LSIL":
            injury = 3
        elif data[2].strip() == "ASC-H":
            injury = 4
        elif data[2].strip() == "HSIL":
            injury = 5
        elif data[2].strip() == "Carcinoma" or data[2] == "ca":
            injury = 6
        else:
            injury = 1
            print(
                """Image classification {} unknow. Using Negativa\n"""
                """\t{}""".format(
                    data[2],
                    data
                )
            )

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
            '{}/api/v1/imagens'.format(REST_API_URL),
            headers=headers,
            # Note, the json parameter is ignored if either data or files is passed.
            data={
                    "id_usuario": 1,  # Use special user for migration
                    "id_lesao": injury,
                    "codigo_lamina": data[7],
                    "dt_aquisicao": '{}-01-01'.format(year),
                },
            # cut-images must have all images in the same siz: 1376x1020
            # The PHP version stored JPG files but we will upload the TIF files
            files={
                'file': open(
                    'images-cut/{}'.format(data[1].replace(".jpg", ".png")),  # Important to have high resolution images
                    'rb'
                )
            },
            hooks={'response': print_url}
        )

        if response.status_code == 201:
            print("Added {}".format(response.json()))
        elif response.status_code == 403:
            print("Invalid request {}".format(data))
            error_log.write("Image: {}".format(data))
            raise Exception("Failed in image")
        elif response.status_code == 409:
            print("Information already exist {}".format(data))
        else:
            print("Failed with {} to add {}\t\n{}".format(
                response.status_code,
                data,
                response)
            )
            error_log.write("Image: {}".format(data))
            raise Exception("Failed in image")

        # Read next line of database query
        data = cursor.fetchone()

def add_classification():
    imagens = requests.get(
        '{}/api/v1/imagens/listar/{}'.format(
            REST_API_URL,
            1  # Use special user for migration
        ),
        headers=headers,
        hooks={'response': print_url}
    )

    for imagem in imagens.json():
        print(
            """Processing classifications from {}""".format(
                imagem["nome"]
            )
        )
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
        #cursor.execute("SELECT * FROM  imagem_nucleos WHERE id_imagem = 1 AND id_usuario = 14 AND excluido =0")
        cursor.execute("""SELECT """
            """nome, """
            """x, """
            """y, """
            """id_imagem_tipo """
            """FROM imagem_nucleos """
            """INNER JOIN imagem ON imagem_nucleos.id_imagem = imagem.id """
            """WHERE nome = '{}' AND """
            """imagem_nucleos.id_usuario = 15 AND """
            """imagem_nucleos.excluido = 0 AND """
            """x < 1376 AND """
            """y < 1020""".format(
                imagem["nome"].replace(".png", ".jpg")
        ))
        data = cursor.fetchone()
        while(data is not None):
            # Mapping from php/src/intra/nucleos_imagem.php
            # <select id="nucleoTipo" onchange="mudaTipo(this.value);">
            # <option value="0">Normal</option>
            # <option value="1">ASC-US</option>
            # <option value="2">LSIL</option>
            # <option value="3">ASC-H</option>
            # <option value="4">HSIL</option>
            # <option value="5">Carcinoma</option>
            # </select>
            if data[3] == 0:  # "Normal"
                injury = 1
            if data[3] == 1:  # "ASC-US"
                injury = 2
            elif data[3] == 2:  # "LSIL"
                injury = 3
            elif data[3] == 3:  # "ASC-H"
                injury = 4
            elif data[3] == 4:  # "HSIL"
                injury = 5
            elif data[3] == 5:  # "Carcinoma"
                injury = 6
            else:
                injury = 1
                print("""Nuclei classification {} unknow. Using 0.\n"""
                    """\t{}""".format(
                        data[3],
                        data
                    )
                )

            response = requests.post(
                '{}/api/v1/imagens/{}/classificacao-celula/{}'.format(
                    REST_API_URL,
                    imagem["id"],  # id_imagem
                    1  # Use special user for migration 
                ),
                headers=headers,
                json={
                    "id_lesao": injury,
                    "coord_centro_nucleo_x": data[1],
                    "coord_centro_nucleo_y": data[2],
                    "alturaCanvas": imagem["altura"],
                    "larguraCanvas": imagem["largura"],
                    "alturaOriginalImg": imagem["altura"],
                    "larguraOriginalImg": imagem["largura"],
                },
                hooks={'response': print_url}
            )

            if response.status_code == 201:
                print("Added {}".format(response.json()))
            elif response.status_code == 403:
                print("Invalid request {}".format(response.request.body))
                error_log.write("Classification: {}".format(data))
                raise Exception("Failed in classification")
            elif response.status_code == 409:
                print("Information already exist {}".format(response.request.body))
            else:
                print("Failed with {} to add {}".format(
                    response.status_code,
                    response.request.body)
                )
                error_log.write("Classification: {}".format(data))
                raise Exception("Failed in classification")

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

def add_segmentation():
    imagens = requests.get(
        '{}/api/v1/imagens/listar/{}'.format(
            REST_API_URL,
            1  # Use special user for migration
        ),
        headers=headers,
        hooks={'response': print_url}
    )

    for imagem in imagens.json():
        print("Begin processing image {}".format(imagem))

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
        cursor.execute("""SELECT """ \
            """imagem_segmentos.id, """ \
            """nome, """ \
            """id_imagem_tipo """ \
            """FROM imagem_segmentos """ \
            """INNER JOIN imagem ON imagem_segmentos.id_imagem = imagem.id """ \
            """WHERE nome = '{}' AND """ \
            """imagem_segmentos.id_usuario = 9 AND """ \
            """imagem_segmentos.excluido = 0""".format(
                imagem["nome"].replace(".png", ".jpg")
        ))
        data = cursor.fetchone()
        while(data is not None):
            print("\tBegin processing segmentation {}".format(data))

            # Migrate table coordenadas_segmento
            #
            # Example of data in the PHP version
            # {
            #     id: ,
            #     id_segmento: ,
            #     x: ,
            #     y: ,
            # }
            cursor_aux.execute(
                """SELECT * """
                """FROM coordenadas_segmento """
                """WHERE id_segmento = {} AND"""
                """x < 1376 AND """
                """y < 1020""".format(
                    data[0]
                )
            )
            data_aux = cursor_aux.fetchall()
            segmentos_citoplasma = list(map(
                lambda row: {"coord_x": row[2], "coord_y": row[3]},
                data_aux
            ))

            # Migrate table coordenadas_nucleo
            #
            # Example of data in the PHP version
            # {
            #     id: ,
            #     id_segmento: ,
            #     x: ,
            #     y: ,
            # }
            cursor_aux.execute(
                """SELECT * """
                """FROM coordenadas_nucleo """
                """WHERE id_segmento = {} AND"""
                """x < 1376 AND """
                """y < 1020""".format(
                    data[0]
                )
            )
            data_aux = cursor_aux.fetchall()
            segmentos_nucleo = list(map(
                lambda row: {"coord_x": row[2], "coord_y": row[3]},
                data_aux
            ))

            # Based on
            # 
            # OLIVEIRA, Paulo Henrique Calaes.
            # Segmentação de núcleos de células cervicais em exame de Papanicolau.
            # 2018. 71 f. Dissertação (Mestrado em Ciência da Computação) -
            # Instituto de Ciências Exatas e Biológicas,
            # Universidade Federal de Ouro Preto, Ouro Preto, 2018.
            if data[2] == 1:
                description = 2
            elif data[2] == 2:
                description = 3
            elif data[2] == 3:
                description = 4
            elif data[2] == 11:
                description = 5
            elif data[2] == 12:
                description = 6
            elif data[2] == 13:
                description = 7
            elif data[2] == 20:
                description = 8
            elif data[2] == 21:
                description = 9
            elif data[2] == 22:
                description = 10
            elif data[2] == 23:
                description = 11
            elif data[2] == 24:
                description = 12
            elif data[2] == 25:
                description = 13
            elif data[2] == 26:
                description = 14
            elif data[2] == 27:
                description = 15
            elif data[2] == 28:
                description = 16
            elif data[2] == 29:
                description = 17
            elif data[2] == 31:
                description = 18
            elif data[2] == 32:
                description = 19
            elif data[2] == 33:
                description = 20
            elif data[2] == 34:
                description = 21
            elif data[2] == 35:
                description = 22
            elif data[2] == 36:
                description = 23
            elif data[2] == 37:
                description = 24
            elif data[2] == 111:
                description = 25
            elif data[2] == 112:
                description = 26
            elif data[2] == 121:
                description = 27
            elif data[2] == 122:
                description = 28
            elif data[2] == 131:
                description = 29
            elif data[2] == 132:
                description = 30
            elif data[2] == 201:
                description = 31
            elif data[2] == 1111:
                description = 32
            elif data[2] == 1112:
                description = 33
            elif data[2] == 1121:
                description = 34
            elif data[2] == 1122:
                description = 35
            elif data[2] == 1211:
                description = 36
            elif data[2] == 1212:
                description = 37
            elif data[2] == 1221:
                description = 38
            elif data[2] == 1222:
                description = 39
            elif data[2] == 1311:
                description = 40
            elif data[2] == 1312:
                description = 41
            elif data[2] == 1313:
                description = 42
            elif data[2] == 1321:
                description = 43
            elif data[2] == 1322:
                description = 44
            elif data[2] == 11111:
                description = 45
            elif data[2] == 11112:
                description = 46
            elif data[2] == 11121:
                description = 47
            elif data[2] == 11122:
                description = 48
            elif data[2] == 11211:
                description = 49
            elif data[2] == 11212:
                description = 50
            elif data[2] == 11221:
                description = 51
            elif data[2] == 11222:
                description = 52
            elif data[2] == 12121:
                description = 53
            elif data[2] == 12122:
                description = 54
            elif data[2] == 12123:
                description = 55
            elif data[2] == 12221:
                description = 56
            elif data[2] == 12222:
                description = 57
            elif data[2] == 13111:
                description = 58
            elif data[2] == 13112:
                description = 59
            elif data[2] == 13121:
                description = 60
            elif data[2] == 13122:
                description = 61
            elif data[2] == 13131:
                description = 62
            elif data[2] == 13132:
                description = 63
            elif data[2] == 13221:
                description = 64
            elif data[2] == 13222:
                description = 65
            elif data[2] == 111121:
                description = 66
            elif data[2] == 111122:
                description = 67
            elif data[2] == 111123:
                description = 68
            elif data[2] == 111221:
                description = 69
            elif data[2] == 111222:
                description = 70
            elif data[2] == 111223:
                description = 71
            elif data[2] == 112121:
                description = 72
            elif data[2] == 112122:
                description = 73
            elif data[2] == 112221:
                description = 74
            elif data[2] == 112222:
                description = 75
            elif data[2] == 131121:
                description = 76
            elif data[2] == 131122:
                description = 77
            elif data[2] == 131123:
                description = 78
            elif data[2] == 131221:
                description = 79
            elif data[2] == 131222:
                description = 80
            elif data[2] == 131223:
                description = 81
            elif data[2] == 131321:
                description = 82
            elif data[2] == 131322:
                description = 83
            elif data[2] == 131323:
                description = 84  

            response = requests.post(
                '{}/api/v1/imagens/{}/segmentacao-celula/{}'.format(
                    REST_API_URL,
                    imagem["id"],  # id_imagem
                    1  # Use special user for migration
                ),
                headers=headers,
                json={
                    "id_descricao": description,
                    "alturaCanvas": imagem["altura"],
                    "larguraCanvas": imagem["largura"],
                    "alturaOriginalImg": imagem["altura"],
                    "larguraOriginalImg": imagem["largura"],
                    "segmentos_citoplasma": segmentos_citoplasma,
                    "segmentos_nucleo": segmentos_nucleo,
                },
                hooks={'response': print_url}
            )

            if response.status_code == 201:
                print("Added".format(response.json()))
            elif response.status_code == 403:
                print("Invalid request {}".format(response.request.body))
                error_log.write("Segmentation: {}".format(data))
                raise Exception("Failed in segmentation")
            elif response.status_code == 409:
                print("Information already exist {}".format(response.request.body))
            else:
                print("Failed with {} to add {}".format(
                    response.status_code,
                    response.request.body)
                )
                error_log.write("Segmentation: {}".format(data))
                raise Exception("Failed in segmentation")

            print("\tFinished with segmentation {}".format(data))
            # Read next line of database query
            data = cursor.fetchone()
        print("Finished with image {}".format(imagem))

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
        '--host',
        default="http://localhost:3000",
        help='Host where the information will be send'
    )
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
    parser.add_argument(
        '--segmentation',
        action='store_true',
        help='Migrate cell classification information'
    )
    args = parser.parse_args()

    REST_API_URL = args.host

    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    cursor_aux = db.cursor()

    with open("error.log", "w") as error_log:
        if args.users or args.all:
            add_users()
        if args.images or args.all:
            add_images()
        if args.classification or args.all:
            add_classification()
        if args.segmentation or args.all:
            add_segmentation()

    # disconnect from server
    db.close()
