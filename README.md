# HeckGuide
1. Install Python

2. Install Postgres

3. Create and enter new working directory eg "HeckGuide"

4. Create Virtual Environment 
```
py -m venv env
```

Activate Environment

*Mac/Unix*
```
source env/bin/activate
```

*Windows*
```
.\env\Scripts\activate
```

5. Install requirements for local development
```
pip install -r requirements/local.txt
```

6. Fill in ```heckguide/sample.env``` and rename to ```heckguide/.env```

7. Make migrations and then run migrations
```
python manage.py makemigrations
python manage.py migrate
```

8. Create a superuser
```
python manage.py createsuperuser
```

9. Generate an API token for the newly created superuser (the one from step 8)
```
python manage.py drf_create_token superusername
```

Make note of the token

10.  Run server
```
python manage.py runserver
```

11.  Open website
```
http://127.0.0.1:8000/
```

12.  Development website
```
https://v2.heckguide.com/
```

## Commands
For a list of commands, run:
```
python manage.py
```

### Command Examples
1. Scrapes a set number of allies '5000' already in the database without fully populated info and fills them, then scrapes the owner and that owner etc. Depth set to '3'
```
python manage.py crawl_allies_by_name 5000 3
```

2. Scrapes allys by price '500000' and set number of pages '1', a random token will be picked to scrape.
```
python manage.py find_allies_by_price 500000 1
```

3. Scrapes allys by random price and random number of pages
```
python manage.py find_random_price_allies
```

4. Purchase an ally via supplied username with token
```
python manage.py buy_ally_by_name kevz 23
```

5. Volley an ally between tokens
```
python manage.py volley kevz
```

6. Strip a users allies, token must be given
```
python manage.py strip_allies kevz 23
```

7. Scrape the realm starting at the lower boundry of the map, loading 20 chunks and stepping through to the upper end, pick which realm to crawl passing the token argument
```
python manage.py crawl_world 1
```

8. Scrape the realms chat history
```
python manage.py poll_map 1
```

## Troubleshooting
1. If you encounter this error:
```
fatal error: libpq-fe.h: No such file or directory
```

Install libpq library, on Debian:
```
apt install libpq-dev
```

2. Missing PosgresSQL:

Install:
```
sudo apt install postgresql postgresql-contrib
```

Make sure it works:
```
sudo -u postgres psql -c "SELECT version();"
```

Output should be something like:
```
 PostgreSQL 14.5 (Ubuntu 14.5-0ubuntu0.22.04.1) on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 11.2.0-19ubuntu1) 11.2.0, 64-bit
```

Create User (heckguide) and DB (heckguide):
```
sudo su - postgres -c "CREATEUSER heckguide"
sudo su - postgres -c "CREATEDB heckguide"
```

Give `heckguide` user access:
```
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE heckguide TO heckguide;
ALTER USER heckguide WITH PASSWORD 'heckguide';
```

Change `.env` to this URL:
```
DATABASE_URL="postgres://heckguide:heckguide@127.0.0.1:5432/heckguide"
```
