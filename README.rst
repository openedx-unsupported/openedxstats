============
openedxstats
============

Description
-----------

*Coming soon*


Requirements and Setup
----------------------

After repo has been pulled onto local machine, we recommend designating a new
virtualenv for the project.

Make sure to have postgresql installed **prior** to installing the
requirements, or it will fail!  If you don't have postgresql installed, we
recommend using homebrew::

    brew install postgresql

Once pulled, navigate to the root directory of the project. All requirements
can be installed through the use of pip::

    pip install -r requirements.txt


Run
---

To run the program:

1.  Start postgres server (user=postgres, db=openedxstats)
    If you do not know how to start a postgres server, make sure you have postgres
    and psql installed on your system and run::

        pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start

    You will need to have a database to store the app data, create one by running
    the following commands::

        psql -U postgres
        create database openedxstats

Now you may exit the PSQL prompt.

2.  Start django server
    You may start the django server using the following command::

        python manage.py runserver

    Make sure you are in the project directory before you run this or it will fail.


Testing
-------

To test the entire django program use::

    python manage.py test

To test a single app, use::

    python manage.py test [app_name]

If you want to run code coverage, you can install coverage.py (`pip install coverage`)
and use the following command::

    coverage run manage.py test [app_name]

Where [app_name] is optional. There are many more options to customize the output of coverage, we recommend checking out
the docs located here_.


Functionality
-------------

*Coming soon*


License
-------

Please see the file named LICENSE.rst


Contact Info
------------

Please send all feature requests, questions, bugs, or other comments to:
*Coming soon*


.. _here: http://coverage.readthedocs.io/en/latest/
