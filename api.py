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

# Delete doesn't work quite right
# I think it has a problem with *args
def DEFAULT_DETERMINATOR(fun_name, fun):
    sig = signature(fun)
    if fun_name in ['delete', 'remove', 'del', 'rm']:
        return 'delete'
    if fun_name in ['get', 'list']:
        return 'get'
    if any(map(lambda p: p[1].kind == Parameter.VAR_KEYWORD or p[1].kind == Parameter.VAR_POSITIONAL, sig.parameters.items())):
        return 'post'
    lines, _ = getsourcelines(fun)
    if any(map(lambda l: 'return' in l, lines)):
        return 'post'
    return 'get'

def create_api(obj, root='/', exclude=[], encoders={}, determinator=DEFAULT_DETERMINATOR):
    __add_encoders__(encoders)
    for public_name in filter(lambda name: name[0] != '_' and not name in exclude, dir(obj)):
        attr = getattr(obj, public_name)
        if ismethod(attr):
            method = __wrapped_method__(attr)
            endpoints[f'{root}{public_name}'] = create_endpoint(public_name, method, root=root, determinator=determinator)
        elif callable(attr):
            create_api(attr, root=f'/{public_name}/')
    return app

def create_endpoint(fun_name, method, root, determinator):
    path = f'{root}{fun_name}'
    {
        'post': app.post,
        'get': app.get,
        'put': app.put,
        'delete': app.delete,
        'options': app.options,
        'head': app.head,
        'patch': app.patch,
    }[determinator(fun_name, method)](path)(method)
