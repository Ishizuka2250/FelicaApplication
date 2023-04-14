import requests
import pprint
import os
import sys
import dotenv

class RequestServer():
  def __init__(self, serverURL: str) -> None:
    self.__URL = serverURL
    self.__DotEnvFilePath = ".env"
    
    # .envファイルの存在確認
    if os.path.exists(self.__DotEnvFilePath):
      # .envファイルからログイン情報を取得
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
    # Accesstokenが保存されていない場合 -> False
    else:
      print("warn: .env file has not The AccessToken. Please try login.")
      return False



