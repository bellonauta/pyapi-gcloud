#--------------------------------------------------------------------
# Facades para execução dos CRUDs com produtos.
#--------------------------------------------------------------------

import sys
import json
import jsonschema

from typing import Union
from abc import abstractmethod
from jsonschema import validate

import py_api_consts as cts
import py_api_functions as fns               
import py_api_classes as cls    
import py_api_product_classes as prod    
import py_api_manufacturer_classes as manu 

class CRUDFacade:
    
    def __init__(self, body:Union[str,dict], db:cls.DatabaseInterface):
        super().__init__()
        #
        self.__db = db
        self.__body = body
        
        self.__status_code = 200
        
    def get_db(self):
        return self.__db
    
    def set_status_code(self, value:int):
        self.__status_code = value
    
    def get_status_code(self):
        return self.__status_code
    
    def set_body(self, value, add_line=False):
        if add_line and type(value) is str:
            self.__body = '(L'+str(sys._getframe().f_back.f_lineno)+') ' + value
        else:    
            self.__body = value
    
    def get_body(self):    
        return self.__body
        
    def get_body_as_dict(self):
        if type(self.__body) is str:
            return {"message": self.__body} 
        else:    
            return self.__body    
    
    @abstractmethod            
    def execute(self):   
        """ Executa o CRUD. """
        pass
    

class PUTProductFacade(CRUDFacade):
    """ 
    Executa os requests de PUT de produto.
    OBS: Sabemos que o FACADE é um grande inimigo do SOLID, mas abri uma exceção para ele, para
         evitar sobrecarregar o consumer com toda a lógica do PUT de produtos. Penso que os riscos
         valem a pena, nesse caso.
    """       
        
    def execute(self):    
        """ 
        Executa o PUT. 
        Inicializa as propriedades __status_code e __body.
        Retorna:
           bool True/False quanto ao sucesso na execução.
        """
        # Inicia o controle de transações...
        if self.get_db().start_transaction():                                    
            # Checagem da estrutura do request...
            check_put_request = prod.CheckProductPUTRequest(body=self.get_body(), db=self.get_db())
            if check_put_request.execute():
                # Inclusão...     
                insert_product = prod.InsertProduct(  schema=check_put_request.get_schema(), 
                                                      request=check_put_request.get_request(), 
                                                      db=self.get_db()
                                                   )                         
                if insert_product.execute():
                    # Tratamento do fabricante do produto...
                    check_manufacturer_put_request = manu.CheckManufacturerPUTRequest(body=self.get_body(), db=self.get_db())
                    if check_manufacturer_put_request.execute():
                        if check_manufacturer_put_request.get_insert_manufacturer():
                            # Inclusão do fabricante...                                                      
                            insert_manufacturer = manu.InsertManufacturer(  manufacturer_name=check_manufacturer_put_request.get_manufacturer_name(), 
                                                                            db=self.get_db()
                                                                         ) 
                            if insert_manufacturer.execute():
                                # Reserva a PK do fabricante incluído...
                                check_manufacturer_put_request.set_manufacturer_id(insert_manufacturer.get_primary_key()['id'])                                        
                                # Inclusão do fabricante para o produto...                                                      
                                insert_product_manufacturer = manu.InsertProductManufacturer(  product_id=insert_product.get_primary_key()['id'],
                                                                                               manufacturer_id=check_manufacturer_put_request.get_manufacturer_id(), 
                                                                                               db=self.get_db()
                                                                                            ) 
                                if not insert_product_manufacturer.execute():                                           
                                    self.set_status_code(insert_product_manufacturer.get_error_code())
                                    self.set_body(insert_product_manufacturer.get_error_message(), True)
                            else:   
                                self.set_status_code(400)
                                self.set_body(insert_manufacturer.get_error_message(), True)   
                        elif check_manufacturer_put_request.get_update_manufacturer():      
                            # Atualiza o fabricante do produto... 
                            update_manufacturer = manu.UpdateManufacturer(  manufacturer_id=check_manufacturer_put_request.get_manufacturer_id(),
                                                                            manufacturer_name=check_manufacturer_put_request.get_manufacturer_name(), 
                                                                            db=self.get_db()
                                                                         )
                            if not update_manufacturer.execute():
                                self.set_status_code(update_manufacturer.get_error_code())
                                self.set_body(update_manufacturer.get_error_message(), True)      
                    else:   
                        self.set_status_code(400)
                        self.set_body(check_manufacturer_put_request.get_error_message(), True)   
                               
                    # Response...
                    if self.get_status_code() == 200: 
                        body = check_put_request.get_request()
                        body['id'] = insert_product.get_primary_key()['id']
                        body['manufacturer']['id'] = check_manufacturer_put_request.get_manufacturer_id()
                        body['manufacturer']['name'] = check_manufacturer_put_request.get_manufacturer_name()    
                        self.set_body(body) # Atualiza
                                    
                else:   
                    self.set_status_code(insert_product.get_error_code())
                    self.set_body(insert_product.get_error_message(), True)   
                      
            else:   
                self.set_status_code(check_put_request.get_error_code())
                self.set_body(check_put_request.get_error_message(), True)   
                
            # Commit & Rollback...
            if self.get_db().in_transaction():
                # Tenta commit...
                if self.get_status_code() == 200:
                    if not self.get_db().commit():
                        self.set_status_code(self.get_db().get_error_code())
                        self.set_body(self.get_db().get_error_message(), True)   
                #      
                # Rollback...
                if self.get_status_code() != 200:
                    self.get_db().rollback()               
            #     
                   
        else:   
            self.set_status_code(self.get_db().get_error_code())
            self.set_body(self.get_db().get_error_message(), True)             
        #
        return self.get_status_code() == 200
    
class POSTProductFacade(CRUDFacade):
    """ 
    Executa os requests de POST de produto.
    OBS: Sabemos que o FACADE é um grande inimigo do SOLID, mas abri uma exceção para ele, para
         evitar sobrecarregar o consumer com toda a lógica do POST de produtos. Penso que os riscos
         valem a pena, nesse caso.
    """       
        
    def execute(self):    
        """ 
        Executa o POST. 
        Inicializa as propriedade __status_code e __body.
        Retorna:
           bool True/False quanto ao sucesso na execução.
        """
        # Inicia o controle de transações...
        if self.get_db().start_transaction():                                    
            # Checagem da estrutura do request...
            check_post_request = prod.CheckProductPOSTRequest(body=self.get_body(), db=self.get_db())
            if check_post_request.execute():
                # Alteração...     
                update_product = prod.UpdateProduct(  schema=check_post_request.get_schema(), 
                                                      request=check_post_request.get_request(), 
                                                      db=self.get_db()
                                                   )                         
                if update_product.execute():
                    # Tratamento do fabricante do produto...
                    check_manufacturer_post_request = manu.CheckManufacturerPOSTRequest(body=self.get_body(), db=self.get_db())
                    if check_manufacturer_post_request.execute():
                        if check_manufacturer_post_request.get_insert_manufacturer():
                            # Inclusão do fabricante...                                                      
                            insert_manufacturer = manu.InsertManufacturer(  manufacturer_name=check_manufacturer_post_request.get_manufacturer_name(), 
                                                                            db=self.get_db()
                                                                         ) 
                            if insert_manufacturer.execute():
                                # Reserva a PK do fabricante incluído...
                                check_manufacturer_post_request.set_manufacturer_id(insert_manufacturer.get_primary_key()['id'])                                        
                                # Inclusão do fabricante para o produto...                                                      
                                insert_product_manufacturer = manu.InsertProductManufacturer(  product_id=update_product.get_primary_key()['id'],
                                                                                               manufacturer_id=check_manufacturer_post_request.get_manufacturer_id(), 
                                                                                               db=self.get_db()
                                                                                            ) 
                                if not insert_product_manufacturer.execute():                                           
                                    self.set_status_code(insert_product_manufacturer.get_error_code())
                                    self.set_body(insert_product_manufacturer.get_error_message(), True) 
                            else:   
                                 self.set_status_code(insert_manufacturer.get_error_code())
                                 self.set_body(insert_manufacturer.get_error_message(), True)    
                        elif check_manufacturer_post_request.get_update_manufacturer():      
                            # Atualiza o fabricante do produto... 
                            update_manufacturer = manu.UpdateManufacturer(  manufacturer_id=check_manufacturer_post_request.get_manufacturer_id(),
                                                                            manufacturer_name=check_manufacturer_post_request.get_manufacturer_name(), 
                                                                            db=self.get_db()
                                                                         )
                            if not update_manufacturer.execute():                                       
                                self.set_status_code(update_manufacturer.get_error_code())
                                self.set_body(update_manufacturer.get_error_message(), True) 
                        #                               
                        if self.get_status_code() == 200:
                            if check_manufacturer_post_request.get_update_product():
                                # Troca de fabricante do produto...                                                      
                                update_product_manufacturer = manu.UpdateProductManufacturer(  product_id=update_product.get_primary_key()['id'],
                                                                                               manufacturer_id=check_manufacturer_post_request.get_manufacturer_id(), 
                                                                                               db=self.get_db()
                                                                                            ) 
                                if not update_product_manufacturer.execute():                                           
                                    self.set_status_code(update_product_manufacturer.get_error_code())
                                    self.set_body(update_product_manufacturer.get_error_message(), True)                                                                          
                                   
                    else:   
                        self.set_status_code(400)
                        self.set_body(check_manufacturer_post_request.get_error_message(), True)      
                               
                    # Response(json encode)...
                    if self.get_status_code() == 200:
                        body = check_post_request.get_request()
                        body['id'] = update_product.get_primary_key()['id']
                        body['manufacturer']['id'] = check_manufacturer_post_request.get_manufacturer_id()
                        body['manufacturer']['name'] = check_manufacturer_post_request.get_manufacturer_name()                                           
                        self.set_body(body) # Atualiza
                                    
                else:   
                    self.set_status_code(update_product.get_error_code())
                    self.set_body(update_product.get_error_message(), True) 
                           
            else:   
                self.set_status_code(check_post_request.get_error_code())
                self.set_body(check_post_request.get_error_message(), True) 
                
            # Commit & Rollback...
            if self.get_db().in_transaction():
                # Tenta commit...
                if self.get_status_code() == 200:
                    if not self.get_db().commit():
                        self.set_status_code(self.get_db().get_error_code())
                        self.set_body(self.get_db().get_error_message(), True) 
                #      
                # Rollback...
                if self.get_status_code() != 200:
                    self.get_db().rollback()               
            #                          
                
        else:   
            self.set_status_code(self.get_db().get_error_code())
            self.set_body(self.get_db().get_error_message(), True) 
        #
        return self.get_status_code() == 200
        
    
class GETProductFacade(CRUDFacade):
    """ 
    Executa os requestes de GET de produtos.
    OBS: Sabemos que o FACADE é um grande inimigo do SOLID, mas abri uma exceção para ele, para
         evitar sobrecarregar o consumer com toda a lógica do GET de produtos. Penso que os riscos
         valem a pena, nesse caso.
    """    
       
    def execute(self):    
        """ 
        Executa o GET. 
        Inicializa as propriedade __status_code e __body.
        Retorna:
           bool True/False quanto ao sucesso na execução.
        """    
        # Checagem da estrutura do request...
        check_get_request = prod.CheckProductGETRequest(body=self.get_body(), db=self.get_db())
        if check_get_request.execute():
            # Consulta...     
            get_product = prod.GetProduct(  schema=check_get_request.get_schema(), 
                                            request=check_get_request.get_request(), 
                                            db=self.get_db()
                                         )                         
            if get_product.execute():
                # Response(json encode)...
                 self.set_body(get_product.get_request())
            else:   
                self.set_status_code(get_product.get_error_code())
                self.set_body(get_product.get_error_message(), True) 
                           
        else:   
            self.set_status_code(check_get_request.get_error_code())
            self.set_body(check_get_request.get_error_message(), True) 
        #
        return self.get_status_code() == 200    


class DELETEProductFacade(CRUDFacade):
    """ 
    Executa os requests de DELETE de produto.
    OBS: Sabemos que o FACADE é um grande inimigo do SOLID, mas abri uma exceção para ele, para
         evitar sobrecarregar o consumer com toda a lógica do DELETE de produtos. Penso que os riscos
         valem a pena, nesse caso.
    """       
        
    def execute(self):    
        """ 
        Executa o DELETE. 
        Inicializa as propriedade __status_code e __body.
        Retorna:
           bool True/False quanto ao sucesso na execução.
        """
        # Inicia o controle de transações...
        if self.get_db().start_transaction():                                    
            # Checagem da estrutura do request...
            check_del_request = prod.CheckProductDELETERequest(body=self.get_body(), db=self.get_db())
            if check_del_request.execute():
                # Exclusão...     
                delete_product = prod.DeleteProduct(  schema=check_del_request.get_schema(), 
                                                      request=check_del_request.get_request(), 
                                                      db=self.get_db()
                                                   )                         
                if delete_product.execute():
                    # Tratamento da exclusão(desativação) da associação produto e fabricante...
                    delete_product_manufacturer = manu.DeleteProductManufacturer(  product_id=delete_product.get_primary_key()['id'],
                                                                                   db=self.get_db()
                                                                                ) 
                    if not delete_product_manufacturer.execute():                                           
                        self.set_status_code(delete_product_manufacturer.get_error_code())
                        self.set_body(delete_product_manufacturer.get_error_message(), True) 
                    else:                              
                        # Response(json encode)...
                        body = check_del_request.get_request()
                        body['id'] = delete_product.get_primary_key()['id']                                   
                        self.set_body(body) # Atualiza
                else:   
                    self.set_status_code(delete_product.get_error_code())
                    self.set_body(delete_product.get_error_message(), True) 
                           
            else:   
                self.set_status_code(check_del_request.get_error_code())
                self.set_body(check_del_request.get_error_message(), True) 
                
            # Commit & Rollback...
            if self.get_db().in_transaction():
                # Tenta commit...
                if self.get_status_code() == 200:
                    if not self.get_db().commit():
                        self.set_status_code(self.get_db().get_error_code())
                        self.set_body(self.get_db().get_error_message(), True) 
                #      
                # Rollback...
                if self.get_status_code() != 200:
                    self.get_db().rollback()               
            #      
                       
        else:   
            self.set_status_code(self.get_db().get_error_code())
            self.set_body(self.get_db().get_error_message(), True) 
        #
        return self.get_status_code() == 200    
# ---------------------------------------------------------------------------------------    