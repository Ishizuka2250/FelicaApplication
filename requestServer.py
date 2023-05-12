import requests
import os
import sys
import dotenv
import json
from enum import Enum

class ShopStatus(Enum):
  CLOSE = 1
  OPEN = 2
  BREAK = 3
  UNKNOWN = 4

  @staticmethod
  def getShopStatus(id: int):
    if id == 1:
      return ShopStatus.CLOSE
    elif id == 2:
      return ShopStatus.OPEN
    elif id == 3:
      return ShopStatus.BREAK
    else:
      return ShopStatus.UNKNOWN

class RequestServer():
  def __init__(self, gui) -> None:
    self.__Gui = gui
    self.__DotEnvFilePath = ".env"
    # .envファイルの存在確認
    if os.path.exists(self.__DotEnvFilePath):
      # .envファイルからログイン情報を取得
      self.__URL = dotenv.get_key(self.__DotEnvFilePath, "SERVER_URL")
      self.__MailAddress = dotenv.get_key(self.__DotEnvFilePath, "MAIL_ADDRESS")
      self.__Password = dotenv.get_key(self.__DotEnvFilePath, "PASSWORD")
      # アプリケーションモード取得
      # ISSUE:順番待ち番号発行モード  UPDATE:順番待ち番号変更モード REGIST:順番待ちカード登録モード
      self.__AppMode = dotenv.get_key(self.__DotEnvFilePath, "APP_MODE")
      # 現在の店状態を取得
      self.__CurrentShopStatus = self.getCurrentShopStatus()
    else:
      # .envファイルが存在しない場合 -> アプリケーション終了
      print("Error:Failed to read .env file.")
      sys.exit(1)

  def sessionCreate(self) -> bool:
    # AccessTokenが有効かチェック
    if not self.__authCheck():
      # AccessTokenが無効 -> ログイン実行
      if not self.__login():
        return False
    # 共用リクエストヘッダーを定義
    self.__Headers = self.createRequestHeaders()
    return True

  def createRequestHeaders(self) -> dict:
    accessToken = dotenv.get_key(".env", "ACCESSTOKEN")
    if accessToken is not None and len(accessToken) > 0:
      # 共用リクエストヘッダー作成
      return {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": "Bearer " + accessToken}
    else:
      return None

  def touchCardRequest(self, idm: str) -> int:
    # 各モードでタッチ後のリクエストを切り替え
    if self.__AppMode == 'ISSUE':
      return self.__issueWaitNumber(idm)
    elif self.__AppMode == 'UPDATE':
      return self.__updateCutNowWaitNumber(idm)
    elif self.__AppMode == 'REGIST':
      return self.__registCard(idm)
    else:
      # ISSUE, UPDATE, REGIST以外のモードが指定された時 -> errorCode:EP0101
      return "EP0101"

  def __login(self) -> bool:
    targetURL = self.__URL + "/api/v1/auth/login"
    # loginAPIへリクエスト
    try:
      response = requests.post(
        url=targetURL,
        params={
          "email": self.__MailAddress,
          "password": self.__Password
        })
    except Exception as e:
      print("Error:Failed to login request.")
      print(e)
      return False
    # ログイン成功 -> True
    if response.status_code == 200:
      print("Info:Login success.")
      dotenv.set_key(self.__DotEnvFilePath, "ACCESSTOKEN", response.json()["access_token"])
      dotenv.set_key(self.__DotEnvFilePath, "MASTER_KEY", response.json()["login_user"]["master_key"])
      return True
    # ログイン失敗 -> False
    else:
      print("Error:Login failed. Please check the login credential in .env file.")
      return False

  def __authCheck(self) -> bool:
    targetURL = self.__URL + "/api/v1/auth/check"
    authBeforeHeaders = self.createRequestHeaders()
    # .envにAccesstokenが記載されているかチェック
    if authBeforeHeaders is None:
      # Accesstokenが保存されていない場合 -> False
      print("Info:.env file has not The AccessToken -> Retry login.")
      return False
    try:
      # AccessTokenチェックAPIにリクエスト
      response = requests.get(
        url=targetURL,
        headers=authBeforeHeaders)
    except Exception as e:
      # リクエスト失敗 -> False
      print("Error:Failed to authentication request.")
      print(e)
      return False
    # Accesstokenが有効 -> True
    if response.status_code == 200:
      print("Info:Authentication success.")
      return True
    # Accesstokenが無効 -> False
    else:
      print("Info:The Accesstoken in .env file has authentication failed -> Retry login.")
      return False

  def __issueWaitNumber(self, idm: str) -> str:
    targetURL = self.__URL + "/api/v1/waiting"
    # 共用ヘッダーが定義されているか？
    if self.__Headers is None:
      # Accesstokenが保存されていない場合 -> errorCode:EP0103
      print("Error:.env file has not The AccessToken. Please try login.")
      return "EP0103"
    try:
      # 待ち番号発行APIにリクエスト
      response = requests.post(
        url=targetURL,
        headers=self.__Headers,
        params={
          "key": idm
        })
    except Exception as e:
      # リクエストに失敗した場合
      print("Error:Failed to issue request.")
      print(e)
      return "EP0102"
    # APIの実行が正常に行われたか？
    if response.status_code != 201:
      # 待ち番号の発行に失敗した場合 -> errorCode:EA0301～EA0306
      print(response.json()["message"])
      return response.json()["errorcode"]
    print("Info:" + response.json()["message"])
    if self.__CurrentShopStatus != ShopStatus.OPEN:
      updateShopStatusResult = self.__updateShopStatus(ShopStatus.OPEN)
      if updateShopStatusResult[0] == 'E': return updateShopStatusResult
    return 'IP0001'
  
  def __updateCutNowWaitNumber(self, idm: str) -> str:
    targetURL = self.__URL + "/api/v1/waiting"
    # 共用ヘッダーが定義されているか？
    if self.__Headers is None:
      # Accesstokenが保存されていない場合 -> errorCode:EP0103
      print("Error:.env file has not The AccessToken. Please try login.")
      return "EP0103"
    try:
      # 待ち番号更新APIにリクエスト
      response = requests.patch(
        url=targetURL,
        headers=self.__Headers,
        params={
          "key": idm
        })
    except Exception as e:
      print("Error:Failed to update (cut now state change) request.")
      print(e)
      return "EP0104"
    # 待ち番号の更新が正常に行われたか？
    if response.status_code != 200:
      # 待ち番号の更新に失敗した場合 -> errorCode:EA0307～EA0315
      print(response.json()["message"])
      return response.json()["errorcode"]
    print("Info:" + response.json()["message"])
    if self.__CurrentShopStatus != ShopStatus.OPEN:
      updateShopStatusResult = self.__updateShopStatus(ShopStatus.OPEN)
      if updateShopStatusResult[0] == 'E': return updateShopStatusResult
    return 'IP0002'

  def updateCutDoneWaitNumber(self) -> str:
    targetURL = self.__URL + "/api/v1/waiting"
    masterKey = dotenv.get_key(".env", "MASTER_KEY")
    waitNumberID = self.__getCutNowWaitNubmerID()
    # タッチされたカード(カット中)の待ち番号が発行されていない場合 -> errorCode:EP0105
    if waitNumberID == 0:
      print("Error:The Cut Now Status does not exist.")
      return "EP0105"
    updateStatus = {
      "waiting_numbers": [{
        "id": waitNumberID,
        "is_cut_wait": 0,
        "is_cut_done": 1,
        "is_cut_call": 0,
        "is_cut_now": 0
      }]}
    # 共用ヘッダーが定義されているか？
    if self.__Headers is None:
      # Accesstokenが保存されていない場合 -> errorCode:EP0103
      print("Error:.env file has not The AccessToken. Please try login.")
      return "EP0103"
    try:
      # 待ち番号更新APIにリクエスト
      response = requests.patch(
        url=targetURL,
        headers=self.__Headers,
        params={
          "key": masterKey
        },
        data=json.dumps(updateStatus))
    except Exception as e:
      print("Error:Failed to update (cut done state change) request.")
      print(e)
      return "EP0106"
    # 待ち番号の更新が正常に行われたか？
    if response.status_code != 200:
      # 待ち番号の更新に失敗した場合 -> errorCode:EA0307～EA0315
      print(response.json()["message"])
      return response.json()["errorcode"]
    print("Info:" + response.json()["message"])
    return 'IP0003'

  def __updateShopStatus(self, shopStatus: ShopStatus) -> str:
    targetURL = self.__URL + "/api/v1/status"
    if shopStatus != ShopStatus.UNKNOWN:
      shopStatus = {"status_id": shopStatus.value}
    else:
      print("Error:Cannot update to The UNKNOWN Shop Status.")
      return "EP0107"
    # 共用ヘッダーが定義されているか?
    if self.__Headers is None:
      # Accesstokenが保存されていない場合 -> errorCode:EP0103
      print("Warn:.env file has not The AccessToken. Please try login.")
      return "EP0103"
    try:
      # 店状態更新APIにリクエスト
      response = requests.patch(
        url=targetURL,
        headers=self.__Headers,
        data=json.dumps(shopStatus))
    except Exception as e:
      # リクエスト失敗 -> errorCode:EP0108
      print("Error:Failed to update (shop status change) request.")
      print(e)
      return "EP0108"
    # 店状態の更新が正常に行われたか？
    if response.status_code != 200:
      # 店状態の更新に失敗した場合 -> errorCode:EA0201～EA0202
      print(response.json()["message"])
      return response.json()["errorcode"]
    print(response.json()["message"])
    self.__CurrentShopStatus = ShopStatus.getShopStatus(response.json()["changed_status"]["id"])
    return 'IP0004'

  def __getCutNowWaitNubmerID(self) -> int:
    # 発行された待ち番号を取得
    waitNumberDictionaries = self.getWaitNumbers()
    # 発行された待ち番号の中から引数に指定された待ち番号を探してIDを返却
    for waitNumberDictionary in waitNumberDictionaries:
      if int(waitNumberDictionary["is_cut_now"]) == 1:
        return int(waitNumberDictionary["id"])
    return 0
  
  def getCurrentShopStatus(self) -> ShopStatus:
    targetURL = self.__URL + "/api/v1/status"
    try:
      # 店情報取得APIにリクエスト
      response = requests.get(url=targetURL)
    except Exception as e:
      # リクエストの実行に失敗 -> ShopStatus.UNKONWN
      print("Error:Failed to get current status request.")
      print(e)
      return ShopStatus.UNKNOWN
    # リクエスト成功時
    if response.status_code == 200:
      return ShopStatus.getShopStatus(response.json()["status_id"])
    else:
      # リクエスト失敗(パラメーター指定ミス) -> ShopStatus.UNKONWN
      print("Error:Failed to get current status request.")
      return ShopStatus.UNKNOWN

  def getWaitNumbers(self) -> dict:
    targetURL = self.__URL + "/api/v1/waiting"
    try:
      # 待ち番号取得APIにリクエスト
      response = requests.get(url=targetURL)
    except Exception as e:
      # リクエストの実行に失敗 -> None
      print("Error:Failed to get the Wait Numbers request.")
      print(e)
      return None
    if response.status_code == 200:
      # リクエスト成功 -> 待ち番号のリストを返却
      return response.json()["wait_number"]
    else:
      return None
  
  def __registCard(self, idm: str) -> str:
    targetURL = self.__URL + "/api/v1/card"
    # 共用ヘッダーが定義されているか？
    if self.__Headers is None:
      # Accesstokenが保存されていない場合 -> errorCode:EP0103
      print("Error:.env file has not The AccessToken. Please try login.")
      return "EP0103"
    # タッチされたカードが登録されているか？
    if not self.__registCardCheck(idm):
      # 登録済みの場合 -> errorCode:EP0109
      print("Error:This card [idm:" + idm + "] has already registed.")
      return "EP0109"
    if not self.__Gui.showConfirmDialog("Regist", "タッチされたカード [IDM:" + idm + "] を登録しますか？"):
      # 登録をキャンセルした場合 -> informationCode:IP0005
      print("Info:This card [idm:" + idm + "] has canceled.")
      return "IP0005"
    try:
      # カード登録APIをリクエスト
      response = requests.post(
        url=targetURL,
        headers=self.__Headers,
        params={
          "key": idm
        })
    except Exception as e:
      # リクエスト失敗 -> errorCode:EP0110
      print("Error:Failed to post the regist card request.")
      print(e)
      return "EP0110"
    if response.status_code != 201:
      # カードの登録に失敗した場合 -> errorCode:EA0402～EA0204
      print(response.json()["message"])
      return response.json()["errorcode"]
    return "IP0006"

  def __registCardCheck(self, idm: str) -> bool:
    targetURL = self.__URL + "/api/v1/card"
    # カード一覧取得APIにリクエスト
    try:
      response = requests.get(
        url=targetURL,
        headers=self.__Headers,
        params={
          "key": idm
        })
    except Exception as e:
      # リクエスト失敗 -> False
      print("Error:Falied to get the card information request.")
      print(e)
      return False
    if response.status_code == 200:
      # リクエスト成功 かつ count == 0 -> True (カード未登録)
      if response.json()["count"] == 0:
        return True
      # リクエスト成功 かつ count != 0 -> False (カード登録済)
      else:
        return False
    else:
      # リクエスト失敗(パラメーター指定ミス) -> False
      print("Error:Falied to get the card information request.")
      print(e)
      return False





