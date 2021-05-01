import logging
import os
import sys
from datetime import datetime
from collections import defaultdict
import click

from flask import Flask, render_template, request, send_from_directory
from jikanpy import Jikan
from ratelimiter import RateLimiter
from waitress import serve


app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

jikan = Jikan()


@RateLimiter( max_calls=1, period=4)
def call_api(call_type, identifier, page=1):
    print(f"Called API for {call_type} with id {identifier} page {page} {datetime.now()}")

    try:
        if call_type == 'user':
            user = jikan.user(username=identifier, request='animelist',
                argument='all', page=page)
            anime = user['anime']

            return anime
        elif call_type == 'person':
            person = jikan.person(identifier)

            return person
        else:
            pass
    except:
        print("OOPS!")
        return []

def get_info(call_type, identifier, page=1):
    if call_type == 'user':
        user_anime = call_api(call_type, identifier, page)

        if len(user_anime) == 300:
            user_anime.extend(get_info(call_type, identifier, page+1))

        return user_anime
    elif call_type == 'person':
        person = call_api(call_type, identifier, page)

        return person
    else:
        pass


@app.route('/favicon.ico')
def fav():
    return send_from_directory(app.root_path, 'favicon.ico')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user = request.form['username']
        user_anime = get_info('user', user)
        print(f"User {user} anime's:", len(user_anime))

        va = request.form['vaid']
        va_info = get_info('person', va)
        print("VA roles:", len(va_info['voice_acting_roles']))

        user_anime_dict = {anime['mal_id']: anime for anime in user_anime}
        va_anime_dict = {(role['anime']['mal_id'], role['character']['mal_id']): role for role in va_info['voice_acting_roles']}

        user_matching_anime_dict = {k: v for k, v in user_anime_dict.items() if k in [va_k[0] for va_k in va_anime_dict.keys()]}
        va_matching_anime_dict = {k: v for k, v in va_anime_dict.items() if k[0] in user_matching_anime_dict}

        joined_matching_anime_dict = {}
        for k, v in user_matching_anime_dict.items():
            joined_matching_anime_dict[k] = v
            va_roles = [v for k, v in filter(lambda kv: kv[0][0] == k, va_matching_anime_dict.items())]
            joined_matching_anime_dict[k]['va_roles'] = va_roles

            print(joined_matching_anime_dict[k]["title"], joined_matching_anime_dict[k]['va_roles'])

        return render_template(
            'result.html',
            matching_anime=joined_matching_anime_dict.values(),
            user=user,
            voice_actor=va_info)

    return render_template('index.html')

@click.command()
@click.option('--dev', is_flag=True)
def main(dev):
    if dev:
        app.run(debug=True)
    else:
        serve(app, host="0.0.0.0", port=5000)


if __name__ == '__main__':
    main()
