import argparse
import os
import unittest

import conf

parser = argparse.ArgumentParser()
parser.add_argument('-u', dest='user', help='the test user (default: %s)' % conf.Default.USER)
parser.add_argument('-k', dest='api_key', help='the API key for the test user', required=True)
parser.add_argument('-s', dest='server', help='server and port where API is (default: %s)' % conf.Default.SERVER)
parser.add_argument('module', nargs='*', help='name of a module in remote_tests package')
parser.parse_args(namespace=conf.Settings)

print 'Running remote tests:'
print '  API endpoint:', conf.Api.make_url(conf.Api.MAIN_ENDPOINT)
print '  user:', conf.Settings.user


def get_module_names(test_suite):
    """
    Get the set of module names for the tests in a test suite.
    """
    names = set()
    for item in test_suite:
        if isinstance(item, unittest.TestSuite):
            names.update(get_module_names(item))
        else:
            names.add(item.__module__)
    return names


module_names = conf.Settings.module
if len(module_names) == 0:
    package_dir = os.path.dirname(__file__)
    tests = unittest.defaultTestLoader.discover(package_dir, pattern='*_tests.py')
    # The tests have NOT been imported into the remote_tests package.  For example, the tests in the
    # AuthenticationTests class of the auth_tests.py module will be instances of the class
    # 'auth_tests.AuthenticationTests', not 'remote_tests.auth_tests.AuthenticationTests'.  Consequently, those
    # tests do NOT see the same settings as this module.  They see 'conf.Settings' while this main module sees
    # 'remote_tests.conf.Settings'.  Therefore, the actual values from the command line are stored in the latter,
    # but the tests only see the default settings.  So we cannot run the retrieved tests and have them see the
    # settings specified on the command line.  As a fix, we collect the names of the test modules, and then reload
    # them (as though the user entered the module names explicitly).
    module_names = get_module_names(tests)

# For convenience, we allow the user to omit the 'remote_tests' package for each module.  But the package needs
# to be prepended to each module name before loading them.
module_names = ['remote_tests.%s' % x for x in module_names]
tests = unittest.defaultTestLoader.loadTestsFromNames(names=module_names)
unittest.TextTestRunner().run(tests)
