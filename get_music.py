from random import choice


def get_random_track():
    song_name = ''
    find_track()


def find_track(search_text):
    url = "https://spotify23.p.rapidapi.com/search/"
    song = choice(songs)
    querystring = {"q": song, "type": "multi", "offset": "0", "limit": "10", "numberOfTopResults": "5"}

    headers = {
        "X-RapidAPI-Key": "81aa96d6bamsh080a667c145161ep135b79jsncb93f929b216",
        "X-RapidAPI-Host": "spotify23.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    print(data)
    track_id = data['tracks']['items'][0]['data']['id']
    name = data['tracks']['items'][0]['data']['name']

    url = "https://spotify23.p.rapidapi.com/tracks/"

    querystring = {"ids": track_id}

    headers = {
        "X-RapidAPI-Key": "81aa96d6bamsh080a667c145161ep135b79jsncb93f929b216",
        "X-RapidAPI-Host": "spotify23.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    file = requests.get(data['tracks'][0]['preview_url'])

    with open(f'audio.mp3', 'wb') as f:
        f.write(file.content)

    await x.reply_audio('audio.mp3', title=f'{name}.mp3')
