from flask import Flask, request, jsonify, make_response, send_file, send_from_directory
from flask_cors import CORS, cross_origin
import pandoc.types
from werkzeug.utils import secure_filename
import threading
import chardet
import os
import time
import uuid
from PIL import Image
import ffmpeg
from pydub import AudioSegment
import pandoc
import subprocess
import zipfile
import tarfile
import py7zr
import rarfile
import shutil 

UPLOAD_FOLDER = 'upload'
DOWNLOAD_FOLDER = 'download'
TEMP_FOLDER = 'temp'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_COOKIE_SAMESITE"] = 'None'
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["DOWNLOAD_FOLDER"] = DOWNLOAD_FOLDER
app.config["TEMP_FOLDER"] = TEMP_FOLDER


FILE_URL = None
IMAGE_FORMATS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'}
VIDEO_FORMATS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
AUDIO_FORMATS = {'mp3', 'wav', 'ogg', 'flac'}
ARCHIVE_FORMATS = {'zip', 'rar', '7z', 'tar.gz', 'gz'}
DOCUMENT_FORMATS = {'doc', 'docx', 'pdf', 'txt', 'odt'}
FORMAT_LIST = {"IMAGE_FORMATS" : IMAGE_FORMATS, 
               "VIDEO_FORMATS" : VIDEO_FORMATS,
               "AUDIO_FORMATS" : AUDIO_FORMATS,
               "ARCHIVE_FORMATS" : ARCHIVE_FORMATS, 
               "DOCUMENT_FORMATS" : DOCUMENT_FORMATS
            }

# Conversion progress dictionary
conversion_progress = {}

def process_conversion(conversion_id, upload_destination, conversion, to_format):
    """Handles the file conversion and updates progress in the dictionary."""
    try:
        # Initialize progress
        conversion_progress[conversion_id] = {"progress": 0, "file_url": None}

        # Simulate initial file loading
        time.sleep(1)
        conversion_progress[conversion_id]["progress"] = 5  # Initial step

        # Do the appropriate conversion
        upload_file = None

        if conversion == 'Images':
            conversion_progress[conversion_id]["progress"] = 10  # Start processing images
            time.sleep(1)

            # Convert and track progress
            conversion_progress[conversion_id]["progress"] = 30  # Image conversion starts
            output_file = convert_image(upload_destination, to_format)

        elif conversion == 'Video':
            conversion_progress[conversion_id]["progress"] = 10  # Start processing video
            time.sleep(1)

            # Simulate different stages
            for progress in [25, 50, 75]:  # Simulating encoding stages
                conversion_progress[conversion_id]["progress"] = progress
                time.sleep(2)  # Simulating actual encoding time

            output_file = convert_video(upload_destination, to_format)

        elif conversion == 'Audio':
            conversion_progress[conversion_id]["progress"] = 10  # Start processing audio

            # Simulate stages
            for progress in [30, 50, 70]:  
                conversion_progress[conversion_id]["progress"] = progress
                time.sleep(1)

            output_file = convert_audio(upload_destination, to_format)

        elif conversion == 'Archives':
            conversion_progress[conversion_id]["progress"] = 10  # Start processing archive

            for progress in [40, 60, 80]:  # Simulating decompression/compression steps
                conversion_progress[conversion_id]["progress"] = progress
                time.sleep(1)

            output_file = convert_archive(upload_destination, to_format)

        elif conversion == 'Documents':
            conversion_progress[conversion_id]["progress"] = 10  # Start processing document
            if to_format == 'pdf':
                conversion_progress[conversion_id]["progress"] = 20  # Preparing document
                time.sleep(1)
                conversion_progress[conversion_id]["progress"] = 50  # Converting content
                output_file = convert_docx_to_pdf_with_libreoffice(upload_destination)
            else:
                conversion_progress[conversion_id]["progress"] = 30  # Converting to other formats
                time.sleep(1)
                output_file = convert_document(upload_destination, to_format)

        # Simulate finalization phase
        conversion_progress[conversion_id]["progress"] = 90  # Finalizing conversion
        time.sleep(1)

        # Finalizing
        conversion_progress[conversion_id]["progress"] = 100  # Completion
        conversion_progress[conversion_id]["file_url"] = '/Users/jacquesdutoit/Developer/conversion' + output_file
        print(f'Conversion complete! File saved at: {output_file}')
        print('file_url: ', conversion_progress[conversion_id]["file_url"])

    except Exception as e:
        conversion_progress[conversion_id]["progress"] = 100  # Mark as done even on failure
        conversion_progress[conversion_id]["file_url"] = None
        print(f"Error in conversion: {e}")

# This function detects the encoding of a document file
def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        raw_data = f.read(10000)  # Read part of the file
    print(chardet.detect(raw_data))
    return chardet.detect(raw_data)["encoding"]

# This function converts a docx file to a pdf
# We used the function below this one for converting to pdf - convert_docx_to_pdf_with_libreoffice
def convert_docx_to_pdf(input_file, output_folder=DOWNLOAD_FOLDER):
    if not input_file.lower().endswith('.docx'):
        raise ValueError("Input file must be a .docx file")

    # print('THIS IS THE FUNCTION INPUT FILE: ', input_file)
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.splitext(input_file)[0].replace(UPLOAD_FOLDER, DOWNLOAD_FOLDER) + ".pdf"
    # print('THIS IS THE FUNCTION OUTPUT FILE: ', output_file)

    try:
        # Run the unoconv command
        subprocess.run(["unoconv", "-f", "pdf", "-o", output_folder, input_file], check=True)
        FILE_URL = '/' + output_file
        print('file_url: ', FILE_URL)
        return FILE_URL
    except subprocess.CalledProcessError as e:
        print(f"Error in conversion: {e}")
        return None
    
# This function converts a docx file to a pdf using LibreOffice
def convert_docx_to_pdf_with_libreoffice(input_file):
    if not input_file.lower().endswith('.docx'):
        raise ValueError("Input file must be a .docx file")

    # os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.splitext(input_file)[0].replace(UPLOAD_FOLDER, DOWNLOAD_FOLDER) + ".pdf"
    
    output_folder = DOWNLOAD_FOLDER
    FILE_URL = '/' + output_file
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", output_folder, input_file], check=True)
    print('file_url: ', FILE_URL)
    return FILE_URL

# TO DO: Add support for multiple file type conversions - bmp -> gif, png -> jpg
def convert_image(file, ext):
    print("Converting image...")
    print('input_file: ' + file)
    output_file = os.path.splitext(file)[0].replace(UPLOAD_FOLDER, DOWNLOAD_FOLDER) + '.' + ext
    print('output_file: ' + output_file)
    im = Image.open(file)
    print(im.format, im.size, im.mode)
    im.save(output_file)
    FILE_URL = '/' + output_file
    print('File saved at: ', FILE_URL)
    return FILE_URL

def convert_video(file, ext):
    print("Converting video...")
    print('input_file: ' + file)
    output_file = os.path.splitext(file)[0].replace(UPLOAD_FOLDER, DOWNLOAD_FOLDER) + '.' + ext
    print('ouput_file: ' + output_file)
    ffmpeg.input(file).output(output_file).run()
    FILE_URL = '/' + output_file
    print('File saved at: ', FILE_URL)
    return FILE_URL

def convert_audio(file, ext):
    print("Converting audio...")
    print('input_file: ' + file)
    input_file_ext = file.split('.')[-1]
    print('input_file_ext: ' + input_file_ext)
    output_file = os.path.splitext(file)[0].replace(UPLOAD_FOLDER, DOWNLOAD_FOLDER) + '.' + ext
    print('ouput_file: ' + output_file)
    song = AudioSegment.from_file(file, format=input_file_ext)
    export_file = song.export(output_file, format=ext)
    FILE_URL = '/' + output_file
    print('File saved at: ', FILE_URL)
    return FILE_URL

def convert_archive(file, ext):

    input_file_ext = file.split('.')[-1]
    print("Converting archive...")

    # Extract ZIP
    def extract_zip(zip_path, extract_to):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

    # Extract TAR.GZ
    def extract_tar_gz(tar_path, extract_to):
        with tarfile.open(tar_path, 'r:gz') as tar_ref:
            tar_ref.extractall(extract_to)

    # Extract 7Z
    def extract_7z(zrfile_path, extract_to):
        with py7zr.SevenZipFile(zrfile_path, mode='r') as archive:
            archive.extractall(path=extract_to)

    # Extract RAR
    def extract_rar(rar_path, extract_to):
        with rarfile.RarFile(rar_path) as archive:
            archive.extractall(path=extract_to)

    if file.split('.')[-1] == 'gz' and file.split('.')[-2] == 'tar':
        new_archive_path = os.path.splitext(file)[0].replace(UPLOAD_FOLDER, DOWNLOAD_FOLDER).replace('.tar', ext)
    else:
        new_archive_path = os.path.splitext(file)[0].replace(UPLOAD_FOLDER, DOWNLOAD_FOLDER) + '.' + ext
    extract_folder = TEMP_FOLDER
    FILE_URL = '/' + new_archive_path

    # Extract archive
    if input_file_ext == 'zip':
        extract_zip(file, extract_folder)
    elif input_file_ext == 'tar.gz':
        extract_tar_gz(file, extract_folder)
    elif input_file_ext == '7z':
        extract_7z(file, extract_folder)
    elif input_file_ext == 'rar':
        extract_rar(file, extract_folder)

    print("FILES HAVE BEEN EXTRACTED, NOW COMPRESSING...")

    # Compress
    if ext == 'zip':
        shutil.make_archive(new_archive_path.replace(".zip", ""), 'zip', extract_folder)
    elif ext == 'tar.gz':
        with tarfile.open(new_archive_path, "w:gz") as tar:
            tar.add(extract_folder, arcname=".")
    elif ext == '7z':
        with py7zr.SevenZipFile(new_archive_path, 'w') as archive:
            archive.writeall(extract_folder, arcname=".")
    elif ext == 'rar':
        try:
            # Run the 'rar' command to create the archive
            subprocess.run(["rar", "a", new_archive_path, extract_folder], check=True)
            print(f"Created {new_archive_path} successfully.")
        except subprocess.CalledProcessError as e:
            print("Error creating RAR archive:", e)

    return FILE_URL

def convert_document(file, ext):
    print("Converting document...")
    # print('input_file: ' + file)
    input_file_ext = file.split('.')[-1]
    # print('input_file_ext: ' + input_file_ext)
    output_file = os.path.splitext(file)[0].replace(UPLOAD_FOLDER, DOWNLOAD_FOLDER) + '.' + ext
    # print('ouput_file: ' + output_file)

    # 🔍 Detect encoding
    encoding = detect_encoding(file)
    print(f"Detected encoding: {encoding}")

    # Open the file in binary mode, read and store it in 'content' variable
    with open(file, 'rb') as f: #, encoding='utf-8') as f:
        content = f.read()

    # Pass the variable to pandoc
    input = pandoc.read(content, format=input_file_ext) #, options=['-f', input_file_ext])
    
    # Covert the contents
    output = pandoc.write(input, format=ext) #, options=['-t', ext, '-o', output_file])
    
    # Save a new file and specify the new extension
    with open(output_file, "wb") as f: #, encoding="utf-8") as f:
        f.write(output)
    
    FILE_URL = '/' + output_file
    # print('File saved at: ', FILE_URL)
    return FILE_URL

# To remove all files in a folder - clean up
def remove_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):  # only delete files, not subfolders
                os.remove(file_path)
        except Exception as e:
            print(f"Error removing {file_path}: {e}")

# When the user goes to the home page, delete all files in the download and upload folder
@app.route("/", methods=['GET'])
@cross_origin(methods=['GET'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def home():
    remove_files_in_folder("download")
    remove_files_in_folder("upload")
    remove_files_in_folder("temp")
    return jsonify({"msg" : "Succesfully loaded"}), 200

@app.route("/convert", methods=['POST'])
@cross_origin(methods=['POST'], supports_credentials=True, origins='http://localhost:3000')
def convert_file():
    # Print out for debugging 
    # print("Received Request:", request.content_type)  
    # print("Request Headers:", request.headers)
    # print("Request Form Data:", request.form)
    # print("Request Files:", request.files)

    if 'formFile' not in request.files:
        return make_response({"err": "No file uploaded"}), 400

    # Get the data from the frontend and store in a dictionary named 'data'
    file = request.files.get('formFile')
    conversion = request.form.get('conversion')
    to_format = request.form.get('toFormat')
    # print(file.filename + '\n' + conversion + '\n' + to_format)
    data = {
        "filename": file.filename,
        "conversion": conversion,   
        "toFormat": to_format
        }
    # print(data)

    # Get the extension of the uploaded file and check whether it is valid for the conversion type
    ext = os.path.splitext(file.filename)[-1].lower().lstrip(".")
    # print('extension:', ext)

    # Determine the list where the extension is present
    found = False # Flag to check if the extension is found
    for list_name, list_items in FORMAT_LIST.items():
        if ext in list_items:
            print(f"Found {ext} in {list_name}")  # This prints the name of the list
            found = True
            # Check if the extension is valid for the conversion type
            if list_name[:3].lower() == data['conversion'][:3].lower():
                filename = secure_filename(file.filename)
                upload_destination = os.path.join(UPLOAD_FOLDER, filename)
                # print('upload_destination:', upload_destination)
                file.save(upload_destination)
            else:
                res = make_response({"error": "Invalid conversion type"})
                res.status_code = 400  # Use 400 for client errors
                return res
    
    # If extension is not found in any list, notify the user
    if not found:
        print("Invalid extension")
        res = make_response({"error": f"Does not support conversion from {ext} files"})
        res.status_code = 400  # Use 400 for client errors
        return res
    
    # Generate a unique conversion ID
    conversion_id = str(uuid.uuid4())
    conversion_progress[conversion_id] = {"progress": 0, "file_url": None}

    # Start conversion in a separate thread
    thread = threading.Thread(target=process_conversion, args=(conversion_id, upload_destination, conversion, to_format))
    thread.start()

    return jsonify({"conversion_id": conversion_id, "msg": "Conversion started"}), 202
        
@app.route("/progress/<conversion_id>", methods=['GET'])
@cross_origin(methods=['GET'], headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], supports_credentials=True, origins='http://localhost:3000')
def get_progress(conversion_id):
    """Fetch the conversion progress for a given conversion ID."""
    if conversion_id in conversion_progress:
        return jsonify(conversion_progress[conversion_id])
    else:
        return jsonify({"error": "Invalid conversion ID"}), 404
    
@app.route("/download/<conversion_id>", methods=['GET'])
@cross_origin()
def download_file(conversion_id):
    """Serve the converted file to the user."""
    file_url = conversion_progress.get(conversion_id, {}).get("file_url")

    if not file_url or not os.path.exists(file_url):
        return jsonify({"error": "File not found"}), 404
    
    print('DOWNLOADED: ', file_url)
    return send_file(file_url, as_attachment=True)

if __name__ == "__main__":
    CORS(app, supports_credentials=True, resource={r"/*": {"origins": "*"}})
    app.run(debug=True)