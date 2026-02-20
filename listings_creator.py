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

# Load base config and determine which schedule to use
today = datetime.now()
base_data = json_load("nmptv.json")

config_file = "nmptv.json"

# Check Christmas schedule
christmas_config = base_data.get("christmas_schedule", {})
if christmas_config.get("enabled", False):
    try:
        xmas_start = datetime.strptime(f"{today.year}-{christmas_config['start']}", "%Y-%m-%d").date()
        xmas_end   = datetime.strptime(f"{today.year}-{christmas_config['end']}",   "%Y-%m-%d").date()
        if xmas_start <= today.date() <= xmas_end:
            config_file = christmas_config.get("config", "nmptv_christmas.json")
            print("🎄 Christmas schedule active!")
    except Exception as e:
        print(f"WARNING: Could not parse Christmas dates: {e}")

# Check weekend schedule (only if Christmas didn't already trigger)
if config_file == "nmptv.json":
    weekend_config = base_data.get("weekend_schedule", {})
    if weekend_config.get("enabled", False):
        day_name = today.strftime("%A")  # e.g. "Saturday"
        if day_name in weekend_config.get("days", []):
            config_file = weekend_config.get("config", "nmptv_weekend.json")
            print(f"Weekend schedule active! ({day_name})")

data = base_data if config_file == "nmptv.json" else json_load(config_file)

# Backup
with open(config_file + ".bak", "w", encoding="utf-8") as f:
    f.write(json.dumps(data, indent=2))

print("Channel:", data["channel_name"])

filled_slots = []
shuffled_episode_lists = defaultdict(list)

for slot in data["template"]:

    # Scene slot — switch directly to an OBS scene at this time
    if "scene" in slot:
        scene_name = slot["scene"][0]
        slot_start_time = datetime.combine(today.date(), datetime.strptime(slot["start"], "%H:%M").time())
        print(f"[SCENE SLOT] {slot['start']} -> '{scene_name}'")
        filled_slots.append({
            "start": slot["start"],
            "scene": scene_name,
            "duration": 0,
            "title": scene_name,
            "description": "",
            "start_seconds": datetime.timestamp(slot_start_time),
            "is_scene": True
        })
        continue

    # Programme slot
    list_name = slot["list"][0]

    if not shuffled_episode_lists[list_name]:
        programme_list = json_load(f"programme lists/{list_name}.json")
        if not programme_list or "episodes" not in programme_list:
            print(f"WARNING: No episodes found in {list_name}")
            continue

        total_episodes = len(programme_list["episodes"])
        played_episodes = set(slot.get("index", [])) if isinstance(slot.get("index", []), list) else set()

        shuffled_episode_lists[list_name] = {
            "info": programme_list,
            "all_episodes": programme_list["episodes"][:],
            "played_episodes": played_episodes,
            "total": total_episodes
        }
        print(f"[{list_name}] {total_episodes - len(played_episodes)}/{total_episodes} episodes remaining")

    entry = shuffled_episode_lists[list_name]

    if len(entry["played_episodes"]) >= entry["total"]:
        print(f"[{list_name}] All episodes played! Resetting...")
        entry["played_episodes"].clear()

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

    filled_slots.append({
        "start": slot["start"],
        "uri": data["base_url"] + episode["url"],
        "duration": metadata["duration_seconds"],
        "description": episode.get("description", entry["info"].get("description", "")),
        "title": entry["info"]["title"],
        "start_seconds": datetime.timestamp(datetime.combine(today.date(), datetime.strptime(slot["start"], "%H:%M").time())),
        "is_scene": False
    })

    slot["index"] = sorted(list(entry["played_episodes"]))

# Save updated indexes back to config
with open(config_file, "w", encoding="utf-8") as f:
    f.write(json.dumps(data, indent=2))

# Build playout commands
previous_end_time = False
command_output = []

first_programme_slot = next((s for s in filled_slots if not s.get("is_scene")), None)
command_output.append({"time": 0, "command": "PREVIEW", "scene": "Media 1"})
if first_programme_slot:
    command_output.append({"time": 0, "command": "LOAD", "url": first_programme_slot["uri"]})

for slot_index, slot_info in enumerate(filled_slots):

    # Scene slot
    if slot_info.get("is_scene"):
        scene_start_time = datetime.combine(today.date(), datetime.strptime(slot_info["start"], "%H:%M").time())
        print(f"[SCENE] '{slot_info['scene']}' at {slot_info['start']}")
        command_output += [
            {"time": 0, "command": "PREVIEW", "scene": slot_info["scene"]},
            {"time": datetime.timestamp(scene_start_time), "command": "PROGRAM", "scene": slot_info["scene"]}
        ]
        previous_end_time = scene_start_time
        print("")
        continue

    # Programme slot
    if not previous_end_time:
        programme_start_time = datetime.combine(today.date(), datetime.strptime(slot_info["start"], "%H:%M").time())
    else:
        programme_start_time = previous_end_time

    programme_end_time = programme_start_time + timedelta(seconds=slot_info["duration"])
    print(slot_info["uri"])
    print("Starts at", programme_start_time, "Ends at", programme_end_time)

    command_output.append({"time": datetime.timestamp(programme_start_time), "command": "PROGRAM", "scene": "Media 1"})

    if previous_end_time:
        print("Slip:", datetime.combine(today.date(), datetime.strptime(slot_info["start"], "%H:%M").time()) - programme_start_time)

    # Find next programme slot for fill calculation
    next_programme_slot = next((s for s in filled_slots[slot_index + 1:] if not s.get("is_scene")), None)

    if next_programme_slot:
        slot_end_time = datetime.combine(today.date(), datetime.strptime(next_programme_slot["start"], "%H:%M").time())
        fill_time = slot_end_time - programme_end_time
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
            {"time": 0, "command": "LOAD", "url": next_programme_slot["uri"]}
        ]

    print("")

if filled_slots:
    last_programme = next((s for s in reversed(filled_slots) if not s.get("is_scene")), None)
    if last_programme:
        command_output.append({"time": datetime.timestamp(programme_end_time), "command": "PROGRAM", "scene": "Ident"})
        command_output.append({"time": datetime.timestamp(programme_end_time) + 20, "command": "PROGRAM", "scene": "OS 1"})

with open("command_output.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(command_output, indent=2))

filled_slots.append({
    "duration": 43200,
    "start_seconds": 999999999999,
    "title": "Pages from Ceefax",
    "description": "Items of news and information from Ceefax, with music."
})

# Write EPG (scene slots excluded as they have no fixed duration)
epg_slots = [s for s in filled_slots if not s.get("is_scene")]
with open("Y:/nmptv_epg.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(epg_slots, indent=2))