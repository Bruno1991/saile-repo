import os
import zipfile
import xml.etree.ElementTree as ET
import hashlib
import re
import shutil
import subprocess
import json

def get_addon_info(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        return {
            "id": root.attrib.get('id'),
            "name": root.attrib.get('name'),
            "version": root.attrib.get('version')
        }
    except Exception:
        return None

def update_version(xml_path, new_version):
    with open(xml_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Substitui a versão na primeira tag <addon> encontrada
    content = re.sub(r'(<addon[^>]+version=")[^"]+(")', r'\g<1>' + new_version + r'\2', content, count=1)
    
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(content)

def get_modified_addons():
    modified = set()
    try:
        status = subprocess.check_output(["git", "status", "--porcelain"], text=True, stderr=subprocess.DEVNULL)
        for line in status.splitlines():
            if len(line) > 3:
                folder = line[3:].strip().replace("\\", "/").split('/')[0]
                modified.add(folder)
                
        try:
            diff = subprocess.check_output(["git", "diff", "origin/main...HEAD", "--name-only"], text=True, stderr=subprocess.DEVNULL)
            for line in diff.splitlines():
                if line:
                    folder = line.strip().replace("\\", "/").split('/')[0]
                    modified.add(folder)
        except Exception:
            pass
    except Exception:
        pass
    return modified

def auto_increment_version(version, bump_type="patch"):
    parts = version.split(".")
    if len(parts) >= 3 and parts[-1].isdigit():
        if bump_type == "major":
            parts[0] = str(int(parts[0]) + 1)
            parts[1] = "0"
            parts[2] = "0"
        elif bump_type == "minor":
            parts[1] = str(int(parts[1]) + 1)
            parts[2] = "0"
        else: # patch
            parts[-1] = str(int(parts[-1]) + 1)
        return ".".join(parts)
    return version

def load_versions_json():
    import os
    if os.path.exists("versions.json"):
        with open("versions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_versions_json(data):
    with open("versions.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
def compare_versions(v1, v2):
    # Retorna True se v1 for logicamente maior que v2 (ex: "2.0.0" > "1.9.9")
    def pad(v):
        return [int(x) if x.isdigit() else 0 for x in v.split(".")]
    return pad(v1) > pad(v2)

def create_zip(folder_path, version):
    addon_id = os.path.basename(folder_path)
    zip_name = f"{addon_id}-{version}.zip"
    
    zip_folder = os.path.join("zips", addon_id)
    os.makedirs(zip_folder, exist_ok=True)
    
    # Limpa ZIPs antigos
    for file in os.listdir(zip_folder):
        if file.endswith('.zip'):
            os.remove(os.path.join(zip_folder, file))
            
    # Copia icon.png e fanart.png/fanart.jpg para a pasta zips
    for img in ["icon.png", "fanart.jpg", "fanart.png"]:
        src_img = os.path.join(folder_path, img)
        if os.path.exists(src_img):
            shutil.copy(src_img, os.path.join(zip_folder, img))
            
    # Cria/Atualiza o index.html dinamicamente para sempre mostrar a versão certa
    html_content = f"<!DOCTYPE html>\n<html>\n<body>\n<a href=\"{zip_name}\">{zip_name}</a><br>\n</body>\n</html>"
    with open(os.path.join(zip_folder, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
            
    zip_path = os.path.join(zip_folder, zip_name)
        
    print(f"Creating {zip_path}...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            if ".git" in root or "__pycache__" in root:
                continue
            for file in files:
                if file.endswith('.zip') or file == ".env":
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.join(addon_id, os.path.relpath(file_path, folder_path))
                zipf.write(file_path, arcname)
                
    return zip_path

def build_addons_xml(addons):
    xml_content = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<addons>\n"
    
    for addon_folder in addons:
        xml_path = os.path.join(addon_folder, "addon.xml")
        if not os.path.exists(xml_path):
            continue
            
        with open(xml_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r'(<addon.*?</addon>)', content, re.DOTALL)
            if match:
                xml_content += match.group(1) + "\n\n"
                
    xml_content += "</addons>\n"
    
    os.makedirs("zips", exist_ok=True)
    
    with open(os.path.join("zips", "addons.xml"), "w", encoding="utf-8", newline='\n') as f:
        f.write(xml_content)
        
    m = hashlib.md5()
    with open(os.path.join("zips", "addons.xml"), "rb") as f:
        m.update(f.read())
        
    with open(os.path.join("zips", "addons.xml.md5"), "w", encoding="utf-8", newline='\n') as f:
        f.write(m.hexdigest())

def push_to_github():
    print("Pushing to GitHub via Git...")
    import subprocess
    import sys
    
    try:
        subprocess.run(["git", "add", "."], check=True)
        
        result = subprocess.run(["git", "commit", "-m", "Auto Update Repo"], capture_output=True, text=True)
        
        if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
            print("Nenhuma alteração para commitar no git. Pulando push.")
            return

        print("Sincronizando com o GitHub remoto antes de enviar...")
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=True)
        
        print("Enviando mudanças para o GitHub...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("Push realizado com sucesso!")
        
    except subprocess.CalledProcessError as e:
        print(f"Erro fatal executando comando Git: {e.cmd}", file=sys.stderr)
        if e.output: print(f"Saída: {e.output}", file=sys.stderr)
        if e.stderr: print(f"Erro: {e.stderr}", file=sys.stderr)
        print("O script foi abortado para proteger a integridade do repositório.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Garante que o script rode a partir da raiz do repositório
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    os.chdir(repo_root)

    addon_dirs = []
    
    # 1. Encontra todos os addons dinamicamente buscando pelo addon.xml
    for item in os.listdir("."):
        if os.path.isdir(item) and item != "zips" and not item.startswith("."):
            xml_path = os.path.join(item, "addon.xml")
            if os.path.exists(xml_path):
                addon_dirs.append(item)
                
    # 2. Identifica quais addons mudaram
    modified_addons = get_modified_addons()
    
    import argparse
    parser = argparse.ArgumentParser(description="Build and Deploy Kodi Repository")
    parser.add_argument('--major', nargs='*', default=[], help='Addons to bump MAJOR version (e.g. --major saile.db)')
    parser.add_argument('--minor', nargs='*', default=[], help='Addons to bump MINOR version')
    parser.add_argument('--major-all', action='store_true', help='Force MAJOR bump for all modified addons')
    parser.add_argument('--minor-all', action='store_true', help='Force MINOR bump for all modified addons')
    args = parser.parse_args()
        
    json_versions = load_versions_json()
    new_json_versions = {}
    
    # 3. Processa cada addon encontrado
    for addon_dir in addon_dirs:
        xml_path = os.path.join(addon_dir, "addon.xml")
        info = get_addon_info(xml_path)
        
        if not info:
            continue
            
        addon_id = info.get("id")
        version = info.get("version")
        json_version = json_versions.get(addon_id)
        
        # Detecta se houve edição manual no versions.json com versão superior ao XML
        is_manual_bump = json_version and compare_versions(json_version, version)
        
        if is_manual_bump:
            modified_addons.add(addon_dir) # Força reconstrução
            new_version = json_version
            update_version(xml_path, new_version)
            print(f"[{addon_id}] Override Manual no JSON detectado. Versão: {version} -> {new_version}")
            version = new_version
        elif addon_dir in modified_addons:
            # Decide o bump_type deste addon específico
            bump_type = "patch"
            if args.major_all or addon_dir in args.major:
                bump_type = "major"
            elif args.minor_all or addon_dir in args.minor:
                bump_type = "minor"
                
            new_version = auto_increment_version(version, bump_type)
            update_version(xml_path, new_version)
            print(f"[{addon_id}] Alterações detectadas. Versão incrementada: {version} -> {new_version}")
            version = new_version
        else:
            print(f"[{addon_id}] Nenhuma alteração. Mantendo versão: {version}")
            
        new_json_versions[addon_id] = version
        create_zip(addon_dir, version)
        
    # Salva o resultado final de volta no JSON para manter o Source of Truth
    save_versions_json(new_json_versions)
        
    # 3. Gera addons.xml com todos os pacotes identificados
    build_addons_xml(addon_dirs)
    
    # Gera os arquivos index.html recursivos para o Kodi File Manager conseguir navegar
    def generate_index_html(folder_path, title="Saile Kodi Repository", is_root=False):
        html = f"<!DOCTYPE html>\n<html>\n<head><title>{title}</title></head>\n<body>\n<h1>{title}</h1>\n<hr/>\n"
        
        # Lista diretórios e arquivos
        for item in sorted(os.listdir(folder_path)):
            if item == "index.html" or item.startswith("."):
                continue
                
            # Na raiz, mostrar SOMENTE a pasta 'zips'
            if is_root and item != "zips":
                continue

            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                html += f'<a href="{item}/">{item}/</a><br>\n'
                # Gera recursivamente para as subpastas
                generate_index_html(item_path, title=f"Index of {item}", is_root=False)
            else:
                html += f'<a href="{item}">{item}</a><br>\n'
        
        html += "</body>\n</html>\n"
        with open(os.path.join(folder_path, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
    
    # Remove qualquer zip que tenha ficado na raiz das execuções antigas
    for f in os.listdir("."):
        if f.startswith("repository.saile") and f.endswith(".zip"):
            os.remove(f)

    # Gera a árvore de navegação (apenas zips na raiz)
    generate_index_html(".", is_root=True)
        
    print("Addons.xml, Zips and Root index.html generated successfully!")
    
    # 4. Envia pro Github
    push_to_github()
