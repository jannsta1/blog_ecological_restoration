# installation

## python 

uv pip install -r requirements.txt

## npm

### install tailwind
* npm install tailwindcss @tailwindcss/cli

To build the .css files from tailwind:
* npm run (watch) # to keep rebuilding the custom tailwind styles

NB. to see updates in chrome, disable cache (while devtools is open): https://stackoverflow.com/questions/20300400/google-chrome-css-doesnt-update-unless-clear-cache
 
# Setup

The user can setup the django settings.py to their preference, here we provide an overview of the envs that need to be set for some common use cases

## Envs

We recommend the use of the `direnv` package to store your envs in a local file .envrc. The listed environment variables are captured in `.envrc_template`. The user may wish to copy this file and save as `.envrc` (used by direnv).

# resources
* blog creation tutorial: https://www.youtube.com/watch?v=SQbe13IF3eM
* https://www.youtube.com/watch?v=qcJZN1pvG6A&list=PL0Zuz27SZ-6NamGNr7dEqzNFEcZ_FAUVX]
* https://cookiecutter-django.readthedocs.io/en/latest/
* https://github.com/django/djangoproject.com
* using django with tailwind: https://medium.com/@bhuwan.pandey9867/django-with-tailwind-css-v4-5679d1f04b0d
* htmx: https://htmx.org/docs/#introduction
* htmx todo list: https://www.youtube.com/watch?v=XdZoYmLkQ4w
* django TV: https://djangotv.com/

# django project examples
- compendium: https://github.com/wsvincent/awesome-django
- sentry: https://github.com/getsentry/sentry
- cookiecutter-django: https://github.com/cookiecutter/cookiecutter-django
- wagtail (content management): https://github.com/wagtail/wagtail

# setting up postgres on qnap
https://rexbytes.com/2023/12/11/qnap-container-station-docker-setup-postgres/

## setup a supabase postgres project? 
https://supabase.com/pricing

## Docker secrets
https://docs.docker.com/engine/swarm/secrets/

## production setup
Docker, nginx, postgres and nginx: https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/



# TODO
## essential features
- create proper account(s) for the blog login and postgresdb 
--> add a dev database as well?
- remove blog comments
## desirable features
- establish how to backup the data / export blog to e.g. json
- evaluate what happens on a fresh install - how do we create .env files? Where are the passwords stored?
- remove "node_modules" folder from github
- website stats - traffic, where logged in from?
- optimise docker build further & make safe
---> uv build optimize
---> multistage build
---> take root access away from the production docker file
- handle image upload failure scenario
- post slug is a unique id rather than the blog title
- add dark mode
- add formatting options for blog posts
- improve website aesthetic
  - the navbar should be aligned left, except for login/logout which should be aligned right
  - improve blog post aesthetic
- add a favicon.ico for the site
- ensure that the cache is cleared when we update .css files
- replace leaf-vector and favicon-leaves with my own logos
## security
- squash our git history to remove any previsouly stored passwords
- upgrade to MFA login for blog admin. Use allauth?: https://docs.allauth.org/en/latest/introduction/index.html
- set CSRF_TRUSTED_ORIGINS to a safe value
## Low priority
- make sure that the impact map is working - the pins don't show for docker-compose-local.yml (not a production issue)
## Getting us on the internet
- get a url
- setup reverse proxy for our webapp: https://github.com/jlesage/docker-nginx-proxy-manager - see https://www.reddit.com/r/qnap/comments/1937gak/nginx_proxy_manager_on_qnap_nas/ for a tip how to do it
- expose webserver to the internet

## .gitignore .envrc, remove from repo and squash history

## handle warning about GCP API error
/home/jan/dev/blog_ecological_restoration/.venv/lib/python3.13/site-packages/google/auth/_default.py:108: UserWarning: Your application has authenticated using end user credentials from Google Cloud SDK without a quota project. You might receive a "quota exceeded" or "API not enabled" error. See the following page for troubleshooting: https://cloud.google.com/docs/authentication/adc-troubleshooting/user-creds. 
  warnings.warn(_CLOUD_SDK_CREDENTIALS_WARNING)

**steps taken**
in terminal `gcloud auth application-default set-quota-project django-blog-data` which yielded:

``` bash
Credentials saved to file: [/home/jan/.config/gcloud/application_default_credentials.json]

These credentials will be used by any library that requests Application Default Credentials (ADC).

Quota project "django-blog-data" was added to ADC which can be used by Google client libraries for billing and quota. Note that some services may still bill the project owning the resource.
```


