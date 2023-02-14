import nfc
import binascii
import tkinter as tk
from multiprocessing import Process
from multiprocessing import Value

print("Stand By OK.")

def on_connect(tag, idm):
  #print(binascii.hexlify(tag.idm).decode().upper())
  idm = tag.idm
  return True

def nfcLoop(idm):
  clf = nfc.ContactlessFrontend('usb')
  while True :
    clf.connect(rdwr={'on-connect': on_connect(idm)})
    print(idm)

def informationWindow():
  rootWindow = tk.Tk()
  rootWindow.geometry("420x400")
  mainFrame = tk.Frame(rootWindow)
  mainFrame.grid()

  label = tk.Label(mainFrame, text="stop", font=("", "40", ""))
  label.grid(row=0, column=0)
  rootWindow.mainloop()

if __name__ == '__main__':
  idm = ('c', '')
  nfcProcess = Process(target=nfcLoop, args=[idm])
  nfcProcess.start()
  informationWindow()
  nfcProcess.terminate()


