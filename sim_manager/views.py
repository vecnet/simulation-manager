from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt


# If this variable is None, then the view function below returns a HTTP NotFound response.
status_to_return = None

captured_request = dict()


@csrf_exempt
def test_output_url(request):
    if status_to_return is None:
        return HttpResponseNotFound()

    captured_request.clear()
    captured_request['method'] = request.method
    captured_request['body'] = request.body

    return HttpResponse(status=status_to_return)