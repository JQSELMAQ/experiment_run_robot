import json
import requests
import wave
import time
import os
import base64
import tempfile
import re
import wget
from evaluator import evaluate, nato_list, numberlist
from Levenshtein import lev
from pydub import AudioSegment
compute_num = 0
url = "https://mcv-testbed.cs.columbia.edu/api/experiment_run/62befe7c27977f737525c4c3"
# https://mcv-testbed.cs.columbia.edu/api/media/

# json is for response objects, requests is for comm with internet, wave to interpret .wav files, wget to download
# wav files, os to clear the screen and manipulate directories, base64 to encode the wav files and send them to the
# Google server, shutil to make copies of files for debugging, regular expressions to exclude special characters.
audio_list = []
encoded_files = {}
M_test_dict = {}
result_dict = {}
evaluation_list = []
response = requests.get(url)
# open testbed
data = response.json()
# json response object to find audio files
iterate = 0
iterate2 = 0
# make sure server accepts request
count = 0
newlines = ""
Answer_list = []
Answer_dict = {}
new_dictionary = {}
listkeys = []
listanswers = []
nato_tune = True
truncated = False
Filename_dict = {}
Trim_dict = {}
Answer_URL_dict = {}
Cut_Answer_URL_dict = {}
Cut_URL_dict = {}
base64_dict = {}
URLvarList = []
URLNumDict = {}
# This is an empty string to convert list items to strings later on in the program


def get_json():
    with open("correct_answers.json") as CA:
        answer_text = CA.readlines()
        assigned_number = 0
        for items in answer_text:

            position = items.find("impaired_")
            positionend = items.rfind(":")
            matchable = items[position:positionend]
            URLvar = items[:positionend]
            valuefix = items[positionend:len(items)]
            # leaving comments for readability
            x_whitespace = matchable.strip()
            v_whitespace = valuefix.strip()
            # another
            x_whitespace = re.sub('"', '', x_whitespace)
            v_whitespace = re.sub('"', '', v_whitespace)
            v_whitespace = re.sub(': ', '', v_whitespace)
            v_whitespace = re.sub(',', '', v_whitespace)
            URLvar = re.sub('"', '', URLvar)
            URLvar = re.sub(' ', '', URLvar)
            URLvarList.append(URLvar)
            URLNumDict[URLvar] = assigned_number - 1
            assigned_number += 1

            # another
            Answer_URL_dict[URLvar] = v_whitespace


def check_name():
    global filepath
    filepath = input()
    if 'current' in filepath:
        return 0
    else:
        try:
            os.listdir(filepath)
        except FileNotFoundError:
            print("\nInvalid pathway. Please try again.\n")
            check_name()
    return filepath
    # This function routes the download to the specified filepath *IF* it's a valid one.


def move_dir(folder):
    dir_choice = input("Would you like to create a separate directory for the experiment files? Y/N.\n")
    if "Y" in dir_choice:
        folder_name = input("Name your folder.\n\n")
        os.system(f"mkdir {folder}/{folder_name}")
        folder += f"/{folder_name}"
    print(folder)
    listed = os.listdir(folder)


print("Beginning file download...")


def deletemode(directory):
    for items in directory:
        if "impaired_" in items:
            os.remove(items)


def download_func(directory):
    global iterate, compute_num
    x = input("Download files in delete mode? (D)\n")
    if "D" in x:
        deletemode(directory)
        listed = os.listdir(directory)
    for items in data["audio"]:
        try:
            try:
                shorthand = data["audio"][compute_num]
                # shortcut for the filepath of the audio
                wget.download(shorthand, out=directory)
                # download file off the web, map it to specified filepath
                pos = shorthand.find("impaired_")
                cut = shorthand[pos:]

                wavetype = cut + ".wav"
                fname = f"{URLNumDict[shorthand]}_{wavetype}"

                Filename_dict[shorthand] = fname
                new_dictionary[shorthand] = iterate
                os.rename(directory + "/" + cut, f"{filepath}/{wavetype}")
                os.rename(directory + "/" + wavetype, f"{filepath}/{iterate}_{wavetype}")

                trimmed = AudioSegment.from_file(f"{iterate}_{wavetype}")
                trimmed_removed = trimmed[1500:]
                Trim_dict[shorthand] = f"cut_{iterate}_{wavetype}"
                trimmed_removed.export(out_f=f"{filepath}/{Trim_dict[shorthand]}",
                                       format="wav")

            except IndexError:
                print("File accessed out of bounds. Breaking loop...")
                break
        except FileExistsError:
            print("Duplicate file found. Replacing...")
            os.remove(filepath + "/" + listed[iterate])
            print(count, "duplicate files found and replaced")


        # rename file
        iterate += 1
        compute_num += 1

iterate = 0


def encode_func(directory, key_url, cur_url):
    print("encode_func called on ", cur_url)
    global iterate
    file_to_use = Filename_dict[cur_url]
    if truncated:
        file_to_use = Trim_dict[cur_url]

    beginencode = open(file_to_use, 'rb')
    # open recording, parameter = read bytes

    decode = beginencode.read()
    # read recording
    convert = base64.b64encode(decode).decode('utf-8')
    try:
        print("1: Going to create base64 for",cur_url)
        base64_dict[cur_url] = convert
    except IndexError:
        print("Attempted to access file out of bounds.")
        return convert


API_URL = "https://speech.googleapis.com/v1p1beta1/speech:recognize?key=AIzaSyB-5VKtWsx7yCGCOxHRfpRDyZGjU8f4N80"

iterate = 0

itervar = 0


def eval_phase(text, cur_item):
    print(f"{new_dictionary[cur_item]}: {text}\n")
    return evaluate(text)


# shutil.copyfile(items, str(iterate) + "_" + items)


def google_sendoff(cur_item):
    global nato_tune
    # print(f"Sending {items} to Google")
    # doesn't matter if truncated: will know to
    post_request = {
        "config": {
            "encoding": "LINEAR16",
            "languageCode": "en-US",

            },

        "audio": {
            "content": base64_dict[cur_item]},
    }

    if nato_tune:
        post_request["config"]["speechContexts"] = [{
                        "phrases": [nato_list],
                        "boost": 100
                    }]
    request = requests.post(API_URL, json=post_request)

    data = request.json()
    try:
        plaintext = data['results'][0]['alternatives'][0]['transcript']
        print("---------------------------------")
        return plaintext

    # print(items, str(iterate)+"_"+items)
    except KeyError:
        # If you chose to download the files to a current directory,
        # chances are there'll be a non .wav file in there somewhere.
        # When this happens, Google is unable to process the file because it's not audio.
        # Which throws a key error when attempting to interpret the response.
        # Hence: the need for this try except.
        print(f"Key error caused by {data}")
        return ""




def mainfunction():
    global itervar, filepath, compute_num
    get_json()
    print("\nSpecify a filepath to send the audio files to. "
          "\nOr, type 'current' the files will automatically be downloaded "
          "to the directory this program is in. Which is:",
          os.getcwd(), "\n")
    check_name()
    if 'current' in filepath:
        tempfile = os.getcwd()
        filepath = str(tempfile)
    else:
        move_dir(filepath)

    iterate = 0
    download_func(filepath)
    print(Trim_dict.keys())
    print("\nAll files successfully downloaded and prepared for evaluation.")
    iterate = 0
    listofkeys = list(Filename_dict.keys())
    for waves in listofkeys:
        try:
            encode_func(filepath, waves, waves)
        except IndexError:
            print("Attempted to access file out of bounds.")
        try:
            g_interpret = google_sendoff(waves)
        except IndexError:
            print("File out of bounds. Terminating loop...")
        if len(g_interpret) > 0:
            try:
                compressed_str = eval_phase(g_interpret, waves)
                compute_num += 1
                print(f"Evaluated {compressed_str} against {Answer_URL_dict[waves]}")
                lev_dist = lev(compressed_str, Answer_URL_dict[waves], True)
                result_dict[waves] = (
                    g_interpret, compressed_str, Answer_URL_dict[waves], lev_dist)
                print(f"Levenshtein distance is: {lev_dist}")
            except IndexError:
                print("Interpreted index value did not exist.")
    print("Encoding function completed successfully")
    iterate = 0


mainfunction()


print("Printing result dictionary in 3.")
time.sleep(0.5)
print("2")
time.sleep(0.5)
print("1")
time.sleep(0.5)
with open("results.json", 'w') as blank:
    json.dump(result_dict, blank)
    blank.close()
