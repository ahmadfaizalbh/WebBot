from chatbot import Chat
from .models import *
from django.db.utils import OperationalError, ProgrammingError


class UserMemory:

    def __init__(self, senderID, *args, **kwargs):
        self.senderID = senderID
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        try:
            return Memory.objects.get(sender__messengerSenderID=self.senderID,
                                      key__iexact=key).value
        except Memory.DoesNotExist:
            raise KeyError(key)

    def __setitem__(self, key, val):
        try:
            memory = Memory.objects.get(sender__messengerSenderID=self.senderID, key__iexact=key)
            memory.value = val
            Memory.save()
        except Memory.DoesNotExist:
            sender = Sender.objects.get(messengerSenderID=self.senderID)
            Memory.objects.create(sender=sender, key=key.lower(), value=val)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
    
    def __delitem__(self, key):
        try:
            return Memory.objects.get(sender__messengerSenderID=self.senderID, key=key).delete()
        except Memory.DoesNotExist:
            raise KeyError(key)

    def __contains__(self, key):
        return Memory.objects.filter(sender__messengerSenderID=self.senderID, key=key)


class UserConversation:

    def __init__(self, senderID, *args):
        self.senderID = senderID
        self.extend(list(*args))

    def get_sender(self):
        return Sender.objects.get(messengerSenderID=self.senderID)

    def get_conversation(self, index):
        try:
            conversations = Conversation.objects.filter(sender__messengerSenderID=self.senderID)
            if index < 0:
                index = -index - 1
                conversations = conversations.order_by('-id')
            return conversations[index]
        except:
            raise IndexError("list index out of range")

    def __getitem__(self, index):
        return self.get_conversation(index).message

    def __setitem__(self, index, message):
        conversation = self.get_conversation(index)
        conversation.message = message
        conversation.save()

    def extend(self, items):
        for item in items:
            self.append(item)
            
    def append(self, message):
        Conversation.objects.create(sender=self.get_sender(), message=message)
    
    def append_bot(self, message):
        Conversation.objects.create(sender=self.get_sender(),message=message,bot=True)
    
    def append_user(self, message):
        Conversation.objects.create(sender=self.get_sender(),message=message,bot=False)

    def __delitem__(self, index):
        self.get_conversation(index).delete()
        
    def pop(self):
        try:
            conversation = self.get_conversation(-1)
            message = conversation.message
            conversation.delete()
            return message
        except IndexError:
            raise IndexError("pop from empty list")

    def __contains__(self, message):
        return Conversation.objects.filter(sender__messengerSenderID=self.senderID,
                                           message=message)


class UserTopic:

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getitem__(self, senderID):
        try:
            sender = Sender.objects.get(messengerSenderID=senderID)
        except Sender.DoesNotExist:
            raise KeyError(senderID)
        return sender.topic

    def __setitem__(self, senderID, topic):
        try:
            sender = Sender.objects.get(messengerSenderID=senderID)
            sender.topic = topic
            sender.save()
        except Sender.DoesNotExist:
            Sender.objects.create(messengerSenderID=senderID, topic=topic)
    
    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
    
    def __delitem__(self, senderID):
        try:
            return Sender.objects.get(messengerSenderID=senderID).delete()
        except Sender.DoesNotExist:
            raise KeyError(senderID)
        
    def __contains__(self, senderID):
        return Sender.objects.filter(messengerSenderID=senderID).count() > 0


class UserSession:

    def __init__(self, object_class, *args, **kwargs):
        self.objClass = object_class
        self.update(*args, **kwargs)

    def __getitem__(self, senderID):
        try:
            return self.objClass(Sender.objects.get(messengerSenderID=senderID).messengerSenderID)
        except:raise KeyError(senderID)

    def __setitem__(self, senderID, val):
        Sender.objects.get_or_create(messengerSenderID=senderID)
        self.objClass(senderID, val)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
    
    def __delitem__(self, senderID):
        try:
            return Sender.objects.get(messengerSenderID=senderID).delete()
        except:
            raise KeyError(senderID)
        
    def __contains__(self, senderID):
        return Sender.objects.filter(messengerSenderID=senderID).count() > 0


class MyChat(Chat):

    def __init__(self, *arg, **kwargs):
        super(MyChat, self).__init__(*arg, **kwargs)
        self._memory = UserSession(UserMemory, self._memory)
        self.conversation = UserSession(UserConversation, self.conversation)
        self.topic.topic = UserTopic(self.topic.topic)


def initiate_chat(*arg, **kwargs):
    try:
        return MyChat(*arg, **kwargs)
    except (OperationalError, ProgrammingError):  # No DB exist
        print("No DB exist")
        return Chat(*arg, **kwargs)
