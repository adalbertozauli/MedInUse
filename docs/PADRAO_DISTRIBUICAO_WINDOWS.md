# Padrão Para Distribuição de Aplicativos Windows

Este documento descreve o padrão recomendado para aplicativos desktop feitos em Python para usuários com pouca experiência técnica.

O objetivo é sempre entregar um instalador simples, com configuração pelo próprio aplicativo, sem exigir que o usuário procure arquivos internos ou use terminal.

## Resultado Esperado

Cada aplicativo deve ter:

- Um instalador `.exe` para publicar em `GitHub Releases`.
- Instalação sem terminal.
- Atalho na Área de Trabalho.
- Atalho no Menu Iniciar.
- Configurações salvas em `%APPDATA%`.
- Botão dentro do app para configurar chaves, tokens ou preferências quando necessário.
- Nenhuma chave sensível versionada no GitHub.

## Regra Principal

Não depender de `.env` ao lado do executável para usuário final.

Para desenvolvimento, `.env` na raiz do projeto é aceitável.

Para usuário final, salvar configuração em:

```text
%APPDATA%\NomeDoApp\.env
```

Exemplo:

```text
%APPDATA%\HoraDoRemedio\.env
```

## Checklist De UX Para Usuário Final

- O usuário baixa apenas um arquivo instalador, por exemplo `MeuAppSetup-v1.0.0.exe`.
- O instalador cria os atalhos.
- Ao abrir o app, existe um botão claro como `Configurar chave da API` quando o app depende de chave externa.
- Se a chave não estiver configurada, a mensagem explica o que fazer sem mencionar terminal.
- O aplicativo deve continuar utilizável para tarefas que não dependem da chave.
- Mensagens de erro devem ser claras, curtas e acionáveis.

## Estrutura Recomendada

```text
projeto/
├── main.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── services/
│   └── config_service.py
├── ui/
│   └── main_window.py
├── assets/
├── installer/
│   └── nome_do_app_installer.py
├── dist/
├── build/
└── release/
```

## Configuração Do Aplicativo

Criar um serviço parecido com `services/config_service.py`.

Responsabilidades:

- Descobrir pasta do app em desenvolvimento.
- Descobrir pasta do executável quando empacotado.
- Descobrir pasta de configuração do usuário em `%APPDATA%`.
- Carregar `.env` local e `.env` do usuário.
- Salvar chaves de API pelo próprio aplicativo.

Padrão recomendado:

```python
def user_config_dir() -> Path:
    root = os.getenv("APPDATA") or str(Path.home())
    return Path(root) / "NomeDoApp"


def user_env_path() -> Path:
    return user_config_dir() / ".env"
```

## Botão De Configuração No App

Todo app que depende de chave externa deve ter um botão visível:

```text
Configurar chave da API
```

Esse botão deve:

- abrir uma caixa de texto;
- permitir colar a chave;
- salvar em `%APPDATA%\NomeDoApp\.env`;
- avisar que a chave foi salva;
- atualizar as variáveis de ambiente da sessão atual.

## Gerar Executável Principal

Instalar PyInstaller:

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller
```

Gerar app principal:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name NomeDoApp --add-data "assets;assets" .\main.py
```

Saída esperada:

```text
dist\NomeDoApp.exe
```

## Gerar Instalador Simples

Criar um script em `installer/`.

Responsabilidades do instalador:

- copiar o `.exe` principal para:

```text
%LOCALAPPDATA%\Programs\Nome Do App\
```

- criar atalho na Área de Trabalho;
- criar atalho no Menu Iniciar;
- abrir o app ao final;
- mostrar mensagem simples de sucesso.

Depois gerar o instalador:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name NomeDoAppSetup --add-data "dist\NomeDoApp.exe;." .\installer\nome_do_app_installer.py
```

Saída esperada:

```text
dist\NomeDoAppSetup.exe
```

Renomear para release:

```text
NomeDoAppSetup-v1.0.0.exe
```

## Gitignore Recomendado

```gitignore
.env
.venv/
__pycache__/
*.py[cod]
build/
dist/
release/
tools/
*.spec
outputs/
```

## Publicação No GitHub Releases

Depois de commitar as mudanças:

```powershell
git add .
git commit -m "Prepara instalador Windows"
git push
```

Criar release pelo terminal:

```powershell
gh release create v1.0.0 ".\release\NomeDoAppSetup-v1.0.0.exe" --title "Nome do App v1.0.0" --notes "Instalador Windows."
```

## Critério De Pronto

Antes de publicar, testar em uma pasta limpa:

- abrir o instalador;
- confirmar que o atalho foi criado;
- abrir o app pelo atalho;
- configurar a chave pelo botão, quando houver;
- fechar e abrir novamente;
- confirmar que a configuração foi mantida.

## Observação Importante

PyInstaller cria executáveis sem assinatura digital. Em alguns computadores, o Windows SmartScreen pode avisar que o aplicativo é desconhecido.

Para distribuição ampla, considerar assinatura digital no futuro.
