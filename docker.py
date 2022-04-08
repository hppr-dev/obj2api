from api import create_api
from docker import from_env
from docker.models.containers import Container 

e = from_env()

encoders = {
    Container: lambda c: c.attrs
}

app = create_api(e, exclude=['from_env'], encoders=encoders)
