# coding:utf-8

#--------------------------------------------------------------------
# TDD UNITTEST - Testes unitários da API dos produtos.
#--------------------------------------------------------------------
# a) Para testar, crie uma subpasta do projeto chamada "tdd" e 
#    coloque esse script dentro dela;
# b) Por fim, estando dentro da pasta do projet, oexecute
#    no terminal/prompt:
#       $ python3 tdd/py_api_test_product.py --url=http://dominio:PORTA
#    O parâmetro "--url" não é obrigatório. Informe-o somente se a
#    url da API for diferente da padrão(http://localhost:5000)
#--------------------------------------------------------------------

import sys
import json
import requests
import unittest

from pathlib import Path
from datetime import datetime
from typing import AbstractSet, Union


# Bibliotecas...
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

import py_api_consts as cts
import py_api_functions as fns
#----------------------------------------------------------------------------------

class ProductAPITests(unittest.TestCase):

    def test_insert_product_with_new_manufacturer(self):
        """ Teste de inclusão de produto e fabricante. """                       
        
        # Arrange...
        body = { 
                  'httpMethod': cts._PUT,  
                  'body': {        
                      "name": fns.now(format='%Y%m%d%H%M%S')+"Chapuleta da corrêia dentada",
                      "description": "Chapa de aço que vai na chapuleta, folheada a ouro",
                      "barcode": "6466546464645",
                      "manufacturer": {  
                                         "name": fns.now(format='%Y%m%d%H%M%S')+"SpaceX & NASA",
                                      },
                      "unitPrice": 101234748.01
                  }   
               }   
      
        # Act...            
        request_error_exception = None
        request_error_message = ""
        put = None
        try: 
            put = requests.put(url=api_url, json=body, timeout=10, allow_redirects=True)   
        except Exception as ex:
            request_error_exception = type(ex).__name__.strip().lower()                                    
            request_error_message = str(ex)
                
        # Asserts...      
        self.assertNotEqual(request_error_exception, 'connecttimeout', 'Tempo esgotado para conexão com "'+api_url+'".')                  
        self.assertEqual(request_error_exception, None, 'Falha na conexão com "'+api_url+'".\n'+request_error_message)                  
        self.assertEqual(type(put), requests.models.Response, 'Retorno deve ser do tipo "Response" mas é do tipo "'+ type(put).__name__)
        self.assertEqual(put.status_code, requests.codes.ok, 'Falha no request para "'+api_url+'".\n'+str(put.status_code)+' - '+put.reason)                  
        self.assertEqual('statusCode' in put.json().keys(), True, 'O atributo "statusCode" não foi retornado.')
        self.assertEqual(type(put.json()['statusCode']), int, 'O atributo "statusCode" deve ser do tipo "int" mas é do tipo "'+type(put.json()['statusCode']).__name__+'".')
        self.assertEqual(200, put.json()['statusCode'], put.json()['body'] if 'body' in put.json().keys() else 'Erro desconhecido.')        
        self.assertEqual('body' in put.json().keys(), True, 'O atributo "body" não foi retornado.')
        self.assertGreater(len(put.json()['body']) , 0, 'O atributo "body" foi retornado vazio.')
        
        try:
            body = json.loads(put.json()['body'])       
            json_valid = True
        except Exception:
            json_valid = False
        
        self.assertEqual(json_valid, True, 'O "body" não contém um json encode válido.')
        
        self.assertEqual('id' in body.keys(), True, 'O atributo "id" não foi retornado.')
        self.assertEqual(type(body['id']), int, 'O atributo "id" deve ser do tipo "int" mas é do tipo "'+type(body['id']).__name__+'".')
        
        self.assertEqual('manufacturer' in body.keys(), True, 'O atributo "manufacturer" não foi retornado.')
        self.assertEqual('id' in body['manufacturer'].keys(), True, 'O atributo "manufacturer.id" não foi retornado.')
        self.assertEqual(type(body['manufacturer']['id']), int, 'O atributo "manufacturer.id" deve ser do tipo "int" mas é do tipo "'+type(body['manufacturer']['id']).__name__+'".')        
            
        
    def test_update_product_and_change_manufacturer(self):
        """ Teste de alteração de produto com troca de fabricante. """       
        
        # Arrange...
        body = { 
                  'httpMethod': cts._POST,  
                  'body': {     
                            "id": 206,                    
                            "name": fns.now(format='%Y%m%d%H%M%S')+"Correia desdentada",
                            "description": "Correia sem dentes, para polias 'ensopadas'.",
                            "barcode": "12379B64AC86BB",
                            "manufacturer": { "id": 201 }, # TROCA
                            # "manufacturer": { "name": fns.now(format='%Y%m%d%H%M%S')+"Sacadas & Truques LTDA" }, # INSERE
                            "unitPrice": 20234748.03
                          }   
               }   
      
        # Act...
        request_error_exception = None
        request_error_message = ""
        post = None
        try: 
            post = requests.post(url=api_url, json=body, timeout=10, allow_redirects=True)   
        except Exception as ex:
            request_error_exception = type(ex).__name__.strip().lower()                                    
            request_error_message = str(ex)     
        
        # Asserts...      
        self.assertNotEqual(request_error_exception, 'connecttimeout', 'Tempo esgotado para conexão com "'+api_url+'".')                  
        self.assertEqual(request_error_exception, None, 'Falha na conexão com "'+api_url+'".\n'+request_error_message)                  
        self.assertEqual(type(post), requests.models.Response, 'Retorno deve ser do tipo "Response" mas é do tipo "'+ type(post).__name__)
        self.assertEqual(post.status_code, requests.codes.ok, 'Falha no request para "'+api_url+'".\n'+str(post.status_code)+' - '+post.reason)                  
        self.assertEqual('statusCode' in post.json().keys(), True, 'O atributo "statusCode" não foi retornado.')
        self.assertEqual(type(post.json()['statusCode']), int, 'O atributo "statusCode" deve ser do tipo "int" mas é do tipo "'+type(post.json()['statusCode']).__name__+'".')
        self.assertEqual(200, post.json()['statusCode'], post.json()['body'] if 'body' in post.json().keys() else 'Erro desconhecido.')        
        self.assertEqual('body' in post.json().keys(), True, 'O atributo "body" não foi retornado.')
        self.assertGreater(len(post.json()['body']) , 0, 'O atributo "body" foi retornado vazio.')
        
        try:
            body = json.loads(post.json()['body'])       
            json_valid = True
        except Exception:
            json_valid = False
        
        self.assertEqual(json_valid, True, 'O "body" não contém um json encode válido.')
        
        self.assertEqual('id' in body.keys(), True, 'O atributo "id" não foi retornado.')
        self.assertEqual(type(body['id']), int, 'O atributo "id" deve ser do tipo "int" mas é do tipo "'+type(body['id']).__name__+'".')
        
        self.assertEqual('manufacturer' in body.keys(), True, 'O atributo "manufacturer" não foi retornado.')
        self.assertEqual('id' in body['manufacturer'].keys(), True, 'O atributo "manufacturer.id" não foi retornado.')
        self.assertEqual(type(body['manufacturer']['id']), int, 'O atributo "manufacturer.id" deve ser do tipo "int" mas é do tipo "'+type(body['manufacturer']['id']).__name__+'".')        
        
        
    def test_delete_product(self):
        """ Teste de exclusão de produto. """   
       
        # Arrange...
        body = { 
                  'httpMethod': cts._DEL,  
                  'body': json.dumps({     
                            "id": 207,                   
                          })   
               }   
      
        # Act...
        request_error_exception = None
        request_error_message = ""
        delete = None
        try: 
            delete = requests.delete(url=api_url, json=body, timeout=10, allow_redirects=True)   
        except Exception as ex:
            request_error_exception = type(ex).__name__.strip().lower()                                    
            request_error_message = str(ex)     
        
        # Asserts...      
        self.assertNotEqual(request_error_exception, 'connecttimeout', 'Tempo esgotado para conexão com "'+api_url+'".')                  
        self.assertEqual(request_error_exception, None, 'Falha na conexão com "'+api_url+'".\n'+request_error_message)                  
        self.assertEqual(type(delete), requests.models.Response, 'Retorno deve ser do tipo "Response" mas é do tipo "'+ type(delete).__name__)
        self.assertEqual(delete.status_code, requests.codes.ok, 'Falha no request para "'+api_url+'".\n'+str(delete.status_code)+' - '+delete.reason)                  
        self.assertEqual('statusCode' in delete.json().keys(), True, 'O atributo "statusCode" não foi retornado.')
        self.assertEqual(type(delete.json()['statusCode']), int, 'O atributo "statusCode" deve ser do tipo "int" mas é do tipo "'+type(delete.json()['statusCode']).__name__+'".')
        self.assertEqual(200, delete.json()['statusCode'], delete.json()['body'] if 'body' in delete.json().keys() else 'Erro desconhecido.')        
        self.assertEqual('body' in delete.json().keys(), True, 'O atributo "body" não foi retornado.')
        self.assertGreater(len(delete.json()['body']) , 0, 'O atributo "body" foi retornado vazio.')
        
        try:
            body = json.loads(delete.json()['body'])       
            json_valid = True
        except Exception:
            json_valid = False
        
        self.assertEqual(json_valid, True, 'O "body" não contém um json encode válido.')
        
        self.assertEqual('id' in body.keys(), True, 'O atributo "id" não foi retornado.')
        self.assertEqual(type(body['id']), int, 'O atributo "id" deve ser do tipo "int" mas é do tipo "'+type(body['id']).__name__+'".')
        
    def test_get_product(self):
        """ Teste de consulta de produto. """     
       
        # Arrange...
        body = { 
                  'httpMethod': cts._GET,  
                  'queryStringParameters': {     
                            "id": '207',      #  0=Listagem  >0=Detalhes de um produto
                            "page": '0', 
                            "order": "name"        
                  }   
               }   
      
        # Act...
        request_error_exception = None
        request_error_message = ""
        get = None
        try: 
            get = requests.get(url=api_url, json=body, timeout=10, allow_redirects=True)   
        except Exception as ex:
            request_error_exception = type(ex).__name__.strip().lower()                                    
            request_error_message = str(ex)     
              
        # Asserts...        
        self.assertNotEqual(request_error_exception, 'connecttimeout', 'Tempo esgotado para conexão com "'+api_url+'".')                  
        self.assertEqual(request_error_exception, None, 'Falha na conexão com "'+api_url+'".\n'+request_error_message)                  
        self.assertEqual(type(get), requests.models.Response, 'Retorno deve ser do tipo "Response" mas é do tipo "'+ type(get).__name__)
        self.assertEqual(get.status_code, requests.codes.ok, 'Falha no request para "'+api_url+'".\n'+str(get.status_code)+' - '+get.reason)                  
        self.assertEqual('statusCode' in get.json().keys(), True, 'O atributo "statusCode" não foi retornado.')
        self.assertEqual(type(get.json()['statusCode']), int, 'O atributo "statusCode" deve ser do tipo "int" mas é do tipo "'+type(get.json()['statusCode']).__name__+'".')
        self.assertEqual(200, get.json()['statusCode'], get.json()['body'] if 'body' in get.json().keys() else 'Erro desconhecido.')        
        self.assertEqual('body' in get.json().keys(), True, 'O atributo "body" não foi retornado.')
        self.assertGreater(len(get.json()['body']) , 0, 'O atributo "body" foi retornado vazio.')
        
        try:
            body = json.loads(get.json()['body'])       
            json_valid = True
        except Exception:
            json_valid = False
        
        self.assertEqual(json_valid, True, 'O "body" não contém um json encode válido.')    
        
        self.assertEqual('maxRowsPerPage' in body.keys(), True, 'O atributo "maxRowsPerPage" não foi retornado.')
        self.assertEqual('rows' in body.keys(), True, 'O atributo "rows" não foi retornado.')
        self.assertLessEqual(len(body['rows']), body['maxRowsPerPage'], 'Mais registros que o permitido sendo retornados')
        
# ----------------------------------------------------------------------------------------------------------------------            

def test_suite():
    suite = unittest.TestSuite()
    #suite.addTest(ProductAPITests('test_insert_product_with_new_manufacturer'))
    #suite.addTest(ProductAPITests('test_update_product_and_change_manufacturer'))
    #suite.addTest(ProductAPITests('test_delete_product'))
    suite.addTest(ProductAPITests('test_get_product'))
    return suite
# ----------------------------------------------------------------------------------------------------------------------            
  

# DEBUG...
# test = ProductAPITests()
# test.test_insert_product_with_new_manufacturer()

if __name__ == '__main__':  
   # Pega a URL da API da linha de comando... 
   api_url = fns.get_cmd_arg(sys.argv, '--url', default=None)
   if api_url == None:
       # Não informada - seta a padrão...
       api_url = 'http://localhost:5000' 
   elif api_url == '':
       # Informada vazia(--url=)...
       print('Comando: python3 tdd/py_api_test_product.py --url=http://dominio:PORTA\n')    
       sys.exit()
   #  
   # Roda os testes...  
   runner = unittest.TextTestRunner(failfast=True, verbosity=2)
   runner.run(test_suite()) 