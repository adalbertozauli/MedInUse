# MedInUse

Aplicativo Windows para ler receitas em `.docx` e gerar uma lista copiável com as medicações em uso, incluindo nome, dose e posologia resumida.

O aplicativo funciona offline, sem IA e sem chave de API obrigatória.

## Como Usar

1. Abra o MedInUse.
2. Clique em `Escolher DOCX`.
3. Escolha o formato da saída:
   - `Uma por linha`: cada medicação começa com `- `.
   - `Linha única`: todas as medicações ficam na mesma linha.
4. Revise a lista gerada.
5. Clique em `Copiar`.

Quando alguma posologia não puder ser inferida com segurança, o app abre uma janela de revisão para correção manual antes da cópia.

## Exemplos De Saída

```text
- Losartana 50mg (1-0-1)
- Anlodipino 5mg (1-0-0)
- Amoxicilina 500mg (1-1-1)
- Cefalexina 500mg (1-1-1-1)
```

## Formato Esperado No DOCX

O app identifica uma linha com a medicação seguida por uma linha de posologia:

```text
Losartana 50mg
Tomar 01 comprimido, de 12/12 horas.
```

Também lê prescrições em tabelas do Word.

## Regras Reconhecidas

Conversões principais:

- `12/12 horas`, `a cada 12 horas`: `(1-0-1)`
- `8/8 horas`, `a cada 8 horas`: `(1-1-1)`
- `6/6 horas`: `(1-1-1-1)`
- `cedo`, `manhã`, `em jejum`, `8:00`: `(1-0-0)`
- `13h` até `17h`: `(0-1-0)`
- `18h` em diante, `noite`, `jantar`, `ao deitar`: `(0-0-1)`
- `café da manhã, almoço e jantar`: `(1-1-1)`
- `antes das refeições`: `(1-1-1)`
- `1 comprimido ao dia`: `(1x/dia)`
- `1 comprimido por semana, 3 meses`: `(1 comp. semana/12 semanas)`
- `dose única`: `(1 comp. dose única)`
- `ampola a cada 30 dias`: `(1 ampola/30 dias)`

Gotas, mL, unidades e puffs:

- `05 gotas de 8/8 horas`: `(5 gts-5gts-5gts)`
- `05 gotas de 12/12 horas`: `(5 gts-0-5gts)`
- `5,0ml de 12/12 horas`: `(5ml-0-5ml)`
- `10 unidades à noite`: `(0-0-10U)`
- `2 puffs pela manhã`: `(2puffs-0-0)`
- `2 jatos em cada narina, 2x/dia`: `(2puffs-0-2puffs)`

Casos variáveis ou clinicamente ambíguos, como Marevan por dias da semana ou insulina sem horário, devem ser revisados manualmente.

## Desenvolvimento

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\main.py
```

## Gerar Instalador Windows

Opção recomendada:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_release.ps1 -Version 1.6.1
```

Saídas esperadas:

```text
dist\MedInUse.exe
release\MedInUseSetup-v1.6.1.exe
```

O instalador copia o aplicativo para `%LOCALAPPDATA%\Programs\MedInUse`, cria atalhos na Área de Trabalho e no Menu Iniciar, e abre o app ao final.

## Publicação No GitHub

O repositório deve conter apenas o código fonte, documentação e scripts.

Não versionar:

- receitas ou documentos de pacientes;
- `.env`;
- `.venv`;
- `build`;
- `dist`;
- `release`;
- arquivos `.spec` gerados pelo PyInstaller.

O instalador `.exe` deve ser publicado em **GitHub Releases**, por exemplo:

```powershell
gh release create v1.6.1 ".\release\MedInUseSetup-v1.6.1.exe" --title "MedInUse v1.6.1" --notes "Instalador Windows."
```

## Privacidade

Não coloque receitas reais, nomes de pacientes, prontuários ou documentos clínicos dentro do repositório.

As amostras usadas para testar regras devem ser transformadas em exemplos fictícios antes de virar teste automatizado.
