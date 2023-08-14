import json, time, sys, select, requests, os, glob
from pytube import YouTube
from pytube.exceptions import PytubeError
from pygame import mixer
from pydub import AudioSegment
from dotenv import load_dotenv
from os.path import exists
load_dotenv()
youtubeApiKey = os.getenv('YOUTBE_API_KEY')

playlistIndex = 0
playlistLength = 0
back = True
playlist = ""

def getPlaylistInfos(playlistId):
    apiUrl = "https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults=30&playlistId={}&key={}".format(playlistId, youtubeApiKey)
    response = requests.get(apiUrl)
    jsonResponse = response.json()
    f = open("playlist.json", "w")
    f.write(json.dumps(jsonResponse))
    f.close()
    return jsonResponse

def getUrl(videoIndex):
    videoId = playlist['items'][videoIndex]['contentDetails']['videoId']
    url = f"https://www.youtube.com/watch?v={videoId}"
    return url

def getTitle(videoIndex):
    return playlist['items'][videoIndex]['snippet']['title']

# convert file
def convertFile(mediaName):
    if mediaName != "Error":
        inputPath = f"downloads/{mediaName}.mp3"
        outputPath = f"music/{mediaName}.mp3"
        sound = AudioSegment.from_file(inputPath)
        sound.export(outputPath, format="mp3", bitrate="128k")
        os.remove(inputPath)

def downloadAudio(videoIndex):
    url = getUrl(videoIndex)
    mediaName = getTitle(videoIndex)
    output_path = "downloads"

    if not exists(f"music/{mediaName}.mp3"):
        try:
            yt = YouTube(url)
        except PytubeError as e:
            # print(f"Error: {mediaName} could not be downloaded", e)
            return "Error"
        else:
            try:
                audio_stream = yt.streams.filter(only_audio=True).first()
            except PytubeError as e:
                # print(f"Error: {mediaName} could not be downloaded", e)
                return "Error"
            else:
                filename = f"{mediaName}.mp3"
                audio_stream.download(output_path=output_path, filename=filename)
                return mediaName
    else:
        return "Error"

def changeIndex(playlistIndex, back):
    if not back:
        if playlistIndex == playlistLength:
            return 0
        else:
            return playlistIndex + 1
    elif playlistIndex != 0:
        return playlistIndex -1
    else: 
        return 0
    
def checkNextSong():
    for i in range(5):
        if playlistIndex + 4 <= playlistLength: 
            path = f"music/{getTitle(playlistIndex + i)}.mp3"
            if not exists(path):
                convertFile(downloadAudio(playlistIndex + i))
        
def manageFiles(removeIndex, downloadIndex, back):
    path = f"music/{getTitle(removeIndex)}.mp3"
    if not back and exists(path):
        os.remove(path)
    convertFile(downloadAudio(downloadIndex))

def manageList(back):
    downloadIndex = 0
    removeIndex = 0
    checkNextSong()
    if not back:
        if playlistIndex > (playlistLength - 4):
            downloadIndex = (playlistIndex - playlistLength) + 3
            removeIndex = playlistIndex - 3
            manageFiles(removeIndex, downloadIndex, back)
        elif playlistIndex < 3:
            downloadIndex = playlistIndex + 4
            removeIndex = (playlistLength - 2) + playlistIndex
            manageFiles(removeIndex, downloadIndex, back)
        else: 
            manageFiles(playlistIndex - 3, playlistIndex + 4, back)
    elif playlistIndex >= 2:
        manageFiles(0, playlistIndex - 2, back)

def mediaControl(paused, seconds, back):
    os.system('cls' if os.name == 'nt' else 'clear')
    titlePlaying = getTitle(playlistIndex)
    print(f"Now playing: \n{titlePlaying}")
    print("[P]lay/Pause | [B]ack | [N]ext | [S]top\n> ", end='')
    if seconds == 1:
        manageList(back)
    while True:
        if not mixer.music.get_busy() and not paused: # add pause because right now, on pause it goes to next because mixer is not busy anymore
            return 'n'
        # Check if there's input available to read without blocking
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            mediaControl = input("")
            return mediaControl
        
def playSong(back):
    path = f"music/{getTitle(playlistIndex)}.mp3" 
    if not exists(path):
        print(f"{getTitle(playlistIndex)} could not be played, skipping...")
        return 'n'
    mixer.init()
    mixer.music.load(path)
    mixer.music.set_volume(0.1)
    mixer.music.play()
    paused = False
    seconds = 0

    while mixer.music.get_busy() or paused:
        # if seconds == 0:
        #     manageList(back)
        time.sleep(1)
        seconds += 1
        
        action = mediaControl(paused, seconds, back)
        if action == 'p':
            if paused == False:
                paused = True
                print("PAUSED")
                mixer.music.pause()
            else:
                paused = False
                print("PLAYING")
                mixer.music.unpause()
        else: 
            mixer.music.stop()
            return action

    mixer.music.stop()
    return 'n'

def removeFolderContent(path):
    filelist = glob.glob(os.path.join(path, "*"))
    for f in filelist:
        os.remove(f)

def generateTracklist():
    f = open('tracklist.txt', 'w')
    for i in range(playlistLength + 1):
        f.write(f"{getTitle(i)}\n")
    f.close()

if __name__ == '__main__':
    removeFolderContent('music/')
    removeFolderContent('downloads/')
    os.remove('tracklist.txt')

    playlistId = input("\nEnter the id of the playlist you want to listen to: \n> ")
    playlist = getPlaylistInfos(playlistId)

    if playlist['pageInfo']['totalResults'] <= playlist['pageInfo']['resultsPerPage']:
        playlistLength = (playlist['pageInfo']['totalResults']) - 1
    else:
        playlistLength = (playlist['pageInfo']['resultsPerPage']) - 1
    
    generateTracklist()
        
    print("Downloading...")

    for i in range(5):
        convertFile(downloadAudio(playlistIndex + i))

    convertFile(downloadAudio(playlistLength - 1))
    convertFile(downloadAudio(playlistLength))

    os.system('cls' if os.name == 'nt' else 'clear')

    while 1:
        outputPlay = playSong(back)

        if outputPlay == 'b':
            back = True
            playlistIndex = changeIndex(playlistIndex, back)

        elif outputPlay == 'n':
            back = False
            playlistIndex = changeIndex(playlistIndex, back)
        
        else:
            break