import discord
import glob
import json
import urllib.request

sources = [
    'config/*.json',
    'data/*.json'
]

# JSON Read
jsons = {}
for target_source in sources:
    targets = glob.glob(target_source)
    for target in targets:
        with open(target, "r") as fp:
            d = json.loads(fp.read())
            jsons.update(d)

# DiscordBotKey
discord_key = jsons["discord_key"]

# ヘルプ(メイン)
fp = open("data/bot_help_main.txt", "r")
botHelp = fp.read()
fp.close()

# ヘルプ(対応言語)
botHelpSourceLanguageCode = '私が知ってる言葉の一覧よ\n```'
for val, lang in jsons["langs"].items():
    botHelpSourceLanguageCode += ("%s%s\n" % (val.ljust(8, ' ') , lang))
botHelpSourceLanguageCode += '```'

# メッセージ
botMessages = jsons["messages"]["lady"]
print(botMessages)

# Source Language Support List
sourceSupportList = jsons["langs"]

# API URLs
api_urls = jsons["api"]

# UrlRequest
method = 'POST'
headers = {'Content-Type': 'application/json;charset=utf-8'}

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if client.user != message.author:
        if message.content.startswith("tb+help language"):
            # Botヘルプ
            await message.channel.send(botHelpSourceLanguageCode)
            return
        elif message.content.startswith("tb+help"):
            # Botヘルプ
            await message.channel.send(botHelp)
            return
        elif isinstance(message.channel, discord.DMChannel) or (client.user in message.mentions):
            url = api_urls["base"] + api_urls["message"]
            msgs = message.content.split("\n")
            msg = ''.join(msgs[1:len(msgs)])
            print(msg)
            data = json.dumps({
                'message':msg
            }).encode('utf-8')
        elif message.content.startswith("tb+status"):
            url = api_urls["base"] + api_urls["status"]
            mes = botMessages['status_lang_setting']
            data = json.dumps({
                'userHash':message.author.avatar
            }).encode('utf-8')
        elif message.content.startswith("tb+set"):
            url = api_urls["base"] + api_urls["set_language"]
            if message.content.startswith("tb+set src="):
                languageCode = message.content.replace('tb+set src=', '')
                disc = ( not ( languageCode in sourceSupportList.keys() ) ) and ( not ( languageCode == 'auto' ) )
                setTarget = 'SourceLanguageCode'
                msg = botMessages['source_lang_set_ok']
            elif message.content.startswith("tb+set dst="):
                languageCode = message.content.replace('tb+set dst=', '')
                disc = ( not (languageCode in sourceSupportList.keys()) )
                setTarget = 'TargetLanguageCode'
                msg = botMessages['target_lang_set_ok']
            if disc:
                await message.channel.send(botMessages['lang_set_error'] % message.author.name)
                return
            data = json.dumps({
                'userHash':message.author.avatar,
                setTarget:languageCode
            }).encode('utf-8')
        elif message.content.startswith("tb+swap language"):
            url = api_urls["base"] + api_urls["swap_language"]
            mes = botMessages['message_lang_swap']
            data = json.dumps({
                'userHash':message.author.avatar
            }).encode('utf-8')
        elif message.content.startswith("tb+run "):
            url = api_urls["base"] + api_urls["run"]
            targetText = message.content.replace('tb+run ', '')
            data = json.dumps({
                'userHash':message.author.avatar,
                'TargetText':targetText
            }).encode('utf-8')
        elif message.content.startswith("tb+stop"):
            # Bot終了
            await message.channel.send(botMessages['bot_stop'])
            await client.logout()
            await client.close()
        else:
            return
        try:
            request = urllib.request.Request(url, data = data, method = method, headers = headers)
            with urllib.request.urlopen(request) as response:
                res = response.read().decode('utf-8')
                print(res)
                res = json.loads(res)
                if 'message' in res:
                    return
                elif 'info' in res:
                    res = res.get('info')
                    if res.get('SourceLanguageCode') == 'auto':
                        await message.channel.send( botMessages['status_lang_setting_src_auto'] % (message.author.name, sourceSupportList[res.get('TargetLanguageCode')]) )
                    else:
                        await message.channel.send( mes % (message.author.name, sourceSupportList[res.get('SourceLanguageCode')], sourceSupportList[res.get('TargetLanguageCode')]) )
                elif 'language' in res:
                    res = res.get('language')
                    if res == 'auto':
                        await message.channel.send(botMessages['source_auto_lang_set_ok'] % message.author.name)
                    elif res == 'SourceAndTargetSameLanguage':
                        await message.channel.send(botMessages['message_lang_same_really'] % (message.author.name, sourceSupportList[languageCode], sourceSupportList[languageCode]))
                    else:
                        await message.channel.send(msg % (message.author.name, sourceSupportList[languageCode]))
                elif 'translatedText' in res:
                    await message.channel.send("%sさんがおっしゃった言葉、翻訳できたわよ\n```%s```"% (message.author.name, res.get('translatedText')))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                await message.channel.send(botMessages['request_limit'])
            elif e.read() == b'ChangeDenied':
                await message.channel.send(botMessages['source_lang_set_error_from_auto'] % message.author.name)
            else:
                await message.channel.send(botMessages['unknown_error'])

client.run(discord_key)