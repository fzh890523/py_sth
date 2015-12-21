from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def test(request):
    # file = request.FILES.get('a')
    # filelist = request.FILES.getlist('a')
    p1 = request.POST.get('p1')
    # print file, filelist
    return HttpResponse("123")