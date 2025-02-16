# # Fan Control Script for Raspberry Pi

## 📋 Description
This script **automatically controls a fan** connected to **GPIO 23** based on the Raspberry Pi CPU temperature.  
It also provides a **compact GUI** to **manually control** the fan, adjust thresholds, and keep the fan off when needed.

---

## ⚡ Features
✅ **Monitors CPU temperature** every 5 seconds  
✅ **Turns ON the fan** when temperature exceeds a set threshold  
✅ **Turns OFF the fan** when temperature drops below another threshold  
✅ **Provides a GUI for manual control & threshold settings**  
✅ **Runs as a background process** and restores the GUI when reopened  
✅ **Runs at startup as a system service**  

---

## 📂 File Locations
| **File**              | **Path** |
|----------------------|---------|
| **Main script**      | `/home/pi/fan_control_gui.py` |
| **Service file**     | `/etc/systemd/system/fan_control.service` |
| **Log output**       | `/var/log/fan_control.log` |

---

## 🛠️ Hardware Setup
### 📌 GPIO Output
- The **fan is connected to GPIO 23**.
- **Wiring:**
  - **GPIO 23 (Pin 16) → Fan Control Input**
  - **GND (Pin 6) → Fan Ground**
  - **5V or External Power Source → Fan Power Input**

---

## 🚀 Installation & Setup
### 1️⃣ Install Dependencies
Run the following command to install required Python libraries:
```bash
sudo apt update
sudo apt install -y python3-pip python3-gpiozero
```

---

### 2️⃣ Move the Script to the Correct Location
Ensure the script is placed in the correct location:
```bash
mv fan_control_gui.py /home/pi/fan_control_gui.py
chmod +x /home/pi/fan_control_gui.py
```

---

### 3️⃣ Test the Script
To verify that it works, run:
```bash
python3 /home/pi/fan_control_gui.py
```
- The **GUI should open** in the top-right corner.
- The **fan should turn ON/OFF automatically** based on the temperature.

If the fan does not turn on, check the GPIO wiring.

---

### 4️⃣ Create a Systemd Service
Create a new service file:
```bash
sudo nano /etc/systemd/system/fan_control.service
```

Copy and paste the following content into the file:
```
[Unit]
Description=Fan Control GUI
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/fan_control_gui.py
WorkingDirectory=/home/pi
StandardOutput=append:/var/log/fan_control.log
StandardError=append:/var/log/fan_control.log
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Save and exit (`CTRL + X`, then `Y`, then `ENTER`).

---

### 5️⃣ Enable & Start the Service
Enable the service so it starts on boot:
```bash
sudo systemctl enable fan_control.service
```

Start the service manually:
```bash
sudo systemctl start fan_control.service
```

Check if it's running:
```bash
sudo systemctl status fan_control.service
```

If everything is working correctly, you should see **"Active: running"**.

---

## 🛑 Managing the Service
| **Command** | **Description** |
|------------|---------------|
| `sudo systemctl start fan_control.service` | Start the service manually |
| `sudo systemctl stop fan_control.service`  | Stop the service |
| `sudo systemctl restart fan_control.service` | Restart the service |
| `sudo systemctl status fan_control.service` | Check if the service is running |
| `sudo systemctl disable fan_control.service` | Disable the service on boot |

---

## ❌ How to Kill the Process Manually
If the GUI is stuck or you need to kill the process:
```bash
pkill -f fan_control_gui.py
```

If the **background process does not stop**, use:
```bash
kill $(cat /tmp/fan_control_socket) && rm -f /tmp/fan_control_socket
```

---

## 📝 Logs & Debugging
To view the service logs:
```bash
sudo journalctl -u fan_control.service --follow
```

If you need to clear the logs:
```bash
sudo truncate -s 0 /var/log/fan_control.log
```

---

## 🔥 Conclusion
Now, your **fan control script runs automatically at startup** and can be manually controlled via the **GUI**.  
If you ever need to modify the temperature thresholds, just open the GUI and update them.  

🚀 **Enjoy automatic cooling on your Raspberry Pi!** 🔥

---

### 💡 Future Improvements
- Add **fan speed control using PWM** instead of just ON/OFF.
- Integrate **temperature graphs** in the GUI.
- Implement **notifications** when the fan turns ON/OFF.

---

This README.md provides everything you need to **install, configure, and manage** the fan control script on Raspberry Pi! 🚀🔥 Let me know if you need further adjustments!
