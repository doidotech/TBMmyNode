#!/bin/bash
#-------------------------------------------------------------------------------
#   Copyright (c) 2020 DOIDO Technologies.
#   Version  : 1.0.1
#   Location : github
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# This script is used to create a MyNode ST7735 lcd service that starts at boot
# systemd is used.
#-------------------------------------------------------------------------------

# Get current user password
gettingPassword=true

# Loop until user enters matching passwords
while $gettingPassword 
	do
    		echo
		read -s -p "Enter Password: " newPassword
		echo
		read -s -p "Re-Enter Password: " re_EnteredPassword
		echo
		#echo $newPassword
		#echo $re_EnteredPassword

		# Check if user correctly re-entered password
		if [ "$newPassword" = "$re_EnteredPassword" ]; then
    			echo "Creating MyNode ST7735 LCD Service."
    			gettingPassword=false
			
			# Get current working directory
			cwd=$(pwd)

			# Create A Unit File
			sudo echo "[Unit]
Description= MyNode ST7735 LCD Service

[Service]
Type=simple
ExecStart=/usr/bin/python3 $cwd/MyNodeLCDV2.py $newPassword

[Install]
WantedBy=multi-user.target" > /lib/systemd/system/myNodeST7735LCD.service

			# The permission on the unit file needs to be set to 644
			sudo chmod 644 /lib/systemd/system/myNodeST7735LCD.service

			# Configure systemd
			sudo systemctl daemon-reload
			sudo systemctl enable myNodeST7735LCD.service
			# Start the service
			systemctl start myNodeST7735LCD.service
			echo "Done Creating MyNode ST7735 LCD Service."
		else
    			echo "Entered passwords do not match!!!"
		fi
	done

