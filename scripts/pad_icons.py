import os
from PIL import Image

def pad_to_poster(image_path):
    print(f"Processando {image_path}...")
    try:
        img = Image.open(image_path).convert("RGBA")
        
        # O aspect ratio de um poster é 2:3.
        # Vamos definir a largura como a largura atual e a altura como 1.5x a largura.
        # Mas se a imagem for mais alta que larga, ajustamos ao contrário.
        w, h = img.size
        
        # Calcula o tamanho ideal de poster baseado no maior lado
        target_w = w
        target_h = int(w * 1.5)
        
        if h > target_h:
            target_h = h
            target_w = int(h / 1.5)
            
        print(f"Original: {w}x{h} -> Novo: {target_w}x{target_h}")
            
        # Cria uma nova imagem transparente com o tamanho alvo
        new_img = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        
        # Calcula a posição centralizada
        x = (target_w - w) // 2
        y = (target_h - h) // 2
        
        # Cola a imagem original no centro
        new_img.paste(img, (x, y))
        
        # Salva sobrepondo o arquivo original
        new_img.save(image_path, "PNG")
        print(f"Sucesso: {image_path}")
        
    except Exception as e:
        print(f"Erro ao processar {image_path}: {e}")

if __name__ == "__main__":
    art_dir = os.path.join("plugin.video.saile.mc", "art")
    icons = ["ao_vivo.png", "vod.png", "series.png", "sync.png"]
    
    for icon in icons:
        path = os.path.join(art_dir, icon)
        if os.path.exists(path):
            pad_to_poster(path)
        else:
            print(f"Aviso: {path} não encontrado.")
