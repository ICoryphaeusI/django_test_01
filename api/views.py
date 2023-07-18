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
                file_info = {'file_name': file_name, 'column_names': column_names}
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
                    file_info = {'file_name': file_name, 'column_names': column_names}
                    files_info.append(file_info)

    return render(request, 'api/index.html', {'files_info': files_info})
    
