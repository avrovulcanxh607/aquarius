import json
from ffprobe import FFProbe
from os.path import isfile, join
from os import listdir

base = "A:/Video/Film & TV/"

def json_load(uri):
	try:
		f = open(uri)
	except:
		print("Error opening '" + uri + "'")
		return False
	
	try:
		data = json.load(f)
	except:
		print("Error loading '" + uri + "'")
		return False
	
	f.close()
	
	return data

def meta_lookup(uri):
	try:
		metadata=FFProbe(uri)
	except:
		print("Error loading '" + uri + "'")
		return False
	
	output = {}
	
	for stream in metadata.streams:
		if stream.is_video():
			output["duration_seconds"] = stream.duration_seconds()
	
	return output

#list = json_load("programme lists/a_touch_of_frost.json")

#for item in list["episodes"]:
#	item["start_seconds"] = 0
#	item["end_seconds"] = meta_lookup(base + item["url"])["duration_seconds"]
#	print(item)

directory_list = listdir("programme lists")

for list_uri in directory_list:
	try:
		list = json_load("programme lists/" + list_uri)
		
		for item in list["episodes"]:
			item["start_seconds"] = 0
			item["end_seconds"] = meta_lookup(base + item["url"])["duration_seconds"]
			print(item)
		
		f = open("programme lists/" + list_uri, "w")
		f.write(json.dumps(list, indent=2))
		f.close()
	except:
		print("ERROR: " + list_uri)