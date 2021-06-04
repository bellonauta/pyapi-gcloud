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

def check_request(request):
    """
    Checagem da estrutura da requisição.
    Args:
        request (any): Parâmetros recebidos
    Returns:
        dict: "success"(bool) com True/False  e 
              "message"(str) com a mensagem de erro/falha quando houver
    """
    check = { 
              'success': True,
              'message': ''
            }
    #
    if type(request) is not dict or 'httpMethod' not in request:
        check['success'] = False
        check['message'] = 'A estrutura da requisição é inválida.'
    elif request['httpMethod'] not in cts._HTTP_METHODS:           
        check['success'] = False
        check['message'] = 'O método de request é desconhecido.'
    elif 'body' not in request or fns.is_empty(request['body']):   
        check['success'] = False
        check['message'] = 'O body do request não foi postado ou está vazio.'           
    #
    return check    


def handler(request, in_production=False):
    """Atende as requisições.

    Args:
        request (any): Parâmetros da rquisição
        in_production (bool, optional): Em produção?. Defaults to False.
    Returns:
        dict: "statusCode"(int): HTML Status code(remember that 200 = OK)
              "headers"(dict): Hardcoded para {'Content-Type': 'application/json'},
              "body"(dict): Retorno da requisição, conforme documentação no README.md.
    """
    # Estrutura para o retorno da API...
    response = cts._API_RESPONSE
    #
    # Consiste estrutura da requisição...
    check = check_request(request=request)
    if not check['success']:
        response['statusCode'] = 400
        response['body'] = {"message": check['message']}   
    elif not os.path.isfile(str(Path(__file__).parent) + '/db/pg_conn.py'):
        # Script com os parâmetros de conexão não encontrado...
        response['statusCode'] = 400
        response['body'] = {"message": 'O script "db/pg_conn.py" não foi encontrado.'}   
    else:   
        # Parâmetros de conexão PostgreSQL...
        from db.pg_conn import _PG_CONNECTION 
        #
        # Conexão com o banco PostgreSQL...
        conn_pars = _PG_CONNECTION['production'] if in_production else _PG_CONNECTION['devel'] # Tipo do ambiente
        database = cls.DBPostgres()  # Wrapper      
        if database.connect(conn_pars=conn_pars) :      
            # Atendimento das requisições...            
            if request['httpMethod'] == cts._PUT:
                # Inclusões... 
                put_product_facade = facade.PUTProductFacade(body=request['body'], db=database)
                put_product_facade.execute()
                response['statusCode'] = put_product_facade.get_status_code()
                response['body'] = put_product_facade.get_body_as_dict()        
            #        
            elif request['httpMethod'] == cts._GET:
                # Consultas... 
                get_product_facade = facade.GETProductFacade(body=request['body'], db=database)
                get_product_facade.execute()
                response['statusCode'] = get_product_facade.get_status_code()
                response['body'] = get_product_facade.get_body_as_dict()      
            #
            elif request['httpMethod'] == cts._POST:
                # Alterações... 
                post_product_facade = facade.POSTProductFacade(body=request['body'], db=database)
                post_product_facade.execute()
                response['statusCode'] = post_product_facade.get_status_code()
                response['body'] = post_product_facade.get_body_as_dict()                     
            #
            elif request['httpMethod'] == cts._DEL:
                # Exclusões... 
                del_product_facade = facade.DELETEProductFacade(body=request['body'], db=database)
                del_product_facade.execute()
                response['statusCode'] = del_product_facade.get_status_code()
                response['body'] = del_product_facade.get_body_as_dict()                  
            #                                    
        else:                   
            response['statusCode'] = 400
            response['body'] = {"message": database.get_error_message()}     
        # 
    #
    response['body'] = json.dumps(response['body'])
    #
    return response