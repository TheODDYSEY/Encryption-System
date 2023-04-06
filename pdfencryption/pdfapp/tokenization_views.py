from django.shortcuts import render
from django.http import HttpResponse, FileResponse
import csv
import json
import secrets
import os


# Define function to tokenize data
def tokenize_data(data):
    token = secrets.token_urlsafe(16)
    return f"{token}:{data}"


# Define function to detokenize data
def detokenize_data(data):
    token, value = data.split(":")
    return value


def tokenize(request):
    if request.method == 'POST':
        # Get the uploaded file from the request
        uploaded_file = request.FILES['file']

        # Check the file type and read the contents accordingly
        if uploaded_file.name.endswith('.csv'):
            file_contents = uploaded_file.read().decode('utf-8')
            file_reader = csv.reader(file_contents.splitlines())
            tokenized_rows = [[tokenize_data(data) for data in row] for row in file_reader]
            tokenized_data = '\n'.join([','.join(row) for row in tokenized_rows])
            filename = 'tokenized.csv'
        elif uploaded_file.name.endswith('.json'):
            file_contents = uploaded_file.read().decode('utf-8')
            data = json.loads(file_contents)
            tokenized_data = json.dumps({key: tokenize_data(value) for key, value in data.items()})
            filename = 'tokenized.json'
        else:
            file_contents = uploaded_file.read().decode('utf-8')
            tokenized_data = tokenize_data(file_contents)
            filename = 'tokenized.txt'

        # Detokenize the tokenized data
        detokenized_data = None
        if tokenized_data:
            if uploaded_file.name.endswith('.csv'):
                file_reader = csv.reader(tokenized_data.splitlines())
                detokenized_rows = [[detokenize_data(data) for data in row] for row in file_reader]
                detokenized_data = '\n'.join([','.join(row) for row in detokenized_rows])
            elif uploaded_file.name.endswith('.json'):
                data = json.loads(tokenized_data)
                detokenized_data = json.dumps({key: detokenize_data(value) for key, value in data.items()})
            else:
                detokenized_data = detokenize_data(tokenized_data)

        # Save the tokenized file to disk
        with open(filename, 'w') as f:
            f.write(tokenized_data)

        # Return the tokenized file as an attachment
        response = FileResponse(open(filename, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        os.remove(filename)
        return response

    return render(request, 'tokenization.html')
