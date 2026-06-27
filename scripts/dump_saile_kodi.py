import os

# Descobre onde o script está rodando
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Se o script estiver dentro da pasta "scripts", o alvo real (raiz) é uma pasta acima
if os.path.basename(CURRENT_DIR) == "scripts":
    ROOT_DIR = os.path.dirname(CURRENT_DIR)
else:
    ROOT_DIR = CURRENT_DIR

# O arquivo de saída será salvo na raiz do addon para fácil acesso
OUTPUT_FILE = os.path.join(ROOT_DIR, "saile_dump.md")

# Arquivos sem extensão convencional que DEVEM ser capturados no dump de código
ALLOWED_SPECIAL_FILES = {
    ".env",
    ".gitignore"
}

# Extensões normais permitidas para leitura de texto
ALLOWED_EXTENSIONS = {
    ".py",
    ".xml",
    ".json",
    ".txt"
}

# Pastas completamente ignoradas tanto na árvore quanto na leitura de código
IGNORE_DIRS = {
    "__pycache__",
    ".git",
    "zips",
    "dist",
    "build",
    "scripts"  # Ignora a si mesmo e outros scripts utilitários
}

# Arquivos ignorados globalmente (na árvore e no conteúdo)
IGNORE_FILES = {
    ".zip", 
    ".md5"
}

# Extensões de arquivos que NÃO devem ter o conteúdo lido (Markdown)
IGNORE_CONTENT_EXTENSIONS = {
    ".md"  # Ignora o conteúdo de arquivos .md para não duplicar documentação
}


def should_ignore_file(filename):
    if any(filename.endswith(ext) for ext in IGNORE_FILES):
        return True
    if any(filename.endswith(ext) for ext in IGNORE_CONTENT_EXTENSIONS):
        return True
    return False


def print_tree(start_path):
    tree_lines = []

    for root, dirs, files in os.walk(start_path):
        # Modifica os subdiretórios in-place para o os.walk não entrar neles
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        level = root.replace(start_path, "").count(os.sep)
        indent = "│   " * level
        
        if root != start_path:
            tree_lines.append(f"{indent}├── {os.path.basename(root)}/")
        else:
            tree_lines.append("├── ./ (raiz do addon)")

        subindent = "│   " * (level + 1)
        for f in files:
            if not should_ignore_file(f):
                tree_lines.append(f"{subindent}{f}")

    return "\n".join(tree_lines)


def extract_files(start_path):
    result = []

    for root, dirs, files in os.walk(start_path):
        # Garante que o loop não processe arquivos de pastas na lista de ignoradas
        if any(skip in root.split(os.sep) for skip in IGNORE_DIRS):
            continue

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            
            if ext not in ALLOWED_EXTENSIONS and file not in ALLOWED_SPECIAL_FILES:
                continue
                
            if should_ignore_file(file):
                continue

            full_path = os.path.join(root, file)

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                rel_path = os.path.relpath(full_path, start_path)
                imports = []

                if ext == ".py":
                    imports = [
                        line.strip()
                        for line in content.splitlines()
                        if line.strip().startswith("import ")
                        or line.strip().startswith("from ")
                    ]

                result.append({
                    "file": rel_path,
                    "content": content,
                    "imports": imports
                })

            except Exception as e:
                rel_path = os.path.relpath(full_path, start_path)
                result.append({
                    "file": rel_path,
                    "content": f"ERROR ao ler arquivo: {e}",
                    "imports": []
                })

    return result


def main():
    print(f"[+] Alvo do Addon detectado em: {os.path.abspath(ROOT_DIR)}")
    print(f"[+] Gerando dump do projeto...")

    tree = print_tree(ROOT_DIR)
    files = extract_files(ROOT_DIR)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# SAILE TV E REPOSITORIO - PROJECT DUMP\n\n")

        f.write("## 📁 TREE STRUCTURE\n\n")
        f.write("```\n")
        f.write(tree)
        f.write("\n```\n\n")

        f.write("## 🧠 SOURCE CODE ANALYSIS\n\n")

        for file in files:
            f.write(f"### 📄 {file['file']}\n\n")

            if file["imports"]:
                f.write("#### Imports\n")
                for imp in file["imports"]:
                    f.write(f"- {imp}\n")
                f.write("\n")

            f.write("#### Code\n")
            f.write("```text\n")
            f.write(file["content"])
            f.write("\n```\n\n")

    print(f"[+] Sucesso! Dump gerado na raiz do projeto: {os.path.abspath(OUTPUT_FILE)}")


if __name__ == "__main__":
    main()