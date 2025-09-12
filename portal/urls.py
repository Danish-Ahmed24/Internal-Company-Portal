from django.urls import path

from portal import views

urlpatterns = [
    path("", views.index,name="index"),
    path("task/<int:id>/", views.task,name="task"),
    path("project/<int:id>/", views.project,name="project"),
    path("login/", views.login,name="login"),
    path("logout/", views.logout,name="logout"),
]
