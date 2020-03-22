from chatbot import register_call
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import wikipedia
import warnings

warnings.filterwarnings("ignore")


@register_call("whoIs")
def get_info(query, session_id="general"):
    try:
        return wikipedia.summary(query)
    except:
        pass
    for new_query in wikipedia.search(query):
        try:
            return wikipedia.summary(new_query)
        except:
            pass
    return "I don't know about " + query


def authenticate(username, password):
    try:
        if "@" in username:
            user = User.objects.get(email__iexact=username)
        else:
            user = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        return None
    if user.check_password(password):
        return user


def login_user(request):
    logout(request)
    context = {"next": request.POST.get('next', "/")}
    if request.method == "POST":
        user = authenticate(request.POST.get('username', ''), request.POST.get('password', ''))
        if user is not None:
            if user.is_active:
                login(request, user)
                url = request.POST.get('next', "/")
                return redirect(url)
            context["error"] = "Your account is not activated, please go to your " \
                               "email and activate your account and then try."
        else:
            context["error"] = "Invalid Username or password"
    return render(request, 'login.html', context=context)


def logout_user(request, *arg):
    logout(request)
    return redirect("/")


@login_required
def index(request):
    return render(request, "index.html")
