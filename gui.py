import tkinter as tk
import tkinter.messagebox as msgbox
import felicaControl as fc
import requestServer as rs
import dotenv
import time

class GUI:
  def __init__(self) -> None:
    self.__request = rs.RequestServer(self)
    # アプリケーションモード取得
    # ISSUE:順番待ち番号発行モード  UPDATE:順番待ち番号変更モード
    self.__AppMode = dotenv.get_key(".env", "APP_MODE")
    # GUIの部品配置
    self.__rootWindow = tk.Tk()
    # 全画面表示
    #self.__rootWindow.attributes("-fullscreen", True)
    self.__rootWindow.geometry("1024x600")
    # Escキーでアプリケーション終了
    self.__rootWindow.bind("<Escape>", self.__applicationTerminate)
    # Updateモードの場合Enterキーでカット中->カット完了の状態変更を実行可
    if self.__AppMode == "UPDATE":
      self.__rootWindow.bind("<Return>", self.__updateCutDoneWaitNumber)
    self.__rootWindow.config(background="white")
    # 上部のフレーム
    self.__headerFrame = tk.Frame(self.__rootWindow, background="white", width=self.messageWidth(), height=100)
    self.__headerFrame.pack(expand=True, anchor=tk.N)
    self.__headerFrame.propagate(False)
    # 中部のフレーム (メッセージ表示用)
    self.__messageFrame = tk.Frame(self.__rootWindow, background="white", highlightbackground="black", highlightcolor="black", highlightthickness=3, width=self.messageWidth(), height=300)
    self.__messageFrame.pack(expand=True, anchor=tk.CENTER)
    self.__messageFrame.propagate(False)
    self.__acceptImg = tk.PhotoImage(file="./image/accept.png")
    self.__warningImg = tk.PhotoImage(file="./image/warning.png")
    self.__touchImg = tk.PhotoImage(file="./image/touch.png")
    self.__messageIcon = tk.Label(self.__messageFrame, background="white", image=self.__touchImg, width=self.messageWidth(), height=100)
    self.__messageIcon.pack(pady=10)
    self.__messageLabel = tk.Label(self.__messageFrame, background="white", text="", font=("", "30", ""))
    self.__messageLabel.pack()
    self.setDefaultMessage()
    # 下部のフレーム
    self.__footerFrame = tk.Frame(self.__rootWindow, background="white", width=self.messageWidth(), height=100)
    self.__footerFrame.pack(expand=True, anchor=tk.S)
    self.__footerFrame.propagate(False)
    # Serverへログイン
    if not self.__request.sessionCreate():
      self.errorExit("サーバーへのログインに失敗しました.")
    self.__felica = fc.FelicaControl(self, self.__request)

  def run(self) -> None:
    # Felicaの読み込みループスタート
    self.__felica.startNFCReadProcess()
    # メインウィンドウ表示
    self.__rootWindow.mainloop()

  def __applicationTerminate(self, e) -> None:
    # ESC押された後のアプリ終了処理
    print("info:Application terminate due to ESC Key pressed.")
    self.__rootWindow.destroy()
  
  def errorExit(self, message) -> None:
    msgbox.showerror("Error", message)
    self.__rootWindow.destroy()
  
  def showConfirmDialog(self, title, message) -> bool:
    return msgbox.askyesno(title, message)

  def __updateCutDoneWaitNumber(self, e) -> None:
    # カット完了ボタン押下後の待ち状態変更処理
    self.changeMessageLabel(self.__request.updateCutDoneWaitNumber())
    self.__rootWindow.after(5000, self.setDefaultMessage)

  def changeMessageLabel(self, requestResult) -> None:
    if (requestResult[0] == 'E'):
      # ISSUEモード時重複タッチ警告は画面に表示しない
      if requestResult == "EA0304": return
      self.__messageIcon.config(image=self.__warningImg)
    else:
      self.__messageIcon.config(image=self.__acceptImg)
    text = dotenv.get_key("MESSAGE_LIST", requestResult)
    # ラベルを text の値に変更
    self.__messageLabel["text"] = text

  def setDefaultMessage(self, isSleep=False) -> None:
    # sleepTime秒後に表示をデフォルトに戻す
    if isSleep: time.sleep(5)
    self.__messageIcon.config(image=self.__touchImg)
    self.__messageLabel["text"] = "カードリーダーに番号札をタッチして下さい。"

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




