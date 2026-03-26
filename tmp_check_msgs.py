import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate.settings')
django.setup()

from listings.models import Message
from django.contrib.auth.models import User
from django.db.models import Q

def check_messages(username):
    user = User.objects.get(username=username)
    print(f"Checking messages for user: {user.username} (ID: {user.id})")
    
    msgs = Message.objects.filter(Q(sender=user) | Q(receiver=user))
    print(f"Total messages found: {msgs.count()}")
    
    unique_senders = msgs.values_list('sender_id', flat=True).distinct()
    unique_receivers = msgs.values_list('receiver_id', flat=True).distinct()
    
    print(f"Unique sender IDs in user's messages: {list(unique_senders)}")
    print(f"Unique receiver IDs in user's messages: {list(unique_receivers)}")
    
    for m in msgs:
        print(f"  [{m.timestamp}] {m.sender.username} -> {m.receiver.username}: {m.content[:20]}...")

if __name__ == "__main__":
    # I don't know the current user, so list all messages
    print("ALL MESSAGES IN DB:")
    for m in Message.objects.all():
        print(f"  {m.id}: {m.sender.username} -> {m.receiver.username} | {m.content}")
