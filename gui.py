import tkinter as tk
import tkinter.messagebox as msgbox
import felicaControl as fc
import requestServer as rs
import sys
import dotenv
import time

class GUI:
  def __init__(self) -> None:
    # GUIの部品配置
    self.__rootWindow = tk.Tk()
    # 全画面表示
    #self.__rootWindow.attributes("-fullscreen", True)
    self.__rootWindow.geometry("1024x600")
    # Escキーでアプリケーション終了
    self.__rootWindow.bind("<Escape>", self.__applicationTerminate)
    self.__rootWindow.config(background="white")

    self.__messageFrame = tk.Frame(self.__rootWindow, background="white", highlightbackground="black", highlightcolor="black", highlightthickness=3, width=self.messageWidth(), height=300)
    self.__messageFrame.pack(expand=True, anchor=tk.CENTER)
    self.__messageFrame.propagate(False)
    
    self.__acceptImg = tk.PhotoImage(file="./image/accept.png")
    self.__warningImg = tk.PhotoImage(file="./image/warning.png")
    self.__touchImg = tk.PhotoImage(file="./image/touch.png")
    self.__messageIcon = tk.Label(self.__messageFrame, background="white", image=self.__touchImg, width=100, height=100)
    self.__messageIcon.pack(pady=10)
    
    self.__label = tk.Label(self.__messageFrame, background="white", text="", font=("", "30", ""))
    self.__label.pack()
    self.setDefaultMessage()

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
    if (len(requestResult) > 0):
      # 顧客側の重複タッチ警告は画面に表示しない
      if requestResult == "A0304":
        return
      self.__messageIcon.config(image=self.__warningImg)
      text = dotenv.get_key("ERROR_MESSAGE", requestResult)
    else:
      self.__messageIcon.config(image=self.__acceptImg)
      if self.__AppMode == "ISSUE":
        requestResult = "P0001"
      elif self.__AppMode == "UPDATE":
        requestResult = "P0002"
    text = dotenv.get_key("ERROR_MESSAGE", requestResult)
    # ラベルを text の値に変更
    self.__label["text"] = text
    # 5秒後にデフォルトのメッセージへ変更
    time.sleep(5)
    self.setDefaultMessage()

  def setDefaultMessage(self) -> None:
    # ラベルを空文字に変更
    self.__messageIcon.config(image=self.__touchImg)
    self.__label["text"] = 'カードリーダーに番号札をタッチして下さい。'

  def autoFontSize(self, text) -> str:
    #print(self.__messageFrame.winfo_width())
    return ''
  
  def messageWidth(self) -> int:
    self.__rootWindow.update_idletasks()
    width = self.__rootWindow.winfo_width()
    margin = width * 0.05
    return self.roundDownWidth(width - margin * 2)

  def roundDownWidth(self, width) -> int:
    return int(width - width % 10)




