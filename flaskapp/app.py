import datetime as dt
import subprocess
from threading import Thread

import picamera as pc

from flask import Flask, render_template, request, redirect, url_for

AWS_INSTANCE_IP = '54.209.52.220'

recorder = MatchRecorder(filename)

app = Flask(__name__)

class MatchRecorder:

    def __init__(self):
        self.filename = None
        self.recording_thread = None
        self.camera = pc.PiCamera(resolution=(640, 480), framerate=90)

    def start_recording(self):
        self.recording_thread = Thread(target=self._start).start()

    def stop_recording(self):
        self._stop()

    def _start(self):
        self.camera.start_recording(self.filename)

    def _stop(self):
        self.camera.stop_recording()


@app.route('/')
def index():
    return redirect(url_for('newgame'))


@app.route('/newgame')
def record():
    """Show the player name entry form"""
    return render_template('newgame.html')


@app.route('/match', methods = ['POST'])
def match():
    """Show a timer of the match length and an upload button"""
    player_west = request.form['player_west']
    player_east = request.form['player_east']
    start_time = dt.datetime.now().strftime('%Y%m%d%H%M')
    
    # generate filename to save video to
    filename = '{}_vs_{}_{}.h264'.format(player_west, player_east, start_time)

    recorder.filename = filename
    recorder.start_recording()

    return render_template('match.html', 
                player_west=player_west, 
                player_east=player_east, 
                filename=filename)


@app.route('/upload', methods=['POST'])
def upload():
    """Upload the video file and show its name"""

    recorder.stop_recording()

    # get the filename the video was recorded to
    filename = request.form['filename']

    # upload it to AWS using a new thread
    upload_thread = Thread(target=upload_video_file, args=(filename,)).start()

    return 'Uploading {}'.format(filename)


def upload_video_file(filename):
    """Upload the specified file to an AWS instance"""

    # copy the video file to the aws instance for processing
    bash_cmd = 'scp -i ~/AmazonLinuxAMI.pem {} ubuntu@{}:/home/ubuntu/pongvu/uploads/'.format(
                    filename,
                    AWS_INSTANCE_IP)

    # run the bash command to upload the file
    subprocess.call(bash_cmd, shell=True)




if __name__ == '__main__':

    app.run()
