import io
import os
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import render
from PyPDF2 import PdfFileReader, PdfFileWriter


# Define function to generate Fernet key
def generate_fernet_key():
    key = Fernet.generate_key()
    return key


# Generate Fernet key
FERNET_KEY = generate_fernet_key()


# Define function to encrypt data
def encrypt_data(data):
    f = Fernet(FERNET_KEY)
    encrypted_data = f.encrypt(data)
    return encrypted_data


# Define function to decrypt data
def decrypt_data(data):
    f = Fernet(FERNET_KEY)
    decrypted_data = f.decrypt(data)
    return decrypted_data


# Define function to process file data
def process_file_data(file, process_func):
    # Read the file data
    file_data = file.read()

    # Process the file data with the given function
    processed_data = process_func(file_data)

    # Return the processed data
    return processed_data


# Define function to encrypt file data
def encrypt_file_data(file):
    return process_file_data(file, encrypt_data)


# Define function to decrypt file data
def decrypt_file_data(file):
    return process_file_data(file, decrypt_data)


# Define view to handle file uploads
def home(request):
    if request.method == 'POST':
        # Get the uploaded file
        uploaded_file = request.FILES['file']

        # Get the filename and extension
        filename, ext = os.path.splitext(uploaded_file.name)

        # Check if the file extension is supported
        if ext not in ['.csv', '.json', '.pdf']:
            return HttpResponse("Unsupported file type!")

        # Encrypt or decrypt the file data based on the button clicked
        if 'encrypt' in request.POST:
            processed_data = encrypt_file_data(uploaded_file)
            processed_filename = f"{filename}_encrypted{ext}"
        elif 'decrypt' in request.POST:
            processed_data = decrypt_file_data(uploaded_file)
            processed_filename = f"{filename}_decrypted{ext}"
        else:
            return HttpResponse("Invalid operation!")

        # Save the processed data to a new file
        processed_file = ContentFile(processed_data)
        processed_file_path = default_storage.save(processed_filename, processed_file)

        # Get the processed file data
        with default_storage.open(processed_file_path) as f:
            processed_file_data = f.read()

        # Create a response with the processed file data
        response = HttpResponse(processed_file_data, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{processed_filename}"'

        # Delete the temporary files
        default_storage.delete(uploaded_file.name)
        default_storage.delete(processed_file_path)

        return response

    return render(request, 'home.html')
