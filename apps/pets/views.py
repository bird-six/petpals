from django.shortcuts import render

# Create your views here.
def index(request):

    return render(request, 'index.html')

def pets(request):
    pets_list = 40
    return render(request, 'pets.html', {'pets_list': pets_list})

def detail(request):
    return render(request, 'pet_detail.html')

def test(request):
    return render(request, 'test.html')
