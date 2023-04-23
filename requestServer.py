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
    else:
      # .envファイルが存在しない場合 -> アプリケーション終了
      print("error:Failed to read .env file.")
      sys.exit(1)

  def login(self) -> bool:
    targetURL = self.__URL + "/api/v1/auth/login"
    
    # loginAPIへリクエスト
    response = requests.post(
      url=targetURL,
      params={
        "email": self.__MailAddress,
        "password": self.__Password
      })
    
    # ログイン成功 -> True
    if response.status_code == 200:
      print("info:Login success.")
      dotenv.set_key(self.__DotEnvFilePath, "ACCESSTOKEN", response.json()["access_token"])
      dotenv.set_key(self.__DotEnvFilePath, "MASTER_KEY", response.json()["login_user"]["master_key"])
      return True
    # ログイン失敗 -> False
    else:
      print("error:Login failed. Please check the login credential in .env file.")
      return False

  def authCheck(self) -> bool:
    targetURL = self.__URL + "/api/v1/auth/check"
    accessToken = dotenv.get_key(".env", "ACCESSTOKEN")
    
    # .envにAccesstokenが記載されているかチェック
    if accessToken is not None and len(accessToken) > 0:
      # AccessTokenチェックAPIにリクエスト
      response = requests.get(
        url=targetURL,
        headers={
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
          "Authorization": "Bearer " + accessToken
        })
      
      # Accesstokenが有効 -> True
      if response.status_code == 200:
        return True
      # Accesstokenが無効 -> False
      else:
        print("error:Authentication failed. Please login again.")
        return False
    else:
      # Accesstokenが保存されていない場合 -> False
      print("warn: .env file has not The AccessToken. Please try login.")
      return False
  
  def issueWaitNumber(self, idm) -> int:
    targetURL = self.__URL + "/api/v1/waiting"
    accessToken = dotenv.get_key(".env", "ACCESSTOKEN")
    
    # .envにAccesstokenが記載されているかチェック
    if accessToken is not None and len(accessToken) > 0:
      # 待ち番号発行APIにリクエスト
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
      print(response.json()["message"])
      # APIの実行が正常に行われたか？
      if response.status_code != 201:
        # 待ち番号の発行に失敗した場合 -> errorCode:1～6
        return response.json()["errorcode"]
    else:
      # Accesstokenが保存されていない場合 -> errorCode:9
      print("warn: .env file has not The AccessToken. Please try login.")
      return 9
    
    return 0
  
  def cutNowWaitNumber(self, idm) -> int:
    targetURL = self.__URL + "/api/v1/waiting"
    accessToken = dotenv.get_key(".env", "ACCESSTOKEN")
    
    # .envにAccesstokenが記載されているかチェック
    if accessToken is not None and len(accessToken) > 0:
      # 待ち番号更新APIにリクエスト
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
      print(response.json()["message"])
      # 待ち番号の更新が正常に行われたか？
      if response.status_code != 200:
        # 待ち番号の更新に失敗した場合 -> errorCode:1～8
        return response.json()["errorcode"]
    else:
      # Accesstokenが保存されていない場合 -> errorCode:9
      print("warn: .env file has not The AccessToken. Please try login.")
      return 9
    return 0
  
  def cutDoneWaitNumber(self, waitNumber) -> int:
    targetURL = self.__URL + "/api/v1/waiting"
    accessToken = dotenv.get_key(".env", "ACCESSTOKEN")
    masterKey = dotenv.get_key(".env", "MASTER_KEY")
    waitNumberID = self.getWaitNumberID(waitNumber)
    # タッチされたカード(カット中)の待ち番号が発行されていない場合 -> errorCode:10
    if waitNumberID == 0:
      print("error: The card number touched has not been issued.")
      return 10
    updateStatus = {
      "waiting_numbers": [{
        "id": waitNumberID,
        "is_cut_wait": 0,
        "is_cut_done": 1,
        "is_cut_call": 0,
        "is_cut_now": 0
      }]
    }
    
    # .envにAccesstokenが記載されているかチェック
    if accessToken is not None and len(accessToken) > 0:
      # 待ち番号更新APIにリクエスト
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
        data=json.dumps(updateStatus)
        )
      print(response.json()["message"])
      # 待ち番号の更新が正常に行われたか？
      if response.status_code != 200:
        # 待ち番号の更新に失敗した場合 -> errorCode:1～8
        return response.json()["errorcode"]
    else:
      # Accesstokenが保存されていない場合 -> errorCode:9
      print("warn: .env file has not The AccessToken. Please try login.")
      return 9
    return 0

  def getWaitNumberID(self, waitNumber) -> int:
    targetURL = self.__URL + "/api/v1/waiting"
    response = requests.get(url=targetURL)
    waitNumberDictionaries = response.json()["wait_number"]
    # 発行された待ち番号の中から引数に指定された待ち番号を探してIDを返却
    for waitNumberDictionary in waitNumberDictionaries:
      if int(waitNumberDictionary["waiting_no"]) == waitNumber:
        return int(waitNumberDictionary["id"])
    return 0





