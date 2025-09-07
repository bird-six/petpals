from django.shortcuts import render

# Create your views here.
def index(request):

    return render(request, 'index.html')

def pets(request):
    return render(request, 'pets.html')

def test(request):
    return render(request, 'test.html')
