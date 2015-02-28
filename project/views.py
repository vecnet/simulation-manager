from django.http import HttpResponse

from sim_manager.version import VERSION

PAGE_TEMPLATE = """
<html>
  <body>
    <h1>Simulation Manager</h1>
    <p>Version {version}
    </p>
  </body>
</html>
"""


def home_page(request):
    html = PAGE_TEMPLATE.format(version=VERSION)
    return HttpResponse(html)