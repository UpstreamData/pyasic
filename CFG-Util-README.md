# CFG-Util

## Interact with bitcoin mining ASICs using a simple GUI.

---
## Input Fields
### Network IP:
* Defaults to 192.168.1.0/24 (192.168.1.0 - 192.168.1.255)
* Enter any IP on your local network and it will automatically load your entire network with a /24 subnet (255 IP addresses)
* You can also add a subnet mask by adding a / after the IP and entering the subnet mask
* Press Scan to scan the selected network for miners

### IP List File:
* Use the Browse button to select a file
* Use the Import button to import all IP addresses from a file, regardless of where they are located in the file
* Use the Export button to export all IP addresses (or all selected IP addresses if you select some) to a file, with each seperated by a new line

### Config File:
* Use the Browse button to select a file
* Use the Import button to import the config file (only toml format is implemented right now)
* Use the Export button to export the config file in toml format


---
## Data Fields
### IP List:
* This field contains all the IP addresses of miners that were either imported from a file or scanned
* Select one by clicking, mutiple by holding CTRL and clicking, and select all between 2 chosen miners by holding SHIFT as you select them
* Use the ALL button to select all IP addresses in the field, or unselect all if they are selected

### Data:
* This field contains all data that is collected by selecting IP addresses and hitting GET
* The GET button gets data on all selected IP addresses
* The SORT IP button sorts the data list by IP address, as well as the IP List
* The SORT HR button sorts the data list by hashrate, as well as the IP List
* The SORT USER button sorts the data list by pool username, as well as the IP List
* The SORT W button sorts the data list by wattage, as well as the IP List

### Config:
* This field contains the configuration file either imported from a miner or from a file
* The IMPORT button imports the configuration file from any 1 selected miner to the config textbox
* The CONFIG button configures all selected miners with the config in the config textbox
* The LIGHT button turns on the fault light/locator light on miners that support it (Only BraiinsOS for now)
* The GENERATE button generates a new basic config in the config textbox