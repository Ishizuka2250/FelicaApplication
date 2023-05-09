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
    try:
      # Felica端末の接続
      clf = nfc.ContactlessFrontend('usb')
      # Felica端末カードタッチ待ちループ
      while True :
        clf.connect(rdwr={"on-connect": self.__onConnect})
    except Exception as e:
      print("Error:Failed to read the Felica Reader.")
      print(e)
      self.__gui.errorExit("Felica端末の読み込みに失敗しました。")

  def startNFCReadProcess(self) -> None:
    # タッチ待ちループスタート
    self.__nfcProcess.start()
    print("info:NFC Read process start.")