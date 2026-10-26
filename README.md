# 🚗 Garage System

A command-line system for a car maintenance center. It opens the webcam, reads the
car's license plate (OCR), and then:

- **Plate already registered** → shows the vehicle, its service history and the upcoming maintenance.
- **Plate not registered** → asks for the owner and car details and saves them.

All data is stored in a JSON file (`data/vehicles.json`).

## Requirements
- **Python 3.11 or newer** (check with `python3 --version`)
- **macOS** for automatic plate reading with the camera (other systems can still type the plate manually)
- A webcam (optional)
- Internet, only once, to install the libraries

## Quick start

**1. Download the project**
```bash
git clone <your-repo-url>
cd <repo-folder-name>
```

**2. Create a virtual environment**
```bash
python3 -m venv venv
```

**3. Activate it**
```bash
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

**4. Install the libraries**
```bash
pip install -r requirements.txt
```

**5. Run**
```bash
python main.py
```
Run it from the **terminal**, inside the project folder.
On Windows use `python` instead of `python3` if needed.

**6. Try the demo**
Choose **Enter plate manually** and type `ABC1234`. This demo car has a service history
and an overdue oil change.



## Camera (macOS only)
Before the first scan, allow your terminal (or VS Code) to use the camera:
**System Settings → Privacy & Security → Camera**, then restart the terminal.

Choose **Scan plate with camera**:
1. Hold the plate in front of the camera. A **green box** appears around it.
2. When the same number is read 3 times in a row, it is captured automatically.
3. Confirm the number (or type it by hand). The system then shows the car or registers it.

Keys (click the camera window first):

| Key | Action |
|-----|--------|
| Space / Enter | accept the number shown |
| M | type the plate manually |
| C | switch camera (Mac webcam / iPhone) |
| Esc | cancel |


Always check the detected plate before confirming; OCR can make mistakes.
If there is no camera or you are not on macOS, the program still works with manual entry.

## Features
- Interactive menu (arrow keys) with colored tables
- Live webcam plate scan using Apple Vision (macOS)
- Service history and total cost per vehicle
- Automatic upcoming maintenance: `OK`, `SOON`, `OVERDUE`, `NO RECORD`
- Input validation (name, phone, year, mileage, cost) and error handling (no camera, corrupted JSON)

## Maintenance rules
| Service    | Every                     |
|------------|---------------------------|
| Oil change | 5,000 km or 6 months      |
| Filters    | 10,000 km or 12 months    |
| Brakes     | 20,000 km                 |
| Tires      | 40,000 km                 |

A service is `OVERDUE` when the km or date limit is passed, and `SOON` when less than
500 km or 30 days remain. Rules can be edited in `SERVICE_RULES` inside `garage/service.py`.
The status depends on today's date, so the demo car may show different results over time.

## Input rules
- **Owner name:** English letters and spaces only (no numbers).
- **Phone:** exactly 10 digits, starting with `05`.
- **Mileage of a new service:** cannot be lower than the car's recorded mileage.
- **Plate (manual entry):** 4 digits then 3 English letters, no spaces, e.g. `8301UJB` (capital or small letters).


## Data files and problems

The program keeps its data in two files inside the `data/` folder:

| File | What it stores |
|------|----------------|
| `data/vehicles.json` | all vehicles, owners and service history |
| `data/camera.json` | the camera to use: `0` = Mac webcam, `1` = iPhone |

**Important rules**
- Stop the program **before** editing a JSON file by hand, and **save** the file (`Cmd+S` / `Ctrl+S`)
  before running the program again. The program only reads the file when it starts.
- Edit the JSON of the same project folder you are running.

### If the vehicle data does not match the JSON file
This happens when `vehicles.json` was edited by hand with a mistake, has a missing comma or bracket,
has old data from another version, or the program shows an error such as
`vehicles.json is corrupted`.

1. Close the program.
2. **Delete `data/vehicles.json`** (or accept the backup question when the program offers it).
3. Run `python main.py` again. The system creates a **new empty vehicle file** automatically
   the first time you register a car.

The old cars are removed with the file. To bring the demo car back, create `data/vehicles.json`
with this content:

<details>
<summary>Demo vehicle (1234ABC)</summary>

```json
{
  "vehicles": [
    {
      "plate": "1234ABC",
      "owner": {
        "name": "Ahmed Alharbi",
        "phone": "0501234567"
      },
      "make": "Toyota",
      "model": "Camry",
      "year": 2018,
      "mileage": 52300,
      "services": [
        {
          "type": "Oil change",
          "date": "2025-12-10",
          "mileage": 45000,
          "cost": 180.0,
          "notes": "Synthetic oil 5W-30"
        },
        {
          "type": "Filters",
          "date": "2025-12-10",
          "mileage": 45000,
          "cost": 120.0,
          "notes": "Oil and air filters"
        },
        {
          "type": "Brakes",
          "date": "2026-03-01",
          "mileage": 40000,
          "cost": 650.0,
          "notes": "Front brake pads replaced"
        }
      ]
    }
  ]
}
```
</details>

### Switching between the iPhone and the Mac camera
Press **C** in the camera window to switch. The chosen camera is saved in `data/camera.json`
and used the next time you run the program.

If the wrong camera keeps opening, or the camera does not switch correctly:

1. Close the program.
2. **Delete `data/camera.json`**.
3. Run `python main.py` again. The program starts with the **Mac webcam** and creates a
   **new `camera.json`** automatically when you press **C** to switch the camera.

You can also create it yourself:
```json
{
  "camera_index": 0
}
```
Use `0` for the Mac webcam or `1` for the iPhone.
To stop the iPhone from being used automatically, turn off *Continuity Camera* on the iPhone
(Settings → General → AirPlay & Handoff).

## Troubleshooting
- **`pip install` fails:** check that Python is 3.11 or newer.
- **Camera does not open:** allow the terminal in Privacy & Security → Camera, then restart it.
- **Wrong camera opens (iPhone / Mac):** press **C**, or delete `data/camera.json` (see above).
- **Plate read wrongly:** answer "No" at the confirmation and type it manually.
- **Data problems:** delete `data/vehicles.json` (see above).
