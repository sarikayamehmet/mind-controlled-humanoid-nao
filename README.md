# mind-controlled-humanoid-nao
Mind controlled Humanoid Robot using Brain-Computer Interface

# 1. Requirements
	- Install Webots
	- Install Anaconda for python
	- Go to the Windows environment variables
	- Add "C:\Users\{UserName}\Anaconda3" to PATH
	- Add "C:\Users\{UserName}\Anaconda3\Library\bin" to PATH
	- Add "LD_LIBRARY_PATH" to System variables with value "C:\Program Files\Webots\lib"

# 2. Neurosky Mindwave Requirements
	- For Mindwave mobile 2, match it with computer bluetooth
	- For Mindwave RF version, insert RF dongle
	- Download Mindwave bundle for windows (http://download.neurosky.com/updates/mindwave/education/1.1.28.0/MindWave.zip)
	- Run Mindwave App Central
	- Ensure your mindwave signal quality
	
# 3. Application
	- Run webots\project624e.wbt
	
# 4. Motions
	- motions folder includes Nao motions

# 5. Controllers
	- "controllers\nao_mindwave" folder includes codes to collect EEG signal and control Nao robot
	- "controllers\nao_mindwave\nao_mindwave_reader.py" script listens Mindwave default port (13584) and records siqnalQuality, blinkStrength, attention and meditation values into "controllers\nao_mindwave\data_eeg.csv" file.
	- "controllers\nao_mindwave\nao_mindwave.py" script is controller for webots. It reads brainwaves from "controllers\nao_mindwave\data_eeg.csv" file and control Nao robots according to blinks and attention level of subjects.

# 6. Demo
![Nao-demo](https://github.com/sarikayamehmet/mind-controlled-humanoid-nao/raw/master/Nao-demo.gif)
