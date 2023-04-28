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
  def __init__(self) -> None:
    self.__DotEnvFilePath = ".env"
    # .envファイルの存在確認
    if os.path.exists(self.__DotEnvFilePath):
      # .envファイルからログイン情報を取得
      self.__URL = dotenv.get_key(self.__DotEnvFilePath, "SERVER_URL")
      self.__MailAddress = dotenv.get_key(self.__DotEnvFilePath, "MAIL_ADDRESS")
      self.__Password = dotenv.get_key(self.__DotEnvFilePath, "PASSWORD")
      # アプリケーションモード取得
      # ISSUE:順番待ち番号発行モード  UPDATE:順番待ち番号変更モード
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
    return True

  def touchCardRequest(self, idm: str) -> int:
    if self.__AppMode == 'ISSUE':
      return self.__issueWaitNumber(idm)
    elif self.__AppMode == 'UPDATE':
      return self.__updateCutNowWaitNumber(idm)
    else:
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
    accessToken = dotenv.get_key(".env", "ACCESSTOKEN")
    # .envにAccesstokenが記載されているかチェック
    if accessToken is not None and len(accessToken) > 0:
      # AccessTokenチェックAPIにリクエスト
      try:
        response = requests.get(
          url=targetURL,
          headers={
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Authorization": "Bearer " + accessToken
          })
      except Exception as e:
        print("Failed to authentication request.")
        print(e)
        return False
      # Accesstokenが有効 -> True
      if response.status_code == 200:
        print("Info:Authentication success.")
        return True
      # Accesstokenが無効 -> False
      else:
        print("Error:Authentication failed. Please login again.")
        return False
    else:
      # Accesstokenが保存されていない場合 -> False
      print("Warn:.env file has not The AccessToken. Please try login.")
      return False
  
  def __issueWaitNumber(self, idm: str) -> str:
    targetURL = self.__URL + "/api/v1/waiting"
    accessToken = dotenv.get_key(".env", "ACCESSTOKEN")
    # .envにAccesstokenが記載されているかチェック
    if accessToken is not None and len(accessToken) > 0:
      # 待ち番号発行APIにリクエスト
      try:
        response = requests.post(
          url=targetURL,
          headers={
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Authorization": "Bearer " + accessToken
          },
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
    else:
      # Accesstokenが保存されていない場合 -> errorCode:EP0202
      print("Error:.env file has not The AccessToken. Please try login.")
      return "EP0103"
    print("Info:" + response.json()["message"])
    if self.__CurrentShopStatus != ShopStatus.OPEN:
      updateShopStatusResult = self.__updateShopStatus(ShopStatus.OPEN)
      if updateShopStatusResult[0] == 'E': return updateShopStatusResult
    return 'IP0001'
  
  def __updateCutNowWaitNumber(self, idm) -> str:
    targetURL = self.__URL + "/api/v1/waiting"
    accessToken = dotenv.get_key(".env", "ACCESSTOKEN")
    # .envにAccesstokenが記載されているかチェック
    if accessToken is not None and len(accessToken) > 0:
      # 待ち番号更新APIにリクエスト
      try:
        response = requests.patch(
          url=targetURL,
          headers={
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Authorization": "Bearer " + accessToken
          },
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
    else:
      # Accesstokenが保存されていない場合 -> errorCode:EP0103
      print("Warn:.env file has not The AccessToken. Please try login.")
      return "EP0103"
    print("Info:" + response.json()["message"])
    if self.__CurrentShopStatus != ShopStatus.OPEN:
      updateShopStatusResult = self.__updateShopStatus(ShopStatus.OPEN)
      if updateShopStatusResult[0] == 'E': return updateShopStatusResult
    return 'IP0002'

  def updateCutDoneWaitNumber(self) -> str:
    targetURL = self.__URL + "/api/v1/waiting"
    accessToken = dotenv.get_key(".env", "ACCESSTOKEN")
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
    # .envにAccesstokenが記載されているかチェック
    if accessToken is not None and len(accessToken) > 0:
      # 待ち番号更新APIにリクエスト
      try:
        response = requests.patch(
          url=targetURL,
          headers={
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Authorization": "Bearer " + accessToken
          },
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
    else:
      # Accesstokenが保存されていない場合 -> errorCode:EP0103
      print("Warn:.env file has not The AccessToken. Please try login.")
      return "EP0103"
    print("Info:" + response.json()["message"])
    return 'IP0003'

  def __updateShopStatus(self, shopStatus: ShopStatus) -> str:
    targetURL = self.__URL + "/api/v1/status"
    accessToken = dotenv.get_key(".env", "ACCESSTOKEN")
    if shopStatus != ShopStatus.UNKNOWN:
      shopStatus = {"status_id": shopStatus.value}
    else:
      print("Error:Cannot update to The UNKNOWN Shop Status.")
      return "EP0107"
    # .envにAccesstokenが記載されているかチェック
    if accessToken is not None and len(accessToken) > 0:
      # 店状態更新APIにリクエスト
      try:
        response = requests.patch(
          url=targetURL,
          headers={
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Authorization": "Bearer " + accessToken
          },
          data=json.dumps(shopStatus))
      except Exception as e:
        print("Error:Failed to update (shop status change) request.")
        print(e)
        return "EP0108"
      # 店状態の更新が正常に行われたか？
      if response.status_code != 200:
        # 店状態の更新に失敗した場合 -> errorCode:EA0201～EA0202
        print(response.json()["message"])
        return response.json()["errorcode"]
    else:
      # Accesstokenが保存されていない場合 -> errorCode:EP0103
      print("Warn:.env file has not The AccessToken. Please try login.")
      return "EP0103"
    print(response.json()["message"])
    self.__CurrentShopStatus = ShopStatus.getShopStatus(response.json()["changed_status"]["id"])
    return 'IP0004'

  def __getCutNowWaitNubmerID(self) -> int:
    waitNumberDictionaries = self.getWaitNumbers()
    # 発行された待ち番号の中から引数に指定された待ち番号を探してIDを返却
    for waitNumberDictionary in waitNumberDictionaries:
      if int(waitNumberDictionary["is_cut_now"]) == 1:
        return int(waitNumberDictionary["id"])
    return 0
  
  def getCurrentShopStatus(self) -> ShopStatus:
    targetURL = self.__URL + "/api/v1/status"
    # 店情報取得APIにリクエスト
    try:
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
      # リクエスト失敗 -> ShopStatus.UNKONWN
      print("Error:Failed to get current status request.")
      return ShopStatus.UNKNOWN

  def getWaitNumbers(self) -> dict:
    targetURL = self.__URL + "/api/v1/waiting"
    try:
      response = requests.get(url=targetURL)
    except Exception as e:
      print("Error:Failed to get the Wait Numbers request.")
      print(e)
      return None
    return response.json()["wait_number"]
    





