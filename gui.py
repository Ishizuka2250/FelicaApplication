import tkinter as tk
import felicaControl as fc

class GUI:
  def __init__(self) -> None:
    # GUIの部品配置
    self.__rootWindow = tk.Tk()
    # 全画面表示
    self.__rootWindow.attributes("-fullscreen", True)
    # Escキーでアプリケーション終了
    self.__rootWindow.bind("<Escape>", self.__applicationTerminate)

    self.__mainFrame = tk.Frame(self.__rootWindow)
    self.__mainFrame.pack(expand=True, anchor=tk.CENTER)
    self.__label = tk.Label(self.__mainFrame, text="Ready.", font=("", "40", ""))
    self.__label.pack(expand=True, anchor=tk.CENTER)

    self.__felica = fc.FelicaControl(self)

  def __applicationTerminate(self, e) -> None:
    print("info:Application terminate due to ESC Key pressed.")
    self.__rootWindow.destroy()

  def run(self) -> None:
    # Felicaの読み込みループスタート
    self.__felica.startNFCReadProcess()
    # メインウィンドウ表示
    self.__rootWindow.mainloop()

  def changeLabel(self, text) -> None:
    # ラベルを text の値に変更
    self.__label["text"] = text



