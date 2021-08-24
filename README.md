# Waatea

Availability management tool

Quick and dirty ReadMe

# Setup:
Edit env file in `.envs/.local` (or .production)
(`.django` for general settings, see `env.example`)

Start locally with `docker-compose -f local.yml up`

Create super user with: 
`docker-compose -f local.yml run django python manage.py createsuperuser`
