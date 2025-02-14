import json
from os import listdir
from os.path import isfile, join

base_url = "A:/Video/Film & TV/"
directory_url = "Documentary/Once Upon A Time/Northern Ireland"

output = []

directory_list = listdir(base_url + directory_url)

for directory in directory_list:
	#file_list = listdir(base_url + directory_url + "/" + directory)
	
	#for file in file_list:
	#	if file.endswith(".mp4"):
	#		output.append({
	#		"url":directory_url + "/" + directory + "/" + file,
	#		"series":directory,
	#		})
	
	if directory.endswith(".mp4"):
		output.append({
		"url":directory_url + "/" + directory,
		})

print(json.dumps(output, indent=2))

f = open("output.json", "w")
f.write(json.dumps(output, indent=2))
f.close()