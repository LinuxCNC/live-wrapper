import os

def install_disk_info():
    os.mkdir("cdroot/.disk")
    with open("cdroot/.disk/info","w") as i:
        i.write("HELLO")
