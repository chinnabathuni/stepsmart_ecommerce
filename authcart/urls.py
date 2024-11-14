from django.urls import path
from authcart import views

urlpatterns = [
    path('signin/',views.signin,name="signin"),
    path('signup/',views.signup,name="signup"),
    path('logout/',views.logout,name="logout"),
]