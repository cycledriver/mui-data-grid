# MUI Data Grid

This is an unofficial toolbox to make integrating a Python web application with Material UI's data grid simpler.

## Documentation

- [Material-UI Data Grid](https://mui.com/x/react-data-grid/)

## Requirements

- Python 3.8.1+

## Features

- Grid Sort Model support
- Grid Filter Model support (partial: missing quick filter support)
- Grid Pagination Model support (LIMIT / OFFSET based, cursor not currently supported)
- Flask integration
- SQLAlchemy integration

## Installation

### Pip

```sh
python -m pip install -U 'mui-data-grid'
```

or with extras:

```sh
python -m pip install -U 'mui-data-grid[flask]'
python -m pip install -U 'mui-data-grid[sqlalchemy]'
python -m pip install -U 'mui-data-grid[flask, sqlalchemy]'
```

### Poetry

```sh
poetry add mui-data-grid
```

## Usage

### Integrations

#### Flask

```python
#!/usr/bin/env python
# examples/main.py

from flask import Flask, jsonify
from flask.wrappers import Response

from mui.v5.integrations.flask import get_grid_models_from_request
# for v6 support, replace this import with:
# from mui.v6.integrations.flask import get_grid_models_from_request

app = Flask(__name__)

FILTER_MODEL_KEY = "filter_model"
SORT_MODEL_KEY = "sort_model[]"
PAGINATION_MODEL_KEY = None  # stored inline in the query string, not encoded as an obj


@app.route("/")
def print_sorted_details() -> Response:
    # models will return default values if the keys don't exist,
    # so you can choose what features you integrate, and when.
    models = get_grid_models_from_request(
        filter_model_key=FILTER_MODEL_KEY,
        pagination_model_key=PAGINATION_MODEL_KEY,
        sort_model_key=SORT_MODEL_KEY,
    )
    return jsonify(
        {
            # sort_model is a list[GridSortItem]
            SORT_MODEL_KEY: [model.model_dump() for model in models.sort_model],
            # filter_model is GridFilterModel
            FILTER_MODEL_KEY: models.filter_model.model_dump(),
            # pagination_model is a GridPaginationModel
            # providing a consistent interface to pagination parameters
            PAGINATION_MODEL_KEY: models.pagination_model,
        }
    )


if __name__ == "__main__":
    app.run()
```

#### SQLAlchemy

```python
    # please see examples/main.py for the full code
    models = get_grid_models_from_request(
        filter_model_key=FILTER_MODEL_KEY,
        pagination_model_key=PAGINATION_MODEL_KEY,
        sort_model_key=SORT_MODEL_KEY,
    )
    session = Session()
    try:
        base_query = session.query(ExampleModel)
        dg_query = apply_request_grid_models_to_query(
            query=base_query,
            request_model=models,
            column_resolver=example_model_resolver,
        )
        # we calculate total separately so that we can reuse the result
        # rather than have .pages() fire off an additional db query.
        total = dg_query.total()
        def item_factory(item: ExampleModel) -> Dict[str, int]:
            return item.model_dump()
        return jsonify(
            {
                "items": dg_query.items(factory=item_factory),
                "page": dg_query.page,
                "pageSize": dg_query.page_size,
                "pages": dg_query.pages(total=total),
                "total": total,
            }
        )
    finally:
        session.close()
```
