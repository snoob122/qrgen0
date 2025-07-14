# qrgen0 - A pure python qr code generator

**qrgen0** is a fully functional, zero-dependency qr code generator written entirely in Python - without a single import. Built from scratch in 8 days, it supports:

- All QR Version (1 - 40)
- Numeric, Alphanumeric and Byte Encoding
- A masking optimisation system
- Bitmap (.bmp) output without Pillow
- ASCII output for terminal or raw file rendering (stored in .txt file)
- A not the best but functional CLI 
- Settings Saved automatically in config (.cfg) file

Once you run it, you will be met with the default CLI that I created, if you prefer prompts over CLI you can change using_cli at line 4
Another problem is that because I have not added a scaling system to the Bitmap (.bmp), the qr reader will have more difficulty reading the qr as the version increases.

It was a miracle that I managed to pull this off considering my coding skill and the difficulty of this, well it was fun atleast.

If you somehow find this helpful feel free to use it and if you really wanna look at my code, beware it is real messy ._.
- Bean -
