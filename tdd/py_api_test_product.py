
# coding:utf-8

#--------------------------------------------------------------------
# TDD UNITTEST - Testes unitários das APIs dos produtos.
#--------------------------------------------------------------------
# a) Para testar, crie uma subpasta do projeto chamada "tdd" e 
#    coloque esse script dentro dela;
# b) Por fim, estando dentro da pasta do projet, oexecute
#    no terminal/prompt:
#       python -m unittest tdd/py_api_test_product.py
#--------------------------------------------------------------------

from typing import AbstractSet, Union
import sys
import unittest
import json
from pathlib import Path

# Bibliotecas...
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

import py_api_consts as cts
import lamba_rest_products as api
#----------------------------------------------------------------------------------

class ProductAPITests(unittest.TestCase):

    def test_insert_product_with_new_manufacturer(self):
        """ Teste de inclusão de produto e fabricante. """                
        
        # Arrange...
        body = { 
                  'httpMethod': cts._PUT,  
                  'body': json.dumps({        
                      "name": "Chapuleta da corrêia dentada",
                      "description": "Chapa de aço que vai na chapuleta, folheada a ouro",
                      "barcode": "6466546464645",
                      "manufacturer": {  
                                         "name": "SpaceX & NASA",
                                      },
                      "unitPrice": 101234748.01
                  })   
               }   
      
        # Act...
        put = api.lambda_handler(event=body, context='')        
        
        # Asserts...                        
        self.assertEqual(type(put), dict, 'Retorno deve ser do tipo "dict" mas é do tipo "'+ type(put).__name__ +'".')
        self.assertEqual('statusCode' in put.keys(), True, 'O atributo "statusCode" não foi retornado.')
        self.assertEqual(type(put['statusCode']), int, 'O atributo "statusCode" deve ser do tipo "int" mas é do tipo "'+type(put['statusCode']).__name__+'".')
        self.assertEqual(200, put['statusCode'], put['body'] if 'body' in put.keys() else 'Erro desconhecido.')        
        self.assertEqual('body' in put.keys(), True, 'O atributo "body" não foi retornado.')
        self.assertGreater(len(put['body']) , 0, 'O atributo "body" foi retornado vazio.')
        
        try:
            put['body'] = json.loads(put['body'])       
            jsonLoadsBody = True
        except Exception:
            jsonLoadsBody = False
        
        self.assertEqual(jsonLoadsBody, True, 'O "body" não contém um json encode válido.')
        
        self.assertEqual('id' in put['body'].keys(), True, 'O atributo "id" não foi retornado.')
        self.assertEqual(type(put['body']['id']), int, 'O atributo "id" deve ser do tipo "int" mas é do tipo "'+type(put['body']['id']).__name__+'".')
        
        self.assertEqual('manufacturer' in put['body'].keys(), True, 'O atributo "manufacturer" não foi retornado.')
        self.assertEqual('id' in put['body']['manufacturer'].keys(), True, 'O atributo "manufacturer.id" não foi retornado.')
        self.assertEqual(type(put['body']['manufacturer']['id']), int, 'O atributo "manufacturer.id" deve ser do tipo "int" mas é do tipo "'+type(put['body']['manufacturer']['id']).__name__+'".')        
            
        
    def test_update_product_and_change_manufacturer(self):
        """ Teste de alteração de produto com troca de fabricante. """       
        
        # Arrange...
        body = { 
                  'httpMethod': cts._POST,  
                  'body': json.dumps({     
                            "id": 206,                    
                            "name": "Correia desdentada",
                            "description": "Correia sem dentes, para polias 'ensopadas'.",
                            "barcode": "12379B64AC86BB",
                            "manufacturer": { "id": 203 }, # TROCA
                            # "manufacturer": { "name": "Sacadas & Truques LTDA" }, # INSERE
                            "unitPrice": 20234748.03
                          })   
               }   
      
        # Act...
        post = api.lambda_handler(event=body, context='')        
        
        # Asserts...        
        self.assertEqual(type(post), dict, 'Retorno deve ser do tipo "dict" mas é do tipo "'+ type(post).__name__ +'".')
        self.assertEqual('statusCode' in post.keys(), True, 'O atributo "statusCode" não foi retornado.')
        self.assertEqual(type(post['statusCode']), int, 'O atributo "statusCode" deve ser do tipo "int" mas é do tipo "'+type(post['statusCode']).__name__+'".')
        self.assertEqual(200, post['statusCode'], post['body'] if 'body' in post.keys() else 'Erro desconhecido.')        
        self.assertEqual('body' in post.keys(), True, 'O atributo "body" não foi retornado.')
        self.assertGreater(len(post['body']) , 0, 'O atributo "body" foi retornado vazio.')
        
        try:
            post['body'] = json.loads(post['body'])       
            jsonLoadsBody = True
        except Exception:
            jsonLoadsBody = False
        
        self.assertEqual(jsonLoadsBody, True, 'O "body" não contém um json encode válido.')
        
        self.assertEqual('id' in post['body'].keys(), True, 'O atributo "id" não foi retornado.')
        self.assertEqual(type(post['body']['id']), int, 'O atributo "id" deve ser do tipo "int" mas é do tipo "'+type(post['body']['id']).__name__+'".')
        
        self.assertEqual('manufacturer' in post['body'].keys(), True, 'O atributo "manufacturer" não foi retornado.')
        self.assertEqual('id' in post['body']['manufacturer'].keys(), True, 'O atributo "manufacturer.id" não foi retornado.')
        self.assertEqual(type(post['body']['manufacturer']['id']), int, 'O atributo "manufacturer.id" deve ser do tipo "int" mas é do tipo "'+type(post['body']['manufacturer']['id']).__name__+'".')   
        
        
    def test_delete_product(self):
        """ Teste de exclusão de produto. """   
       
        # Arrange...
        body = { 
                  'httpMethod': cts._DEL,  
                  'body': json.dumps({     
                            "id": 66,                   
                          })   
               }   
      
        # Act...
        post = api.lambda_handler(event=body, context='')        
        
        # Asserts...        
        self.assertEqual(type(post), dict, 'Retorno deve ser do tipo "dict" mas é do tipo "'+ type(post).__name__ +'".')
        self.assertEqual('statusCode' in post.keys(), True, 'O atributo "statusCode" não foi retornado.')
        self.assertEqual(type(post['statusCode']), int, 'O atributo "statusCode" deve ser do tipo "int" mas é do tipo "'+type(post['statusCode']).__name__+'".')
        self.assertEqual(200, post['statusCode'], post['body'] if 'body' in post.keys() else 'Erro desconhecido.')        
        self.assertEqual('body' in post.keys(), True, 'O atributo "body" não foi retornado.')
        self.assertGreater(len(post['body']) , 0, 'O atributo "body" foi retornado vazio.')
        
        try:
            post['body'] = json.loads(post['body'])       
            jsonLoadsBody = True
        except Exception:
            jsonLoadsBody = False
        
        self.assertEqual(jsonLoadsBody, True, 'O "body" não contém um json encode válido.')
        
        self.assertEqual('id' in post['body'].keys(), True, 'O atributo "id" não foi retornado.')
        self.assertEqual(type(post['body']['id']), int, 'O atributo "id" deve ser do tipo "int" mas é do tipo "'+type(post['body']['id']).__name__+'".')
        
    def test_get_product(self):
        """ Teste de consulta de produto. """     
       
        # Arrange...
        body = { 
                  'httpMethod': cts._GET,  
                  'queryStringParameters': json.dumps({     
                            "id": '42',      #  0=Listagem  >0=Detalhes de um produto
                            "page": '2', 
                            "order": "name"        
                  })   
               }   
      
        # Act...
        get = api.lambda_handler(event=body, context='')        
        
        # Asserts...        
        self.assertEqual(type(get), dict, 'Retorno deve ser do tipo "dict" mas é do tipo "'+ type(get).__name__ +'".')
        self.assertEqual('statusCode' in get.keys(), True, 'O atributo "statusCode" não foi retornado.')
        self.assertEqual(type(get['statusCode']), int, 'O atributo "statusCode" deve ser do tipo "int" mas é do tipo "'+type(get['statusCode']).__name__+'".')
        self.assertEqual(200, get['statusCode'], get['body'] if 'body' in get.keys() else 'Erro desconhecido.')        
        self.assertEqual('body' in get.keys(), True, 'O atributo "body" não foi retornado.')
        self.assertGreater(len(get['body']) , 0, 'O atributo "body" foi retornado vazio.')
        
        try:
            get['body'] = json.loads(get['body'])       
            jsonLoadsBody = True
        except Exception:
            jsonLoadsBody = False
        
        self.assertEqual(jsonLoadsBody, True, 'O "body" não contém um json encode válido.')    
        
        self.assertEqual('maxRowsPerPage' in get['body'].keys(), True, 'O atributo "maxRowsPerPage" não foi retornado.')
        self.assertEqual('rows' in get['body'].keys(), True, 'O atributo "rows" não foi retornado.')
        self.assertLessEqual(len(get['body']['rows']), get['body']['maxRowsPerPage'], 'Mais registros que o permitido sendo retornados')
        
# ----------------------------------------------------------------------------------------------------------------------            

# DEBUG...
# test = ProductAPITests()
# test.test_insert_product_with_new_manufacturer()