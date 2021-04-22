
from http import HTTPStatus

from django.http import HttpResponseRedirect

class HttpResponseSeeOther(HttpResponseRedirect):

    status_code = HTTPStatus.SEE_OTHER
