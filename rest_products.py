#--------------------------------------------------------------------
# Responde as solicitações da API REST para operações de
# manutenção e consulta de produtos.
#--------------------------------------------------------------------

import os
import sys
import json

import py_api_consts as cts
import py_api_classes as cls     
import py_api_functions as fns                   
import py_api_product_facades as facade     

from pathlib import Path

from typing import AbstractSet, Union

def handler(event, context, in_production=False):
    # Estrutura para o retorno da API...
    response = {
                   'statusCode': 200, 
                   'headers': {
                                 'Content-Type': 'application/json'
                              },
                   'body': ''                 
               }
    #
    if not os.path.isfile(str(Path(__file__).parent) + '/db/pg_conn.py'):
        # Script com os parâmetros de conexão não encontrado...
        response['statusCode'] = 400
        response['body'] = {"message": 'O script "db/pg_conn.py" não foi encontrado.'}   
    else:   
        # Consiste estrutura da requisição...
        if type(event) is not dict or 'httpMethod' not in event:
            response['statusCode'] = 400
            response['body'] = {"message": 'A estrutura da requisição é inválida.'}
        elif event['httpMethod'] not in cts._HTTP_METHODS:           
            response['statusCode'] = 400
            response['body'] = {"message": 'O método de request é desconhecido.'}
        elif event['httpMethod'] != cts._GET and ('body' not in event or fns.is_empty(event['body'])):   
            response['statusCode'] = 400
            response['body'] = {"message": 'O body do request não foi postado ou está vazio.'}       
        elif event['httpMethod'] == cts._GET and ('queryStringParameters' not in event or fns.is_empty(event['queryStringParameters'])):   
            response['statusCode'] = 400
            response['body'] = {"message": 'A query do request não foi postada ou está vazia.'}            
        else:
            # Parâmetros de conexão PostgreSQL...
            from db.pg_conn import _PG_CONNECTION 
            #
            # Conexão com o banco PostgreSQL...
            conn_pars = _PG_CONNECTION['production'] if in_production else _PG_CONNECTION['devel'] # Tipo do ambiente
            database = cls.DBPostgres()  # Wrapper      
            if database.connect(conn_pars=conn_pars) :      
                # Atendimento das requisições...            
                if event['httpMethod'] == cts._PUT:
                    # Inclusões... 
                    put_product_facade = facade.PUTProductFacade(body=event['body'], db=database)
                    put_product_facade.execute()
                    response['statusCode'] = put_product_facade.get_status_code()
                    response['body'] = put_product_facade.get_body_as_dict()        
                #        
                elif event['httpMethod'] == cts._GET:
                    # Consultas... 
                    get_product_facade = facade.GETProductFacade(body=event['queryStringParameters'], db=database)
                    get_product_facade.execute()
                    response['statusCode'] = get_product_facade.get_status_code()
                    response['body'] = get_product_facade.get_body_as_dict()      
                #
                elif event['httpMethod'] == cts._POST:
                    # Alterações... 
                    post_product_facade = facade.POSTProductFacade(body=event['body'], db=database)
                    post_product_facade.execute()
                    response['statusCode'] = post_product_facade.get_status_code()
                    response['body'] = post_product_facade.get_body_as_dict()                     
                #
                elif event['httpMethod'] == cts._DEL:
                    # Exclusões... 
                    del_product_facade = facade.DELETEProductFacade(body=event['body'], db=database)
                    del_product_facade.execute()
                    response['statusCode'] = del_product_facade.get_status_code()
                    response['body'] = del_product_facade.get_body_as_dict()                  
                #                                    
            else:                   
                response['statusCode'] = 400
                response['body'] = {"message": database.get_error_message()}
            #                                         
        # 
    #
    response['body'] = json.dumps(response['body'])
    #
    return response