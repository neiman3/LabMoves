# Lab Moves Tool

## About
This tool will automate creation of lab move schedules. It will generate a spreadsheet file with the full schedule, dates, and equipment requriements, broken down by both lab section view and by room view.

## Installation
- Download this repository.
- Ensure Python3 is installed on your machine.
- [Create a new python venv](https://docs.python.org/3/library/venv.html) in your base folder.
- Activate the venv
- Install all requirements using `requirements.txt` file by running `pip3 install -r requirements.txt`
- Make a launcher script. On Windows it could look like this:

```
@echo off
call ".\Scripts\activate.bat" & call ".\venv\Scripts\python.exe" .\main.py
pause
exit
```

## Use
You should have the following information ready before you start:
- [ ] Lab assistant schedule
- [ ] Course number, section number, instructor, room number, number of groups, day, and time of all lab classes
- [ ] Lab manuals for all lab courses (or a list of default equipment)
- [ ] Quarter start and end dates
- [ ] Dates of academic holidays
- [ ] Description of all required inventory items

Activate the venv and run the `main.py` script. To start a new project, type `1`. If you want to recalculate a completely filled out schedule, use `2`. Wait for the sheet to open and for the program to say STEP 1.

### Step 1
Fill out sheets 1 through 3 in Excel. When you fill out the inventory, make sure to assign a unique shortcode to each inventory item. For example, for Resistor Box II, you could make a shortcode called `RB2`. Make sure each one is unique. You will reference these shortcodes frequently in steps 2 and 3, so it may be a good idea to keep another separate excel file open that you paste into the working sheet. 

Close the sheet, return to the terminal, and press enter.

### Step 2
The spreadsheet will open again, this time with equipment autofilled into the Equipment tab. If you see a warning that the sheet is corrupted, just click "repair" and save as the original file name, overwriting the existing excel file. This happens frequently due to a issue with the excel library- it's totally fine. Check to see if the console shows STEP 2. Fill out the equipment requirements for each week of each course using the lab manuals. Use the shortcodes you defined in step 1.

The quantities you enter on this sheet are per-group numbers. If you need a set number of items for an entire class (not per group), enter the quantity as a negative number.

Next, close the sheet, return to the terminal, and press enter.

### STEP 3
The equipmment schedule will now auto-populate into the Master Schedule tab. You can customize the exact schedule of every lab section in this tab. This is useful if an instructor has an alternate schedule, or if a lab needs to be rescheduled, modified, etc.

This uses a specific notation for specifying the equipment. If a lab needs 24 decade resistor boxes, one LCR meter, and 10 5mH inductors, and your shortcodes for those items were DRB, LCR, and IND5MH, you would enter this on a single line in the equipment column: `24 x DRB, 1 x LCR, 10 x IND5MH` (case sensitive). 

Make your final modifications to the schedule. Save and close.

### STEP 4 (OR) Open existing project

The program will now create a new excel file with the schedule output. It is named from your project file. A project named `foobar` will create a excel file in `./Output Files/foobar.xlsx` and an output excel file in `./Output Files/foobar-output.xlsx`. If you select option 2 at startup, you can load in the previously filled `foobar.xlsx` file and re-generate a new schedule. The `foobar-output.xlsx` file is always overwritten.

#### Formatting hints for the schedule
There are a few steps you can take to increase readability of the final schedule.
- Firstly, you can format the output sheets as tables within Excel.
- You should keep text wrapping on but make the columns nice and wide. The second tab (room schedule) should have one line per equipment. You can autofit the columns after widening them to make excel set the widths correctly.
- You can sort the table however you like (by date, section, instructor, etc).

## Customization and Troubleshooting
If you need to add a new room number, you have to manually edit `templates/lab_rooms_layout.dat`. There are in-file instructions. This file generates a Graph using the `nplcore.py` Graph class to model the rooms. This is for future-proofing spatial optimizations when automatically calculating lab moves (future feature). If you use a room number in the spreadsheet that doesn't exist in this graph, it won't show up in the list.
