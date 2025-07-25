LAN Documentation

Detailed step-by-step guide for setting up the LAN transfer software on a new device.

Step1
Install Python on the computer.
Open Official Website https://www.python.org/downloads/ 
Download the latest version of Python for Windows.
Click the check box        - Add to PATH below Install.
Setup it.

Step2
Open Command Prompt / cmd.
Write Python --version.
If it shows this then everything is fine.

C:\Users\HP>Python --version
Python 3.12.6

If it shows 

doesn’t recognised.

Then open Settings > Apps > App execution aliases > Enable all for Python.
Recheck 
Write Python --version.

Step3
Add the LAN Transfer Software folder in the computer.

Step4
Windows + r write wf.msc click ok.
Windows Defender Firewall with Advanced Security on Local Computer > Inbound Rules > Find File and Printer Sharing (Echo Request) it should be 4 to 5 - Enable All.

Step5
Close Everything.
Open Command Prompt / cmd.
Write ipconfig > Note Down ipv4 address of the device.

Step6
Open Command Prompt / cmd on a different computer in the same network.
Write ping 192.168.1.13 (ip address example).
If it shows this then everything is fine.

C:\Users\HP>ping 192.168.1.13

Pinging 192.168.1.13 with 32 bytes of data:
Reply from 192.168.1.13: bytes=32 time<1ms TTL=128
Reply from 192.168.1.13: bytes=32 time<1ms TTL=128
Reply from 192.168.1.13: bytes=32 time<1ms TTL=128
Reply from 192.168.1.13: bytes=32 time<1ms TTL=128

Ping statistics for 192.168.1.13:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 0ms, Maximum = 0ms, Average = 0ms


Step7
Open Command Prompt / cmd.
cd Desktop > cd lan_transfer.
Write pip install -r requirements.txt .
After installing all required packages
Close the Command Prompt / cmd.

Step8
Open the main foder lan_transfer
Find ip_config.txt
Right Click > Edit > Rename it with your actual device ip address

Step9
Close Everything.
Create a Shortcut on Desktop  > Location - lan_transfer > Select run_sender. Name it Sender.
Create a Shortcut on Desktop  > Location - lan_transfer > Select run_receiver. Name it Receiver.

Step10
Click the Sender > it will open the default browser automatically
Click the Receiver > it will open the default browser automatically

Final Step
Add the Device Name and ip address in the Main Google SpreadSheet > Lan Transfer Logs > Devices.

To close it, end the python.exe process from the Task Bar / Task Manager.

