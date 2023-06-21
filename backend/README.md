# VisionFive 2 WS2812B Demo

## Installing Dependencies & Running the project

```
pip install virtualenv
# Create a virtual environment
python -m venv vf2-ws2812b-demo
```

Then enter the virtual environment:

 - For (Windows) Command Prompt users: `vf2-ws2812b-demo\Scripts\activate.bat`
 - For (Windows) PowerShell users: `vf2-ws2812b-demo/Scripts/Activate.ps1`
 - For macOS/Linux users: `vf2-ws2812b-demo/bin/activate`

```
# Install Dependencies
pip install -r requirements.txt
# Run the program (we need sudo for /dev/spi* access)
sudo python3 app.py
# Remember to exit
deactivate
```

## License

WTFPL
