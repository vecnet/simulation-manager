Simulation Manager for VecNet

Initial Deployment
------------------

1)  Configure web server.

2)  Obtain copy of the source code.
      -- Either Subversion checkout or source archive (e.g., tarball)

3)  Setup virtual environment for Python 2.6 or 2.7.

4)  Activate the virtual environment and install requirements based on
    the Python version:

      (Python 2.7) pip install -r requirements.txt

      (Python 2.6) pip install -r requirements-py26.txt

5)  Set project settings.  There are two groups of settings:

    a)  Django settings which are specified by the DJANGO_SETTINGS_MODULE
        environment variable.  The available modules are in the settings/
        package:

          settings.development
          settings.production

        NOTE: if that environment variable is not set, then the manage.py
        script uses the development settings by default.  Therefore, if you
        don't set that environment variable and want to use the production
        settings, then you must use the --settings option.  For example:

          ./manage.py --settings=settings.production ...

        If deploying a production instance of this project, then these
        additional configuration steps are required:

          i)  Create a secrets.py module in the settings/ package by running
              this script in the virtual environment:

                python settings/make-secrets.py

          ii)  If this is the first deployment on the current host, then the
               host-specific settings for the current host need to be set.
               These settings are:

                 PYTHON_FOR_SCRIPTS in settings/common.py
                 ALLOWED_HOSTS      in settings/production.py


    b)  Settings for the command-line scripts; these are in the
        sim_manager/scripts/conf.py module.  This module includes the paths
        to the various versions of simulation models available on the server.

6)  Create the database, and apply migrations for those Django applications
    that have them:

      ./manage.py syncdb --noinput --migrate

    The --noinput option is required to prevent the creation of an admin user
    during this step.  If this option is omitted, then the syncdb will fail
    with an error about missing tables for Tastypie.  The Tastypie application
    needs to be migrated before an admin user can be created.

7) Create an admin user:

      ./manage.py createsuperuser

8)  Create the special user that's used by the command-line scripts to
    interact with Simulation Manager's REST API to create and update database
    records.

      ./manage.py scriptuser create

    For more information about that management command, enter:

      ./manage.py scriptuser --help


Working Directories
-------------------
By default, the working directories for simulation groups and individual
simulations are created in the "working-dirs" subdirectory:

  working-dirs/sim-groups/
  working-dirs/simulations/


Run Local Tests
---------------
Some of the tests use Django's live server.  It's highly recommended that
you specify a range of ports for the live test server.  If a test fails,
then the default port will remain assigned; subsequent test executions
will fail with errors about the port in use.  A range of ports is specified
with this environment variable:

  export DJANGO_LIVE_TEST_SERVER_ADDRESS="localhost:8000-8010,8080,9200-9300"

Specify the Simulation Manager's application when running the tests:

  ./manage.py test sim_manager

If "sim_manager" is omitted above, then manage.py will also run tests in the
vecnet_utils project.  Some of them are currently broken.

Some tests for the sim_manager application create output files, but they do
so in special folders (named "tests/output/").  The working directories are
not used during tests.


Create a User for Each Client System
------------------------------------
Each client system that will be submitting simulations needs a user account.
Create the accounts in the Django admin interface.  Note: Do NOT put spaces
in a username; it'll break authentication (the authorization header is split
on spaces).

You may want to consider creating a special user account for test purposes.
The remote tests (see below) can be run with any user name, but they default
to using the "test-user" username.

Each user has an API key that is automatically generated.  The keys are
available under the Tastypie application.  Copy a client's username and API
key to the client's secrets location.

Remote Tests
------------
The remote_tests/ package contains tests that can be run with a remote server.
In other words, the tests interact with Simulation Manager on another system.
They are typically run from a developer's machine.

The package is independent of the rest of the project.  It does not depend
upon the Django application.  It can be downloaded (e.g., svn checkout)
by itself.  All it requires is the requests and vecnet.simulation libraries.

  TODO: Put a requirements.txt file into the package & its own README.txt ??

Help for the tests is available:

  (Python 2.7) python -m remote_tests --help

  (Python 2.6) python -m remote_tests.main --help

NOTE: The main module in the remote_tests/ package has to specified when using
      Python 2.6.  In the examples below in this section, replace the package
      name "remote_tests" with the module path "remote_tests.main".

To test authentication credentials, run the auth_tests module:

  python -m remote_tests -u CLIENT_USERNAME -k $API_KEY -s client.server.com:8080 auth_tests

There is a module for simple mock simulations using a Mock simulation model
(which is available on all deployments):

  python -m remote_tests -u CLIENT_USERNAME -k $API_KEY -s client.server.com:8080 mock_tests

NOTE: These tests are partially done; they don't check everything.


Updating a Deployment (with newer source code)
----------------------------------------------

1)  Obtain the latest version of the source code.
      -- Either Subversion update or source archive (e.g., tarball)

2)  Create any new database tables:

      ./manage.py syncdb

    Note: this project uses the South package for database migrations.  South
          modifies the "syncdb" command so it only runs on the installed
          applications that are not configured for database migrations (e.g.,
          tastypie).

2)  Check if there are database migrations by reviewing the list of known
    migrations:

      ./manage.py migrate --list

    Migrations that have been applied are listed as "(*)", so you're looking
    for migrations that have not yet been applied, which are listed as "( )".

3)  If there are outstanding migrations for the sim_manager application, apply
    them:

      ./manage.py migrate sim_manager
