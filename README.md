# cute-eve-pos
A point of sale system for cute eve limited outlets.

[![Build Status](https://app.travis-ci.com/KabakiAntony/cute-eve-pos.svg?branch=develop)](https://app.travis-ci.com/KabakiAntony/cute-eve-pos) [![Coverage Status](https://coveralls.io/repos/github/KabakiAntony/cute-eve-pos/badge.svg?branch=develop)](https://coveralls.io/github/KabakiAntony/cute-eve-pos?branch=develop)

## what is cute-eve-pos
This is a webbased point of sale system for cute eve limited outlets, it helps them make sale on their outlets and record each sale online.



## Setup and installation

   The first step is clone this application and cd into the directory like so

   ```bash
        https://github.com/KabakiAntony/cute-eve-pos.git

   ```

1. Set up virtualenv

   ```bash
        virtualenv venv
   ```

2. Activate virtualenv 

   ```bash
      LINUX/MAC

      . venv/bin/activate

      WINDOWS

      . venv/scripts/activate
      
   ```

3. Install dependencies

   ```bash
        pip install -r requirements.txt
   ```

4. Database configuration.

   The project uses PostgreSQL to persist data and if you wish to use the same you can [get it here](https://www.postgresql.org/download/) ,it supports different Operating Systems just follow the prompts for the different cases, depending on your operating system. The default installation also comes with PgAdmin make sure to check that it is checked to have it installed it will come in handy in helping you manage databases using a graphical user interface.

   Once the installation is finished create two databases on pgadmin that is **cute_eve_main** and **cute_eve_testdb**.

   ## .env file example

   Then create a **.env** file in the root of your project and below is an example of it's contents.

   ```bash
      FLASK_APP = wsgi.py
      FLASK_DEBUG = 1
      FLASK_ENV = "development"
      SECRET_KEY = "yoursecretkey"
      SENDGRID_KEY = "sendgrid api key to assit in sending emails"
      DATABASE_URL = "postgres://postgres:{your postgres password}@localhost/cute-eve-pos"
      TEST_DATABASE_URL= "postgres://postgres:{your postgres password}@localhost/cute-eve-pos_test_db"
      VERIFY_EMAIL_URL= "{url for your frontend app}/verify"
      PASSWORD_RESET_URL = "{url for your frontend app}/reset"
   ```

   Once you are done with the **.env** file then you can run the below command

   ```bash
      flask db init

      flask db migrate -m "initial migration"
      
      flask db upgrade
   ```

5. Running tests 

You can run tests to assertain that the setup works

   ```bash
      python -m pytest --cov=app/api
   ```

6. Start the server

   ```bash
      flask run or python wsgi.py 
   ```

<details>
<summary>cute-eve-pos endpoints</summary>

METHOD       | ENDPOINT      |  DESCRIPTION
------------ | ------------- | ------------
POST  |  /users/create       | create a user
POST  |  /users/login        | logs in a user
POST  |  /users/forgot       | send reset password link
PUT   |  /users/update       |change/update a user password
POST  |  /sales/record       | record or save a sale
GET   |  /sales              | get all sales by user on a given date
GET   |  /sales/<startdate>/<enddate>  | get all sales by all users on a given date
POST  |  /items/upload       | upload new items into the database
GET   |  /items              | get all stock items
PATCH |  /items/<id>         | make changes to an item
DELETE|  /items/<id>         | remove an item from inventory
GET   |  /items/<startdate>/<enddate>| get composite sales information for various items in a given date line



</details>

<details open>

Incase of a bug or anything else use any on the below channels to reach me

[Find me on twitter](https://twitter.com/kabakikiarie) OR  drop me an email at kabaki.antony@gmail.com.
