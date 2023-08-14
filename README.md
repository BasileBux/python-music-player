# Python youtube music player
This project is a terminal python based youtube music player. You give it a playlist and it plays the songs. 

# How it works
With the youtube API, it fetches the list of video from your playlist and gets the URL of every video. Then, it will download some audio files with pytube and play them with pygame's mixer. 

### Interface
```bash
Now playing: 
Kenya Grace - Meteor
[P]lay/Pause | [B]ack | [N]ext | [S]top
> 
```