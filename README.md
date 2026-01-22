# REQUISIÇÃO

# 📘 Documentação do Sistema de Requisições Xodó

## 1. Visão Geral

O **Sistema de Requisições Xodó** é uma aplicação web desenvolvida em **Django**, criada para gerenciar requisições internas de produtos/itens entre usuários e um setor administrativo (estoque).

O sistema permite:

* Usuários criarem requisições de produtos
* Setor administrativo visualizar pedidos recebidos
* Geração de PDF dos pedidos
* Controle de status (Pendente / Concluído)
* Histórico seguro via Django Admin

---

## 2. Tecnologias Utilizadas

* **Python 3.10+**
* **Django**
* **PostgreSQL** (produção – Render)
* **SQLite** (ambiente local)
* **Gunicorn** (servidor WSGI)
* **Whitenoise** (arquivos estáticos)
* **Cloudinary** (imagens)
* **xhtml2pdf** (geração de PDF)
* **Render** (deploy)
* **GitHub** (controle de versão)

---

## 3. Estrutura do Projeto

```
requisicoes/
├── core/
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── migrations/
│   ├── templates/
│   │   ├── admin/
│   │   ├── user/
│   │   └── pdf/
│   └── static/
├── requisicoes/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

---

## 4. Modelos do Sistema

### 4.1 Requisition

Representa uma categoria de requisição.

* `name`
* `description`
* `image` (Cloudinary)
* `icon` (Cloudinary)
* `created_at`

### 4.2 Product

Produtos vinculados a uma requisição.

* `requisition`
* `name`
* `image`
* `unit`

### 4.3 Order (Pedido)

Representa um pedido criado por um usuário.

* `user`
* `requisition`
* `created_at`
* `status` (**PENDENTE | CONCLUIDO**)
* `concluded_at`

### 4.4 OrderItem

Itens pertencentes a um pedido.

* `order`
* `product`
* `quantity`

---

## 5. Fluxo do Sistema

### 5.1 Usuário

1. Usuário faz login
2. Seleciona uma requisição
3. Escolhe produtos e quantidades
4. Envia o pedido
5. Visualiza seus pedidos enviados

### 5.2 Setor Administrativo

1. Acessa área administrativa
2. Visualiza apenas pedidos **PENDENTES**
3. Gera PDF do pedido
4. Marca pedido como **CONCLUÍDO**
5. Pedido sai da lista de pendentes

---

## 6. Controle de Status (ATUALIZAÇÃO IMPLEMENTADA)

### 📌 Nova Funcionalidade

Foi implementado um **controle de status profissional** para os pedidos.

### Status possíveis:

* `PENDENTE` (default ao criar pedido)
* `CONCLUIDO` (após ação do setor)

### Comportamento:

* Tela **Pedidos Recebidos** mostra **apenas pendentes**
* Ao clicar em **Concluir**, o pedido:

  * Atualiza status para CONCLUÍDO
  * Registra data/hora de conclusão
  * Some da lista de pendentes
* Pedido continua acessível no **Django Admin** como histórico

### Benefícios:

* Não há exclusão de dados
* Histórico preservado
* Controle real de fluxo

---

## 7. Geração de PDF

### Características:

* PDF gerado sob demanda
* Conteúdo simples e otimizado
* Sem QR Code
* Sem logo (otimização de performance)

### Otimizações aplicadas:

* Uso de `select_related` e `prefetch_related`
* Menos queries ao banco
* Melhor desempenho em produção (Render)

---

## 8. Django Admin

O Django Admin é usado como:

* Painel de histórico
* Auditoria de pedidos
* Filtro por status (Pendente / Concluído)
* Consulta completa sem criar novas telas

---

## 9. Segurança

* HTTPS forçado em produção
* Cookies seguros
* CSRF habilitado
* Variáveis sensíveis via Environment Variables

---

## 10. Deploy (Render)

### Build Command

```
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

### Start Command

```
gunicorn requisicoes.wsgi:application --bind 0.0.0.0:10000 --workers 2 --threads 2 --timeout 120
```

### Variáveis de Ambiente

* `DATABASE_URL`
* `SECRET_KEY`
* `DEBUG=0`
* `CLOUDINARY_URL`

---

## 11. Controle de Versão

O projeto utiliza **Git + GitHub** para versionamento:

* Branch principal: `main`
* Commits descritivos
* Deploy automático via Render

---

## 12. Conclusão

O Sistema de Requisições Xodó está:

* Estável
* Seguro
* Escalável
* Com fluxo profissional de pedidos

A atualização de **status PENDENTE / CONCLUÍDO** elevou o sistema a um nível de uso real em produção, com rastreabilidade e controle adequados.

---

📌 **Desenvolvido por:** Diogo Silva
📅 **Última atualização:** Janeiro / 2026
