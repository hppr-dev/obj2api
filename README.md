# obj2api

A way to create an api from any abitrary object.

A silly experiment.

## Usage

Serving the docker module:

```
from api import create_api
from docker import from_env

client = from_env()
app = create_api(client)
```

and then run `uvicorn app:app`.

This will serve an api that can be used to interact with docker.

Use the exclude keyword argument to create_api to exclude methods from the api.

Use the root keyword argument to specify a different root for the api. (defaults to '/')

Use the encoders keyword argument to add json encoders to deal with custom types.
