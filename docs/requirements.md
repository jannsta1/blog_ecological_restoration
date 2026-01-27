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
    * activity tags (e.g. tree planting, surveys)  [perhaps deprecated? Since we have the activity link  itself. Maybe this can be renamed to `skills`]
- there shall be a way to refer to the blog images from the blog content text - maybe use: https://django-photologue.readthedocs.io/en/stable/index.html
- the images shall be stored in the cloud - e.g. google image bucket
- there shall be additional specific blog post types - this is linked to the "activity" that was conducted:
    * tree planting session
        * tree plant
            * tree species planted [drawn from a choices field?]
            * number of trees planted
            * GPS coordinates of planting sessions
    * vole guard removal
        * plastic recovered
        * GPS route of area covered?
    * Workshops
- each activity has a environmental cost associated with it

## Film / Book reviews

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