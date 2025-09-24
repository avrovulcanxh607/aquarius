# Aquarius - Beginner's Guide
*TV Playout Controller for OBS*

## What is Aquarius?

Aquarius is a Python system that remotely controls OBS Studio via WebSockets to create an automated live TV stream. It consists of three main components:

1. **Programme Lists** - JSON files containing your video library organized by show
2. **Schedule Template** - A configuration file (`nmptv.json`) defining what shows play when
3. **Automated Playout** - Scripts that generate and execute OBS commands

⚠️ **Important**: This is experimental software with no warranty or support. The creator no longer offers help, so you must figure it out yourself.

## How It Works

The system follows this workflow:
1. Create **programme lists** (JSON files) for each TV series/show
2. Configure your **schedule template** in `nmptv.json`
3. Run **listings_creator.py** to generate OBS commands
4. Run **aquarius.py** to execute the commands and control OBS

## What You Need

### Software Requirements
- **OBS Studio** (version 28+ with WebSocket support)
- **Python 3.x**
- **FFprobe** (for video duration detection)

### Python Libraries
```bash
pip install obs-websocket-py
```

### Knowledge Requirements
- Basic OBS Studio setup
- Basic Python understanding
- File/folder organization skills

## Installation & Setup

### Step 1: Prepare OBS Studio

1. **Install OBS Studio** (version 28 or higher)

2. **Enable WebSocket Server**:
   - Go to `Tools` → `WebSocket Server Settings`
   - Enable `WebSocket server`
   - **Important**: Do NOT set a password - leave it blank
   - Set the port to `4455`

Your OBS scenes should look like this:
```
- Media 1        (contains "VT 1" Media Source)
- Clock          (for time filler)
- Ident          (for channel branding)  
- Breakfiller    (for short fill content)
- OS 1           (for teletext/information pages)
```

**VT 1 Media Source Setup**:
- Use regular Media Source (NOT VLC Video Source)
- Leave "Local File" field empty
- Enable "Restart playback when source becomes active"
- Enable "Show nothing when playback ends"
- The script will load files into this source automatically

4. **Add VT Source**:
   - In the "Media 1" scene, add a **Media Source** (NOT VLC Video Source)
   - Name it exactly **"VT 1"**
   - **Important**: Leave the "Local File" field completely empty in the properties
   - Check "Restart playback when source becomes active" 
   - Check "Show nothing when playback ends"
   - This is where videos will be loaded automatically by the script

### Step 2: Install Aquarius

1. **Download the files**:
   ```bash
   git clone https://github.com/avrovulcanxh607/aquarius.git
   cd aquarius
   ```

2. **Install dependencies**:
   ```bash
   pip install websocket-client
   ```

3. **Ensure FFprobe is available**:
   - Windows: Download from https://ffmpeg.org/
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg` then also `pip install ffmpeg`

## Creating Programme Lists

### Using episode_list_creator.py

1. **Organize your video files**:
   ```
   A:/Video/Film & TV/
   ├── top_gear/
   │   ├── S15E01.mp4
   │   ├── S15E02.mp4
   │   └── S15E03.mp4
   ├── father_ted/
   │   ├── S01E01 Good Luck Father Ted.mp4
   │   ├── S01E02 Entertaining Father Stone.mp4
   │   └── S01E03 The Passion of Saint Tibulus.mp4
   └── blackadder/
       ├── S01E01 The Foretelling.mp4
       ├── S01E02 Born to be King.mp4
       └── S01E03 The Archbishop.mp4
   ```

2. **Run the episode list creator**:
   ```bash
   python episode_list_creator.py
   ```

3. **Answer the prompts**:
   ```
   Base URL: A:/Video/Film & TV/
   Directory name: top_gear
   Series title: Top Gear
   Series description: Motoring show with Jeremy Clarkson
   ```

4. **Save the output** as `programme lists/top_gear.json`

### Example Programme List Structure:
```json
{
  "title": "Top Gear",
  "description": "Motoring show with Jeremy Clarkson",
  "episodes": [
    {
      "url": "top_gear/S15E01.mp4"
    },
    {
      "url": "top_gear/S15E02.mp4"
    },
    {
      "url": "top_gear/S15E03.mp4"
    }
  ]
}
```

## Configuring Your Schedule

### The nmptv.json File

This file controls what shows play when. Here's how it works:

```json
{
  "channel_name": "Your Channel Name",
  "base_url": "A:/Video/Film & TV/",
  "template": [
    {
      "start": "10:00",
      "list": ["top_gear"],
      "index": [0, 0],
      "movement": 1
    },
    {
      "start": "11:00", 
      "list": ["father_ted"],
      "index": [0, 0],
      "movement": 1
    }
  ]
}
```

### Understanding the Template Fields:

- **start**: What time the show starts (24-hour format)
- **list**: Array of programme list names (can have multiple for rotation)
- **index**: [list_index, episode_index] - tracks progress through episodes **DO NOT MODIFY MANUALLY - the system updates this automatically**
- **movement**: How many episodes to advance total. If you have Top Gear 3 times in your schedule, set this to 3 so each slot gets a different episode instead of repeating the same one

### Using the Schedule Editor

For easier editing, use the included GUI:
```bash
python "schedule editor V9.py"
```

This provides a user-friendly interface to:
- Load/save schedule files
- Add/edit time slots
- Manage show rotations
- Set movement patterns

## Running the System

### Step 1: Generate Commands
```bash
python listings_creator.py
```

This reads your `nmptv.json` and creates `command_output.json` with all the OBS commands.

### Step 2: Start Playout
```bash
python aquarius.py
```

This connects to OBS and executes the commands at the scheduled times.

## Understanding Filler Content

The system automatically fills gaps between programmes:

### Fill Logic:
- **> 400 seconds**: Clock → OS 1 (teletext) → Ident (complex fill)
- **50-400 seconds**: Breakfiller → Ident (medium fill)
- **15-50 seconds**: Ident only (short fill)
- **< 15 seconds**: Clock only (minimal fill)

### Required OBS Scenes:
- **Clock**: Shows current time
- **Ident**: Channel branding/logo
- **Breakfiller**: Short programmes (30-second segments)
- **OS 1**: Teletext/information pages

## Example Daily Schedule

```json
{
  "channel_name": "My TV Channel",
  "base_url": "A:/Video/Film & TV/",
  "template": [
    {
      "start": "09:00",
      "list": ["top_gear"],
      "index": [0, 0],
      "movement": 1
    },
    {
      "start": "10:00",
      "list": ["father_ted"],
      "index": [0, 0], 
      "movement": 1
    },
    {
      "start": "10:30",
      "list": ["blackadder"],
      "index": [0, 0],
      "movement": 1
    },
    {
      "start": "11:00",
      "list": ["top_gear"],
      "index": [0, 1],
      "movement": 1
    }
  ]
}
```

## Troubleshooting

### Common Issues:

1. **"Error opening nmptv.json"**:
   - Ensure the file exists in the same directory
   - Check JSON syntax is valid

2. **WebSocket connection fails**:
   - Check OBS WebSocket is enabled (no password!)
   - Verify port 4455 is correct
   - Make sure OBS is running

3. **Videos don't play**:
   - Check file paths in programme lists
   - Ensure video files exist
   - Verify FFprobe can read video durations

4. **"Skipping episode due to metadata error"**:
   - Video file is corrupted or unsupported format
   - Check FFprobe can analyze the file

### Testing:
1. Start with a simple 1-hour test schedule
2. Use short video clips initially
3. Monitor the console output for errors
4. Test each OBS scene manually first

## File Structure

Your working directory should look like this:
```
aquarius/
├── programme lists/
│   ├── top_gear.json
│   ├── father_ted.json
│   └── blackadder.json
├── nmptv.json
├── aquarius.py
├── listings_creator.py
├── episode_list_creator.py
├── schedule editor V9.py
├── command_output.json (generated)
└── nmptv.json.bak (backup)
```

## Advanced Tips

### Multiple Show Rotation:
```json
{
  "start": "15:00",
  "list": ["some_mothers_do_ave_em", "fawlty_towers"],
  "index": [0, 4],
  "movement": 1
}
```
This rotates between two shows when one runs out of episodes.

### Episode Advancement:
```json
{
  "movement": 3
}
```
This advances 3 episodes total. Useful when you have the same show multiple times in your schedule - ensures each slot gets a different episode rather than repeating the same one.

### Index Management:
The system automatically updates the `index` values in `nmptv.json` to track progress through your shows. **Never modify these manually** - let the system handle episode progression.

Remember: This is powerful but experimental software. Take time to understand how it works before running a full schedule!

