#--------------------------------------------------------------------
# Responde as solicitações da API REST para operações de
# manutenção e consulta de fabricantes.
#--------------------------------------------------------------------

import json
from typing import Union
import jsonschema
from jsonschema import validate

import py_api_consts as cts
import py_api_functions as fns               
import py_api_classes as cls          

class CheckManufacturerPUTRequest(cls.CheckRequest):
    """
    Checagem do request para PUT(Inclusão de fabricante).
    A inclusão do fabricante estará associada ao request
    de inclusão do produto e causa uma implementação
    específica no método "execute".
    """
    
    def __init__(self, body:Union[str,dict], db: cls.DatabaseInterface):
        super().__init__(httpMethod=cts._PUT, body=body, db=db) 
                
        self.__manufacturer_id = 0
        self.__manufacturer_name = ""
                   
        self.__insert_manufacturer = False  
        self.__update_manufacturer = False                  
        
        self.__schema = cts._INSERT_PRODUCT_JSON_SCHEMA 
        
    def get_schema(self) -> dict:        
        return self.__schema    
    
    def get_insert_manufacturer(self):    
        """Retornará True quando um fabricante deva ser incluído no cadastro."""
        return self.__insert_manufacturer    
    
    def get_update_manufacturer(self):      
        """Retornará True quando um fabricante deva ser atualizado no cadastro."""          
        return self.__update_manufacturer  
    
    def set_manufacturer_id(self, value:int):
        self.__manufacturer_id = value
    def get_manufacturer_id(self):
        return self.__manufacturer_id 
        
    def get_manufacturer_name(self):
        return self.__manufacturer_name 
            
    def check(self):
        """ Implementação da validação dos atributos do request. """
        super().check()
        #
        if not self.get_error():
            # Validação do request pelo schema...
            try:
                validate(instance=self.get_request(), schema=self.get_schema())
            except jsonschema.exceptions.ValidationError as err:
                self.set_error('Request com schema inválido. [{}]'.format(err.message))     
            #
            if not self.get_error():          
                # Verifica se o "id" ou o "name" do fabricante foram informados...
                manufacturerKeys = self.get_request()['manufacturer'].keys() if 'manufacturer' in self.get_request().keys() else {}
                #
                if 'id' not in manufacturerKeys and 'name' not in manufacturerKeys: 
                     self.set_error('Fabricante não informado(Informe o "id" ou o "name" ou ambos).')
                else:                                                     
                     # Verifica a existência cadastral do fabricante do produto pela
                     # presença do atributo "id" do fabricante...
                     if 'id' in self.get_request()['manufacturer'].keys():
                          # Fabricante já deveria estar cadastrado - Verifica...
                          # (O SQL também seria automático com a utilização de um dicionário de dados ou framework.)
                          self.get_db().query(  sql='SELECT name FROM manufacturer WHERE id = %(id)s',
                                                pars={ 
                                                        'id': self.get_request()['manufacturer']['id']
                                                     },
                                                commit=False                                              
                                             )                          
                          #
                          if self.get_db().get_error():   
                              # Erro 
                              self.set_error(self.get_db().get_error_message())
                          elif len(self.get_db().get_rows()) == 0:
                              # Fabricante com "id" não cadastrado - Erro... 
                              self.set_error('Fabricante não cadastrado(id={})'.format(self.get_request()['manufacturer']['id'])) 
                          else:
                              # Reserva o "id" e o "name" do fabricante informado no request...
                              self.__manufacturer_id = self.get_request()['manufacturer']['id']                             
                              self.__manufacturer_name = self.get_db().get_rows()[0]['name']                        
                          #     
                     elif 'id' not in manufacturerKeys and 'name' in manufacturerKeys: 
                          # "id" não informado mas "name" informado - Marca para cadastrar o fabricante... 
                          self.__insert_manufacturer = True  
                     elif 'id' in manufacturerKeys and 'name' in manufacturerKeys: 
                          # "id" e "name" informados - Marca para atualizar o fabricante... 
                          self.__update_manufacturer = True
                          # Reserva o "id" do fabricante informado no request...
                          self.__manufacturer_id = self.get_request()['manufacturer']['id']            
                     #
                     # Reserva o nome do fabricante informado no request...
                     if not self.get_error() and 'name' in manufacturerKeys: 
                         self.__manufacturer_name = self.get_request()['manufacturer']['name']                                                                                                                              
            #             
        #                        
        return not self.get_error()         
    
class CheckManufacturerPOSTRequest(cls.CheckRequest):
    """
    Checagem do request para POST(Alteração de fabricante).
    A alteração do fabricante estará associada ao request
    de alteração do produto e causa uma implementação
    específica no método "execute".
    """
    
    def __init__(self, body:Union[str,dict], db:cls.DatabaseInterface):
        super().__init__(httpMethod=cts._POST, body=body, db=db) 
        
        self.__manufacturer_id = 0
        self.__manufacturer_name = ""

        self.__update_product = False        
        self.__insert_manufacturer = False  
        self.__update_manufacturer = False
        
        self.__schema = cts._UPDATE_PRODUCT_JSON_SCHEMA             
     
        
    def get_schema(self) -> dict:        
        return self.__schema    
    
    def get_insert_manufacturer(self) -> bool:    
        """Retornará True quando um fabricante deva ser incluído no cadastro."""
        return self.__insert_manufacturer    
    
    def get_update_manufacturer(self) -> bool:        
        """Retornará True quando um fabricante deva ser atualizado no cadastro."""          
        return self.__update_manufacturer  
    
    def get_update_product(self) -> bool:        
        """Retornará True quando um produto deva ter seu fabricante alterado no cadastro."""          
        return self.__update_product    
    
    def set_manufacturer_id(self, value:int):
        self.__manufacturer_id = value
    def get_manufacturer_id(self):
        return self.__manufacturer_id 
        
    def get_manufacturer_name(self):
        return self.__manufacturer_name 
            
    def check(self):
        """ Implementação da validação dos atributos do request. """
        super().check()
        #
        if not self.get_error():
            # Validação do request pelo schema...
            try:
                validate(instance=self.get_request(), schema=self.get_schema())
            except jsonschema.exceptions.ValidationError as err:
                self.set_error('Request com schema inválido. [{}]'.format(err.message))       
            #
            if not self.get_error():          
                # Verifica se o "id" ou o "name" do fabricante foram informados...
                manufacturerKeys = self.get_request()['manufacturer'].keys() if 'manufacturer' in self.get_request().keys() else {}
                #                                                         
                # Verifica a existência cadastral do fabricante do produto pela
                # presença do atributo "id" do fabricante...
                if 'id' in self.get_request()['manufacturer'].keys(): 
                     # Fabricante já deveria estar cadastrado - Verifica...
                     self.get_db().query(  sql='SELECT name FROM manufacturer WHERE id = %(id)s',
                                           pars={ 
                                                   'id': self.get_request()['manufacturer']['id']
                                                },
                                           commit=False                                              
                                        )                       
                     #
                     if self.get_db().get_error():   
                         # Erro 
                         self.set_error(self.get_db().get_error_message())
                     elif len(self.get_db().get_rows()) == 0:
                         # Fabricante não cadastrado - Erro... 
                         self.set_error('Fabricante não cadastrado(id={})'.format(self.get_request()['manufacturer']['id'])) 
                     else:
                         # Reserva o "id" e o "name" do fabricante informado no request...
                         self.__manufacturer_id = self.get_request()['manufacturer']['id']                             
                         self.__manufacturer_name = self.get_db().get_rows()[0]['name']                                                         
                     #                             
                elif 'id' not in manufacturerKeys and 'name' in manufacturerKeys: 
                     # "id" não informado mas "name" informado - Marca para cadastrar o fabricante... 
                     self.__insert_manufacturer = True  
                elif 'id' in manufacturerKeys and 'name' in manufacturerKeys: 
                     # "id" e "name" informados - Marca para atualizar o fabricante... 
                     self.__update_manufacturer = True
                     # Reserva o "id" do fabricante informado no request...
                     self.__manufacturer_id = self.get_request()['manufacturer']['id']            
                #
                if not self.get_error():
                    # Reserva o nome do fabricante informado no request...
                    if 'name' in manufacturerKeys: 
                         self.__manufacturer_name = self.get_request()['manufacturer']['name']                                                                                                                                                       
                    #
                    if not self.__insert_manufacturer:
                       # Verifica se ainda é o mesmo fabricante já associado ao produto. Se não for, troca...
                       self.get_db().query(   sql='SELECT manufacturer_id FROM productmanufacturer WHERE product_id = %(id)s',
                                              pars={ 
                                                      'id': self.get_request()['id']
                                                   },
                                              commit=False                                              
                                          )                       
                       #
                       if self.get_db().get_error():   
                          # Erro 
                          self.set_error(self.get_db().get_error_message())
                       elif len(self.get_db().get_rows()) == 0:
                          self.set_error('Produto sem fabricante associado(product_id={})'.format(self.get_request()['id'])) 
                       elif self.get_db().get_rows()[0]['manufacturer_id'] != self.get_request()['manufacturer']['id']:
                          # Marca para trocar o fabricante do produto...
                          self.__update_product = True                                                            
                #             
        #                        
        return not self.get_error()             
    
class CheckManufacturerGETRequest(cls.CheckRequest):
    """ 
    Checagem do request para GET(Consultas/Queries) de fabricantes. 
    """    
    
    def __init__(self, body:Union[str,dict], db:cls.DatabaseInterface):
        super().__init__(httpMethod=cts._GET, body=body, db=db) 
        
        # Importa o schema json de validação do request...
        self.__schema = cts._GET_MANUFACTURER_JSON_SCHEMA         
        
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
    
#----------------------------------------------------------------------------------------------     

class InsertManufacturer(cls.InsertDetailRecord):
    """ Classe para inserção(PUT) de fabricantes de produtos no banco. """
    
    def __init__(self, manufacturer_name:str, db:cls.DatabaseInterface):
        super().__init__(db=db)
        #
        self.__manufacturer_name = manufacturer_name
         
    def execute(self):                  
        """ Inclusão de fabricante. """
         # Tenta incluir...
        if super().execute():           
            self.get_db().insert(  table='manufacturer', 
                                   fields={'name': self.__manufacturer_name}, 
                                   sufix='RETURNING id'
                                )        
            if self.get_db().get_error():
                self.set_error(self.get_db().get_error_message())    
            else:
                # Reserva a chave primária criada na inclusão...
                self.set_primary_key({'id':self.get_db().get_rows()[0]})                              
        #    
        return not self.get_error()    
            
         
class UpdateManufacturer(cls.UpdateDetailRecord):
    """ Classe para atualização(POST) de fabricantes de produtos no banco. """
    
    def __init__(self, manufacturer_id:int, manufacturer_name:str, db:cls.DatabaseInterface):
         super().__init__(db=db)
         #
         self.__manufacturer_id = manufacturer_id
         self.__manufacturer_name = manufacturer_name
         
    def execute(self):                           
        """ Atualização de fabricante. """        
        # Tenta alterar...
        if super().execute():
            pk = { 'id': self.__manufacturer_id }
            self.get_db().update(  table='manufacturer', 
                                   pk=pk,
                                   fields={ 'name': self.__manufacturer_name }
                                )        
            if self.get_db().get_error():
                self.set_error(self.get_db().get_error_message(), (404 if self.get_db().key_not_found() else 400))      
            else:
                # Reserva a chave primária alterada...
                self.set_primary_key(pk)                              
        #    
        return not self.get_error()        
    
class GetManufacturer(cls.GetDetailRecord):
    """
    Classe para consultas(GET) de fabricantes no banco.
    """    
    def __init__(self, schema:dict, request:dict, db:cls.DatabaseInterface):
          # Define o filtro da consulta pela presença e valor do atributo "id" no request...
          # 'id' = 0 ou ausente implicará em listagem de todos os fabricantes, senão retornará detalhes de um fabricante. 
          if 'id' not in request.keys():
               request['id'] = 0 # Listagem. Se houver ID informado retornará detalhes de um fabricante.             
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
        # Define o tipo da consulta...        
        #  OBS: Num ambiente profissional, já existirá uma padronização/metodologia para
        #       a nomenclatura das coluna do SELECT. Usarei no momento, a mais básica possível.
        #       E certamente também já existirá até um framework/biblioteca que automatize isso tudo.   
        #       Mas se nada disso existir, desenvolvemos também, se preciso for!    
        if self.get_request()['id'] == 0:
            # Listagem(Paginada)...        
            order = self.get_request()['order'].strip().lower()                                              
            sql = ('SELECT id, name '+
                   'FROM manufacturer '+
                   'WHERE id > %(id)s '+
                   'ORDER BY ' + ('id' if order == '' else order) +' '+
                   'LIMIT '+ fns.to_str(cts._QRY_PAGE_ROWS_LIMIT) +' OFFSET '+ fns.to_str((self.get_request()['page']-1) * cts._QRY_PAGE_ROWS_LIMIT))            
        else:
            # Detalhes...                 
            sql = ('SELECT id, name '+
                   'FROM manufacturer '+                          
                   'WHERE id = %(id)s') 
        #
        self.get_db().query(sql=sql, pars={'id': self.get_request()['id']}, commit=True) 
        if (self.get_db().get_error()):
            self.set_error(self.get_db().get_error_message())
        else:
            # Prepara o objeto de retorno...
            request = self.get_request()
            request['maxRowsPerPage'] = cts._QRY_PAGE_ROWS_LIMIT
            request['rows'] = []
            for row in self.get_db().get_rows():
                request['rows'].append({
                     'id': row['id'],
                     'name': row['name']
                })                                           
            #
            # Atualiza o request com as propriedades/atributos para retorno da consulta...
            self.set_request(request)                            
        #    
        return not self.get_error()            
    
#--------------------------------------------------------------------------------------------------                                
         
class InsertProductManufacturer(cls.InsertDetailRecord):
    """ Classe para inserção(PUT) de fabricantes POR produtos no banco. """
    
    def __init__(self, product_id:int, manufacturer_id:int, db:cls.DatabaseInterface):
         super().__init__(db=db)
         #
         self.__product_id = product_id
         self.__manufacturer_id = manufacturer_id
           
    def execute(self):       
        if super().execute(): 
            # Primeiro desativa(se já existir) a associação atual...
            self.get_db().update(  table='productmanufacturer', 
                                   pk={ 'product_id': self.__product_id },
                                   fields={ 'active': cts._NO }
                                )                    
            if self.get_db().get_error() and not self.get_db().key_not_found(): 
                self.set_error(self.get_db().get_error_message())    
            else:
                # Por fim, insere a nova associação...   
                fields = { 
                            'product_id': self.__product_id, 
                            'manufacturer_id': self.__manufacturer_id,
                            'active': cts._YES
                         }        
                self.get_db().insert(  table='productmanufacturer', 
                                       fields=fields                              
                                    )        
                #
                if self.get_db().get_error():
                    self.set_error(self.get_db().get_error_message())    
                else:
                    # Reserva a chave primária...
                    self.set_primary_key({ 
                                            'product_id': self.__product_id,
                                            'manufacturer_id': self.__manufacturer_id
                                         })                              
        #    
        return not self.get_error()       
    
class UpdateProductManufacturer(cls.UpdateDetailRecord):
    """ Classe para atualização/troca(POST) do fabricante de um produto no banco. """
    
    def __init__(self, product_id:int, manufacturer_id:int, db:cls.DatabaseInterface):
         super().__init__(db=db)         
         #
         self.__product_id = product_id
         self.__manufacturer_id = manufacturer_id
         
    def execute(self):                           
        """ Troca do fabricante do produto. """        
        # Tenta alterar...
        if super().execute():         
            # Primeiro desativa a associação atual...
            self.get_db().update(  table='productmanufacturer', 
                                   pk={ 'product_id': self.__product_id },
                                   fields={ 'active': cts._NO }
                                )        
            if self.get_db().get_error():
                self.set_error(self.get_db().get_error_message(), (404 if self.get_db().key_not_found() else 400))      
            else:
                # Por fim, insere a nova associação...
                self.get_db().insert(  table='productmanufacturer', 
                                       fields={ 
                                                 'product_id': self.__product_id,
                                                 'manufacturer_id': self.__manufacturer_id,
                                                 'active': cts._YES
                                              }
                                    )        
                if self.get_db().get_error():
                    self.set_error(self.get_db().get_error_message())     
                else:
                    # Reserva a chave primária...
                    self.set_primary_key({ 
                                            'product_id': self.__product_id,
                                            'manufacturer_id': self.__manufacturer_id
                                         })                                
        #    
        return not self.get_error()                     
    
class DeleteProductManufacturer(cls.DeleteDetailRecord):
    """ Classe para exclusão(DELETE) da associação produto e fabricante. """
    
    def __init__(self, product_id:int, db:cls.DatabaseInterface):
         super().__init__(db=db)         
         #
         self.__product_id = product_id
         
    def execute(self):                           
        """ 
        Exclusão da associação produto e fabricante.
        OBS: A associação não é excluída, somente desativada.
        """        
        # Tenta excluir/desativar...
        if super().execute():         
            self.get_db().update(  table='productmanufacturer', 
                                   pk={ 'product_id': self.__product_id, 'active': cts._YES },
                                   fields={ 'active': cts._NO }
                                )        
            if self.get_db().get_error():
                self.set_error(self.get_db().get_error_message(), (404 if self.get_db().key_not_found() else 400))   
            else:
                # Reserva a chave primária(Parcial/Master)...
                self.set_primary_key({ 'product_id': self.__product_id })           
        #    
        return not self.get_error()                            
#--------------------------------------------------------------------------------------------------