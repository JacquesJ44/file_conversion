import ffmpeg

UPLOAD_FOLDER = 'upload'
DOWNLOAD_FOLDER = 'download'
FILE_URL = None

input_file = 'upload/file_example_WAV_5MG.wav'
output_file = 'download/file_example_WAV_5MG.mp3'
def convert_video(input_file, output_file):
    print("Converting video...")
    # print(file)
    # output_file = os.path.splitext(file)[0].replace(UPLOAD_FOLDER, DOWNLOAD_FOLDER)
    # print(output_file + '.' + ext)
    ffmpeg.input(input_file).output(output_file).run()
    # ffmpeg.run(input_file)
    print('File saved at: ', FILE_URL)
    return True


from pydub import AudioSegment

song = AudioSegment.from_wav(input_file)
file_handle = song.export(output_file, format="mp3")