from tkinter import N, NW, Canvas, Event, Tk,PhotoImage, filedialog, ttk, messagebox
try:
    from PIL import ImageTk,Image,ImageDraw
except:#pillowがない環境ならインストールする
    from subprocess import run
    run("pip install pillow==9.2.0")
    from PIL import ImageTk,Image,ImageDraw

class main:
    def __init__(self) -> None:
        """
        点の画像の生成
        判定に使う&初期化されていない可能性のある物を初期化しておく
        """
        #読み込んだ画像の最初のサイズを保管
        self.picture_default_size = [None,None]
        #マーカーimageを作る
        self.marker = Image.new(mode="RGBA",size=(7,7),color=(0,0,0,0))
        marker_draw = ImageDraw.Draw(self.marker)
        marker_draw.ellipse((0,0,6,6),fill=(255,190,0,255),outline=(255,255,255))
        self.move_old = None
        self.bef_move = ""
    def affine(self,show_img : bool) -> Image:
        """
        変形処理をする
        """
        try:
            int(self.save_size_x_entry.get())
            int(self.save_size_y_entry.get())
        except:
            messagebox.showerror("エラー","保存サイズには数字以外を入力しないでください")
            return
        point_location = []
        for i in range(1,5):#1-4まで(それぞれの座標のリストを作る)
            tmp = self.master.coords(f"{i}_mark")
            tmp[0] , tmp[1] = (tmp[0] - 250) * self.change_size_num_re , (tmp[1] - 100) * self.change_size_num_re
            point_location.append(tmp)
        quad_data = (
            point_location[0][0], point_location[0][1],   # 左上
            point_location[1][0], point_location[1][1],   # 左下
            point_location[2][0], point_location[2][1],   # 右下
            point_location[3][0], point_location[3][1]    # 右上
            )
        #４点からなる四角形を幅、高さからなる長方形へ変換
        after_pic = self.now_picture.transform(
                    (int(self.save_size_x_entry.get()), int(self.save_size_y_entry.get())),     #出力サイズ(幅, 高さ)
                    Image.QUAD,     #変換方法
                    quad_data,      #４点の座標
                    Image.BICUBIC   #補間方法
                    )
        #プレビューモードなら生成した画像を見る
        if show_img:
            after_pic.show()
            return
        #そうでなければ画像を返す
        return after_pic
    def save(self) -> None:
        """
        画像を保存する関数
        """
        try:
            save_pic = self.affine(show_img=False)
            file_name = filedialog.asksaveasfilename(
                        title = "名前を付けて保存",
                        filetypes= [("PNG", ".png"), ("JPEG", ".jpg"), ("PDF",".pdf")],
                        initialdir="./",
                        defaultextension = "png"
            )
            save_pic.save(f"{file_name}")
            messagebox.showinfo(title="保存",message=f"保存に成功しました\n保存先：{file_name}")
        except:
            messagebox.showerror(title="エラー",message="保存に失敗しました")
    def click(self,event) -> None:
        """
        クリックのみの判定
        これを使用し、前回のものをつかんだままなのかを判定する。
        """
        self.change_flag = True#これがTrueになっているときのみ新しく図形を探索する
    def point_move(self,event : Event) -> None:#クリック＆移動検知
        """
        点の移動を行う関数
        """
        def move_main(i) -> bool:
            if not self.change_flag:#今回は前回のものを動かすなら
                point_location = self.master.coords(self.bef_move)
                self.move_space = 1000
                c_flag = False
            elif i == None:
                point_location = self.master.find_closest(event.x,event.y)
                c_flag = True
            else:
                point_location = self.master.coords(f"{i + 1}_mark")
                c_flag = True
            if abs(point_location[0] - event.x) <= self.move_space and abs(point_location[1] - event.y) <= self.move_space:#移動確定なら
                self.move_old = i#ここで移動したものを保管しておく
                x , y = event.x , event.y#移動するはずの値
                #それぞれ画像をオーバーしているなら動かさない
                if event.x < 250 - 3:
                    x = 250 - 3
                elif event.x > 250 + self.picture_window_size[0] - 3:
                    x = 250 + self.picture_window_size[0] - 3
                if event.y < 100 - 3:
                    y = 100 - 3
                elif event.y > 100 + self.picture_window_size[1] - 3:
                    y = 100 + self.picture_window_size[1] - 3
                #要は今回つかんでいるのは新しく判定されたものなのか前回と同じなのか
                if c_flag:
                    self.bef_move = f"{i + 1}_mark"
                    self.master.moveto(f"{i + 1}_mark",x,y)
                else:
                    self.master.moveto(self.bef_move,x,y)
                #線を再描写する
                self.marker_line()
                #Trueが返ると今回の処理は終了
                return True
            else : return False
        try:
            self.move_space = 10
            #外からつかんでいる場合はつかめる距離を広くとる
            if event.x < 250 - 3 or event.x > 250 + self.picture_window_size[0] - 3 or event.y < 100 - 3 or event.y > 100 + self.picture_window_size[1] - 3:
                self.move_space = 100
                move_main(self.move_old)
            #4本の点に対して
            for i in range(4):
                flag = move_main(i)
                if flag: 
                    self.change_flag = False
                    return
        except:pass#まだ画像が読まれていない
    def marker_line(self) -> None:
        """
        4点を結ぶ線を表示する
        """
        #自身を削除する
        self.master.delete("black_line")
        #ここにそれぞれの点の座標を入れる
        location_list = []
        for i in range(1,5):#1-4まで(それぞれの座標のリストを作る)
            location_list.append(self.master.coords(f"{i}_mark"))
        #線を引く
        self.master.create_line(location_list[0][0],location_list[0][1],
                                location_list[1][0],location_list[1][1],
                                location_list[2][0],location_list[2][1],
                                location_list[3][0],location_list[3][1],
                                location_list[0][0],location_list[0][1],tags="black_line")
    def marker_format(self,marker_pin) -> None:
        """
        4点を描写する
        """
        self.master.delete("point_img")
        for location in marker_pin:
            #番号を付けておく。またこの点に接する線にも同じタグを付与する事で点と同時に線も削除し、再描写する
            self.master.create_image(location[0],location[1],image = self.marker,tags = (f"{location[2]}_mark","point_img"))
        
    def put_pic_marker(self,path) -> None:
        """
        元画像のサイズの変更を行う
        ここでの変更は最終保存の画質には影響しない
        """
        #まずはpictureを生成してセットする
        self.now_picture = Image.open(path)
        #元々のサイズを格納する(後にウィンドウ上のサイズ/初期サイズを取り、データ上の画像と表示されてる画像の比がずれないようにする)
        self.picture_default_size[0] = self.now_picture.size[0]
        self.picture_default_size[1] = self.now_picture.size[1]
        #保存サイズの初期状態を設定する
        self.save_size_x_entry.delete(0,len(self.save_size_x_entry.get()))
        self.save_size_x_entry.insert(0,self.now_picture.size[0])
        self.save_size_y_entry.delete(0,len(self.save_size_y_entry.get()))
        self.save_size_y_entry.insert(0,self.now_picture.size[1])
        #ウィンドウ用の画像生成
        if self.picture_default_size[0] * 4 <= self.picture_default_size[1] * 5:
            #ここでは対比に対して縦が大きいので縦に合わせて横のサイズを変更したい(x = ? , y = 500 * (7/9))
            #元のサイズに対しての横のサイズ比を算出(元のサイズを500 * (7 / 9)にしているので)
            self.change_size_num = 500 * (4/5) / self.picture_default_size[1]
            #であればその逆数を掛ければ元のサイズに戻るので
            self.change_size_num_re = self.picture_default_size[1] / (500 * (4/5))
            self.window_picture = self.now_picture.resize((int(500  * (4 / 5) * self.picture_default_size[0] / self.picture_default_size[1]),int(500 * (4 / 5))))
        else:
            self.change_size_num = 500 / self.picture_default_size[0]
            self.change_size_num_re = self.picture_default_size[0] / 500
            self.window_picture = self.now_picture.resize((int(500),int(500 * self.picture_default_size[1] / self.picture_default_size[0])))
        self.picture_window_size = self.window_picture.size
        self.window_picture = ImageTk.PhotoImage(self.window_picture)
        self.master.create_image(250,100,image = self.window_picture, anchor=NW)
        #ここからマーカーを((0,0),(0,y_max),(x_max,0),(x_max,y_max))に配置する
        mark_put_list = [[250 , 100 , 1],
                        [250 , 100 + self.picture_window_size[1] , 2],
                        [250 + self.picture_window_size[0] , 100 + self.picture_window_size[1] , 3],
                        [250 + self.picture_window_size[0] , 100 , 4]]
        #点描写関数
        self.marker_format(mark_put_list)
        #線描写関数
        self.marker_line()

    def set_img(self) -> None:
        """
        グリッド画像と左のロゴを生成
        """
        #背景を作る
        self.back_image = Image.new("RGBA",(900,700),(64,64,64,255))
        self.back_image_tk = ImageTk.PhotoImage(self.back_image)
        self.master.create_image(0,0,image = self.back_image_tk , anchor = NW)
        transparent_bg = Image.new(mode="RGB",size=(500,400),color=(0,0,0,255))
        #縦横20*16の26ピクセル刻みのグリッドを作成
        for grid_x in range(20):#横
            for grid_y in range(16):#縦
                if (grid_x + grid_y) % 2 == 0:
                    color = (128,128,128,255) 
                else:
                    color = (96,96,96,255)
                transparent_bg.paste(Image.new("RGBA",(32,32),color),(grid_x * 32,grid_y * 32))
        #どうやらローカル変数だと参照が消えてGCされてる感じなのでself.
        self.transparent_bg_tk = ImageTk.PhotoImage(transparent_bg)
        self.master.create_image(250,100,image = self.transparent_bg_tk,anchor = NW)
        #ロゴ読み込み
        self.logo = PhotoImage(file = "./assets/picture/logo_gradation.png")
        self.master.create_image(-50,0,image = self.logo,anchor = NW)

    def set_obj(self) -> None:
        """
        初期から置かれているボタン等を設置
        """
        def affine_false(show_bool : bool):
            def tmp():
                self.affine(show_bool)
            return tmp
        def make_marker() -> PhotoImage:
            """
            マーカーの画像を返す
            """
            image = ImageTk.PhotoImage(self.marker)
            return image
        def file_reference() -> None:
            """
            ファイル参照処理
            """
            path = filedialog.askopenfilename(filetypes=[("PNG", ".png"), ("JPEG", ".jpg"), ("PDF",".pdf")])
            if path == "":
                pass
            else:
                self.image_path_entry["state"] = "NORMAL"
                self.image_path_entry.delete(0,len(self.image_path_entry.get()))
                self.image_path_entry.insert(0,path)
                self.image_path_entry["state"] = "disabled"
                self.put_pic_marker(path)
        self.marker = make_marker()
        self.master.create_text(250,30 + 4,text="参照path",fill="white",tags="reference_path",anchor=N)
        self.image_path_entry = ttk.Entry(width=80, state='disabled')
        self.image_path_entry.place(x=300,y=30)
        self.reference_path_button = ttk.Button(text="参照",command=file_reference)
        self.reference_path_button.place(x = 800 , y = 30 - 2)
        self.save_button = ttk.Button(text="保存",command=self.save)
        self.save_button.place(x = 800, y = 450)
        self.preview_button = ttk.Button(text="プレビュー",command=affine_false(True))
        self.preview_button.place(x = 800 , y = 400)
        self.master.create_text(800,300,text="保存サイズ",fill="white",anchor=NW)
        self.master.create_text(800,330,text="x",fill="white",anchor=NW)
        self.save_size_x_entry = ttk.Entry(width=5)
        self.save_size_x_entry.place(x = 820, y = 330)
        self.master.create_text(800,350,text="y",fill="white",anchor=NW)
        self.save_size_y_entry = ttk.Entry(width=5)
        self.save_size_y_entry.place(x = 820, y = 350)

    def bind(self) -> None:
        """
        ドラッグ操作とクリックをバインド
        """
        self.master.bind("<Button1-Motion>",self.point_move)
        self.master.bind("<Button-1>",self.click)

    def main(self) -> None:
        """
        windowを生成し、各種処理を開始する
        """
        self.root = Tk()
        self.root.geometry("900x600")
        self.root.title("image deformationer")
        self.root.resizable(0,0)
        self.root.iconbitmap("./assets/icon/mitsuki.ico")
        self.master = Canvas(self.root,width=900,height=600)
        self.master.pack()
        self.bind()
        self.set_img()
        self.set_obj()
        self.master.mainloop()

if __name__ == "__main__":
    main_instance = main()
    main_instance.main()