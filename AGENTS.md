# AGENTS.md

## Padrão de distribuição Windows

Para aplicativos desktop Windows em Python, seguir obrigatoriamente o padrão documentado em:

docs/PADRAO_DISTRIBUICAO_WINDOWS.md

Regras principais:

- Gerar instalador `.exe` para usuário final.
- Não entregar apenas script Python ou executável portátil, salvo pedido explícito.
- O instalador deve criar atalhos na Área de Trabalho e Menu Iniciar.
- Configurações sensíveis devem ficar em `%APPDATA%\NomeDoApp\.env`.
- O app deve ter botão visual para configurar chave de API quando depender de serviço externo.
- Não exigir que usuário final edite `.env` manualmente.
- Publicação deve considerar GitHub Releases.
