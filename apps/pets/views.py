from django.shortcuts import render, get_object_or_404
from apps.pets.models import Pet
from tools.pet_age import calculate_pet_age


def index(request):

    return render(request, 'index/index.html')

def pets(request):
    pets_list = Pet.objects.order_by('-created_at')
    for pet in pets_list:
        pet.age = calculate_pet_age(pet.birth_date)

    return render(request, 'pets/pets.html', {
        'pets_list': pets_list,
        'pets_count': pets_list.count(),
    })

def detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    pet.age = calculate_pet_age(pet.birth_date)
    return render(request, 'pets/pet_detail.html', {
        'pet': pet,
    })

def test(request):
    return render(request, 'test.html')
