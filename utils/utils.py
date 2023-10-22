from pytube import YouTube

def get_yt_video_length(link):
    video = link
    yt = YouTube(video)  ## this creates a YOUTUBE OBJECT
    video_length = yt.length

    return video_length / 60

def get_yt_video_title(link):
    video = link
    yt = YouTube(video)  ## this creates a YOUTUBE OBJECT
    title = yt.title

    return title

