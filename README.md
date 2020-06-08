# Discord用翻訳Bot ゆき

## 成長記録
2019.08.03 Discordで翻訳をするための翻訳Botとしてゆきちゃんは誕生しました。  
2019.08.06 AWS CloudFormationでDynamoDBにゆきちゃんの記憶を入れるためのものをつくるものを公開しました。  
           AWS Lambda用Python 3.7向けゆきちゃんの考えかたを公開しました。  
  
## 概要
Discordサーバーで使える翻訳Botです。  

このBotには以下の機能があります。  
1.使用ユーザーごとに翻訳元、翻訳後の言語を保存する機能  
2.翻訳元、翻訳後の言語を入れ替える機能  
3.設定内容(翻訳元、翻訳後の言語)を確認する機能  
4.設定した内容で翻訳する機能  
5.Botに話しかけることができる機能(チャンネル・DM両方)（現時点で未実装・話しかけても反応しません）  
