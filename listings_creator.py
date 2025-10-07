import json, subprocess, random
from datetime import date, datetime, timedelta
from math import trunc
from collections import defaultdict

def meta_lookup(uri):
    try:
        result = subprocess.run(
            [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format', uri
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False
        )

        if not result.stdout.strip():
            print(f"ERROR: ffprobe returned no output for {uri}")
            return False

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as je:
            print(f"ERROR: Invalid JSON from ffprobe for {uri}: {je}")
            return False

        if "format" not in data or "duration" not in data["format"]:
            print(f"ERROR: ffprobe returned no duration for {uri}")
            return False

        duration = float(data['format']['duration'])
        return {"duration_seconds": duration}

    except Exception as e:
        print(f"Error loading '{uri}': {e}")
        return False

def json_load(uri):
    try:
        with open(uri, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading '{uri}': {e}")
        return False

data = json_load("nmptv.json")

# Backup maken
with open("nmptv.json.bak", "w", encoding="utf-8") as f:
    f.write(json.dumps(data, indent=2))

print("Channel:", data["channel_name"])

filled_slots = []
shuffled_episode_lists = defaultdict(list)

for slot in data["template"]:
    list_name = slot["list"][0]

    # Laad lijst indien nog niet gedaan
    if not shuffled_episode_lists[list_name]:
        programme_list = json_load(f"programme lists/{list_name}.json")
        if not programme_list or "episodes" not in programme_list:
            print(f"WARNING: No episodes found in {list_name}")
            continue

        total_episodes = len(programme_list["episodes"])
        
        # NIEUW: Lees welke afleveringen al zijn afgespeeld
        saved_index = slot.get("index", [])
        played_episodes = set(saved_index) if isinstance(saved_index, list) else set()
        
        shuffled_episode_lists[list_name] = {
            "info": programme_list,
            "all_episodes": programme_list["episodes"][:],
            "played_episodes": played_episodes,
            "total": total_episodes
        }
        
        remaining = total_episodes - len(played_episodes)
        print(f"[{list_name}] {remaining}/{total_episodes} episodes remaining")

    entry = shuffled_episode_lists[list_name]

    # Als alle afleveringen zijn afgespeeld, reset de lijst
    if len(entry["played_episodes"]) >= entry["total"]:
        print(f"[{list_name}] All episodes played! Resetting...")
        entry["played_episodes"].clear()

    # Kies een random aflevering die nog niet is afgespeeld
    available_indices = [i for i in range(entry["total"]) if i not in entry["played_episodes"]]
    
    if not available_indices:
        print(f"ERROR: No available episodes for {list_name}")
        continue
    
    chosen_index = random.choice(available_indices)
    episode = entry["all_episodes"][chosen_index]
    entry["played_episodes"].add(chosen_index)

    metadata = meta_lookup(data["base_url"] + episode["url"])
    if not metadata:
        print(f"ERROR: Failed to get metadata for: {episode['url']}")
        continue

    selected_programme = {
        "start": slot["start"],
        "uri": data["base_url"] + episode["url"],
        "duration": metadata["duration_seconds"],
        "description": episode.get("description", entry["info"].get("description", "")),
        "title": entry["info"]["title"],
        "start_seconds": datetime.timestamp(
            datetime.combine(datetime.now().date(),
            datetime.strptime(slot["start"], "%H:%M").time())
        )
    }

    filled_slots.append(selected_programme)

    # Sla de lijst van afgespeelde afleveringen op
    slot["index"] = sorted(list(entry["played_episodes"]))

# Wegschrijven van nieuwe indexen naar nmptv.json
with open("nmptv.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(data, indent=2))

# Playout-opbouw
previous_end_time = False
command_output = []

command_output.append({"time": 0, "command": "PREVIEW", "scene": "Media 1"})
if filled_slots:
    command_output.append({"time": 0, "command": "LOAD", "url": filled_slots[0]["uri"]})

for slot_index, slot_info in enumerate(filled_slots):
    if not previous_end_time:
        programme_start_time = datetime.combine(datetime.now().date(), datetime.strptime(slot_info["start"], "%H:%M").time())
    else:
        programme_start_time = previous_end_time

    programme_end_time = programme_start_time + timedelta(seconds=slot_info["duration"])
    print(slot_info["uri"])
    print("Starts at", programme_start_time, "Ends at", programme_end_time)

    command_output.append({"time": datetime.timestamp(programme_start_time), "command": "PROGRAM", "scene": "Media 1"})

    if previous_end_time:
        print("Slip:", datetime.combine(datetime.now().date(), datetime.strptime(slot_info["start"], "%H:%M").time()) - programme_start_time)

    if (slot_index + 1) < len(filled_slots):
        slot_end_time = datetime.combine(datetime.now().date(), datetime.strptime(filled_slots[slot_index + 1]["start"], "%H:%M").time())
        fill_time = (slot_end_time - programme_end_time)
        print("Time to fill:", fill_time)

        if fill_time > timedelta(seconds=400):
            print("-> Fill: Ceefax")
            previous_end_time = slot_end_time
            command_output += [
                {"time": 0, "command": "PREVIEW", "scene": "Clock"},
                {"time": datetime.timestamp(programme_end_time), "command": "PROGRAM", "scene": "Clock"},
                {"time": 0, "command": "PREVIEW", "scene": "OS 1"},
                {"time": datetime.timestamp(programme_end_time) + 10, "command": "PROGRAM", "scene": "OS 1"},
                {"time": 0, "command": "PREVIEW", "scene": "Ident"},
                {"time": datetime.timestamp(previous_end_time) - 20, "command": "PROGRAM", "scene": "Ident"}
            ]
        elif fill_time > timedelta(seconds=50):
            print("-> Fill: Breakfiller")
            bf_duration = trunc((fill_time.total_seconds() - 20) / 30) * 30
            previous_end_time = programme_end_time + timedelta(seconds=bf_duration + 20)
            command_output += [
                {"time": 0, "command": "PREVIEW", "scene": "Breakfiller"},
                {"time": datetime.timestamp(programme_end_time), "command": "PROGRAM", "scene": "Breakfiller"},
                {"time": 0, "command": "PREVIEW", "scene": "Ident"},
                {"time": datetime.timestamp(previous_end_time) - 15, "command": "PROGRAM", "scene": "Ident"}
            ]
        elif fill_time > timedelta(seconds=15):
            print("-> Fill: Ident")
            previous_end_time = programme_end_time + timedelta(seconds=20)
            command_output += [
                {"time": 0, "command": "PREVIEW", "scene": "Ident"},
                {"time": datetime.timestamp(programme_end_time), "command": "PROGRAM", "scene": "Ident"}
            ]
        else:
            print("-> Fill: Clock")
            previous_end_time = programme_end_time + timedelta(seconds=5)
            command_output += [
                {"time": 0, "command": "PREVIEW", "scene": "Clock"},
                {"time": datetime.timestamp(programme_end_time), "command": "PROGRAM", "scene": "Clock"}
            ]

        command_output += [
            {"time": 0, "command": "PREVIEW", "scene": "Media 1"},
            {"time": 0, "command": "LOAD", "url": filled_slots[slot_index + 1]["uri"]}
        ]

    print("")

if filled_slots:
    command_output.append({"time": datetime.timestamp(programme_end_time), "command": "PROGRAM", "scene": "Ident"})
    command_output.append({"time": datetime.timestamp(programme_end_time) + 20, "command": "PROGRAM", "scene": "OS 1"})

with open("command_output.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(command_output, indent=2))

# Toevoegen aan eindlijst voor volledigheid
filled_slots.append({
    "duration": 43200,
    "start_seconds": 999999999999,
    "title": "Pages from Ceefax",
    "description": "Items of news and information from Ceefax, with music."
})

# EPG wegschrijven
with open("Y:/nmptv_epg.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(filled_slots, indent=2))
