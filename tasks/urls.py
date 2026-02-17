from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="list"),
    path("update/<int:pk>/", views.updateTask, name="update"),
    path("delete/<int:pk>/", views.deleteTask, name="delete"),
    path("accounts/signup/", views.signup, name="signup"),
]
