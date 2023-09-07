import json, time, sys, select, requests, os, glob
from pytube import YouTube
from pytube.exceptions import PytubeError
from pygame import mixer
from pydub import AudioSegment
from dotenv import load_dotenv
from os.path import exists, isdir
from datetime import datetime
from tracklist import getTracklist, printTracklist, tracklistActions

youtubeApiKey = ""
playlistIndex = 0
playlistLength = 0
back = True
playlist = ""
playlistId = "Error"
dirName = os.path.dirname(__file__)
loop = 0
guts = False
tracklist = []

def getEnv():
    global youtubeApiKey
    load_dotenv()
    youtubeApiKey = os.getenv('YOUTBE_API_KEY')

def getPlaylistInfos(playlistId):
    apiUrl = "https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults=50&playlistId={}&key={}".format(playlistId, youtubeApiKey)
    response = requests.get(apiUrl)
    jsonResponse = response.json()
    f = open(f"{dirName}/playlist.json", "w")
    f.write(json.dumps(jsonResponse))
    f.close()
    return jsonResponse

def getUrl(videoIndex):
    videoId = playlist['items'][videoIndex]['contentDetails']['videoId']
    url = f"https://www.youtube.com/watch?v={videoId}"
    return url

def getTitle(videoIndex):
    title = playlist['items'][videoIndex]['snippet']['title']
    if '/' in title:
        title = title.replace('/', '')
        return title
    else: 
        return title

def convertFile(mediaName):
    if mediaName == 'Error':
        return 'Error'
    inputPath = f"{dirName}/downloads/{mediaName}.mp3"
    outputPath = f"{dirName}/music/{mediaName}.mp3"
    if exists(inputPath):
        sound = AudioSegment.from_file(inputPath)
        sound.export(outputPath, format="mp3", bitrate="128k")
        addLog(f"File: {outputPath} file converted successfully")
        os.remove(inputPath)
        addLog(f"File: {inputPath} removed successfully")
    else:
        addLog(f"Error: {inputPath} not found, no possible conversion")

def downloadAudio(videoIndex):
    global guts
    if guts:
        mediaName = "grifith"
        url = f"https://www.youtube.com/watch?v=izGwDsrQ1eQ"
    else:
        url = getUrl(videoIndex)
        mediaName = getTitle(videoIndex)
    output_path = f"{dirName}/downloads"

    if not exists(f"{dirName}/music/{mediaName}.mp3"):
        try:
            yt = YouTube(url)
        except PytubeError as e:
            addLog(f"Error: {output_path}/{mediaName}.mp3 could not be downloaded")
            return "Error"
        else:
            try:
                audio_stream = yt.streams.filter(only_audio=True).first()
            except PytubeError as e:
                addLog(f"Error: {output_path}/{mediaName}.mp3 could not be downloaded")
                return "Error"
            else:
                filename = f"{mediaName}.mp3"
                audio_stream.download(output_path=output_path, filename=filename)
                addLog(f"File: {output_path}/{mediaName}.mp3 downloaded successfully")
                return mediaName
    else:
        addLog(f"File: {dirName}/music/{mediaName}.mp3 already exists")
        return "Error"

# loop playlistIndex inside the range defined by playlistLength
def changeIndex(playlistIndex, back):
    if not back:
        if playlistIndex >= playlistLength:
            return 0
        else:
            return playlistIndex + 1
    elif playlistIndex != 0:
        return playlistIndex -1
    else: 
        return 0

# checks if all the next songs are downloaded and if not, downloads them
def checkNextSong():
    if playlistIndex + 4 < playlistLength: 
        for i in range(5):
            path = f"{dirName}/music/{getTitle(playlistIndex + (i + 1))}.mp3"
            if not exists(path):
                convertFile(downloadAudio(playlistIndex + (i + 1)))
    else: 
        for i in range(playlistLength - playlistIndex):
            path = f"{dirName}/music/{getTitle(playlistIndex + (i + 1))}.mp3"
            if not exists(path):
                convertFile(downloadAudio(playlistIndex + (i + 1)))

def checkSong(songIndex):
    if not exists(f"{dirName}/music/{getTitle(songIndex)}.mp3"):
        convertFile(downloadAudio(songIndex))

def checkPrevSong():
    if playlistIndex - 2 >= 0: 
        for i in range(3):
            path = f"{dirName}/music/{getTitle(playlistIndex - i)}.mp3"
            if not exists(path):
                convertFile(downloadAudio(playlistIndex - i))
    else: 
        for i in range(playlistIndex):
            path = f"{dirName}/music/{getTitle(playlistIndex - (i + 1))}.mp3"
            if not exists(path):
                convertFile(downloadAudio(playlistIndex - (i + 1)))


def manageFiles(removeIndex, downloadIndex, back):
    if removeIndex != 'Error':
        path = f"{dirName}/music/{getTitle(removeIndex)}.mp3"
        if not back and exists(path):
            os.remove(path)
    convertFile(downloadAudio(downloadIndex))

# manages files to always have them and delete them
def manageList(back):
    if playlistLength >= 7:
        downloadIndex = 0
        removeIndex = 0
        checkNextSong()
        checkPrevSong()
        if not back:
            # end of playlist
            if playlistIndex > (playlistLength - 4):
                downloadIndex = (playlistIndex - playlistLength) + 3
                removeIndex = playlistIndex - 3
                manageFiles(removeIndex, downloadIndex, back)
            # begining of playlist
            elif playlistIndex < 3:
                downloadIndex = playlistIndex + 4
                removeIndex = (playlistLength - 2) + playlistIndex
                manageFiles(removeIndex, downloadIndex, back)
            # middle of playlist
            else: 
                manageFiles(playlistIndex - 3, playlistIndex + 4, back)
        elif playlistIndex >= 2:
            manageFiles('Error', playlistIndex - 2, back)

def goToGestion():
    removeFolderOverload()
    checkSong(playlistIndex)

# print album infos (Album name, Artist, Year)
def albumPrint():
    songDescription = playlist['items'][playlistIndex]['snippet']['description']
    
    # check if the song's playlist was generated by youtube and therefore, the structure of informations is almost always the same
    if songDescription[:8] == 'Provided': 
        songDescription = songDescription[songDescription.find(' · ') + 3:]
        # check if the structure is the one anticipated
        if songDescription.find(' · ') != -1 and songDescription.find('℗') != -1:
            songDescription = songDescription[:songDescription.find('℗') + 6]
            # extracting useful infos from description
            artist = songDescription[:songDescription.find('\n')]
            songDescription = songDescription.replace(f"{artist}\n\n", "")
            album = songDescription[:songDescription.find('\n')]
            songDescription = songDescription.replace(f"{album}\n\n℗ ", "")
            date = songDescription
            print(f"{album} - {artist} - {date}")

def infoPrint(paused, songDuration):
    os.system('cls' if os.name == 'nt' else 'clear')
    titlePlaying = getTitle(playlistIndex)
    print(f"Now playing: \n{titlePlaying}", end='')
    print(f" [{playlistIndex + 1}/{playlistLength + 1}", end='|')
    if int(songDuration%60) < 10:
        print(f"{int(songDuration/60)}:0{int(songDuration%60)}]")
    else:
        print(f"{int(songDuration/60)}:{int(songDuration%60)}]")
    albumPrint()
    if loop != 0:
        print(f"plays left: {loop}")
    if paused:
        print("PAUSED")
    print("\n[P]lay/Pause | [B]ack | [N]ext | [S]top | Loop [x]\n> ", end="")

def mediaControl(paused, seconds, back, songDuration):
    infoPrint(paused, songDuration)
    if seconds == 1:
        manageList(back)
    while True:
        if not mixer.music.get_busy() and not paused:
            return 'f'
        # Check if there's input available to read without blocking
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            mediaControl = input("")
            return mediaControl
        
def playSong(back):
    global loop, guts, playlistIndex
    if guts:
        path = f"{dirName}/music/grifith.mp3"
        guts = False
    else:
        path = f"{dirName}/music/{getTitle(playlistIndex)}.mp3" 
    if not exists(path):
        addLog(f"Error: {getTitle(playlistIndex)} could not be played")
        return 'n'
    # song initialization and playing
    mixer.init()
    mixer.music.load(path)
    mixer.music.set_volume(0.3)
    a = mixer.Sound(path)
    songDuration = a.get_length()
    mixer.music.play()
    addLog(f"Playback: {path} strating playback")
    paused = False
    seconds = 0
    # loop to play song until the end
    while mixer.music.get_busy() or paused:
        time.sleep(1)
        seconds += 1
        action = mediaControl(paused, seconds, back, songDuration)
        if action == 'p':
            if paused == False:
                paused = True
                mixer.music.pause()
            else:
                paused = False
                mixer.music.unpause()

        elif action.isdigit():
            loop += int(action)
            if loop == (70 - 1):
                mixer.music.stop()
                mixer.quit()
                return 'c'
        
        elif action == 'f':
            if loop != 0:
                loop -= 1
            mixer.music.stop()
            mixer.quit()
            return 'n'

        elif 'goto' in action:
            if 'goto ' in action:
                goTo = action.replace('goto ', '')
            else:
                goTo = action.replace('goto', '')
            if goTo.isdigit():
                goTo = int(goTo)
                if goTo <= playlistLength + 1 and goTo >= 1:
                    if goTo == playlistIndex:
                        loop = 0
                        mixer.music.stop()
                        mixer.quit()
                        return 'b'
                    elif goTo == playlistIndex + 2:
                        loop = 0
                        mixer.music.stop()
                        mixer.quit()
                        return 'n'
                    playlistIndex = goTo - 1
                    return 'g'
        
        elif action == 'l':
            tracklistGestion = tracklistFunction()
            if tracklistGestion != -1:
                playlistIndex = tracklistGestion
                loop = 0
                mixer.music.stop()
                mixer.quit()
                return 'g'

        elif action == 's' or action == 'n' or action == 'b' or action == 'q':
            loop = 0
            mixer.music.stop()
            mixer.quit()
            return action
    if loop != 0:
        loop -= 1
    mixer.music.stop()
    mixer.quit()
    return 'n'

def tracklistFunction():
    global playlistIndex, playlistLength
    lineNb = 0
    tracklist = getTracklist(f"{dirName}/tracklist.txt")
    printTracklist(lineNb, tracklist, playlistIndex,  0, (os.get_terminal_size()[1]) - 2, playlistLength)
    return tracklistActions(playlistIndex, playlistLength, tracklist)

def removeFolderContent(path):
    filelist = glob.glob(os.path.join(f"{dirName}/{path}/", "*"))
    for f in filelist:
        os.remove(f)
    addLog(f"File: emptied {dirName}/{path} folder")

def removeFolderOverload():
    global playlistIndex
    filelist = glob.glob(os.path.join(f"{dirName}/music/", "*"))
    for f in filelist:
        if playlistIndex >= 2 and playlistIndex <= playlistLength - 4:
            for i in range(playlistIndex - 2, playlistIndex + 5):
                if f == f"{dirName}/music/{getTitle(i)}.mp3":
                    remove = False
                    break
                else:
                    remove = True
            if remove == True:
                os.remove(f)


def directoryGestion(path):
    if not isdir(f"{dirName}/{path}"):
        os.makedirs(f"{dirName}/{path}")
        addLog(f"File: {dirName}/{path} directory was created")
    else:
        removeFolderContent(path)

def generateTracklist():
    f = open(f"{dirName}/tracklist.txt", 'w')
    for i in range(playlistLength + 1):
        f.write(f"{i + 1}. {getTitle(i)}\n")
    f.close()
    addLog(f"File: {dirName}/tracklist.txt generated")

def getPlaylistLength():
    if playlist['pageInfo']['totalResults'] <= playlist['pageInfo']['resultsPerPage']:
            return (playlist['pageInfo']['totalResults']) - 1
    else:
        return (playlist['pageInfo']['resultsPerPage']) - 1

def envSetup():
    global youtubeApiKey
    if not exists(f"{dirName}/.env"):
        f = open(f"{dirName}/.env", "w")
        youtubeApiKey = input("Enter your youtube API key\n> ")
        f.write(f"YOUTBE_API_KEY=\"{youtubeApiKey}\"")
        f.close()
        os.system('cls' if os.name == 'nt' else 'clear')
        addLog("Debug: .env file created storing API key")
    else: 
        getEnv()
        addLog("Debug: API key extracted from env")

def logGetTime():
    now = str(datetime.now())
    now = now[:-7]
    return now

def generateLog():
    if exists(f"{dirName}/main.log"):
        os.remove(f"{dirName}/main.log")
    f = open(f"{dirName}/main.log", 'w')
    f.write(f"{logGetTime()} File: {dirName}/main.log created\n")
    f.close()

def addLog(message):
    f = open(f"{dirName}/main.log", 'a')
    f.write(f"{logGetTime()} {message}\n")
    f.close()

def userInputManagement(userInput):
    if 'OL' in userInput or 'PL' in userInput or "RDC" in userInput:
        if  'youtube.com' in userInput:
            return userInput[userInput.find('list=') + 5:]
        else:
            return userInput
    else:
        return "Error"

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    generateLog()
    envSetup()
    directoryGestion("music")
    directoryGestion("downloads")

    if exists(f"{dirName}/tracklist.txt"):
        os.remove(f"{dirName}/tracklist.txt")

    while playlistId == 'Error':
        playlistId = userInputManagement(input("\nEnter the link of the playlist you want to listen to: \n> "))
        if playlistId == 'Error':
            print("Error invalid link or playlist Id")
        else:
            break
    
    playlist = getPlaylistInfos(playlistId)
    playlistLength = getPlaylistLength()
    generateTracklist()

    if playlistLength > 1:
        print("Downloading...")
        if playlistLength >= 7:
            for i in range(5):
                convertFile(downloadAudio(playlistIndex + i))
            convertFile(downloadAudio(playlistLength - 1))
            convertFile(downloadAudio(playlistLength))
        else:
            for i in range(playlistLength):
                convertFile(downloadAudio(playlistIndex + i))

        os.system('cls' if os.name == 'nt' else 'clear')

        while 1:
            outputPlay = playSong(back)

            if outputPlay == 'b':
                back = True
                playlistIndex = changeIndex(playlistIndex, back)
                checkSong(playlistIndex)

            elif outputPlay == 'n':
                back = False
                if loop == 0:
                    playlistIndex = changeIndex(playlistIndex, back)
                    checkSong(playlistIndex)

            elif outputPlay == 'g':
                back = False
                goToGestion()

            elif outputPlay == 'c':
                back = False
                guts = True
                convertFile(downloadAudio(0))

            else:
                addLog("Script: 's' interrupt")
                os.system('cls' if os.name == 'nt' else 'clear')
                print("kthxbye")
                break
    else:
        print("Error: playlist to short :(")