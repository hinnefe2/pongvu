import datetime as dt
import subprocess
from threading import Thread


from flask import Flask, render_template, request, redirect

AWS_INSTANCE_IP = '52.87.191.99'

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello world'


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

    return render_template('match.html', 
                player_west=player_west, 
                player_east=player_east, 
                filename=filename)


@app.route('/upload', methods=['POST'])
def upload():
    """Upload the video file and show its name"""
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

    # upload the file in a new thread
    subprocess.call(bash_cmd, shell=True)


if __name__ == '__main__':
    app.run()
