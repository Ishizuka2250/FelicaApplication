import nfc
import binascii
import threading
import gui

class FelicaControl():
  def __init__(self, guiInstance) -> None:
    self.__gui = guiInstance
    # nfc読み込みループスレッドの定義
    self.__nfcProcess = threading.Thread(target=self.__nfcLoop, daemon=True)

  def __onConnect(self, tag) -> bool:
    idm = binascii.hexlify(tag.idm).decode().upper()
    # GUI側のラベルを読み込んだIDMの値に変更
    self.__gui.changeLabel(idm)
    return True

  def __nfcLoop(self) -> None:
    clf = nfc.ContactlessFrontend('usb')
    while True :
      clf.connect(rdwr={'on-connect': self.__onConnect})

  def startNFCReadProcess(self) -> None:
    print("info:NFC Read process start.")
    self.__nfcProcess.start()




