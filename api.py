from inspect import getsourcelines, ismethod, signature, Parameter
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from typing import Optional
from pydantic.json import ENCODERS_BY_TYPE

app = FastAPI()
endpoints = {}

def __modify_sig__(sig):
    params = sig.parameters
    for name, param in params.items():
        if param.kind == Parameter.VAR_POSITIONAL:
            params[name]._annotation=Optional[list]
        elif param.kind == Parameter.VAR_KEYWORD:
            params[name]._annotation=Optional[dict]
    return sig

def __wrapped_method__(fun):
    sig = signature(fun)
    def str_fun(*args, **kwargs):
        if 'kwargs' in kwargs:
            kwargs.update(kwargs['kwargs'])
            kwargs.pop('kwargs')
        ret = fun(*args, **kwargs)
        try:
            return jsonable_encoder(ret)
        except Exception as e:
            print(e)
            return repr(ret)
    str_fun.__signature__ = __modify_sig__(sig)
    str_fun.__doc__ = fun.__doc__
    return str_fun

def __add_encoders__(encoders):
    ENCODERS_BY_TYPE.update(encoders)

def create_api(obj, root='/', exclude=[], encoders={}):
    __add_encoders__(encoders)
    for public_name in filter(lambda name: name[0] != '_' and not name in exclude, dir(obj)):
        attr = getattr(obj, public_name)
        if ismethod(attr):
            method = __wrapped_method__(attr)
            endpoints[f'{root}{public_name}'] = create_endpoint(public_name, method, root=root)
        elif callable(attr):
            create_api(attr, root=f'/{public_name}/')
    return app

# Need a good way to figure out which endpoints should be what method
# If they have/need/use kwargs, then it needs to be post or put
def create_endpoint(fun_name, method, root='/'):
    path = f'{root}{fun_name}'
    app.post(path)(method)
