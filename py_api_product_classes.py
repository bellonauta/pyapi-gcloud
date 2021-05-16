#--------------------------------------------------------------------
# Responde as solicitações da API REST para operações de
# manutenção e consulta de produtos.
#--------------------------------------------------------------------

import json
from typing import Union
import jsonschema
from jsonschema import validate

import py_api_consts as cts
import py_api_functions as fns               
import py_api_classes as cls          

class CheckProductPUTRequest(cls.CheckRequest):
    """ Checagem do request para PUT(Inclusão de produto). """
    
    def __init__(self, body:Union[str,dict], db:cls.DatabaseInterface):
        super().__init__(httpMethod=cts._PUT, body=body, db=db) 
        
        # Importa o schema json de validação do request...
        self.__schema = cts._INSERT_PRODUCT_JSON_SCHEMA         
        
    def get_schema(self) -> dict:        
        return self.__schema        
            
    def check(self):
        """ Implementação da validação dos atributos do request. """
        if super().check():
            try:
                 validate(instance=self.get_request(), schema=self.get_schema())
            except jsonschema.exceptions.ValidationError as err:
                 self.set_error('Request inválido. [{}]'.format(err.message))
        #
        return not self.get_error() 
    
class CheckProductPOSTRequest(cls.CheckRequest):
    """ Checagem do request para POST(Alteração de produto). """
    
    def __init__(self, body:Union[str,dict], db:cls.DatabaseInterface):
        super().__init__(httpMethod=cts._POST, body=body, db=db) 
        
        # Importa o schema json de validação do request...
        self.__schema = cts._UPDATE_PRODUCT_JSON_SCHEMA         
        
    def get_schema(self) -> dict:        
        return self.__schema
            
    def check(self):
        """ Implementação da validação dos atributos do request. """
        try:
            validate(instance=self.get_request(), schema=self.get_schema())
        except jsonschema.exceptions.ValidationError as err:
            self.set_error('Request inválido. [{}]'.format(err.message))
        #
        return not self.get_error()   
   

class CheckProductDELETERequest(cls.CheckRequest):
    """ 
    Checagem do request para DELETE(Exclusão de produto). 
    OBS: Um produto nunca é excluído, ele somente é desativado.
    """    
    
    def __init__(self, body:Union[str,dict], db:cls.DatabaseInterface):
        super().__init__(httpMethod=cts._DEL, body=body, db=db) 
        
        # Importa o schema json de validação do request...
        self.__schema = cts._DELETE_PRODUCT_JSON_SCHEMA         
        
    def get_schema(self) -> dict:        
        return self.__schema
            
    def check(self):
        """ Implementação da validação dos atributos do request. """
        try:
            validate(instance=self.get_request(), schema=self.get_schema())
        except jsonschema.exceptions.ValidationError as err:
            self.set_error('Request inválido. [{}]'.format(err.message))
        #
        return not self.get_error()       
    
class CheckProductGETRequest(cls.CheckRequest):
    """ 
    Checagem do request para GET(Consultas/Queries). 
    """    
    
    def __init__(self, body:Union[str,dict], db:cls.DatabaseInterface):
        super().__init__(httpMethod=cts._GET, body=body, db=db) 
        
        # Importa o schema json de validação do request...
        self.__schema = cts._GET_PRODUCT_JSON_SCHEMA         
        
    def get_schema(self) -> dict:        
        return self.__schema
            
    def check(self):
        """ Implementação da validação dos atributos do request. """
        try:
            validate(instance=self.get_request(), schema=self.get_schema())
        except jsonschema.exceptions.ValidationError as err:
            self.set_error('Request inválido. [{}]'.format(err.message))            
        #
        return not self.get_error()               

#---------------------------------------------------------------------------------------    

class InsertProduct(cls.InsertMasterRecord):
    """ Classe para inserção(PUT) de produtos no banco. """

    def __init__(self, schema:dict, request:dict, db:cls.DatabaseInterface):
          super().__init__(schema=schema, request=request, db=db)
        
    def execute(self):           
        if super().execute():                  
            fieldValues = {'active': cts._YES} # Marca o produto como ativo na inclusão
         
            # Lê os atributos do schema e faz relay para os campos da tabela...           
            for a in self.get_schema()['properties'].keys():
                if a != 'id' and a != 'manufacturer':
                    # Desvia do "id" que é PK auto-incremento e do "manufacturer" que é tratado em outra classe.
                    # --> Com um framework e dicionário de dados isso seria automático.
                    fieldValues[a] = self.get_request()[a]
                 
            # Tenta incluir(Com retorno do novo ID no sufix.)...
            self.get_db().insert(  table='product', 
                                   fields=fieldValues, 
                                   sufix='RETURNING id;'
                                )        
            if self.get_db().get_error():
                self.set_error(self.get_db().get_error_message())    
            else:
                # Reserva a chave primária criada na inclusão...                
                self.set_primary_key({'id': self.get_db().get_rows()[0]})                              
        #    
        return not self.get_error()                     
    
class UpdateProduct(cls.UpdateMasterRecord):
    """ Classe para atualização(POST) de produtos no banco. """

    def __init__(self, schema:dict, request:dict, db:cls.DatabaseInterface):
          super().__init__(schema=schema, request=request, db=db)
        
    def execute(self):             
        if super().execute():                
            fieldValues = {}
            pk = { 'id': self.get_request()['id'] }
         
            # Lê os atributos do schema e faz relay para os campos da tabela...
            for a in self.get_schema()['properties'].keys():
                if a != 'id' and a != 'manufacturer':
                    # Desvia do "id" que é PK auto-incremento e do "manufacturer" que é tratado em outra classe.
                    # --> Com um framework e dicionário de dados isso seria automático.
                    fieldValues[a] = self.get_request()[a]
                 
            # Tenta atualizar...
            self.get_db().update(  table='product', 
                                   pk=pk,
                                   fields=fieldValues
                                )        
            if self.get_db().get_error():
                self.set_error(self.get_db().get_error_message(), (404 if self.get_db().key_not_found() else 400))    
            else:
                # Reserva a chave primária alterada...
                self.set_primary_key(pk)                              
        #    
        return not self.get_error()                         
    
class DeleteProduct(cls.DeleteMasterRecord):
    """
    Classe para exclusão(POST) de produtos no banco.
    OBS: O produto não é excluído, somente marcado como desativado.
    """
    
    def __init__(self, schema:dict, request:dict, db:cls.DatabaseInterface):
          super().__init__(schema=schema, request=request, db=db)
        
    def execute(self):                             
        fieldValues = {'active': cts._NO} # Marca o produto como inativo na exclusão            
        # Lê a PK no request...
        pk = { 'id': self.get_request()['id'] }                
        # Tenta atualizar...
        self.get_db().update(  table='product', 
                               pk=pk,
                               fields=fieldValues
                            )        
        if self.get_db().get_error():
            self.set_error(self.get_db().get_error_message(), (404 if self.get_db().key_not_found() else 400))     
        else:
            # Reserva a chave primária excluída(desativada)...
            self.set_primary_key(pk)                              
        #    
        return not self.get_error()                             
    
class GetProduct(cls.GetMasterRecord):
    """
    Classe para consultas(GET) de produtos no banco.
    """    
    def __init__(self, schema:dict, request:dict, db:cls.DatabaseInterface):
          # Define o filtro da consulta pela presença e valor do atributo "id" no request...
          # 'id' = 0 ou ausente implicará em listagem de todos os produtos, senão retornará detalhes de um produto. 
          if 'id' not in request.keys():
               request['id'] = 0 # Listagem. Se houver ID informado retornará detalhes de um produto.             
          else: 
               request['id'] = max(0, int(request['id']))  # Conversão   
          #
          if 'page' not in request.keys():
               request['page'] = 1
          else: 
               request['page'] = max(1, int(request['page']))  # Conversão     
          # Order...     
          if 'order' not in request.keys():
               request['order'] = 'id' # Ordem padrão de classificação da consulta.       
          #    
          super().__init__(schema=schema, request=request, db=db)              
        
    def execute(self):        
        getType = 'L' # Listagem é default
        parameters = {'id': self.get_request()['id'], 'active': cts._YES}
        #
        # Define o tipo da consulta...        
        #  OBS: Num ambiente profissional, já existirá uma padronização/metodologia para
        #       a nomenclatura das coluna do SELECT. Usarei no momento, a mais básica possível.
        #       E certamente também já existirá até um framework/biblioteca que automatize isso tudo.   
        #       Mas se nada disso existir, desenvolvemos também, se preciso for!    
        if self.get_request()['id'] == 0:
            # Listagem(Paginada)...        
            order = self.get_request()['order'].strip().lower()                                              
            sql = ('SELECT id, name '+
                   'FROM product '+
                   'WHERE id > %(id)s AND active = %(active)s '+
                   'ORDER BY ' + ('id' if self.get_request()['order'] == '' else self.get_request()['order']) +' '+
                   'LIMIT '+ fns.to_str(cts._QRY_PAGE_ROWS_LIMIT) +' OFFSET '+ fns.to_str((self.get_request()['page']-1) * cts._QRY_PAGE_ROWS_LIMIT))            
        else:
            # Detalhes...                 
            getType = 'D'
            sql = ('SELECT product.id, product.name AS product_name, product.description, '+
                          'product.barcode, product.unitprice, product.active, '+
                          'manufacturer.id AS manufacturer_id, manufacturer.name AS manufacturer_name '+
                   'FROM product'+
                   
                   ' INNER JOIN productmanufacturer'+
                      ' ON productmanufacturer.product_id = product.id'+
                     ' AND productmanufacturer.active = %(active)s'+
                     
                       ' INNER JOIN manufacturer'+
                          ' ON manufacturer.id = productmanufacturer.manufacturer_id '+  
                          
                   'WHERE product.id = %(id)s') 
        #
        self.get_db().query(sql=sql, pars=parameters, commit=True) 
        if (self.get_db().get_error()):
            self.set_error(self.get_db().get_error_message())
        else:
            # Prepara o objeto de retorno...
            request = self.get_request()
            request['maxRowsPerPage'] = cts._QRY_PAGE_ROWS_LIMIT
            request['rows'] = []
            for row in self.get_db().get_rows():
                if getType == 'L':
                    request['rows'].append({
                          'id': row['id'],
                        'name': row['name']
                    })                                           
                else:
                    request['rows'].append({
                          "id": row["id"],
                          "name": row["product_name"],
                          "description": row["description"],
                          "barcode": row["barcode"],
                          "manufacturer": {
                                "id": row["manufacturer_id"],
                                "name": row["manufacturer_name"],
                          },
                          "unitPrice": float(row["unitprice"]),
                          "active": "Yes" if row["active"] == cts._YES else 'No',
                    })     
            #
            # Atualiza o request com as propriedades/atributos para retorno da consulta...
            self.set_request(request)                            
        #    
        return not self.get_error()      
#--------------------------------------------------------------------------------------    