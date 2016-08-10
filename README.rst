============
openedxstats
============

Intro
-----

openedxstats gives the Open edX team a standalone and extensible way to manage
the list of sites powered by the `Open edX platform`_. This application is hosted
on Heroku_.


Why?
----

Up until now, keeping track of all sites powered by the Open edX software was handled by a Google Sheet. While
low-tech, this solution sufficed for the simple needs of tracking and aggregating data on number of courses, sites,
etc. The biggest missing piece to the system was a way to track historical changes to sites, something Google Sheets
was not built to provide.

Enter openedxstats.

This Django application is built to satisfy the expanding needs of the Open edX team by offering an extensible,
easy-to-use dashboard for managing and exploring the list of Open edX powered sites. Using a record system to keep
track of all changes made to any site in the database, the openedxstats dashboard allows for viewing of "snapshots" of
site status for a given time in the past. Additionally, easy navigation and simple management of sites makes for a
highly user friendly experience.

In the future, other Django apps can be added on as desired to satisfy the needs of the Open edX team and community.


What is a Site Version?
-----------------------

Throughout this readme you will see the use of the term "site" and "site version." A site represents exactly what you
would imagine: a unique website using the Open edX software hosted online. A site version is a representation of the
status of a site over a certain time period. A site may have multiple versions, but a version can only be associated
with one site. For instance, example.org may have 3 versions. When example.org was first created it will be in its first
version, which represents its initial statistics (i.e. # courses, # learners, Name, etc.). Two months later, 5 new
courses were added, so we create a new version of the site to show the changes. The first version is no longer current.
Finally, three months later, the name of the site changes, so we once again create a new version to catalogue these
changes. This new version is now the most current version. The two older versions are not deleted, and as such, we can
always see the status of the example.org site at different points in the past, drawing upon the older versions.

Always remember that all versions of a site will have the same url!


Requirements and Setup
----------------------

After the repo has been pulled onto your local machine, we recommend designating a new
virtualenv for the project. This documentation assumes you are on a Linux or Mac machine, with the
following already installed (we recommend installing in this order if you don't):

- `Python 3.5+`_ (this project is not compatible with Python 2!)
- PostgreSQL_ (OPTIONAL IF YOU ONLY PLAN ON RUNNING TESTS! See 'Testing' section below)
- pip_
- virtualenv_
- virtualenvwrapper_
- If you are on Linux/Ubuntu you will also need ``libpq-dev`` and ``python3-dev``::

    sudo apt-get update
    sudo apt-get install libpq-dev
    sudo apt-get install python3-dev

**Note:** Installing postgresql is often a pain for first timers. If you're on a Mac, the easiest
way to install is using homebrew_::

    brew update
    brew install postgresql

If you're on Linux, things are little bit more challenging, and we recommend looking
at this guide_, or more detailed instructions provided on the `postgresql wiki`_.
With these prerequisites satisfied, begin by setting up a new virtualenv::

    mkvirtualenv -p python3 openedxstats
    workon openedxstats

| 
Now, navigate to the root directory of the project. We assume you have installed all necessary
requirements up to this point, otherwise the following command will fail.
All remaining requirements can be installed through the use of pip::

    pip install -r requirements.txt

In order to run the app, you will need to have a running postgres server. You will need to locate
where postgres was installed on your machine. For instance, if it was installed to /usr/local/var/postgres,
you may start a local server in the background using::

    pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start

If at any point you get an error message of ``peer authentication failed for user USER``, make
sure that your ``pg_hba.conf`` file is configured like `seen here`_, and restart the server.
You will need to have a database to store the app data, create one by running the following commands::

    psql -U postgres
    create database openedxstats

You may now exit the psql prompt. Note that this step (creating a database) only needs to be
done once, but you must have the postgres server running any time you wish to run the app.
Finally, if you do not already have one, create a Django superuser or user. You will need these
credentials to log in to the website. You may create a User from the Django python shell, or easily
create a superuser through the command::

    python manage.py createsuperuser


**Development:**
If you plan on developing or making changes to the code, make sure to turn DEBUG mode to True in the base.py
Django settings, or you will not be able to see errors! Remember to turn it back to False once you are done 
making changes for production testing.


Run
---

**IMPORTANT:**
If this is your first time running the server, make sure to run the following commands to prepare
the database and any static assets for use *prior* to running the server::

    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic

To run the program:

**1.  Start django server**
    You may start the django server using the following command::

        python manage.py runserver

    Make sure you are in the project directory before you run this or it will fail.

**2.  [Optional] Import bulk data**
    If you wish, you may import data into the database using the included import_sites
    management command. Please look at the comments included in the command source code
    to make sure that you correctly format the csv file, or it will likely fail! There is
    correctly formatted data available for import located in the /test_data directory in the sites
    app. Example command usage to import the test_sites file while in the
    project root directory::

        python manage.py import_sites openedxstats/apps/sites/test_data/test_sites.csv


Heroku Deployment
-----------------

*This section assumes you have permission to deploy to Heroku.*

Deploying the app is made quick and easy with Heroku. Once you are given access to the edX Open Source Heroku team,
install the Heroku CLI, it's the easiest way to deploy and what the following instructions are tailored for. Generally,
it's good practice to make sure the code you push has been reviewed and merged in the GitHub repo before deploying,
so as to minimize errors and bugs. Assuming you have the most up-to-date code on your machine and are on your local
master branch, use the following command to deploy::

    git push heroku master

**Important:** This command will push whatever local branch you are on to Heroku's master, even if you aren't on your
local master!

If you encounter database errors after pushing changes to models, try running the following commands::

    heroku run python manage.py makemigrations
    heroku run python manage.py migrate

There is a huge amount of functionality and associated use-cases that Heroku has built in, and we highly recommend
you visit their `comprehensive docs`_ to help answer any questions you have.


Functionality
-------------

- Clean and simple forms for adding new sites, languages, and geozones
- Data sorting
- Keyword searching
- Historical data tracking and searching
- Live updated graphs incorporating historical data
- Quick "edit" functionality on most recent site versions allows for quick changes when creating a new version of the same site
- Automatic site discovery

How to Use
----------

**1.  Authentication**
    When you first navigate to the website - either hosted on your local machine, or at `openedxstats.herokuapp.com`_
    - you will be prompted with a login page. You will have to be provided with a username and password in order to
    access this site, and the rest of this documentation will assume you have been. Once logged in you will be
    redirected to the Sites List page, where you can view all Open edX Sites currently known about. At any time, you
    may logout by pressing the logout button at the upper right corner of the page.

**2.  The Sites List**
    This is where all Open edX Site versions will be listed, and is the homepage for the dashboard.
    
    **a.  Navigating the DataTable**
        The Sites List page uses the JQuery `DataTables plugin`_, allowing for easy sorting and viewing of large amounts of
        data. The table is presorted upon page load to show current versions of sites first, ordered by most recently
        created. You may change the sorting at any time by clicking on the desired column in the table. Current versions
        are clearly marked with a green check.
    **b.  Site Action Buttons**
        There are two to three action buttons to the right of every record in the DataTable, which are meant to
        expedite managing the Sites List. The Detail button will bring you to a page that will show all of the
        attributes of that site, rather than just the ones displayed in the DataTable. The Edit button will bring you to
        the same form used for adding a site version, but prepopulated with the data of that site, to allow for quick
        edits. Be aware that updating a site does not actually update that version, but rather makes a new current
        version with the data you entered. Finally, the Delete button will allow you to delete that site version,
        after a confirmation prompt.
    **c.  Keyword Searching**
        You may search the DataTable for any keyword or letter combination in real time by using the bar marked "Search"
        to the upper right of the DataTable.
    **d.  Historic Searching**
        The search bar to the upper left of the DataTable allows for historical searching. By entering a date/datetime
        into this bar, you will be given a list of all sites that were current *at that time*. This allows you to view
        "snapshots" of what the Sites List contained at different points in time.

**3.  Adding a Site Version**
    In order to add a new site version, click the "Add Site" on the upper navbar. This will bring you to a form
    that will let you specify the details of this new site version. At a bare minimum, you must enter in a url for
    the version. Be aware that you cannot create a site version with a url *and* active start date that matches that
    of an existing version!

**4.  Updating a Site**
    You may only update the *current* version of a site. This prevents you from working off older, obsolete data.
    To update a site, simply click on the Edit button in the action buttons bar to the right of a site version in the
    sites list, or on a site version's detail page. This will bring up the same form used for adding a site version,
    but prepopulated with the information from the version you are editing, allowing for quick, headache-free changes.

**5.  Deleting a Site Version**
    There shouldn't be many circumstances in which you need to delete a site version, unless you entered information
    incorrectly while creating it. Deleting old versions will limit your ability to use historical tracking. To delete
    a version, click on the Delete button in the action buttons bar, or on a site version's detail page.

**6.  Adding a Language**
    Click on the "Add Language" navbar tab. Fill out the one field form to create a language. It will now be an option
    in the Language selector when adding a site version.

**7.  Adding a GeoZone**
    Click on the "Add GeoZone" navbar tab. Fill out the one field form to create a geozone. It will now be an option
    in the GeoZone selector when adding a site version.

**8.  Viewing the Over-Time Data Chart**
    The Over-Time (OT) Data Chart is a real-time visualization of the aggregate courses and sites (not versions) since
    the Sites List was first started. Every data point is a snapshot of the courses and site versions current at
    that time. A new data point is created at the end of each day.

**9.  The Site Discovery List**
    Click on the "Discovery" tab on the navbar to view the Site Discovery List. This list is updated daily with the
    results of the fetch_referrer_logs.py script that is run with Heroku Scheduler. The list contains all domains that
    have downloaded the "Powered by Open edX" logo. The higher the download count next to a domain, the more traffic
    a site is probably getting. A domain will only be listed in the Site Discovery List if it is not in the Sites List
    already (this feature needs ironing out as it wrongly distinguishes sub-domains of the same domain as different sites).
    Use this page to find new sites that are using the edX Platform!


Testing
-------

In order to save time, if you don't plan on developing with the code and only wish to run the tests, you can avoid
installing postgres. To use a SQLITE database to run tests::

    python manage.py test --settings=openedxstats.settings.testing

The following commands use the default database, which is postgres, although you can change the settings like shown
above to use SQLITE instead. To test the entire django program use::

    python manage.py test

To test a single app, use::

    python manage.py test [app_name]

If you want to run code coverage, you can install coverage.py (``pip install coverage``)
and use the following command::

    coverage run manage.py test [app_name]

Where [app_name] is optional. There are many more options to customize the output of coverage,
we recommend checking out the docs located here_.


FAQ
---

**Q:** What if the url of one of the sites changes and that needs to be reflected in a new version?

**A:** Unfortunately, there is no support for url changes between versions at the moment.

**Q:** How do I get credentials to log in?

**A:** Speak to a member of the Open edX team to be given access to the site.

**Q:** Can I delete a Language/GeoZone?

**A:** No, you cannot delete a Language/GeoZone at this time, as it is unlikely for languages and geographies to suddenly cease existing.

**Q:** When does the site discovery script run?

**A:** The script that fetches new referrer logs runs each day at 12am EST, and generally takes 10-30 minutes to complete.


License
-------

Please see the file named LICENSE.rst


.. _comprehensive docs: https://devcenter.heroku.com
.. _DataTables plugin: https://datatables.net/
.. _guide: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-14-04
.. _seen here: http://stackoverflow.com/a/18664239
.. _PostgreSQL: https://www.postgresql.org/
.. _Python 3.5+: https://www.python.org/downloads/
.. _postgresql wiki: https://wiki.postgresql.org/wiki/Detailed_installation_guides
.. _homebrew: http://brew.sh/
.. _Heroku:
.. _openedxstats.herokuapp.com: https://openedxstats.herokuapp.com/sites/all
.. _Open edX platform: https://open.edx.org/
.. _pip: https://pip.pypa.io/en/stable/
.. _virtualenv: https://virtualenv.pypa.io/en/stable/
.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/en/latest/
.. _here: http://coverage.readthedocs.io/en/latest/
