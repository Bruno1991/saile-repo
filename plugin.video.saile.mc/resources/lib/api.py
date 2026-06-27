import xbmcaddon
import xbmcgui
import sys
import json
import urllib.request
import config
import database

def get_credentials():
    host, user, password = config.get_credentials()

    if not host or host == 'http:/' or not user or not password:
        xbmcgui.Dialog().ok('Saile IPTV', 'Por favor, configure suas credenciais Xtream.')
        xbmcaddon.Addon().openSettings()
        sys.exit()

    return host, user, password

def fetch_xtream(endpoint):
    host, user, password = get_credentials()
    url = f"{host}/player_api.php?username={user}&password={password}&{endpoint}"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Kodi-Saile-v7'})

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data if isinstance(data, (dict, list)) else {}
    except Exception:
        return {}

def sync_database():
    import xbmc

    if xbmc.Monitor().abortRequested():
        return

    database.init_db()
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('Saile IPTV', 'Indexando dados do Xtream no Banco de Dados Local...')
    
    try:
        pDialog.update(15, 'Baixando categorias de canais...')
        database.save_categories(fetch_xtream('action=get_live_categories'), 'live')
        
        pDialog.update(30, 'Baixando categorias de filmes...')
        database.save_categories(fetch_xtream('action=get_vod_categories'), 'vod')
        
        pDialog.update(45, 'Baixando categorias de séries...')
        database.save_categories(fetch_xtream('action=get_series_categories'), 'series')
        
        pDialog.update(65, 'Indexando Canais Ao Vivo (Isso pode levar alguns segundos)...')
        database.save_streams(fetch_xtream('action=get_live_streams'), 'live')
        
        pDialog.update(80, 'Indexando Filmes...')
        database.save_streams(fetch_xtream('action=get_vod_streams'), 'vod')
        
        pDialog.update(95, 'Indexando as Séries da lista...')
        database.save_series(fetch_xtream('action=get_series'))
        
        pDialog.update(100, 'Tudo Pronto! Navegação Liberada.')
    except Exception as e:
        xbmcgui.Dialog().ok('Erro de Rede', f'Falha ao carregar dados: {str(e)}')
    finally:
        pDialog.close()