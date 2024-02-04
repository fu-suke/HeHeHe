# HeHeHe

## これは何ですか

Pythonスクリプトを難読化してくれるツールです。名前の由来は難読化に「へ」をたくさん使うからです。「へ？」と思ったあなた、もう少しだけ先を読んでみてください。

## 機能

- 識別子名（変数名・関数名など）の難読化
- 定数の難読化
- 組み込み関数・組み込み型の難読化
- 難読化後に使う文字の指定

## 使い方の例

1. 難読化したいPythonのコード（単一ファイル）を用意します。今回は、リポジトリにあるsample.pyを利用します。sample.pyは実行すると以下のような結果が得られます。
    ```
    > python sample.py
    Doubled Value:  20
    Function is being called
    Function call completed
    Function result:  12
    Squares:  [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    Caught division by zero error
    Incremented:  10
    Square:  16
    ```

2. main.py を実行します。出来上がったファイルも確認してみます。大体の識別子やら定数が「へ（ひらがな）」か「ヘ（カタカナ）」に置き換わっています。
※非推奨ですが、Pythonでは大体のUnicode文字を識別子名として利用できます。
    ```
    > python main.py sample.py
    Obfuscation completed!: sample.py -> out.py

    > cat out.py
    ...

    class へヘヘへヘへヘヘへヘへヘへヘへへへ:

    def __init__(self, へヘヘヘヘへへヘヘヘヘヘへヘへ):
        self.へヘヘヘヘへへヘヘヘヘヘへヘへ = へヘヘヘヘへへヘヘヘヘヘへヘへ

    def へヘへへヘへへへへへへへへへへヘヘ(self):
        return self.へヘヘヘヘへへヘヘヘヘヘへヘへ * へヘヘヘへヘへへへヘへへへヘへ()

    ...
    ```

3. 出来上がったout.pyを実行してみます。1.と同様の結果が得られていれば成功です。
    ```
    > python out.py           
    Doubled Value:  20
    Function is being called
    Function call completed
    Function result:  12
    Squares:  [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    Caught division by zero error
    Incremented:  10
    Square:  16
    ```

4. より詳細な機能は以下のコマンドで参照してください。
    ```
    > python main.py --help
    ```
    
