import json
import requests
import wave
import time
import os
import base64
import sys
import re
import wget
import tempfile
from evaluator import evaluate, nato_list, numberlist
from Levenshtein import lev
from pydub import AudioSegment
compute_num = 0
try:
    exper_id = sys.argv[1]
except IndexError:
    print("Missing argument to run program.")
alturl = f"https://mcv-testbed.cs.columbia.edu/api/experiment_run/{exper_id}"
url = "https://mcv-testbed.cs.columbia.edu/api"
# https://mcv-testbed.cs.columbia.edu/api/media/

# json is for response objects, requests is for comm with internet, wave to interpret .wav files, wget to download
# wav files, os to clear the screen and manipulate directories, base64 to encode the wav files and send them to the
# Google server, shutil to make copies of files for debugging, regular expressions to exclude special characters.
audio_list = []
encoded_files = {}
trim_dict = {}
result_dict = {}
evaluation_list = []

iterate = 0
iterate2 = 0
# make sure server accepts request
count = 0
newlines = ""
answer_dict = {}
new_dictionary = {}
answer_url_dict = {}
listkeys = []
nato_tune = True
truncated = True
# This is an empty string to convert list items to strings later on in the program

def check_name(enter):
    if 'current' in enter:
        return enter
    else:
        return
    # This function routes the download to the specified filepath *IF* it's a valid one.


folder = tempfile.mkdtemp()
listed = os.listdir(folder)
print(folder)
print("Beginning file download...")


def deletemode(directory):
    listed = os.listdir(directory)
    for items in listed:
        if "impaired_" in items:
            os.system(f'rm {items}')




def fetch_steps(id):
    global url
    response = requests.get(f'{url}/experiment_run/{id}')
    response.raise_for_status()
    experiment_run = response.json()
    if 'experiment' in experiment_run:
        response = requests.get(f'{url}/experiment/{experiment_run["experiment"]}')
        response.raise_for_status()
        experiment = response.json()
    else:
        raise Exception('Experiment could not be found')

    if 'audio' in experiment_run:
        for i, url in enumerate(experiment_run['audio']):
            yield (url, experiment['steps'][i]['correct_answer'])
    else:
        for step in experiment['steps']:
            yield (step['audio'], step.get('correct_answer', None))
print("Function called.")




def download_func(directory):
    global iterate, compute_num
    x = input("Download files in delete mode? (D)\n")
    if "D" in x:
        deletemode(directory)
        listed = os.listdir(directory)
    try:

        for url, correct_answer in fetch_steps(exper_id):
            print(f"The correct answer for {url} is {correct_answer}")
            position = url.find("impaired_")
            matchable = url[position:len(url)]
            answer_dict[matchable] = correct_answer
            answer_url_dict[matchable] = url
            shorthand = answer_url_dict[matchable]

            wget.download(shorthand, out=directory)
            print(" Downloading:", shorthand)
            # download file off the web, map it to specified filepath
            pos = shorthand.find("impaired_")
            cut = shorthand[pos:]
            wavetype = cut + ".wav"

            if truncated:
                new_dictionary[f"cut_{iterate}_{wavetype}"] = iterate
            else:
                new_dictionary[wavetype] = iterate
            os.rename(f"{directory}/{cut}", f"{directory}/{wavetype}")
            os.rename(f"{directory}/{wavetype}", f"{directory}/{iterate}_{wavetype}")
            print(f"Renamed {cut} to {iterate}_{wavetype}")
            trimmed = AudioSegment.from_file(f"{directory}/{iterate}_{wavetype}")
            trimmed_removed = trimmed[1500:]
            trimmed_removed.export(out_f=f"{directory}/cut_{iterate}_{wavetype}",
                                       format="wav")
            trim_dict[wavetype] = f"cut_{iterate}_{wavetype}"
            iterate += 1
            compute_num += 1
    except FileExistsError:
        print("Duplicate file found. Replacing...")
        os.remove(directory + "/" + listed[iterate])
        print(count, "duplicate files found and replaced")

        # convert to wav file
        # rename file



iterate = 0


def encode_func(directory, waves):
    global truncated
    if truncated is True:
        if "cut_" in waves:
            try:
                beginencode = open(f"{folder}/{waves}", 'rb')
            except FileNotFoundError:
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




API_URL = f"https://speech.googleapis.com/v1p1beta1/speech:recognize?key={os.environ['GOOGLE_STT_KEY']}"
iterate = 0

itervar = 0


def eval_phase(text, cur_file):
    global itervar
    print(f"File index: {new_dictionary[cur_file]}, Response: {text}\n")
    return evaluate(text)

# shutil.copyfile(items, str(iterate) + "_" + items)


def google_sendoff(lists, cur_item):
    global nato_tune
    # print(f"Sending {items} to Google")

    config = {"config": {
            "encoding": "LINEAR16",
            "languageCode": "en-US",

        },

            "audio": {
                "content": lists[cur_item]},
        }
    if nato_tune is True:
        config["config"]["speechContexts"] = [{
            "phrases": [nato_list],
            "boost": 100
        }]

    request = requests.post(API_URL, json=config)

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


def api_submission(web_address, identification, file_index, response):
    sendreq = requests.post(web_address, json=
                            {"_id":  identification,
                                "steps": [{
                                    "file_idx": file_index,
                                        "response": response
                                            }]
                            }
                            )
    json_obj = sendreq.json()
    print(json_obj['steps'])


def mainfunction():
    global itervar, compute_num, url, alturl

    print("\nType 'current' to download the files to the directory you're running the program from.\n Which is:",
          os.getcwd(), "\n or type literally anything else to create a temporary folder for the experiment files.")
    filepath = input()
    check_name(filepath)
    if 'current' == filepath:
        tempfile = os.getcwd()
        filepath = str(tempfile)
        try:
            download_func(filepath)
        except KeyError:
            print("A file could not be accessed from the testbed database. "
                  "Please check to make sure your experiment id is a valid one.")
            exit(1)
        listed = os.listdir()
    else:
        try:
            download_func(folder)
        except KeyError:
            print("\nA file could not be accessed from the testbed database. "
                  "Please check to make sure your experiment id is a valid one.\n")
            exit(1)

        listed = os.listdir(folder)



    iterate = 0
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
                api_submission(alturl, exper_id, new_dictionary[items], compressed_str)
                compute_num += 1
                poskey = items.find("impaired_")
                poskeyend = items.find(".wav")
                lev_dist = lev(compressed_str, answer_dict[items[poskey:poskeyend]], True)
                result_dict[items] = (g_interpret, compressed_str, answer_dict[items[poskey:poskeyend]], lev_dist)
                print(f"Levenshtein distance is: {lev_dist}")
                iterate += 1


mainfunction()


os.system(f"rmdir {folder}")

print("Printing result dictionary in 3.")
time.sleep(0.5)
print("2")
time.sleep(0.5)
print("1")
time.sleep(0.5)
with open("results.json", 'w') as blank:
    json.dump(result_dict, blank)
    blank.close()

# verify this is the same dictionary structure as result_dict
