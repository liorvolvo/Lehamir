import os
import uuid
import tempfile
from flask import Flask, request, send_file, render_template
from yt_dlp import YoutubeDL

app = Flask(__name__)

# Update this path if `which ffmpeg` gives you a different one
FFMPEG_PATH = "/opt/homebrew/bin"  # for Apple Silicon, adjust if needed

def download_to_tempfile(url, as_audio=True):
    tmpdir = tempfile.mkdtemp()
    file_id = str(uuid.uuid4())
    extension = "mp3" if as_audio else "mp4"
    output_path = os.path.join(tmpdir, f"{file_id}.%(ext)s")
    final_path = os.path.join(tmpdir, f"{file_id}.{extension}")

    ydl_opts = {
        'outtmpl': output_path,
        'ffmpeg_location': FFMPEG_PATH,
    }

    if as_audio:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        ydl_opts.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'merge_output_format': 'mp4',
        })

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return final_path

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form.get('url')
        format_type = request.form.get('format')

        if not url or format_type not in ['mp3', 'mp4']:
            return "Invalid request", 400

        try:
            as_audio = format_type == 'mp3'
            temp_file_path = download_to_tempfile(url, as_audio)
            download_name = f"lehamir_download.{format_type}"
            return send_file(
                temp_file_path,
                as_attachment=True,
                download_name=download_name,
                mimetype='audio/mpeg' if as_audio else 'video/mp4'
            )
        except Exception as e:
            print(f"Download failed: {e}")
            return "Download failed", 500

    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
