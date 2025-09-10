from django.shortcuts import render

def users(request):
    return render(request, 'user_profile.html')
