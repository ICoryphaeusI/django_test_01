from django.shortcuts import render
from .models import File
from django.contrib import messages
import pandas as pd
import chardet
import io
import os

# Create your views here.

def create_db(file_data):
    result = chardet.detect(file_data)
    encoding = result['encoding']

    file_data = file_data.decode(encoding)
    df = pd.read_csv(io.StringIO(file_data), delimiter=',')
    column_names = df.columns.tolist()  # Get the list of column names
    return column_names

def index(request):
    if request.method == 'POST':
        file = request.FILES['file']
        file_name = file.name
        file_extension = file_name.split('.')[-1].lower()
        file_path = 'files/' + file_name

        if file_extension != 'csv':
            messages.warning(request, 'Only CSV files are allowed.')
        else:
            # Save the uploaded file
            with open(file_path, 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Read the file and call create_db() function
            with open(file_path, 'rb') as file:
                column_names = create_db(file.read())
                file_info = {
                    'file_name': file_name,
                    'column_names': column_names,
                    'file_url': f'/files/{file_name}'  # URL-адрес файла
                }
                files_info = request.session.get('files_info', [])
                files_info.append(file_info)
                request.session['files_info'] = files_info

    files_info = []

    # Get information about already downloaded files
    folder_path = 'files/'
    if os.path.exists(folder_path):
        file_list = os.listdir(folder_path)
        for file_name in file_list:
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as file:
                    column_names = create_db(file.read())
                    file_info = {
                        'file_name': file_name,
                        'column_names': column_names,
                        'file_url': f'/files/{file_name}'  # URL-адрес файла
                    }
                    files_info.append(file_info)

    return render(request, 'api/index.html', {'files_info': files_info})

def file_detail(request, file_name):
    folder_path = 'files/'
    file_path = folder_path + file_name

    if not file_path.endswith('.csv'):
        return render(request, 'api/error.html', {'error_message': 'Only CSV files are allowed.'})

    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
            result = chardet.detect(file_data)
            encoding = result['encoding']

            file_data = file_data.decode(encoding)
            df = pd.read_csv(io.StringIO(file_data), delimiter=',')

            # Фильтрация данных
            filters = {}
            for column_name in df.columns:
                value = request.GET.get(column_name)
                if value:
                    filters[column_name] = value
            if filters:
                df = df.query(' and '.join(f'{k} == "{v}"' for k, v in filters.items()))

            # Сортировка данных
            sort_column = request.GET.get('sort_column')
            sort_order = request.GET.get('sort_order')
            if sort_column and sort_order:
                df = df.sort_values(by=sort_column, ascending=sort_order == 'asc')

            column_names = df.columns.tolist()

            file_info = {
                'file_name': file_name,
                'column_names': column_names,
                'file_data': df.to_html()  # Преобразуйте данные файла в HTML-таблицу или другой формат, если необходимо
            }

            return render(request, 'api/file_detail.html', {'file_info': file_info})
    except FileNotFoundError:
        return render(request, 'api/error.html', {'error_message': 'File not found.'})
