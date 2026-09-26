# wifi counter (vibe coding)

How to Set Up and Run the Counter Server on macOS

This guide provides step-by-step instructions on how to deploy the Flask + WebSocket server on your MacBook. This server acts as the central hub, receiving data from your ESP32-C3 counters via Wi-Fi and pushing real-time updates to your web browser.

📋 Prerequisites

· A MacBook running macOS.
· Terminal application (pre-installed on macOS).
· Python 3 installed.
· Your Mac and the ESP32-C3 devices must be connected to the same Wi-Fi network.

---

Step 1: Open Terminal and Verify Python

First, open the Terminal app (press Command + Space, type "Terminal", and hit Enter).

Check if Python 3 is installed by running:

```bash
python3 --version
```

If you see a version number (e.g., Python 3.11.5), you are good to go. If not, install it via Homebrew by running brew install python3.

Step 2: Create a Project Folder and Virtual Environment

It is best practice to create a dedicated folder and a virtual environment for your Python project.

1. Create the project folder and navigate into it:
   ```bash
   
   mkdir ~/Desktop/masterful_studio
   cd ~/Desktop/masterful_studio
   
   ```
2. Create a virtual environment:
   ```bash
   
   python3 -m venv .venv
   
   ```
3. Activate the virtual environment:
   ```bash
   
   source .venv/bin/activate
   
   ```
   Note: Your terminal prompt will now start with (.venv), indicating the environment is active.

Step 3: Install Dependencies

With the virtual environment activated, install the required Python libraries:

```bash

pip install flask flask-socketio

```

(Note: We use the built-in threading mode in the code, so you do NOT need to install eventlet or gevent, which often cause compatibility issues with newer Python versions.)

Step 4: Add the Server Code

Create a new file named app.py inside your masterful_studio folder:

```bash

touch app.py

```

Open this file with a text editor (like VS Code, Sublime Text, or TextEdit) and paste the complete app.py Flask server code we developed earlier. Make sure to save the file.

Step 5: Run the Server

In your Terminal (make sure you are in the masterful_studio directory and (.venv) is active), start the server:

```bash

python3 app.py

```

If successful, you will see output similar to:

```text
>>> 正在啟動 Masterful Studio 伺服器...
>>> 伺服器準備就緒，請打開瀏覽器訪問 http://127.0.0.1:5000
>>> 若要停止伺服器，請按 Ctrl + C
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

Keep this Terminal window open and running. If you close it, the server will stop.

Step 6: Find Your Mac's Local IP Address

Your ESP32-C3 devices need to know where to send the data. Open a new Terminal tab (Command + T) and run:

```bash

ipconfig getifaddr en0

```

· This will output your local IP address (e.g., 192.168.1.100).
· If it returns nothing, try ipconfig getifaddr en1 (if using Ethernet).
· Copy this IP address. You will need to paste it into the serverHost variable in your ESP32-C3 Arduino code.

Step 7: Configure macOS Firewall (Crucial)

macOS firewall often blocks incoming connections by default. When you first ran python3 app.py, a popup may have asked to allow incoming connections. If you missed it, or if your ESP32 cannot connect, do this:

1. Go to System Settings > Network > Firewall.
2. Click Options...
3. Click the + button.
4. Navigate to your project folder (~/Desktop/masterful_studio/.venv/bin/), select the python3 executable, and click Add.
5. Change its setting from "Block incoming connections" to "Allow incoming connections".
6. Click OK.

Step 8: Test the Server

1. Local Test (on your Mac): Open a browser and go to http://127.0.0.1:5000. You should see the 9-zone counter interface.
2. Network Test (on your phone): Connect your phone to the same Wi-Fi, open a browser, and go to http://<YOUR_MAC_IP>:5000 (e.g., http://192.168.1.100:5000). If you can see the page, your server is fully accessible.

Step 9: Keep Server Running in Background (Optional)

If you want to close the Terminal window but keep the server running, use the nohup command:

```bash

nohup python3 app.py > server.log 2>&1 &

```

· This runs the server in the background.
· Any print statements (like "Zone 1 pressed") will be saved to server.log.
· To stop the server later, run ps aux | grep app.py to find its PID, then kill <PID>.

---

Next Steps

Now that your Mac server is live:

1. Open your ESP32-C3 Arduino code.
2. Update the ssid and password to match your Wi-Fi.
3. Update the serverHost to the IP address you found in Step 6.
4. Set the DEVICE_ID (1-9) for each board and upload the code.
5. Press the physical buttons and watch the magic happen on your browser screen!
