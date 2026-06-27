import os
import urllib.parse
import xbmcgui
import xbmcplugin
import api
import database

LIB_DIR = os.path.dirname(__file__)
ADDON_DIR = os.path.dirname(os.path.dirname(LIB_DIR))
ART_DIR = os.path.join(ADDON_DIR, 'art')

ICON_AO_VIVO = os.path.join(ART_DIR, 'ao_vivo.png')
ICON_VOD = os.path.join(ART_DIR, 'vod.png')
ICON_SERIES = os.path.join(ART_DIR, 'series.png')

class AddonInterface:
    def __init__(self, base_url, handle):
        self.base_url = base_url
        self.handle = handle
        database.init_db()

    def build_url(self, query):
        return self.base_url + '?' + urllib.parse.urlencode(query)

    def add_folder(self, name, query, icon=""):
        url = self.build_url(query)
        li = xbmcgui.ListItem(label=name)
        if icon:
            # Povoa todas as propriedades conhecidas de visualização de skins (Corrige o Widelist)
            li.setArt({
                'thumb': icon,
                'icon': icon,
                'landscape': icon,
                'fanart': icon,
                'banner': icon,
                'poster': icon
            })
        xbmcplugin.addDirectoryItem(handle=self.handle, url=url, listitem=li, isFolder=True)

    def show_main_menu(self):
        xbmcplugin.setContent(self.handle, 'videos')
        self.add_folder('Canais ao Vivo', {'action': 'live_menu'}, icon=ICON_AO_VIVO)
        self.add_folder('Filmes (VOD)', {'action': 'vod_menu'}, icon=ICON_VOD)
        self.add_folder('Séries', {'action': 'series_menu'}, icon=ICON_SERIES)
        # Força uma sincronização manual se o usuário quiser atualizar a lista
        self.add_folder(
            '[COLOR yellow]Sincronizar Conteúdo (Atualizar IPTV)[/COLOR]',
            {'action': 'sync_db'},
            icon=ICON_AO_VIVO
        )
        xbmcplugin.endOfDirectory(self.handle)

    def show_live_menu(self):
        if not database.has_data():
            xbmcgui.Dialog().notification(
                "Saile IPTV",
                "Sem dados locais. Clique em Sincronizar Conteúdo.",
                xbmcgui.NOTIFICATION_INFO,
                4000
            )
            xbmcplugin.endOfDirectory(self.handle)
            return

        for cat in database.get_categories('live'):
            self.add_folder(cat['name'], {'action': 'live_streams', 'category_id': cat['id']})

        xbmcplugin.endOfDirectory(self.handle)

    def show_vod_menu(self):
        if not database.has_data():
            xbmcgui.Dialog().notification(
                "Saile IPTV",
                "Sem dados locais. Use 'Sincronizar Conteúdo'.",
                xbmcgui.NOTIFICATION_INFO,
                4000
            )
            xbmcplugin.endOfDirectory(self.handle)
            return

        for cat in database.get_categories('vod'):
            self.add_folder(cat['name'], {'action': 'vod_streams', 'category_id': cat['id']})

        xbmcplugin.endOfDirectory(self.handle)

    def show_series_menu(self):
        if not database.has_data():
            xbmcgui.Dialog().notification(
                "Saile IPTV",
                "Sem dados locais. Use 'Sincronizar Conteúdo'.",
                xbmcgui.NOTIFICATION_INFO,
                4000
            )
            xbmcplugin.endOfDirectory(self.handle)
            return

        for cat in database.get_categories('series'):
            self.add_folder(cat['name'], {'action': 'series_list', 'category_id': cat['id']})

        xbmcplugin.endOfDirectory(self.handle)

    def show_live_streams(self, category_id):
        xbmcplugin.setContent(self.handle, 'videos')
        host, user, password = api.get_credentials()
        for ch in database.get_streams(category_id, 'live'):
            url = f"{host}/live/{user}/{password}/{ch['stream_id']}.ts"
            li = xbmcgui.ListItem(label=ch['name'])
            if ch['icon']: li.setArt({'thumb': ch['icon'], 'icon': ch['icon'], 'landscape': ch['icon'], 'fanart': ch['icon']})
            li.getVideoInfoTag().setTitle(ch['name'])
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=self.handle, url=url, listitem=li, isFolder=False)
        xbmcplugin.endOfDirectory(self.handle)

    def show_vod_streams(self, category_id):
        xbmcplugin.setContent(self.handle, 'movies')
        host, user, password = api.get_credentials()
        for mv in database.get_streams(category_id, 'vod'):
            url = f"{host}/movie/{user}/{password}/{mv['stream_id']}.{mv['ext']}"
            li = xbmcgui.ListItem(label=mv['name'])
            if mv['icon']: li.setArt({'thumb': mv['icon'], 'icon': mv['icon'], 'poster': mv['icon'], 'fanart': mv['icon']})
            tag = li.getVideoInfoTag()
            tag.setTitle(mv['name'])
            tag.setPlot(mv['plot'])
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=self.handle, url=url, listitem=li, isFolder=False)
        xbmcplugin.endOfDirectory(self.handle)

    def show_series_list(self, category_id):
        xbmcplugin.setContent(self.handle, 'tvshows')
        for sr in database.get_series(category_id):
            self.add_folder(sr['name'], {'action': 'series_seasons', 'series_id': sr['series_id']}, icon=sr['cover'])
        xbmcplugin.endOfDirectory(self.handle)

    def show_series_seasons(self, series_id):
    xbmcplugin.setContent(self.handle, 'seasons')

    data = api.fetch_xtream(f"action=get_series_info&series_id={series_id}")

    if not isinstance(data, dict):
        xbmcgui.Dialog().notification(
            "Saile IPTV",
            "Erro ao carregar série",
            xbmcgui.NOTIFICATION_ERROR,
            3000
        )
        xbmcplugin.endOfDirectory(self.handle)
        return

    episodes_by_season = data.get('episodes', {})

    for season in sorted(episodes_by_season.keys(), key=lambda x: int(x)):
        self.add_folder(
            f"Temporada {season}",
            {
                'action': 'series_episodes',
                'series_id': series_id,
                'season_num': season
            }
        )

    xbmcplugin.endOfDirectory(self.handle)

    def show_series_episodes(self, series_id, season_num):
        xbmcplugin.setContent(self.handle, 'episodes')
        data = api.fetch_xtream(f"action=get_series_info&series_id={series_id}")
        eps = data.get('episodes', {}).get(season_num, [])
        host, user, password = api.get_credentials()
        for ep in eps:
            name = ep.get('title', f"Episodio {ep.get('episode_num')}")
            url = f"{host}/series/{user}/{password}/{ep.get('id')}.{ep.get('container_extension', 'mp4')}"
            full_name = f"E{ep.get('episode_num')} - {name}"
            li = xbmcgui.ListItem(label=full_name)
            img = ep.get('info', {}).get('movie_image', '')
            if img: li.setArt({'thumb': img, 'icon': img, 'landscape': img, 'fanart': img})
            tag = li.getVideoInfoTag()
            tag.setTitle(full_name)
            tag.setPlot(ep.get('info', {}).get('plot', ''))
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=self.handle, url=url, listitem=li, isFolder=False)
        xbmcplugin.endOfDirectory(self.handle)