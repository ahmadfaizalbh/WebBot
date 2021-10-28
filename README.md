# Setup
```bash
git clone https://github.com/ahmadfaizalbh/WebBot.git
cd WebBot
pip install -r requirements.txt
```

# Initialize
```bash
python manage.py makemigrations
python manage.py migrate
```

# Create Super User
```bash
python manage.py createsuperuser
```

# Run server
```bash
python manage.py runserver
```

# In Brouser
open http://localhost:8000

# Live Replit
https://ChatBotAI-Demo.ahmadfaizal.repl.co


### Note:-
update `CONTACT_FROM` and `CONTACT_TO` in settings.py
```python
CONTACT_FROM = 'from_email@domain.com'
CONTACT_TO = ['to_email@domain.com']
```
