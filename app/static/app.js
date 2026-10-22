// NovaStore - State Management & Client Logic
let cart = JSON.parse(localStorage.getItem("novastore_cart") || "[]");
let currentCategory = "todos";
let currentSearch = "";

function saveCart() {
  localStorage.setItem("novastore_cart", JSON.stringify(cart));
  renderCartUI();
}

function renderCartUI() {
  const totalCount = cart.reduce((acc, item) => acc + item.quantity, 0);
  const badgeEl = document.getElementById("cartBadge");
  if (badgeEl) {
    badgeEl.textContent = totalCount;
  }

  const listEl = document.getElementById("drawerCartList");
  const totalEl = document.getElementById("drawerTotal");
  const checkoutBtn = document.getElementById("btnGoToCheckout");

  if (!listEl) return;

  if (cart.length === 0) {
    listEl.innerHTML = `
      <div style="text-align: center; color: var(--text-dim); padding: 4rem 1rem;">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" style="margin-bottom: 1rem; opacity: 0.5;">
          <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>
          <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
        </svg>
        <p style="font-weight: 600; color: var(--text-muted);">Seu carrinho esta vazio.</p>
        <p style="font-size: 0.82rem; margin-top: 0.25rem;">Adicione itens da loja para continuar.</p>
      </div>
    `;
    if (totalEl) totalEl.textContent = "R$ 0,00";
    if (checkoutBtn) checkoutBtn.disabled = true;
    return;
  }

  let total = 0;
  listEl.innerHTML = cart
    .map((item, idx) => {
      const subtotal = item.price * item.quantity;
      total += subtotal;
      return `
        <div class="cart-item">
          <div class="item-info">
            <div class="item-name">${item.name}</div>
            <div class="item-price">R$ ${item.price.toFixed(2).replace(".", ",")}</div>
          </div>
          <div class="item-controls">
            <button class="qty-btn" onclick="updateQty(${idx}, -1)">&minus;</button>
            <span class="qty-display">${item.quantity}</span>
            <button class="qty-btn" onclick="updateQty(${idx}, 1)">&plus;</button>
          </div>
          <button class="btn-remove" title="Remover item" onclick="deleteItem(${idx})">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
        </div>
      `;
    })
    .join("");

  if (totalEl) {
    totalEl.textContent = `R$ ${total.toFixed(2).replace(".", ",")}`;
  }
  if (checkoutBtn) {
    checkoutBtn.disabled = false;
  }
}

function addToCart(id, name, price) {
  const existing = cart.find((i) => i.id === id);
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.push({ id, name, price, quantity: 1 });
  }
  saveCart();
  showToast(`Item "${name}" adicionado ao carrinho.`);
}

function updateQty(index, delta) {
  if (cart[index]) {
    cart[index].quantity += delta;
    if (cart[index].quantity <= 0) {
      cart.splice(index, 1);
    }
    saveCart();
  }
}

function deleteItem(index) {
  if (cart[index]) {
    const name = cart[index].name;
    cart.splice(index, 1);
    saveCart();
    showToast(`"${name}" removido.`);
  }
}

// Drawer Controls
function openDrawer() {
  document.getElementById("cartDrawer").classList.add("active");
  renderCartUI();
}

function closeDrawer() {
  document.getElementById("cartDrawer").classList.remove("active");
}

function handleBackdropClick(event) {
  if (event.target.id === "cartDrawer") {
    closeDrawer();
  }
}

// Modal Checkout Controls
function openCheckoutModal() {
  closeDrawer();
  const summaryEl = document.getElementById("checkoutSummary");
  let total = 0;
  let itemsHtml = '<div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 1rem; margin-bottom: 1.25rem;">';
  
  cart.forEach((i) => {
    const sub = i.price * i.quantity;
    total += sub;
    itemsHtml += `
      <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.4rem;">
        <span style="color: var(--text-muted);">${i.name} &times; ${i.quantity}</span>
        <span style="font-weight: 600;">R$ ${sub.toFixed(2).replace(".", ",")}</span>
      </div>
    `;
  });

  itemsHtml += `
    <div style="display: flex; justify-content: space-between; font-size: 1rem; font-weight: 800; border-top: 1px solid var(--border-subtle); padding-top: 0.6rem; margin-top: 0.6rem;">
      <span>Total com frete incluso:</span>
      <span style="color: var(--primary);">R$ ${total.toFixed(2).replace(".", ",")}</span>
    </div>
  </div>`;

  summaryEl.innerHTML = itemsHtml;
  document.getElementById("checkoutModal").classList.add("active");
}

function closeCheckoutModal() {
  document.getElementById("checkoutModal").classList.remove("active");
}

// Filtering & Live Search
function filterCategory(cat, btn) {
  currentCategory = cat;
  document.querySelectorAll(".chip-btn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  applyCardFilters();
}

function handleSearch(query) {
  currentSearch = query.trim().toLowerCase();
  applyCardFilters();
}

function applyCardFilters() {
  const cards = document.querySelectorAll(".card");
  cards.forEach((card) => {
    const cardCat = card.getAttribute("data-category");
    const cardTitle = card.getAttribute("data-title");

    const matchesCategory = currentCategory === "todos" || cardCat === currentCategory;
    const matchesSearch = !currentSearch || cardTitle.includes(currentSearch);

    if (matchesCategory && matchesSearch) {
      card.style.display = "flex";
    } else {
      card.style.display = "none";
    }
  });
}

// Toast Feedback
function showToast(msg) {
  const toast = document.getElementById("toast");
  toast.innerHTML = `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
    <span>${msg}</span>
  `;
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, 2600);
}

// Checkout Submission
async function handleCheckout(event) {
  event.preventDefault();
  const btn = document.getElementById("submitOrderBtn");
  btn.disabled = true;
  btn.innerHTML = `<span>Processando pagamento e estoque...</span>`;

  const payload = {
    customer_name: document.getElementById("custName").value.trim(),
    customer_email: document.getElementById("custEmail").value.trim(),
    customer_address: document.getElementById("custAddress").value.trim(),
    payment_method: document.getElementById("custPayment").value,
    items: cart.map((i) => ({ product_id: i.id, quantity: i.quantity })),
  };

  try {
    const res = await fetch("/api/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Falha na transacao");
    }

    const data = await res.json();
    cart = [];
    localStorage.removeItem("novastore_cart");
    window.location.href = `/order/${data.order_id}`;
  } catch (err) {
    alert(`Erro na transacao: ${err.message}`);
    btn.disabled = false;
    btn.innerHTML = `<span>Efetivar Pedido</span>`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  renderCartUI();
});
