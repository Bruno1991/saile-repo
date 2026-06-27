# Contribuindo para o Saile TV

Obrigado pelo seu interesse em contribuir para o projeto **Saile TV**! Este é um projeto de código aberto e todas as contribuições são bem-vindas, sejam elas correções de bugs, novas funcionalidades ou melhorias na documentação.

## 🛠️ Como Contribuir

1. Faça um **Fork** do repositório original.
2. Crie uma branch para a sua feature ou correção (`git checkout -b feature/minha-feature`).
3. Faça suas modificações no código.
4. **IMPORTANTE:** Nunca modifique os arquivos `addons.xml` ou gere os arquivos `.zip` manualmente.
5. Após terminar suas modificações, rode o nosso script oficial de build:
   ```bash
   python scripts/build_repo.py
   ```
   *Este script fará o incremento automático da versão (se houver mudanças detectadas), atualizará o `addons.xml`, atualizará os hashes MD5 e criará/atualizará os arquivos `.zip` correspondentes na pasta `zips/`.*
6. Faça o commit das suas mudanças (`git commit -m 'feat: Adicionada nova funcionalidade X'`).
7. Faça o Push para a sua branch (`git push origin feature/minha-feature`).
8. Abra um **Pull Request** detalhando as alterações que foram feitas.

## Padrões de Código
- O código é escrito em Python 3 nativo do Kodi (Matrix/Nexus/Omega).
- Atualmente utilizamos um padrão MVC (Model-View-Controller).
  - Lógica visual de Menu e Construção de Listas -> Pasta `controllers/`.
  - Consumo de API Externa -> `*_api.py`.
  - Manipulação de Banco de Dados -> `database.py`.

Agradecemos o apoio para tornar este o melhor addon de Kodi do Brasil!
