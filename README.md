# pystaKifuViewer


[Pythonista3](http://omz-software.com/pythonista/) で`.csa` 形式の棋譜データを閲覧


[`ui`](http://omz-software.com/pythonista/docs/ios/ui.html) module　を使用しているので、Pythonista 以外は動かない


`reader.py` なら、`print` してなんとか見れるかも


## routing


### View: `view`

- ゲームの情報を知らない
  - `data` から与えられた、盤面情報を描画するだけ

### Model: `data`

- ゲーム全体のデータを保持
  - 初期盤面配置
  - 盤面情報
    - 毎回0手目から、指定手目までループして構築
  - 初手から終局までの指し手情報
    - 初期盤面から、指し手情報を盤面情報を更新
  - 持ち駒
    - いい感じで、取得や使った情報を更新

### Control: `push`
    
- 何手目かの指示を出す
  - スライダーやボタン
  - ゲーム開始時は0手目
- 何手目を指示しているかの情報を保持



```
view:      data のn手目    |              data のn+1手目
           情報に書き換え    |              情報に書き換え
          /               |             /
data:   0..n と0 からloop   |             0...n+1 とloop
        n手目まで、進めて     |             0からn+1 まで進めて
        盤面情報を保持       |             盤面情報を保持
       /                  |            /
push: n手目                |push から   n+1手目
     (指示番号を保持=n)      |更新指示    (指示番号を保持=n+1)

```


## todo


- [ ] 盤面は木色じゃないと、対局中バグるから変える
  - [ ] 木目をシェーダー で書く？ <- 軽く調べたらエグいから様子見
  - [ ] 駒を五角形で書く？
- [ ] スライダーより、前後ボタン移動の方が多いから、スライダーを挟む？
- [ ] 手駒表示をどこに置くか
- [ ] 出番表示をどこに置くか
- [ ] 後手駒を天地逆に
- [ ] 移動した番地に色をつけるとわかりやすいかも


### 今後
- [ ] 棋譜を選択さす
- [ ] 縦と横のレイアウト
- [ ] iPad でのレイアウト確認

