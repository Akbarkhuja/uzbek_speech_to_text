from uzbek_speech_to_text_converter import STT_Pipeline

import os
from os import listdir
from os.path import isfile, join

import argparse


def main():
    os.environ["STT_API"] = "some_stt_api"

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Parse a file path and a partition number.")
    
    # Add arguments
    parser.add_argument(
        "--path", 
        type=str, 
        required=True, 
        help="The path to the library where the audio recordings are stored."
    )
    parser.add_argument(
        "--partition", 
        type=int, 
        required=True, 
        help="The number for local partitions (must be an integer)."
    )
    parser.add_argument(
        "--youtube", 
        type=str, 
        required=False, 
        help="The text file with youtube links."
    )
    
    
    # Parse arguments
    args = parser.parse_args()
    path = args.path
    partition = args.partition
    youtube = args.youtube

    # List of audio pathes
    audioFiles = [path + f for f in listdir(path) if isfile(join(path, f))]

    if youtube != None:
        with open(youtube, 'r') as file:
            links = file.readlines()
        audioFiles.extend(links)

    df = STT_Pipeline(audioFiles, local_partition=partition)
    df.save(save_mode='append')

# Example: python main.py --path xb_audio/ --partition 100
if __name__ == "__main__":
    main()
