# qvft
Free volatile file transfer program using right click menu as unique interface

    Qvft is at the moment only compatible with gnome environnement, 
    clients for KDE & Windows are in development.
    Files hosted on Qvft are volatile , this mean that their life period is very short, 
    once you have uploaded files, your peers are supposed to retrieve these files rather quickly.
    Qvft is not a file hoster. files size is limited to 15MB.
    

    
![output_u4tjip](https://cloud.githubusercontent.com/assets/597457/6761562/e9efa83c-cf54-11e4-9c59-eba49574476e.gif)


#Install Qvft for Debian/Gnome WM

  apt-get install python-nautilus python-requests python-easygui

  mkdir ~/.local/share/nautilus-python/extensions && cp qvft_nautilus.py ~/.local/share/nautilus-python/extensions

  nautilus -q && nautilus
