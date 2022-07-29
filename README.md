This is a tool for a Corio2 750. Purpose is change the resolution and settings of a Corio2 750 since it canot save some settings to memory permanently.

Code is given as is.

Users are free to modify the settings based on their needs.

240p/480i settings are based on my resolution list. You may have to change yours based on your resolution list.

Actual Use:
Connect a Pi (with a IR receiver at GPIO 14) with this code running in the background. It waits for IR signals and changes display settings of the corio as needed.

Requirements:
1. Generic IR receiver conected at GPIO 14
2. PySerial installed
3. Python3
4. A Corio2 750
5. USB RS232 connected between Pi and Corio2 750
