# Bulb File Explorer
<img width="680" height="398" alt="image" src="https://github.com/user-attachments/assets/e09fb004-7c59-480d-9742-af87683bcc38" />
<br>

***Bulb*** is a simple file explorer for your [Tulip Creative Computer](https://tulip.computer/)!

With it you can:
- ➕📁 create new directories
- ➕📄 create new files
- ➕⚡ create new app templates
- 🔀 rename files and directories
- 🗑️ delete files and directories
- 📋 copy, ✂️ cut, and 📋 paste
- ✏️ edit files in the default editor
- ⚡ execute programs
- 🔼 upload to Tulip World

## Try it!
You can check it out in action on [Tulip Web](https://share.tulip.computer/xhIQ9W).
Just type this command into the REPL and hit Enter:
```
run('bulb.py')
```

## Download it!
Download it from Tulip World with the following command:
```
world.download('bulb', 'kreativkodok')
```
Or you can download it from this repo:
1. Download from [releases](https://github.com/KreativKodok/Bulb/releases)
2. Install `mpremote` using [this guide](https://github.com/shorepine/tulipcc/blob/main/docs/getting_started.md#using-mpremote)
3. *(Windows only)* From the downloaded files, drag `bulb.py` onto `tulip_mpremote.bat`

## Launch it!
Insert the following in your `boot.py` or run it from REPL:
```
run('bulb')
```

## Use it!
- Use the top row to navigate the directory tree


<img width="676" height="41" alt="image" src="https://github.com/user-attachments/assets/b109998d-e2fa-4318-92b7-0113c8c8369d" />
<br>

- Select files and directories by tapping on them
- Long pressing will enter directories and execute executables


<img width="675" height="283" alt="image" src="https://github.com/user-attachments/assets/f3fe0b89-d0c7-469f-8740-55fc6eceef06" />
<br>

- Use the bottom row of commands to manipulate files


<img width="671" height="63" alt="image" src="https://github.com/user-attachments/assets/056b99b2-211f-4baf-ba5c-5d735eb0ccd1" />
<br>

## Bonus: Add it to your Launcher!

<img width="326" height="220" alt="image" src="https://github.com/user-attachments/assets/42925214-a531-4278-976c-dee83e91617d" />
<br>

Put the following commands in your `boot.py`:
```
import bulb
bulb.add_to_launcher()
```
you can also specify its index in the list:

```
import bulb
bulb.add_to_launcher(index = 3)
```
**Known bug:** closing ***Bulb*** later will also remove it from the Launcher :(

