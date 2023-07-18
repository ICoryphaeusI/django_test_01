from django.shortcuts import render
from .models import File
import pandas as pd
import chardet
import io
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Create your views here.

def create_db(file_data):
    result = chardet.detect(file_data)
    encoding = result['encoding']

    file_data = file_data.decode(encoding)
    df = pd.read_csv(io.StringIO(file_data), delimiter=',')
    return df

def index(request):
    if request.method == 'POST':
        file = request.FILES['file']
        file_name = file.name
        file_path = 'files/' + file_name

        # Удаление существующего файла, если он есть
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        # Сохранение нового файла
        default_storage.save(file_path, ContentFile(file.read()))

        # Чтение файла и вызов функции create_db()
        with default_storage.open(file_path) as file:
            create_db(file.read())

    return render(request, 'api/index.html')