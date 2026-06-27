""" main.py (O seu Novo Roteador Limpo)
        Agora sim! O seu arquivo principal ficou extremamente enxuto. 
        A única função dele é receber a requisição do sistema, 
        ler os parâmetros da URL e despachar para a tela correta dentro do módulo navigation."""

import os
import sys
import urllib.parse

# Injeta a pasta resources/lib dentro do PATH de execução do Python do Kodi
LIB_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'lib')
sys.path.append(LIB_PATH)

# Importa a nossa interface desacoplada
from navigation import AddonInterface

# Captura os argumentos que o Kodi envia nativamente
base_url = sys.argv[0]
handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])

action = args.get('action', [None])[0]
category_id = args.get('category_id', [None])[0]
series_id = args.get('series_id', [None])[0]
season_num = args.get('season_num', [None])[0]

# Instancia o controlador passando o handle do Kodi
ui = AddonInterface(base_url, handle)

# --- SISTEMA DE ROTAS ---
if action is None:
    ui.show_main_menu()

elif action == 'live_menu':
    ui.show_live_menu()

elif action == 'vod_menu':
    ui.show_vod_menu()

elif action == 'series_menu':
    ui.show_series_menu()

elif action == 'live_streams':
    ui.show_live_streams(category_id)

elif action == 'vod_streams':
    ui.show_vod_streams(category_id)

elif action == 'series_list':
    ui.show_series_list(category_id)

elif action == 'series_seasons':
    ui.show_series_seasons(series_id)

elif action == 'series_episodes':
    ui.show_series_episodes(series_id, season_num)

elif action == 'sync_db':
    import api
    api.sync_database()