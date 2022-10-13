# Creo BOM Export Tool

## How to Use
- Place *.bom file from Creo client into creo_bom_imports folder
- Place any images you want attached to Excel viewer in creo_images directory
- run creoBOMtool.py from root folder
- Import *.bom file from selection menu
- Browse tree / export XLS or JSON file as needed (located in exports folder)

## How to export images automatically from Creo

Add following code to your config.pro file or enable via configuration manager

bitmap_size 1000 !Suggested pixel size for image
save_bitmap alllevels !NOTE: This will save jpeg for all subassemblies every time you do a save-as or backup, disable by default
save_bitmap_type jpeg
