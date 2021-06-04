# *------------------------------------------------------------------*
# *  Biblioteca de funções base para a API.                          *  
# *------------------------------------------------------------------*

import json

def is_empty(v) -> bool:
    """Retorna True quando "v" estiver vazia(o) ou não inicializado, conforme seu tipo."""
    tip = type(v)
    return ( v is None or
              (tip is str and v.strip() == '') or 
              ( (tip is list or tip is set or tip is tuple or tip is dict) and len(v) <= 0 ) 
           ) 
    
def dict_merge(d1:dict, d2:dict) -> dict:
    """
    Junta dois dicionários e retorna.
    As chaves iguais são atualizadas com os valores em d2.
    """
    ret = None
    if type(d1) is dict and type(d2) is dict:
        ret = d1.copy() 
        ret.update(d2)  
    #
    return ret    

def implode(separador:str=',', lista:list=[]) -> list:
    """
    Une os itens de uma lista em uma string separados por separador.
    """
    if type(lista) is list or type(lista) is tuple or type(lista) is set:
        return separador.join(to_str(lista))
    else:
        return lista
   
def to_str(val,def_val:str='') -> str: 
    """
    Retorna val convertido para string.
     val - Um int/float/bool ou uma list
     def_val - Retorna quando for vazio ou houver erro na conversão.
    """   
    if val is None:
        ret = '' 
    elif type(val) is str:
        ret = val  
    elif not type(val) is str:
        if type(val) is list or type(val) is tuple or type(val) is set:
            ret = val[:] # Listas são mutáveis
            # Converte os itens da lista para string...
            for v in range(len(ret)):
                ret[v] = to_str(ret[v])
        elif type(val) is bool:
            ret = 'true' if val else 'false' 
        else:        
            try:           
                ret = str(val)  
            except Exception:        
                ret = def_val
    #         
    return (ret if len(ret) > 0 and (not type(ret) is str or ret.strip() != '') else def_val)     

def get_cmd_arg(args:list, argname:str, default=None):   
    """
    Retorna o valor de um argumento/parâmetro contido na lista passada para o script.            
    Args:
        args (list): Argumentos recebidos pelo script(sys.argv).
        argname (str): Nome do argumento a retornar.
        default (any, optional): Valor a retornar quando argumento não encontrado no array. Defaults to None.
    Returns:
        mixed: Valor do argumento ou, se argumento não encontrado, o valor em default
    """       
    ret = default
    argname = argname.strip()
    if type(args) is list and len(args) > 0 and argname != '':
        for arg in args:
           if type(arg) is str: 
               arg = arg.strip()         
               if arg != '' and arg[0:len(argname)+1] == argname+'=':     
                   ret = arg[len(argname)+1:].strip()
                   break
    #           
    return ret