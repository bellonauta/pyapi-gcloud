#--------------------------------------------------------------------
# Responde as solicitações da API REST para operações de
# manutenção e consulta de produtos.
#--------------------------------------------------------------------

import json

from typing import AbstractSet, Union
import py_api_consts as cts
import py_api_functions as fns               
import py_api_classes as cls          
import py_api_product_classes as prod   
import py_api_manufacturer_classes as manu

def lambda_handler(event, context):
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
        ret['body'] = 'A estrutura da requisição é inválida.'
    elif event['httpMethod'] not in cts._HTTP_METHODS:           
        ret['statusCode'] = 400
        ret['body'] = 'O método de request é desconhecido.'
    elif event['httpMethod'] != cts._GET and ('body' not in event or fns.is_empty(event['body'])):   
        ret['statusCode'] = 400
        ret['body'] = 'O body do request não foi postado ou está vazio.'        
    elif event['httpMethod'] == cts._GET and ('queryStringParameters' not in event or fns.is_empty(event['queryStringParameters'])):   
        ret['statusCode'] = 400
        ret['body'] = 'A query do request não foi postada ou está vazia.'            
    else:
        # Conexão com o banco PostgreSQL...
        database = cls.DBPostgres()
        if database.connect(conn_pars=cts._PG_CONNECTION):      
            # Atendimento das requisições...            
            if event['httpMethod'] == cts._PUT:
                # Inclusões... 
                #
                # Inicia o controle de transações...
                if database.start_transaction():                                    
                   # Checagem da estrutura do request...
                   checkPUTRequest = prod.CheckProductPUTRequest(body=event['body'], db=database)
                   if checkPUTRequest.execute():
                       # Inclusão...     
                       insertProduct = prod.InsertProduct(  schema=checkPUTRequest.get_schema(), 
                                                            request=checkPUTRequest.get_request(), 
                                                            db=database
                                                         )                         
                       if insertProduct.execute():
                           # Tratamento do fabricante do produto...
                           checkManufacturerPUTRequest = manu.CheckManufacturerPUTRequest(body=event['body'], db=database)
                           if checkManufacturerPUTRequest.execute():
                               if checkManufacturerPUTRequest.get_insert_manufacturer():
                                   # Inclusão do fabricante...                                                      
                                   insertManufacturer = manu.InsertManufacturer(  manufacturer_name=checkManufacturerPUTRequest.get_manufacturer_name(), 
                                                                                  db=database
                                                                               ) 
                                   if insertManufacturer.execute():
                                       # Reserva a PK do fabricante incluído...
                                       checkManufacturerPUTRequest.set_manufacturer_id(insertManufacturer.get_primary_key()['id'])                                        
                                       # Inclusão do fabricante para o produto...                                                      
                                       insertProductManufacturer = manu.InsertProductManufacturer(  product_id=insertProduct.get_primary_key()['id'],
                                                                                                    manufacturer_id=checkManufacturerPUTRequest.get_manufacturer_id(), 
                                                                                                    db=database
                                                                                                 ) 
                                       if not insertProductManufacturer.execute():                                           
                                           ret['statusCode'] = 400
                                           ret['body'] = insertProductManufacturer.get_error_message()
                                   else:   
                                       ret['statusCode'] = 400
                                       ret['body'] = insertManufacturer.get_error_message()   
                               elif checkManufacturerPUTRequest.get_update_manufacturer():      
                                   # Atualiza o fabricante do produto... 
                                   updateManufacturer = manu.UpdateManufacturer(  manufacturer_id=checkManufacturerPUTRequest.get_manufacturer_id(),
                                                                                  manufacturer_name=checkManufacturerPUTRequest.get_manufacturer_name(), 
                                                                                  db=database
                                                                               )
                           else:   
                               ret['statusCode'] = 400
                               ret['body'] = checkManufacturerPUTRequest.get_error_message()     
                               
                           # Response(json encode)...
                           if ret['statusCode'] == 200: 
                               ret['body'] = checkPUTRequest.get_request()
                               ret['body']['id'] = insertProduct.get_primary_key()['id']
                               ret['body']['manufacturer']['id'] = checkManufacturerPUTRequest.get_manufacturer_id()
                               ret['body']['manufacturer']['name'] = checkManufacturerPUTRequest.get_manufacturer_name()    
                                    
                       else:   
                           ret['statusCode'] = 400
                           ret['body'] = insertProduct.get_error_message()
                           
                   else:   
                       ret['statusCode'] = 400
                       ret['body'] = checkPUTRequest.get_error_message()               
                      
                else:   
                    ret['statusCode'] = 400
                    ret['body'] = database.get_error_message()         
                           
             
            #        
            elif event['httpMethod'] == cts._GET:
                # Consultas... 
                #                                      
                # Checagem da estrutura do request...
                checkGETRequest = prod.CheckProductGETRequest(body=event['queryStringParameters'], db=database)
                if checkGETRequest.execute():
                    # Consulta...     
                    getProduct = prod.GetProduct(  schema=checkGETRequest.get_schema(), 
                                                   request=checkGETRequest.get_request(), 
                                                   db=database
                                                )                         
                    if getProduct.execute():
                        # Response(json encode)...
                        ret['body'] = getProduct.get_request()
                    else:   
                        ret['statusCode'] = 400
                        ret['body'] = getProduct.get_error_message()  
                           
                else:   
                    ret['statusCode'] = 400
                    ret['body'] = checkGETRequest.get_error_message()  
            #
            elif event['httpMethod'] == cts._POST:
                # Alterações... 
                #
                # Inicia o controle de transações...
                if database.start_transaction():                                    
                   # Checagem da estrutura do request...
                   checkPOSTRequest = prod.CheckProductPOSTRequest(body=event['body'], db=database)
                   if checkPOSTRequest.execute():
                       # Alteração...     
                       updateProduct = prod.UpdateProduct(  schema=checkPOSTRequest.get_schema(), 
                                                            request=checkPOSTRequest.get_request(), 
                                                            db=database
                                                         )                         
                       if updateProduct.execute():
                           # Tratamento do fabricante do produto...
                           checkManufacturerPOSTRequest = manu.CheckManufacturerPOSTRequest(body=event['body'], db=database)
                           if checkManufacturerPOSTRequest.execute():
                               if checkManufacturerPOSTRequest.get_insert_manufacturer():
                                   # Inclusão do fabricante...                                                      
                                   insertManufacturer = manu.InsertManufacturer(  manufacturer_name=checkManufacturerPOSTRequest.get_manufacturer_name(), 
                                                                                  db=database
                                                                               ) 
                                   if insertManufacturer.execute():
                                       # Reserva a PK do fabricante incluído...
                                       checkManufacturerPOSTRequest.set_manufacturer_id(insertManufacturer.get_primary_key()['id'])                                        
                                       # Inclusão do fabricante para o produto...                                                      
                                       insertProductManufacturer = manu.InsertProductManufacturer(  product_id=updateProduct.get_primary_key()['id'],
                                                                                                    manufacturer_id=checkManufacturerPOSTRequest.get_manufacturer_id(), 
                                                                                                    db=database
                                                                                                 ) 
                                       if not insertProductManufacturer.execute():                                           
                                           ret['statusCode'] = 400
                                           ret['body'] = insertProductManufacturer.get_error_message()
                                   else:   
                                       ret['statusCode'] = 400
                                       ret['body'] = insertManufacturer.get_error_message()   
                               elif checkManufacturerPOSTRequest.get_update_manufacturer():      
                                   # Atualiza o fabricante do produto... 
                                   updateManufacturer = manu.UpdateManufacturer(  manufacturer_id=checkManufacturerPOSTRequest.get_manufacturer_id(),
                                                                                  manufacturer_name=checkManufacturerPOSTRequest.get_manufacturer_name(), 
                                                                                  db=database
                                                                               )
                                   if not updateManufacturer.execute():                                       
                                       ret['statusCode'] = 400
                                       ret['body'] = updateManufacturer.get_error_message()   
                               #                               
                               if ret['statusCode'] == 200:
                                   if checkManufacturerPOSTRequest.get_update_product():
                                       # Troca de fabricante do produto...                                                      
                                       updateProductManufacturer = manu.UpdateProductManufacturer(  product_id=updateProduct.get_primary_key()['id'],
                                                                                                    manufacturer_id=checkManufacturerPOSTRequest.get_manufacturer_id(), 
                                                                                                    db=database
                                                                                                 ) 
                                       if not updateProductManufacturer.execute():                                           
                                           ret['statusCode'] = 400
                                           ret['body'] = updateProductManufacturer.get_error_message()                                                                          
                                   
                           else:   
                               ret['statusCode'] = 400
                               ret['body'] = checkManufacturerPOSTRequest.get_error_message()     
                               
                           # Response(json encode)...
                           if ret['statusCode'] == 200:
                               ret['body'] = checkPOSTRequest.get_request()
                               ret['body']['id'] = updateProduct.get_primary_key()['id']
                               ret['body']['manufacturer']['id'] = checkManufacturerPOSTRequest.get_manufacturer_id()
                               ret['body']['manufacturer']['name'] = checkManufacturerPOSTRequest.get_manufacturer_name()                                           
                                    
                       else:   
                           ret['statusCode'] = 400
                           ret['body'] = updateProduct.get_error_message()  
                           
                   else:   
                       ret['statusCode'] = 400
                       ret['body'] = checkPOSTRequest.get_error_message()                        
                
                else:   
                    ret['statusCode'] = 400
                    ret['body'] = database.get_error_message()                       
                
            #
            elif event['httpMethod'] == cts._DEL:
                # Exclusões... 
                #
                # Inicia o controle de transações...
                if database.start_transaction():                                    
                   # Checagem da estrutura do request...
                   checkDELRequest = prod.CheckProductDELETERequest(body=event['body'], db=database)
                   if checkDELRequest.execute():
                       # Exclusão...     
                       deleteProduct = prod.DeleteProduct(  schema=checkDELRequest.get_schema(), 
                                                            request=checkDELRequest.get_request(), 
                                                            db=database
                                                         )                         
                       if deleteProduct.execute():
                           # Tratamento da exclusão(desativação) da associação produto e fabricante...
                           deleteProductManufacturer = manu.DeleteProductManufacturer(  product_id=deleteProduct.get_primary_key()['id'],
                                                                                        db=database
                                                                                     ) 
                           if not deleteProductManufacturer.execute():                                           
                               ret['statusCode'] = 400
                               ret['body'] = deleteProductManufacturer.get_error_message() 
                           else:                              
                               # Response(json encode)...
                               ret['body'] = checkDELRequest.get_request()
                               ret['body']['id'] = deleteProduct.get_primary_key()['id']                                    
                       else:   
                           ret['statusCode'] = 400
                           ret['body'] = deleteProduct.get_error_message()  
                           
                   else:   
                       ret['statusCode'] = 400
                       ret['body'] = checkDELRequest.get_error_message()      
                       
                else:   
                    ret['statusCode'] = 400
                    ret['body'] = database.get_error_message()                           
            #              
            #--------------------------------------------------------------------------------------
            #
            # Commit & Rollback...
            if database.in_transaction():
                # Tenta commit...
                if ret['statusCode'] == 200:
                    if not database.commit():
                        ret['statusCode'] = 400
                        ret['body'] = database.get_error_message()
                #      
                # Rollback...
                if ret['statusCode'] != 200:
                    database.rollback()               
            #               
        else:                   
            ret['statusCode'] = 400
            ret['body'] = database.get_error_message()                                          
    
    #
    ret['body'] = json.dumps(ret['body'] if type(ret['body']) == dict else {'message': ret['body']})
    #
    return ret