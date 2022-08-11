import json
import requests
import wave
import time
import os
import base64
import shutil
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
guess = {}
new_dictionary = {}
listkeys = []
listanswers = []
nato_tune = True
truncated = True
# This is an empty string to convert list items to strings later on in the program


def get_json():
    with open("correct_answers.json") as CA:
        answer_text = CA.readlines()
        for items in answer_text:
            position = items.find("impaired_")
            positionend = items.rfind(":")
            matchable = items[position:positionend]
            valuefix = items[positionend:len(items)]
            # leaving comments for readability
            x_whitespace = matchable.strip()
            v_whitespace = valuefix.strip()
            # another
            x_whitespace = re.sub('"', '', x_whitespace)
            v_whitespace = re.sub('"', '', v_whitespace)
            v_whitespace = re.sub(': ', '', v_whitespace)
            v_whitespace = re.sub(',', '', v_whitespace)
            # another
            Answer_dict[x_whitespace] = v_whitespace
            # another
            listkeys.append(x_whitespace)
            # another
            listanswers.append(v_whitespace)


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
        filepath += f"/{folder_name}"
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
                print("Downloading:", shorthand)
                # download file off the web, map it to specified filepath
                pos = shorthand.find("impaired_")
                cut = shorthand[pos:]

                if cut == listkeys[iterate]:
                    new_dictionary[cut] = iterate
                wavetype = cut + ".wav"
                os.rename(directory + "/" + cut, f"{filepath}/{wavetype}")
                os.rename(directory + "/" + wavetype, f"{filepath}/{iterate}_{wavetype}")
                trimmed = AudioSegment.from_file(f"{iterate}_{wavetype}")
                trimmed_removed = trimmed[1500:]
                trimmed_removed.export(out_f=f"{filepath}/cut_{iterate}_{wavetype}",
                                       format="wav")
            except IndexError:
                print("File accessed out of bounds. Breaking loop...")
                break
        except FileExistsError:
            print("Duplicate file found. Replacing...")
            os.remove(filepath + "/" + listed[iterate])
            print(count, "duplicate files found and replaced")

        # convert to wav file
        # rename file
        iterate += 1
        compute_num += 1
        print(Answer_dict[cut])


iterate = 0


def encode_func(directory, waves):
    global truncated
    if truncated is True:
        if "cut_" in waves:
            beginencode = open(waves, 'rb')
            # open recording, parameter = read bytes

            decode = beginencode.read()
            # read recording
            convert = base64.b64encode(decode).decode('utf-8')
            try:
                encoded_files[waves] = convert
            except IndexError:
                print("Attempted to access file out of bounds.")
                return 0

    else:
        beginencode = open(waves, 'rb')
        # open recording, parameter = read bytes

        decode = beginencode.read()
        # read recording
        convert = base64.b64encode(decode).decode('utf-8')
        encoded_files[waves] = convert
        # encode to base 64 then decode back to utf-8 string


API_URL = "https://speech.googleapis.com/v1p1beta1/speech:recognize?key=AIzaSyB-5VKtWsx7yCGCOxHRfpRDyZGjU8f4N80"

iterate = 0

itervar = 0


def eval_phase(text, cur_item):
    global itervar
    print(str(itervar) + ":", text, "\n")
    return evaluate(text)

# shutil.copyfile(items, str(iterate) + "_" + items)


def google_sendoff(lists, cur_item):
    global nato_tune
    # print(f"Sending {items} to Google")
    if nato_tune is True:
        request = requests.post(API_URL, json={"config": {
                "encoding": "LINEAR16",
                "languageCode": "en-US",
                "speechContexts": [{
                    "phrases": [nato_list],
                    "boost": 100
                }]
        },

            "audio": {
                "content": lists[cur_item]},
        })
        # encoded files of items

    else:
        request = requests.post(API_URL, json={"config": {
            "encoding": "LINEAR16",
            "languageCode": "en-US",
        },

            "audio": {
                "content": lists[cur_item]},  # encoded files of items
            # ship off fully formed request with audio file to Google for interpretation,
            # evaluation, and correction. Thus conducting a complete experiment
        })
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
        print("There was a problem transcribing this audio file")
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
        listed = os.listdir()
        tempfile = os.getcwd()
        filepath = str(tempfile)
    else:
        move_dir(filepath)

    iterate = 0
    download_func(filepath)
    listed = os.listdir(filepath)
    print("\nAll files successfully downloaded and prepared for evaluation.")
    iterate = 0
    for waves in listed:
        if "impaired_" in waves:
            try:
                encode_func(filepath, waves)
            except IndexError:
                print("Attempted to access file out of bounds.")
                return 0

    print("Encoding function completed successfully")
    iterate = 0
    iterable_ver_of_dict = list(encoded_files.keys())
    for items in listed:
        if items in encoded_files:
            try:
                g_interpret = google_sendoff(encoded_files, items)
            except IndexError:
                print("File out of bounds. Terminating loop...")
            if len(g_interpret) > 0:
                try:
                    compressed_str = eval_phase(g_interpret, items)
                except IndexError:
                    print("Interpreted index value did not exist.")

                compute_num += 1
                poskey = items.find("impaired_")
                poskeyend = items.find(".wav")
                lev_dist = lev(compressed_str, Answer_dict[items[poskey:poskeyend]], True)
                result_dict[items] = (g_interpret, compressed_str, Answer_dict[items[poskey:poskeyend]], lev_dist)
                print(f"Levenshtein distance is: {lev_dist}")
                iterate += 1


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
