#--------------------------------------------------------------------
# Facades para execução dos CRUDs com produtos.
#--------------------------------------------------------------------

import sys
from abc import abstractmethod
import json
from typing import Union
import jsonschema
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
            checkPUTRequest = prod.CheckProductPUTRequest(body=self.get_body(), db=self.get_db())
            if checkPUTRequest.execute():
                # Inclusão...     
                insertProduct = prod.InsertProduct(  schema=checkPUTRequest.get_schema(), 
                                                     request=checkPUTRequest.get_request(), 
                                                     db=self.get_db()
                                                  )                         
                if insertProduct.execute():
                    # Tratamento do fabricante do produto...
                    checkManufacturerPUTRequest = manu.CheckManufacturerPUTRequest(body=self.get_body(), db=self.get_db())
                    if checkManufacturerPUTRequest.execute():
                        if checkManufacturerPUTRequest.get_insert_manufacturer():
                            # Inclusão do fabricante...                                                      
                            insertManufacturer = manu.InsertManufacturer(  manufacturer_name=checkManufacturerPUTRequest.get_manufacturer_name(), 
                                                                           db=self.get_db()
                                                                        ) 
                            if insertManufacturer.execute():
                                # Reserva a PK do fabricante incluído...
                                checkManufacturerPUTRequest.set_manufacturer_id(insertManufacturer.get_primary_key()['id'])                                        
                                # Inclusão do fabricante para o produto...                                                      
                                insertProductManufacturer = manu.InsertProductManufacturer(  product_id=insertProduct.get_primary_key()['id'],
                                                                                             manufacturer_id=checkManufacturerPUTRequest.get_manufacturer_id(), 
                                                                                             db=self.get_db()
                                                                                          ) 
                                if not insertProductManufacturer.execute():                                           
                                    self.set_status_code(insertProductManufacturer.get_error_code())
                                    self.set_body(insertProductManufacturer.get_error_message(), True)
                            else:   
                                self.set_status_code(400)
                                self.set_body(insertManufacturer.get_error_message(), True)   
                        elif checkManufacturerPUTRequest.get_update_manufacturer():      
                            # Atualiza o fabricante do produto... 
                            updateManufacturer = manu.UpdateManufacturer(  manufacturer_id=checkManufacturerPUTRequest.get_manufacturer_id(),
                                                                           manufacturer_name=checkManufacturerPUTRequest.get_manufacturer_name(), 
                                                                           db=self.get_db()
                                                                            )
                            if not updateManufacturer.execute():
                                self.set_status_code(updateManufacturer.get_error_code())
                                self.set_body(updateManufacturer.get_error_message(), True)      
                    else:   
                        self.set_status_code(400)
                        self.set_body(checkManufacturerPUTRequest.get_error_message(), True)   
                               
                    # Response...
                    if self.get_status_code() == 200: 
                        body = checkPUTRequest.get_request()
                        body['id'] = insertProduct.get_primary_key()['id']
                        body['manufacturer']['id'] = checkManufacturerPUTRequest.get_manufacturer_id()
                        body['manufacturer']['name'] = checkManufacturerPUTRequest.get_manufacturer_name()    
                        self.set_body(body) # Atualiza
                                    
                else:   
                    self.set_status_code(insertProduct.get_error_code())
                    self.set_body(insertProduct.get_error_message(), True)   
                      
            else:   
                self.set_status_code(checkPUTRequest.get_error_code())
                self.set_body(checkPUTRequest.get_error_message(), True)   
                
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
            checkPOSTRequest = prod.CheckProductPOSTRequest(body=self.get_body(), db=self.get_db())
            if checkPOSTRequest.execute():
                # Alteração...     
                updateProduct = prod.UpdateProduct(  schema=checkPOSTRequest.get_schema(), 
                                                     request=checkPOSTRequest.get_request(), 
                                                     db=self.get_db()
                                                  )                         
                if updateProduct.execute():
                    # Tratamento do fabricante do produto...
                    checkManufacturerPOSTRequest = manu.CheckManufacturerPOSTRequest(body=self.get_body(), db=self.get_db())
                    if checkManufacturerPOSTRequest.execute():
                        if checkManufacturerPOSTRequest.get_insert_manufacturer():
                            # Inclusão do fabricante...                                                      
                            insertManufacturer = manu.InsertManufacturer(  manufacturer_name=checkManufacturerPOSTRequest.get_manufacturer_name(), 
                                                                           db=self.get_db()
                                                                        ) 
                            if insertManufacturer.execute():
                                # Reserva a PK do fabricante incluído...
                                checkManufacturerPOSTRequest.set_manufacturer_id(insertManufacturer.get_primary_key()['id'])                                        
                                # Inclusão do fabricante para o produto...                                                      
                                insertProductManufacturer = manu.InsertProductManufacturer(  product_id=updateProduct.get_primary_key()['id'],
                                                                                             manufacturer_id=checkManufacturerPOSTRequest.get_manufacturer_id(), 
                                                                                             db=self.get_db()
                                                                                          ) 
                                if not insertProductManufacturer.execute():                                           
                                    self.set_status_code(insertProductManufacturer.get_error_code())
                                    self.set_body(insertProductManufacturer.get_error_message(), True) 
                            else:   
                                 self.set_status_code(insertManufacturer.get_error_code())
                                 self.set_body(insertManufacturer.get_error_message(), True)    
                        elif checkManufacturerPOSTRequest.get_update_manufacturer():      
                            # Atualiza o fabricante do produto... 
                            updateManufacturer = manu.UpdateManufacturer(  manufacturer_id=checkManufacturerPOSTRequest.get_manufacturer_id(),
                                                                           manufacturer_name=checkManufacturerPOSTRequest.get_manufacturer_name(), 
                                                                           db=self.get_db()
                                                                           )
                            if not updateManufacturer.execute():                                       
                                self.set_status_code(updateManufacturer.get_error_code())
                                self.set_body(updateManufacturer.get_error_message(), True) 
                        #                               
                        if self.get_status_code() == 200:
                            if checkManufacturerPOSTRequest.get_update_product():
                                # Troca de fabricante do produto...                                                      
                                updateProductManufacturer = manu.UpdateProductManufacturer(  product_id=updateProduct.get_primary_key()['id'],
                                                                                             manufacturer_id=checkManufacturerPOSTRequest.get_manufacturer_id(), 
                                                                                             db=self.get_db()
                                                                                          ) 
                                if not updateProductManufacturer.execute():                                           
                                    self.set_status_code(updateProductManufacturer.get_error_code())
                                    self.set_body(updateProductManufacturer.get_error_message(), True)                                                                          
                                   
                    else:   
                        self.set_status_code(400)
                        self.set_body(checkManufacturerPOSTRequest.get_error_message(), True)      
                               
                    # Response(json encode)...
                    if self.get_status_code() == 200:
                        body = checkPOSTRequest.get_request()
                        body['id'] = updateProduct.get_primary_key()['id']
                        body['manufacturer']['id'] = checkManufacturerPOSTRequest.get_manufacturer_id()
                        body['manufacturer']['name'] = checkManufacturerPOSTRequest.get_manufacturer_name()                                           
                        self.set_body(body) # Atualiza
                                    
                else:   
                    self.set_status_code(updateProduct.get_error_code())
                    self.set_body(updateProduct.get_error_message(), True) 
                           
            else:   
                self.set_status_code(checkPOSTRequest.get_error_code())
                self.set_body(checkPOSTRequest.get_error_message(), True) 
                
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
        checkGETRequest = prod.CheckProductGETRequest(body=self.get_body(), db=self.get_db())
        if checkGETRequest.execute():
            # Consulta...     
            getProduct = prod.GetProduct(  schema=checkGETRequest.get_schema(), 
                                           request=checkGETRequest.get_request(), 
                                           db=self.get_db()
                                        )                         
            if getProduct.execute():
                # Response(json encode)...
                 self.set_body(getProduct.get_request())
            else:   
                self.set_status_code(getProduct.get_error_code())
                self.set_body(getProduct.get_error_message(), True) 
                           
        else:   
            self.set_status_code(checkGETRequest.get_error_code())
            self.set_body(checkGETRequest.get_error_message(), True) 
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
            checkDELRequest = prod.CheckProductDELETERequest(body=self.get_body(), db=self.get_db())
            if checkDELRequest.execute():
                # Exclusão...     
                deleteProduct = prod.DeleteProduct(  schema=checkDELRequest.get_schema(), 
                                                     request=checkDELRequest.get_request(), 
                                                     db=self.get_db()
                                                  )                         
                if deleteProduct.execute():
                    # Tratamento da exclusão(desativação) da associação produto e fabricante...
                    deleteProductManufacturer = manu.DeleteProductManufacturer(  product_id=deleteProduct.get_primary_key()['id'],
                                                                                 db=self.get_db()
                                                                              ) 
                    if not deleteProductManufacturer.execute():                                           
                        self.set_status_code(deleteProductManufacturer.get_error_code())
                        self.set_body(deleteProductManufacturer.get_error_message(), True) 
                    else:                              
                        # Response(json encode)...
                        body = checkDELRequest.get_request()
                        body['id'] = deleteProduct.get_primary_key()['id']                                   
                        self.set_body(body) # Atualiza
                else:   
                    self.set_status_code(deleteProduct.get_error_code())
                    self.set_body(deleteProduct.get_error_message(), True) 
                           
            else:   
                self.set_status_code(checkDELRequest.get_error_code())
                self.set_body(checkDELRequest.get_error_message(), True) 
                
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