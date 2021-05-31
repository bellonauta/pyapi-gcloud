#--------------------------------------------------------------------
# Biblioteca de constantes base para o desafio TOTVS.
#--------------------------------------------------------------------

import json

# Ambiente...
_IN_PRODUCTION = False

# Constantes de conexão com o banco de dados...
_PG_CONNECTION = {
                    'devel': {
                       'host': 'localhost',
                       'port': 5432,
                       'name': 'pyapi',
                       'user': 'postgres',
                        'pwd': 'postgres'
                    },
                    'production': {
                       'host': '35.199.98.84', # Gcloud
                       'port': 5432,
                       'name': 'gcloud',
                       'user': 'postgres',
                        'pwd': '03*1966pggc'
                    }
}                    

# Constantes de estado/situação/atividade...
_YES = 'y'
_NO = 'n'

# Constantes para métodos HTTP...
_GET = 'GET'
_PUT = 'PUT'
_POST = 'POST'
_DEL = 'DELETE'
_HTTP_METHODS = [_GET, _PUT, _POST, _DEL]

# Constantes para queries...
_QRY_PAGE_ROWS_LIMIT = 50

# Schema validador de json esperado nos requests de inclusão(PUT) de produto...
_INSERT_PRODUCT_JSON_SCHEMA = { 
       "type": "object",
       "properties": {
            "id": {"type":"number", "minimum": 1},
            "name": {"type":"string", "minLength": 10, "maxLength": 60},
            "description": {"type":"string"},
            "barcode": {"type":"string"},
            "manufacturer": {
                 "type": "object",
                 "properties": {
                     "id": {"type":"number", "minimum": 1},
                     "name": {"type":"string", "minLength": 10, "maxLength": 60},
                 }
            }, 
            "unitPrice": {"type":"number", "minimum": 0.01,  "maximum": 9999999999.99}  # (11,2)
       },    
       "required": ["name","description","barcode","manufacturer","unitPrice"]       
} 

# Schema validador de json esperado nos requests de alteração(POST) de produto...
_UPDATE_PRODUCT_JSON_SCHEMA = { 
       "type": "object",
       "properties": {
            "id": {"type":"number", "minimum": 1},
            "name": {"type":"string", "minLength": 10, "maxLength": 60},
            "description": {"type":"string"},
            "barcode": {"type":"string"},
            "manufacturer": {
                 "type": "object",
                 "properties": {
                     "id": {"type":"number", "minimum": 1},
                     "name": {"type":"string", "minLength": 10, "maxLength": 60},
                 }
            }, 
            "unitPrice": {"type":"number", "minimum": 0.01,  "maximum": 9999999999.99}  # (11,2)
       },    
       "required": ["id"]
}   

# Schema validador de json esperado nos requests de exclusão(DELETE) de produto...
_DELETE_PRODUCT_JSON_SCHEMA = { 
       "type": "object",
       "properties": {
            "id": {"type":"number", "minimum": 1}
       },
       "required": ["id"]         
}         

# Schema validador de json esperado nos requests de consulta(GET) de produto...
_GET_PRODUCT_JSON_SCHEMA = { 
       "type": "object",
       "properties": {
            "id": {"type":"string", "pattern": "^[0-9]+$"},
            "page": {"type":"string", "pattern": "^[0-9]+$"},
            "order": {"type":"string", "enum": ["id","name"]}
       },
       "required": []         
}   

#--------------------------------------------------------------------------------

# Schema validador de json esperado nos requests de consulta(GET) de fabricante...
_GET_MANUFACTURER_JSON_SCHEMA = { 
       "type": "object",
       "properties": {
            "id": {"type":"string", "pattern": "^[0-9]+$"},
            "page": {"type":"string", "pattern": "^[0-9]+$"},
            "order": {"type":"string", "enum": ["id","name"]}
       },
       "required": []         
}   