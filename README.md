# Python youtube music player
This project is a terminal Python-based YouTube music player. You give it a playlist, and it plays the songs.

# How it works
With the [YouTube API](https://developers.google.com/youtube/v3/), it fetches the list of videos from your playlist and gets the URL of every video. Then, it will download some audio files with [Pytube](https://pytube.io/en/latest/) and play them with [PyGame's mixer](https://www.pygame.org/docs/ref/mixer.html). 

### Interface
```bash
Now playing: 
Kenya Grace - Meteor
[P]lay/Pause | [B]ack | [N]ext | [S]top
> 
```

![python-function-general](assets/python-youtube-player-general.png)

When you run the program, it will ask you to enter a valid YouTube playlist ID. To find it, go to the playlist you want to download and find the link. It should look something like this: `https://www.youtube.com/playlist?list=PL9JM2aC37BG03vlqyhiYX54NG_thqqvbg`. The character string after `list=` is the playlist's id, so in this case, `PL9JM2aC37BG03vlqyhiYX54NG_thqqvbg`. 

Then, it will download some songs (it may take a bit of time ~20s) and there you go!

Now, navigate with the controls (characters inside the square brackets).

### Specific
The mp3 files that are downloaded by PyTube aren't readable by PyGame's mixer. I tried the VLC Python module, which can read these files, but the module is pretty bad overall. The solution I went with was to convert the file with Pydub. Which creates a file that Pygame's mixer can read.
<!-- <p align="center"> -->
<img src="assets/python-youtube-player-download.png" alt="python-function-download" width="660" />
<!-- </p> -->

### :warning: Possible Issue
A big restriction of this program is that, for various reasons, YouTube videos cannot be downloaded. This is annoying because it means that some songs from your playlist won't be played. I use the PyTube exceptions to skip downloading these songs and stop the program from crashing. But with the way that file management is done, this issue could make the playlist unreadable.

## How to use
1. Install Python 3.8 or higher if not already installed.
2. Install required packages by running:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file in the main folder and add your YouTube API key:
```bash
YOUTBE_API_KEY='your-api-key'
```
<details>
<summary>To get your API key, follow this guide. </summary>
<!-- <br> -->
<ul>
    <li>Log in to <a href="https://console.developers.google.com/" target="_blank">Google Developers Console</a>.</li>
    <li>Create a new project. </li>
    <li>On the new project dashboard, click Explore & Enable APIs. </li>
    <li>In the library, navigate to YouTube Data API v3 under YouTube APIs.</li>
    <li>Enable the API. </li>
    <li>Create a credential.</li>
    <li>A screen will appear with the API key. </li>
</ul>
Guide from: <a href="https://blog.hubspot.com/website/how-to-get-youtube-api-key" target="_blank">HubSpot</a>
</details>
<br>

4. Run the main script:
```bash
python main.py
```
5. Enter the YouTube playlist ID as prompted.
6. Enjoy the music! Use the provided controls to navigate through the playlist.

## Next features
- [ ] Add possibility to give a youtube playlist link
- [ ] Add loop once and loop infinitely controls
- [ ] Add song duration
- [ ] Add index in playlist (7/23)