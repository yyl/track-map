# Django project demo on Heroku #

This is a django template project for you to get started on Heroku, features:

- full project structure including static and templates folders
- a sample app with a simple view for the home page (thanks to [bootstrap][1] project)
- serve static files from [Amazon S3][2] (you have to setup your bucket by yourself)
- providing `requirements.txt` for the development including all dependecies you will need (using pip)
- using gunicorn as WCGI server
- come with a `.gitignore` file for easy pushing (copying from [.gitignore project][3])

Notes:

1. I use a `keys.py` to store all my password, API keys and refer them in corresponding files. You could follow this convention or do your own style. It is not included in the repo.

2. For heroku shared database, instead of the default `dj_database_url` in the official tutorial, I use [postgresify][4], because somehow the former one could not find the local database for me.

3. For local database setup, besides `settings.py`, you have to include `export LOCAL_DEV=true` in your `~/.bash_profile`.

4. Please check the `requirements.txt` to see what packages I use and search corresponding documentation if neccessary.

Feel free to use/fork it for you to start your django project on heroku. The notes might not cover all possible tricks I use to make it work; I will improve them during the development. I am still new to github so please contact with me if I skip any conventions, thank you.

ps. the project structure (by django default):
	
	project_name/
	|    -- manage.py
	|    -- app/
	|	|    -- __init__.py
	|	|    -- views.py
	|	|    -- models.py
	|	|    -- tests.py
	|    -- project_name/
	|	|    -- __init__.py
	|	|    -- settings.py
	|	|    -- wsgi.py
	|	|    -- urls.py
	|    -- requirements.txt
	|    -- Procfile
	|    -- .gitignore


[1]: http://twitter.github.com/bootstrap/
[2]: http://aws.amazon.com/s3/
[3]: https://github.com/github/gitignore
[4]: https://github.com/rdegges/django-heroku-postgresify
