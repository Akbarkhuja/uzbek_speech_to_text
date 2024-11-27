import os
from os import listdir
from os.path import isfile, join

from time import time
from uzbek_speech_to_text_converter import STT_Pipeline

youtube_urls = [
    "https://www.youtube.com/watch?v=gZNjh9zbEJE"
    "https://www.youtube.com/watch?v=gZNjh9zbEJE",
    "https://www.youtube.com/watch?v=wnBQBPPnokk",
    "https://www.youtube.com/watch?v=_ZoAZVaUSPQ",
    "https://www.youtube.com/watch?v=TLuaTrYh7Pk",
    "https://www.youtube.com/watch?v=4ymODZahOc4"
]
os.environ["STT_API"] = "some_stt_api"

path = input("Enter the path with audio files: ") # put your dir path 
inputs = [path + f for f in listdir(path) if isfile(join(path, f))]

inputs.extend(youtube_urls)


start = time()
df = STT_Pipeline(inputs)
spent = time() - start

print(spent)

start = time()
df.save()
spent = time() - start

print(spent)
