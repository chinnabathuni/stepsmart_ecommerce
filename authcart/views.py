from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login

# Create your views here.
def signup(request):
    if request.method=="POST":
        email=request.POST['email']
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password != confirm_password:
            messages.warning(request,"Password is not Matching")
            return render(request,'authentication/signup.html')
        
        try:
            if User.objects.get(username=email):
                messages.info(request,"Email Already Taken")
                #return HttpResponse("email already exist")
                return render(request,"authentication/signup.html")
        except Exception as identifier:
            pass

        user=User.objects.create_user(email,email,password)
        user.save()
        messages.info(request,"User created")
        return render(request,"authentication/signin.html")
    return render(request,"authentication/signup.html")

def signin(request):
    if request.method=="POST":
        username=request.POST['email']
        userpassword=request.POST['password']
        myuser=authenticate(username=username,password=userpassword)
        if myuser is not None:
            login(request,myuser)
            messages.success(request,"Login Success")
            return render(request,"index.html")
        else:
            messages.error(request,"Invalid Credentials")
    return render(request,"authentication/signin.html")



def logout(request):
    return redirect("/auth/signin")
    