import nfc
import binascii
import threading

class FelicaControl():
  def __init__(self, guiInstance, request) -> None:
    self.__gui = guiInstance
    self.__request = request
    # nfc読み込みループスレッドの定義
    self.__nfcProcess = threading.Thread(target=self.__nfcLoop, daemon=True)

  def __onConnect(self, tag) -> bool:
    idm = binascii.hexlify(tag.idm).decode().upper()
    # タッチしたカードのidmをサーバーへリクエスト
    requestResult = self.__request.touchCardRequest(idm)
    # リクエスト結果をUI側で表示
    self.__gui.changeMessageLabel(requestResult)
    # 5秒後にUI側のメッセージを戻す
    self.__gui.setDefaultMessage(True)
    return True

  def __nfcLoop(self) -> None:
    clf = nfc.ContactlessFrontend('usb')
    while True :
      clf.connect(rdwr={'on-connect': self.__onConnect})

  def startNFCReadProcess(self) -> None:
    print("info:NFC Read process start.")
    self.__nfcProcess.start()




