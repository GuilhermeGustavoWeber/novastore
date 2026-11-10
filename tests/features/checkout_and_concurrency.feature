# language: pt
Funcionalidade: Fechamento de Pedidos e Controle de Concorrência de Estoque

  Como cliente do NovaStore
  Quero adicionar itens ao carrinho e realizar o checkout com segurança
  Para garantir que compras concorrentes não causem venda duplicada ou saldo negativo

  Cenário: Checkout com sucesso e decremento de estoque
    Dado que o produto "Teclado Mecanico TKL RGB" possui 25 unidades em estoque
    Quando o cliente solicita o checkout de 2 unidades via PIX
    Então o pedido deve ser confirmado com status "Confirmado"
    E o estoque do produto deve ser atualizado para 23 unidades

  Cenário: Bloqueio de venda por estoque insuficiente
    Dado que o produto "Dock Station USB-C 10 em 1" possui 15 unidades em estoque
    Quando o cliente tenta comprar 20 unidades
    Então o sistema deve rejeitar a transação com código HTTP 400
    E exibir a mensagem "Estoque insuficiente"
    E o estoque do produto deve permanecer inalterado em 15 unidades

  Cenário: Cancelamento e devolução atômica de estoque
    Dado que existe um pedido confirmado contendo 2 unidades de "Teclado Mecanico TKL RGB"
    Quando o administrador altera o status do pedido para "Cancelado"
    Então o estoque de 2 unidades deve ser estornado automaticamente para a vitrine
