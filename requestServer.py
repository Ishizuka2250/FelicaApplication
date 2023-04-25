import requests
import os
import sys
import dotenv
import json

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

  def touchCardRequest(self, idm) -> int:
    if self.__AppMode == 'ISSUE':
      return self.__issueWaitNumber(idm)
    elif self.__AppMode == 'UPDATE':
      return self.__cutNowWaitNumber(idm)
    else:
      return "P0101"

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
  
  def __issueWaitNumber(self, idm) -> str:
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
        return "P0102"
      
      # APIの実行が正常に行われたか？
      if response.status_code != 201:
        # 待ち番号の発行に失敗した場合 -> errorCode:A0301～A0306
        print(response.json()["message"])
        return response.json()["errorcode"]
    else:
      # Accesstokenが保存されていない場合 -> errorCode:P0202
      print("Error:.env file has not The AccessToken. Please try login.")
      return "P0103"
    print("Info:" + response.json()["message"])
    return ''
  
  def __cutNowWaitNumber(self, idm) -> str:
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
        return "P0104"
      # 待ち番号の更新が正常に行われたか？
      if response.status_code != 200:
        # 待ち番号の更新に失敗した場合 -> errorCode:A0307～A0315
        print(response.json()["message"])
        return response.json()["errorcode"]
    else:
      # Accesstokenが保存されていない場合 -> errorCode:P0103
      print("Warn:.env file has not The AccessToken. Please try login.")
      return "P0103"
    print("Info:" + response.json()["message"])
    return ''
  
  def cutDoneWaitNumber(self, waitNumber) -> int:
    targetURL = self.__URL + "/api/v1/waiting"
    accessToken = dotenv.get_key(".env", "ACCESSTOKEN")
    masterKey = dotenv.get_key(".env", "MASTER_KEY")
    waitNumberID = self.__getWaitNumberID(waitNumber)
    # タッチされたカード(カット中)の待ち番号が発行されていない場合 -> errorCode:P0105
    if waitNumberID == 0:
      print("Error:The card number touched has not been issued.")
      return "P0105"
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
        return "P0106"
      # 待ち番号の更新が正常に行われたか？
      if response.status_code != 200:
        # 待ち番号の更新に失敗した場合 -> errorCode:A0307～A0315
        print(response.json()["message"])
        return response.json()["errorcode"]
    else:
      # Accesstokenが保存されていない場合 -> errorCode:P0103
      print("Warn:.env file has not The AccessToken. Please try login.")
      return "P0103"
    print("Info:" + response.json()["message"])
    return ''

  def __getWaitNumberID(self, waitNumber) -> int:
    waitNumberDictionaries = self.getWaitNumbers()
    # 発行された待ち番号の中から引数に指定された待ち番号を探してIDを返却
    for waitNumberDictionary in waitNumberDictionaries:
      if int(waitNumberDictionary["waiting_no"]) == waitNumber:
        return int(waitNumberDictionary["id"])
    return 0
  
  def getWaitNumbers(self) -> dict:
    targetURL = self.__URL + "/api/v1/waiting"
    try:
      response = requests.get(url=targetURL)
    except Exception as e:
      print("Error:Failed to get the Wait Numbers request.")
      print(e)
      return None
    return response.json()["wait_number"]
    





