TAB ASSET LAYOUT
================
Each main-menu tab has its own folder under assets/tabs/:

assets/tabs/story/
assets/tabs/characters/
assets/tabs/map/
assets/tabs/options/
assets/tabs/developer/

The code accepts .png, .jpg, .jpeg, .webp and .bmp.

For every tab folder:
  background.<ext>   = image/background shown after opening the tab
  <tab>.<ext>        = image shown on the main menu tab itself

Examples:
  tabs/map/background.png
  tabs/map/background.webp
  tabs/map/background.jpg
  tabs/map/map.png
  tabs/map/map.webp
  tabs/map/map.jpg

Only one file for each name is normally needed. If several formats exist,
the loader prefers: PNG, JPG/JPEG, WEBP, BMP, then alphabetical order.

CHARACTERS TAB EXTRA IMAGES
  tabs/characters/lucia.<ext>
  tabs/characters/jason.<ext>

MAP
  tabs/map/map.<ext> is the actual map image used by the zoom/pan map.

You can add your own files without changing Python code as long as the base
names stay the same. Case does not matter.
