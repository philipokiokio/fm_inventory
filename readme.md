
# Fm Inventory

FM Inventory is an Inventory management software which focuses of product and carting of product. 

It includes the CRUD for Product, and Actions for Cart, such as fetching a users cart, adding products to a cart, and purchasing items in a cart.



## Documentation
The documentation for this server can be found at /docs route. Once the root of the server is hit, the server redirects to the doc. 



## Installation

The codebase is python and the framework used is FastAPI, the datalayer is Postgres. 
Migrations is managed by alembic.

To get started, I advice a virtual env like venv or virtualenv

This creates a venv

```bash
  python3 -m venv venv
```
    
activating the env in unix environment
```bash
source venv/bin/activate
```
A Database needs to created for the application to work smoothly. I used Postgres in my case.

For environmental variables an .env file with the name of .fm.env convention is required to be created. An example env file called .env.fm has been provided in the route of the server to show what is expected.

All packages used for development can be found in the requirements.txt and it can be install via the code below.

```bash
pip install -r requirements.txt

```

To run migrations 
```bash
alembic upgrade heads
```

This sync what the migration script to the just created DB.

To start server this command can be used.

```bash

uvicorn fm_inventory.app:app --reload --port=9000
```
