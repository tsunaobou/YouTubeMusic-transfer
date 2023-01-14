#フォルダを指定したらその直下の楽曲ファイルを全部探索して全部Youtube Musicにupしてくれるスクリプト
from ytmusicapi import YTMusic
import glob
from tqdm import tqdm
import time
import os

print("Youtube Music song importer\n")
print("実行する動作を選んでください\n")
print("1.フォルダパスを入力して転送\n")
print("2.エラーログファイルからの再開\n")
userChoice =input(">>")

#曲のフルパスが入るリストを作成
songList=[]

#失敗した場合にレジュームできるように
failedSongList=[]

if userChoice =="1":
    parentDir = input("転送したいファイルのあるパスを入力してください.直下のファイルすべてを転送します\n>>")
    searchExtension =[".flac",".mp3",".m4a",".ogg",".wma"]
    for ext in searchExtension:
        #globでディレクトリ内を検索
        templist = glob.glob(parentDir + "\**\*" + ext,recursive=True)
        songList.extend(templist)
elif userChoice =="2":
    with open("error_log.txt",mode="r",encoding="utf-8") as f:
        print("エラーログから抽出中\n")
        songList.extend([s.strip() for s in f.readlines()])

ytmusic = YTMusic('headers_auth.json')
print("合計{}曲のファイルを転送します\n".format(len(songList)))

#楽曲のアップロード部分 成功,重複,過負荷エラー,その他のエラーを取る
succeeded_count,duplicated_count, error_count = 0, 0, 0
for song in tqdm(songList):
        stat = ytmusic.upload_song(song)
        songTitle = os.path.split(song)[1]
        if stat=="STATUS_SUCCEEDED":
            print("{}のアップロードに成功しました\n".format(songTitle))
            succeeded_count += 1
        elif stat.status_code == 409:
            print("409エラー. {}はすでにアップロード済みのファイルです\n".format(songTitle))
            duplicated_count += 1
        elif stat.status_code == 503:
            failedSongList.append(song)
            print("503エラー. 過負荷が影響しています {}のアップロードに失敗しました\n".format(songTitle))
            error_count += 1
        else:
            print("予期せぬエラーです\n")
            print(stat)
        #5秒スリープ挟んで503回避
        print("5秒のスリープ中...\n")
        time.sleep(5)        
print("結果: 成功 {} ファイル  , 重複 {} ファイル , 失敗 {} ファイル\n".format(succeeded_count,duplicated_count, error_count))  
if error_count > 0:
    with open("error_log.txt","w",encoding= "utf-8") as f:
        for errorFilePath in failedSongList:
            f.write(errorFilePath+"\n")
    print("error_log.txtに保存しました.\n")