# NovaStore - E-Commerce Web Application

Aplicacao de e-commerce rapida e funcional desenvolvida com FastAPI, SQLite e Vanilla JavaScript.

## Tecnologias
- **Backend**: Python 3.15 com FastAPI e Pydantic (tipagem estrita).
- **Servidor ASGI**: Uvicorn.
- **Banco de Dados**: SQLite relacional nativo (`products`, `orders`, `order_items`).
- **Templates**: Jinja2.
- **Frontend**: HTML5, CSS3 responsivo (tema escuro com glassmorphism) e JavaScript nativo sem dependencias externas de CDN.

## Funcionalidades
1. Catalogo de produtos com categorizacao e precos.
2. Filtro dinamico por categorias no client-side.
3. Carrinho de compras com persistencia local via `localStorage`.
4. Fluxo de checkout com validacao estrita de dados e estoque.
5. Emissao de recibo/resumo de pedido com codigo unico de rastreio (`ORD-XXXXXXXX`).
6. Documentacao interativa da API em `/docs`.

## Como Executar

```powershell
# Acessar a pasta do projeto
cd C:\Users\Pichau\Desktop\DEV_Workspace\store_app

# Iniciar o servidor
uv run run.py
```

Acesse no navegador:
- Loja: `http://127.0.0.1:8000`
- API Docs (Swagger): `http://127.0.0.1:8000/docs`
