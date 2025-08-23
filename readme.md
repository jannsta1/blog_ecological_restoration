# installation

## npm
* npm install tailwindcss @tailwindcss/cli

## building
* npm run (watch) # to keep rebuilding the custom tailwind styles


# Credits
This code was developed by following this tutorial: 

## resources:
* blog creation tutorial: https://www.youtube.com/watch?v=SQbe13IF3eM
* https://www.youtube.com/watch?v=qcJZN1pvG6A&list=PL0Zuz27SZ-6NamGNr7dEqzNFEcZ_FAUVX]
* https://cookiecutter-django.readthedocs.io/en/latest/
* https://github.com/django/djangoproject.com
* using django with tailwind: https://medium.com/@bhuwan.pandey9867/django-with-tailwind-css-v4-5679d1f04b0d
* htmx: https://htmx.org/docs/#introduction
* htmx todo list: https://www.youtube.com/watch?v=XdZoYmLkQ4w

# requirements

## Landing page
- there shall be a landing page with an introduction to the blog

## Conservation how tos  
- there shall be a page which summarises the howto blog posts. 

## blog posts
- the blog owner shall be able to create new posts
- general post features include:
    * blog title
    * blog date posted
    * blog date refering to (could be a span of multiple days)
    * blog content
    * blog images
    * activity location 
    * activity tags (e.g. tree planting, surveys)
- there shall be a way to refer to the blog images from the blog content text - maybe use: https://django-photologue.readthedocs.io/en/stable/index.html
- the images shall be stored in the cloud - e.g. google image bucket
- there shall be additional specific blog post types:
    * tree planting
        * tree species planted
        * number of trees planed
        * GPS coordinates of planting session

## viewing
- there shall be a page for viewing blogs
- it shall be possible to sort blogs by:
    * date posted (ascending/descending)
    * words in blog title
    * blog type (label?)

## Activity Summary page
- there shall be a dashboard style summary page with the following stats:
    * total trees planted (estimate)
    * map of planting activities


## contact page
- there shall be a contact form

## Backups
- the blog data shall be backed up regularly