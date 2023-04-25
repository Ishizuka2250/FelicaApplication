import tkinter as tk
import tkinter.messagebox as msgbox
import felicaControl as fc
import requestServer as rs
import sys
import dotenv

class GUI:
  def __init__(self) -> None:
    # GUIの部品配置
    self.__rootWindow = tk.Tk()
    # 全画面表示
    #self.__rootWindow.attributes("-fullscreen", True)
    self.__rootWindow.geometry("1024x600")
    # Escキーでアプリケーション終了
    self.__rootWindow.bind("<Escape>", self.__applicationTerminate)

    self.__mainFrame = tk.Frame(self.__rootWindow)
    self.__mainFrame.pack(expand=True, anchor=tk.CENTER)
    self.__label = tk.Label(self.__mainFrame, text="Ready.", font=("", "30", ""))
    self.__label.pack(expand=True, anchor=tk.CENTER)

    # アプリケーションモード取得
    # ISSUE:順番待ち番号発行モード  UPDATE:順番待ち番号変更モード
    self.__AppMode = dotenv.get_key(".env", "APP_MODE")
    self.__request = rs.RequestServer()
    if not self.__request.sessionCreate():
      msgbox.showerror("Error","サーバーへのログインに失敗しました.")
      sys.exit(1)
    
    self.__felica = fc.FelicaControl(self, self.__request)

  def __applicationTerminate(self, e) -> None:
    print("info:Application terminate due to ESC Key pressed.")
    self.__rootWindow.destroy()

  def run(self) -> None:
    # Felicaの読み込みループスタート
    self.__felica.startNFCReadProcess()
    # メインウィンドウ表示
    self.__rootWindow.mainloop()

  def changeLabel(self, requestResult) -> None:
    # ラベルを text の値に変更
    text = ''
    print(requestResult)
    if (len(requestResult) > 0):
      text = dotenv.get_key("ERROR_MESSAGE", requestResult)
    else:
      if self.__AppMode == "ISSUE":
        requestResult = "P0001"
      elif self.__AppMode == "UPDATE":
        requestResult = "P0002"

    text = dotenv.get_key("ERROR_MESSAGE", requestResult)
    self.__label["text"] = text



