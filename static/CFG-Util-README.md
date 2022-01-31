


[//]: # (If you can read this, you are viewing this document incorrectly.)
[//]: # (This is a Markdown document.  Use an online Markdown viewer to)
[//]: # (view this file, such as https://dillinger.io/)



# CFG-Util

## Interact with bitcoin mining ASICs using a simple GUI.

---
## Input Fields
### Network IP:
* Defaults to 192.168.1.0/24 (192.168.1.0 - 192.168.1.255)
* Enter any IP on your local network, and it will automatically load your entire network with a /24 subnet (255 IP addresses).
* You can also add a subnet mask by adding a / after the IP and entering the subnet mask.
* Press Scan to scan the selected network for miners, and get data on them.

### IP List File:
* Use the Browse button to select a file.
* Use the Import button to import all IP addresses from a file, regardless of where they are located in the file.
* Use the Export button to export all IP addresses (or all selected IP addresses if you select some) to a file, with each separated by a new line.

### Config File:
* Use the Browse button to select a file.
* Use the Import button to import the config file (only toml format is implemented right now).
* Use the Export button to export the config file in toml format.


---
## Data Fields
### Buttons:
* ALL: Selects all miners in the table, or deselects all if they are already all selected.
* REFRESH DATA: Refreshes data for the currently selected miners, or all miners if none are selected.
* OPEN IN WEB: Opens all currently selected miners web interfaces in your default browser.

### Table:
* Click any header in the table to sort that row.
  * You can copy (CTRL + C) a list of IP's directly from the rows selected in the table.

* #### IP:
  * Contains all the IP's scanned.

* #### Model:
  * The model of the miners scanned.

* #### Hostname:
  * The hostname of the miners scanned.
  * ? will be displayed if the tool is unable to get it.

* #### Hashrate:
  * The hashrate of the miners scanned.

* #### Temperature:
  * The average board temperature of the miners scanned.

* #### Current User:
  * The current first pool user of the miners scanned.

* #### Wattage
  * The current wattage of the miners scanned.
  * 0 W will be displayed if it is unknown.

### Config:
* This field contains the configuration file either imported from a miner or from a file.
* The IMPORT button imports the configuration file from any 1 selected miner to the config textbox.
* The CONFIG button configures all selected miners with the config in the config textbox.
* The LIGHT button turns on the fault light/locator light on miners that support it (Only BraiinsOS for now).
* The GENERATE button generates a new basic config in the config textbox.
