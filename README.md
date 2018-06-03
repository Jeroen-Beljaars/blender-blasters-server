# Blender Blasters Server

#### 1 Host your own server auto setup [Simple]
Note: the auto-setup will only work on linux servers!

Login to your linux VPS and clone the following repository
You can do this by executing the following command:
```sh
$ git clone https://github.com/Jeroen-Beljaars/blender-blasters-server.git
```
Now switch to the right directory by executing the following command:

```sh
$ cd blender-blasters-server
```

Now execute the auto-setup by executing the following command:

```
python3 setup.py
```

It might ask you to press Y sometimes if so press Y so the packages can continue to install
After te setup is finished a screen with information will appear once you see this screen press enter.

And execute the following command:
```sh
$ python3 manage_servers.py
```
And last but not least press:
**Cntrl + a + d**

If this all worked you can go ahead to step 3 if not then go to step 2

#### 2 Host your own server manual setup [Advanced]
If you want to host a game that is accessible from all over the world then you have to host the server on a Virtual Private Server. Once you’ve found a good server provider then go ahead and connect to it. 
Once you have connected to the server you will be able to execute commands. First we will download the server files from our cloud storage. 
Please copy the following command from beginning to end and paste it in the server terminal, and press enter.
```sh
$ git clone https://github.com/Jeroen-Beljaars/blender-blasters-server.git && cd blender-blasters-server
```
Now we have to change the settings of the server in order for the server to work.
To do this please execute the following command:
```sh
$ vi network_config.json
```
The content of the configuration file will now be displayed on the screen. You can change the position of the cursor with the arrow keys. Please navigate to the content next to the manager_ip which usually is “127.0.0.1”
When the cursor is located at the end of the ip press i. Remove the 127.0.0.1 and replace it with the ip of the server which can be found on the provider of your vps. 
Do the same for the server_ip.
The result is supposed to look like this:
https://image.ibb.co/hBWvOJ/image.png
![Expected Result](https://image.ibb.co/hBWvOJ/image.png)

Make sure you haven’t changed anything else then the IP’s! 
Now press ESCAPE (ESC)
Then press colon (:)
And type **wq** and then press enter.
If you want to run the script 24/7 then you have to install screen 
You can do this by executing the following commands:
```sh
$ sudo apt-get update
$ sudo apt-get install screen
```
Now execute the following command:
```sh
$ screen
```
And press enter
If you are still located in the right folder then type:

```sh
$ python3 manage_servers.py
```

Otherwise execute this:
```sh
$ cd blender-blasters-server && python3 manage_server.py
```
And now the server is running! 
Now press cntrl+a+d
And that’s it for the server side!

#### 3 Configure the game [Simple]
Open the folder that contains the .blend file. Then navigate to Scripts > Network
and open network_config.json with a text editor and change the IP’s to the IP of your server.