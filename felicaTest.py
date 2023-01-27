import nfc
import binascii

print("Stand By OK.")

def on_connect(tag):
  print(binascii.hexlify(tag.idm).decode().upper())
  return True
  
clf = nfc.ContactlessFrontend('usb')
while True :
  clf.connect(rdwr={'on-connect': on_connect})

