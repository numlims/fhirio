# fhirio

read and write fhir resources.

```
import fhirio
entries = fhirio.read_entries("my/input/dir")
```

api doc [here](https://numlims.github.io/fhirio/).


## install

download fhirio whl from
[here](https://github.com/numlims/fhirio/releases). install whl with
pip:

```
pip install fhirio-<version>.whl
```

reference from your `pyproject.toml`, e.g.:

```
dependencies = [
  "fhirio @ git+https://github.com/numlims/fhirio.git"
]
```


## dev

edit [`fhirio/main.ct`](./fhirio/main.ct) and [`fhirio/init.ct`](./fhirio/init.ct).

generate the code from ct with [ct](https://github.com/tnustrings/ct) or [ct for vscode](https://marketplace.visualstudio.com/items?itemName=tnustrings.codetext).

build and install:

```
make install
```

test:

```
make test
```


generate api doc:

```
make doc
```


