# Building Plan Extraction

This is a REST API for processing and extracting information out of building plans (dxf-files).

<br/>

**Used technologies:** Redis Pub/Sub, Docker Compose, Flask, Numpy, Shapely, EZDXF, Flask-Testing, Matplotlib, Jupyter NB, Loguru, Reportlab

<br/>

## Usage

To install a redis conainer (docker required), run:

```sh
cd infrastructure
docker-compose up -d
```

To start the application, run:

```sh
pip install pipenv
pipenv install && pipenv run flask run
```

For testing the API, run:

```sh
curl http://localhost:5010/api/v1/example/
```

The available endpoints can be retrieved from the postman export. To use the export, import it to postman and change the variable ` project_path` accordingly.
