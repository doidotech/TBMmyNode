Install LCD drivers on Bitcoin Machine(Mynode)

1. If there was a previous myNodeST7735LCD service:

a. Run the command to stop the current running service.
sudo systemctl stop myNodeST7735LCD.service 

b. Run the command to disable the service.
sudo systemctl disable myNodeST7735LCD.service 

c. Run the command to delete the service unit file.
 sudo rm /lib/systemd/system/myNodeST7735LCD.service 

d. Safely reboot the device, the run the following commands to reinstall new MynodeLCD.

git clone https://github.com/doidotech/TBMmyNode.git

cd TBMmyNode/
cd MyNodeLCDV2_0_4/
chmod +x myNodeLCDServiceSetup.sh

sudo ./myNodeLCDServiceSetup.sh

Reboot the machine from Mynode Dashboard.
