


[//]: # (If you can read this, you are viewing this document incorrectly.)
[//]: # (This is a Markdown document.  Use an online Markdown viewer to)
[//]: # (view this file, such as https://dillinger.io/)



# CFG-Util

## Interact with bitcoin mining ASICs using a simple GUI.

---
## Tabs:
* Scan
* Pools
* Configure
* Command


### Scan Tab - 
#### Fields
* Scan IP: The IP/network to scan.  Defaults to 192.168.0.1/24 subnet, and you can pass just a single IP address on a subnet, which will use /24 subnet as a default, or an IP range such as 192.168.1.20 - 192.168.1.55

#### Buttons
* Scan: Scan the network entered in Scan IP.
* ALL: Select all items in the table (You can also select the table and press CTRL+A).
* REFRESH DATA: Refresh the data for the miners in the table.
* OPEN IN WEB: Open all selected miners in your web browser.


### Pools Tab -
#### Additional Tabs
* All: Data on both pools.
* Pool 1: Data on pool 1.
* Pool 2: Data on pool 2.

#### Buttons
* ALL: Select all items in the table (You can also select the table and press CTRL+A).
* REFRESH DATA: Refresh the data for the miners in the table.
* OPEN IN WEB: Open all selected miners in your web browser.


### Configure Tab - 
#### Fields
* Config Field: Located on the right side of the screen, this is where imported and generated configs are stored for editing.

#### Buttons
* IMPORT: Import a config from the selected miner.
* CONFIG: Configure all selected miners with the config in the config field.
* GENERATE: Generate a configuration.
* ALL: Select all items in the table (You can also select the table and press CTRL+A).
* OPEN IN WEB: Open all selected miners in your web browser.
* Append IP to Username: Append the last octet of the IP address to the config when configuring.

### Command Tab - 
#### Fields
* Custom Command: The custom command to send to the miners.

#### Buttons
* Send Command: Send the custom command in the custom command field to the selected miners.
* ALL: Select all items in the table (You can also select the table and press CTRL+A).
* LIGHT: Turn on the fault light on selected miners.
* REBOOT: Reboot selected miners.
* RESTART BACKEND: Restart the mining process on selected miners.
