from django.shortcuts import render

#viSTA DE PRUEBA UNICAMENTE 
def home(request):
    return render(request, "base.html")