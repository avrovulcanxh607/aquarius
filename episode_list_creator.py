#Made by Nathan Dane enhanced by Max de Vos

import json
from os import listdir
from os.path import isfile, join

# Ask user for all required information
base_url = input("What is the base URL? (e.g. A:/Video/Film & TV/): ")
directory_url = input("What is the directory name? (e.g. South Park): ")
title = input("What is the series title? ")
description = input("What is the series description? ")

episodes = []

directory_list = listdir(base_url + directory_url)

for directory in directory_list:
	#file_list = listdir(base_url + directory_url + "/" + directory)
	
	#for file in file_list:
	#	if file.endswith(".mp4"):
	#		episodes.append({
	#		"url":directory_url + "/" + directory + "/" + file,
	#		"series":directory,
	#		})
	
	if directory.endswith(".mp4"):
		episodes.append({
		"url":directory_url + "/" + directory,
		})

# Create the final output structure
output = {
	"title": title,
	"description": description,
	"episodes": episodes
}

print(json.dumps(output, indent=2))

f = open("output.json", "w")
f.write(json.dumps(output, indent=2))
f.close()