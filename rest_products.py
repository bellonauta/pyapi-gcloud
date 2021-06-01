#--------------------------------------------------------------------
# Responde as solicitações da API REST para operações de
# manutenção e consulta de produtos.
#--------------------------------------------------------------------

import json

from typing import AbstractSet, Union
import py_api_consts as cts
import py_api_functions as fns               
import py_api_classes as cls          
import py_api_product_facades as facade

def handler(event, context, in_production=False):
    # Estrutura para o retorno da API...
    ret = {'statusCode': 200, 
              'headers': {
                           'Content-Type': 'application/json'
                         },
                 'body': ''                 
          }

    # Consiste estrutura da requisição...
    if type(event) is not dict or 'httpMethod' not in event:
        ret['statusCode'] = 400
        ret['body'] = {"message": 'A estrutura da requisição é inválida.'}
    elif event['httpMethod'] not in cts._HTTP_METHODS:           
        ret['statusCode'] = 400
        ret['body'] = {"message": 'O método de request é desconhecido.'}
    elif event['httpMethod'] != cts._GET and ('body' not in event or fns.is_empty(event['body'])):   
        ret['statusCode'] = 400
        ret['body'] = {"message": 'O body do request não foi postado ou está vazio.'}       
    elif event['httpMethod'] == cts._GET and ('queryStringParameters' not in event or fns.is_empty(event['queryStringParameters'])):   
        ret['statusCode'] = 400
        ret['body'] = {"message": 'A query do request não foi postada ou está vazia.'}            
    else:
        # Conexão com o banco PostgreSQL...
        conn_pars = cts._PG_CONNECTION['production'] if in_production else cts._PG_CONNECTION['devel'] # Tipo do ambiente
        database = cls.DBPostgres()  # Wrapper      
        if database.connect(conn_pars=conn_pars) :      
            # Atendimento das requisições...            
            if event['httpMethod'] == cts._PUT:
                # Inclusões... 
                put_product_facade = facade.PUTProductFacade(body=event['body'], db=database)
                put_product_facade.execute()
                ret['statusCode'] = put_product_facade.get_status_code()
                ret['body'] = put_product_facade.get_body_as_dict()        
            #        
            elif event['httpMethod'] == cts._GET:
                # Consultas... 
                get_product_facade = facade.GETProductFacade(body=event['queryStringParameters'], db=database)
                get_product_facade.execute()
                ret['statusCode'] = get_product_facade.get_status_code()
                ret['body'] = get_product_facade.get_body_as_dict()      
            #
            elif event['httpMethod'] == cts._POST:
                # Alterações... 
                post_product_facade = facade.POSTProductFacade(body=event['body'], db=database)
                post_product_facade.execute()
                ret['statusCode'] = post_product_facade.get_status_code()
                ret['body'] = post_product_facade.get_body_as_dict()                     
            #
            elif event['httpMethod'] == cts._DEL:
                # Exclusões... 
                del_product_facade = facade.DELETEProductFacade(body=event['body'], db=database)
                del_product_facade.execute()
                ret['statusCode'] = del_product_facade.get_status_code()
                ret['body'] = del_product_facade.get_body_as_dict()                  
            #                                    
        else:                   
            ret['statusCode'] = 400
            ret['body'] = database.get_error_message()                                          
    
    #
    ret['body'] = json.dumps(ret['body'])
    #
    return ret