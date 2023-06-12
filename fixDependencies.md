in flask_uploads.py change 
"from werkzeug import secure_filename, FileStorage" 
to
"from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename"