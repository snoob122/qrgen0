# qrgen0 v1.2 - A pure python qr code generator

**qrgen0 v1.2** is a fully functional, zero-dependency qr code generator written entirely in Python - without a single import. Built from scratch in 10 days, it supports:

V1.0:
- All QR Version (1 - 40)
- Numeric, Alphanumeric and Byte Encoding
- A masking optimisation system
- Bitmap (.bmp) output without Pillow
- ASCII output for terminal or raw file rendering (stored in .txt file)
- A not the best but functional CLI
- Settings Saved automatically in config (.cfg) file

V1.1:
- Automatically create settings.cfg if not found and write default data to it
- The main file (qrgen0_v1.2.py) is the only file needed to run properly now
- Improve automatic saving system
- Added more configuration settings
- Small changes regarding the look of the CLI
- Changing the name of ascii file when written to prevent overriding
- Fixed some small bugs and improve user experience a little more
  (I want to organize the output a little more by adding folders, but I can not do that without importing, or I do not know how)

V1.2:
- Added a Little Logo
- Added a quiet zone thickness adjusting system
- Added a status to some settings to display action responses
- Added reset current settings to default settings
- Added example_files and change_logs to make files look more organized
- Added a system to generate qr from a file of choice alongside typing in directly
- Made some enhancements and small tweaks to the code

Once you run it, you will be met with the default CLI that I created, if you prefer prompts to CLI you can change using_cli at line 4 Another problem is that because I have not added a scaling system to the Bitmap (.bmp), the qr reader will have more difficulty reading the qr as the version increases.

It was a miracle that I managed to pull this off considering my coding skill and the difficulty of this, well it was fun at least.

If you somehow find this helpful feel free to use it and if you really want to look at my code, beware it is real messy ._.

'- Bean -'

