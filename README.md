# Steps:
=========
> Make Sure You have Python installed on your system 
>

- After Installing the Zip Unzip and Run `pip install -r requirments.txt` in the current directory of the file

- After finishing to install the required libraries now enter in edit mode to main.py and add the IP-s of your device and path to the directory you wish to save the logs.

- Put the Username and Password also the Enable Secret in .env file
!!Attention it is not suggested to store plaintext passwords in scripting files.(To reduce the risks of the following bug, make sure this user only has read access to the devices).

- Now from terminal run `python main.py` this will create folder with date and save every log by each device in a file daily in realtime in case a syslog message appears in the network on port 514.
 