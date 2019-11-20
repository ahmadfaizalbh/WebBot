
from .handler import initiate_chat
from chatbot import reflections, multiFunctionCall
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import wikipedia
import os
import warnings

warnings.filterwarnings("ignore")


def get_info(query, sessionID="general"):
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


call = multiFunctionCall({"whoIs": get_info})


chat = initiate_chat(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "chatbotTemplate",
                                  "webbot.template"
                                  ),
                     reflections,
                     call=call)


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
        user = authenticate(request.POST.get('username',''),request.POST.get('password',''))
        if user is not None:
            if user.is_active:
                login(request, user)
                url = request.POST.get('next',"/")
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


@csrf_exempt
@login_required
def web_hook(request):
    sender_id = request.user.username
    last_message_id = None
    if sender_id not in chat.conversation:
        chat.start_new_session(sender_id)
        chat.conversation[sender_id].append_bot('Welcome to WebBot')
    if request.method == "POST":
        message = request.POST.get("message")
        last_message_id = request.POST.get("last_message_id")
        if message:
            chat.attr[sender_id] = {'match': None,
                                    'pmatch': None,
                                    '_quote': False,
                                    'substitute': True}
            chat.conversation[sender_id].append_user(message)
            message = message.rstrip(".! \n\t")
            result = chat.respond(message, sessionID=sender_id)
            chat.conversation[sender_id].append_bot(result)
            del chat.attr[sender_id]
    msgs = Conversation.objects.filter(sender__messengerSenderID=sender_id)
    if last_message_id:
        msgs = msgs.filter(id__gt=last_message_id)
    count = msgs.count()
    msgs = msgs.order_by("id")
    if count > 50:
        msgs = msgs[50:]
    return JsonResponse({
        "status": "Success",
        "messages": [{"id": msg.id,
                      "text": msg.message,
                      "created": msg.created.strftime('%Y-%m-%d %H:%M:%S'),
                      "by": "bot" if msg.bot else "user"
                      } for msg in msgs]
        })



