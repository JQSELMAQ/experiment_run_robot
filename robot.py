import json, requests, wave, time, wget, os, base64
#json is for response objects, requests is for comm with internet, wave to interpret .wav files, wget to download wav files, os to clear the screen, base64 to encode the wav files and send them to the google server
audiolist = []

url = "https://mcv-testbed.cs.columbia.edu/api/experiment_run/62befe7c27977f737525c4c3"
response = requests.get(url)
data = response.json()
iterate = 0
print("Beginning file download")
print(response)
print(data["audio"][iterate])
count = 0

listed = os.listdir()
for files in listed:
    if "impaired_" in listed[iterate]:
        os.remove(listed[iterate])
        os.system('clear') #if you are operating on macOS, this line will return an error in the terminal, 'cls' is the command to clear the screen on windows. on macOS the command is 'clear'. Or vice versa if it has been changed.
        print(count, "duplicate files found and removed")
        count += 1
    iterate += 1

iterate = 0
    
for items in data["audio"]:
    shorthand = data["audio"][iterate]
    wget.download(shorthand)
    cut = shorthand[46 : ]
    wav = cut+".wav"
    os.rename(cut, wav)
    print(" file successfully downloaded")
    iterate += 1
print(shorthand)

beginencode = open("TESTAUDIOFILE.wav", 'rb')
decode = beginencode.read()
convert = base64.b64encode(decode).decode('utf-8')
APIURL = "https://speech.googleapis.com/v1p1beta1/speech:recognize?key=AIzaSyB-5VKtWsx7yCGCOxHRfpRDyZGjU8f4N80"
#apikey AIzaSyB-5VKtWsx7yCGCOxHRfpRDyZGjU8f4N80


request = requests.post(APIURL, json = { "config": {
    "encoding" : "LINEAR16",
    "languageCode" : "en-US"
    },
    "audio" : {
        "content" : convert }
        }
        )
data = request.json()
print(data)
