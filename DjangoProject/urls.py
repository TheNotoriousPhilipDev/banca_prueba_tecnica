from django.urls import path
from technical_challenge_andres_gomez import views

urlpatterns = [
    path('', views.predict_from_excel, name='upload'),
    path('eliminar/<int:registro_id>/', views.eliminar_registro, name='eliminar_registro'),
    path('ver_prediccion/<int:registro_id>/', views.ver_prediccion, name='ver_prediccion')
]

