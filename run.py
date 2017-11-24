#!flask/bin/python
#the above comment is a real shebang (no joke, google it)
from app import app
app.run(host='0.0.0.0', port = 8080, debug=True)