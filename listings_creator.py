import json
from datetime import date, datetime, timedelta
from ffprobe import FFProbe
from math import trunc

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

data = json_load("nmptv.json")

f = open("nmptv.json.bak", "w")
f.write(json.dumps(data, indent=2))
f.close()

print(data["channel_name"])

filled_slots = []

for slot in data["template"]:
	list_index = slot["index"][0]
	programme_index = slot["index"][1]
	
	selected_programme = False
	
	attempts = 0
	
	while selected_programme == False:
		programme_list = json_load("programme lists/" + slot["list"][list_index] + ".json")
		
		if programme_list != False:
			if len(programme_list) < (programme_index + slot["movement"]):
				if len(slot["list"]) < (list_index + 1):
					list_index = 0
				else:
					list_index += 1
				
				programme_index = 0
			else:
				programme_index += slot["movement"]
				
				selected_programme = {
					"start":slot["start"],
					"uri":data["base_url"] + programme_list[programme_index]["url"],
					"duration":meta_lookup(data["base_url"] + programme_list[programme_index]["url"])["duration_seconds"]
				}
		elif len(slot["list"]) > 1:
			if len(slot["list"]) < (list_index + 1):
				list_index = 0
			else:
				list_index += 1
		else:
			break
		
		attempts += 1
		
		if attempts > 10:
			break
	
	if selected_programme != False:
		filled_slots.append(selected_programme)
	
	slot["index"][0] = list_index
	slot["index"][1] = programme_index

f = open("nmptv.json", "w")
f.write(json.dumps(data, indent=2))
f.close()

previous_end_time = False

command_output = []

command_output.append({"time":0,"command":"PREVIEW","scene":"Playout 1"})
command_output.append({"time":0,"command":"LOAD","url":filled_slots[0]["uri"]})
#command_output.append({"time":,"command":"PREVIEW","scene":"Ceefax Caption"})
#command_output.append({"time":,"command":"FADE_TO_BLACK","duration":600})
#command_output.append({"time":,"command":"CROSSFADE","duration":600})
#command_output.append({"time":,"command":"FADE_TO_BLACK","duration":600})

for slot_index,slot_info in enumerate(filled_slots):
	if previous_end_time == False:
		programme_start_time = datetime.combine(datetime.now().date(), datetime.strptime(slot_info["start"],"%H:%M").time())
	else:
		programme_start_time = previous_end_time
	
	programme_end_time = programme_start_time + timedelta(seconds=slot_info["duration"])
	
	print(slot_info["uri"])
	print("Starts at " + str(programme_start_time))
	print("Ends at " + str(programme_end_time))
	
	command_output.append({"time":datetime.timestamp(programme_start_time),"command":"PROGRAM","scene":"Playout 1"})
	
	if previous_end_time != False:
		print("Slip: " + str(datetime.combine(datetime.now().date(), datetime.strptime(slot_info["start"],"%H:%M").time()) - programme_start_time))
	
	if (slot_index + 1) < len(filled_slots):
		slot_end_time = datetime.combine(datetime.now().date(), datetime.strptime(filled_slots[slot_index + 1]["start"],"%H:%M").time())
		fill_time = (slot_end_time - programme_end_time)
		#print(slot_end_time)
		print("Time to fill " + str(fill_time))
		
		if fill_time > timedelta(seconds=400):
			print("Fill time with Ceefax")
			command_output.append({"time":0,"command":"PREVIEW","scene":"Clock"})
			command_output.append({"time":datetime.timestamp(programme_end_time),"command":"PROGRAM","scene":"Clock"})
			command_output.append({"time":0,"command":"PREVIEW","scene":"Ceefax Caption"})
			command_output.append({"time":datetime.timestamp(programme_end_time)+5,"command":"PROGRAM","scene":"Ceefax Caption"})
			command_output.append({"time":0,"command":"PREVIEW","scene":"Ceefax Feed"})
			command_output.append({"time":datetime.timestamp(programme_end_time)+10,"command":"PROGRAM","scene":"Ceefax Feed"})
			command_output.append({"time":0,"command":"PREVIEW","scene":"Ceefax Caption"})
			command_output.append({"time":datetime.timestamp(previous_end_time)-25,"command":"PROGRAM","scene":"Ceefax Caption"})
			command_output.append({"time":0,"command":"PREVIEW","scene":"Ident"})
			command_output.append({"time":datetime.timestamp(previous_end_time)-20,"command":"PROGRAM","scene":"Ident"})
			previous_end_time = slot_end_time
		elif fill_time > timedelta(seconds=50):
			print("Fill time with Breakfiller")
			print((trunc((fill_time.total_seconds() - 20)/30) * 30))
			previous_end_time = programme_end_time + timedelta(seconds=(trunc((fill_time.total_seconds() - 20)/30) * 30)) + timedelta(seconds=20)
			command_output.append({"time":0,"command":"PREVIEW","scene":"Breakfiller"})
			command_output.append({"time":datetime.timestamp(programme_end_time),"command":"PROGRAM","scene":"Breakfiller"})
			command_output.append({"time":0,"command":"PREVIEW","scene":"Ident"})
			command_output.append({"time":datetime.timestamp(previous_end_time)-15,"command":"PROGRAM","scene":"Ident"})
		elif fill_time > timedelta(seconds=15):
			print("No fill, run Ident")
			previous_end_time = programme_end_time + timedelta(seconds=20)
			command_output.append({"time":0,"command":"PREVIEW","scene":"Ident"})
			command_output.append({"time":datetime.timestamp(programme_end_time),"command":"PROGRAM","scene":"Ident"})
		else:
			print("No fill, run Clock")
			previous_end_time = programme_end_time + timedelta(seconds=5)
			command_output.append({"time":0,"command":"PREVIEW","scene":"Clock"})
			command_output.append({"time":datetime.timestamp(programme_end_time),"command":"PROGRAM","scene":"Clock"})
	
		command_output.append({"time":0,"command":"PREVIEW","scene":"Playout 1"})
		command_output.append({"time":0,"command":"LOAD","url":filled_slots[slot_index + 1]["uri"]})
	
	print("")

command_output.append({"time":datetime.timestamp(programme_end_time),"command":"PROGRAM","scene":"Ident"})
command_output.append({"time":datetime.timestamp(programme_end_time)+25,"command":"PROGRAM","scene":"Ceefax Caption"})
command_output.append({"time":datetime.timestamp(programme_end_time)+30,"command":"PROGRAM","scene":"Ceefax Feed"})

f = open("command_output.json", "w")
f.write(json.dumps(command_output, indent=2))
f.close()