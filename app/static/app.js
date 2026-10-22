// State management
let cart = JSON.parse(localStorage.getItem("store_cart") || "[]");

function saveCart() {
  localStorage.setItem("store_cart", JSON.stringify(cart));
  updateCartUI();
}

function updateCartUI() {
  const totalCount = cart.reduce((acc, item) => acc + item.quantity, 0);
  const cartCountEl = document.getElementById("cartCount");
  if (cartCountEl) {
    cartCountEl.textContent = totalCount;
  }

  const cartList = document.getElementById("cartItemsList");
  const cartTotalVal = document.getElementById("cartTotalVal");
  const checkoutBtn = document.getElementById("proceedToCheckoutBtn");

  if (!cartList) return;

  if (cart.length === 0) {
    cartList.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 2rem 0;">Seu carrinho esta vazio.</p>';
    if (cartTotalVal) cartTotalVal.textContent = "R$ 0,00";
    if (checkoutBtn) checkoutBtn.disabled = true;
    return;
  }

  let total = 0;
  cartList.innerHTML = cart
    .map((item, idx) => {
      const subtotal = item.price * item.quantity;
      total += subtotal;
      return `
        <div class="cart-row">
          <div class="cart-row-info">
            <div class="cart-row-name">${item.name}</div>
            <div class="cart-row-price">R$ ${item.price.toFixed(2).replace(".", ",")} un.</div>
          </div>
          <div class="qty-control">
            <button class="qty-btn" onclick="changeQty(${idx}, -1)">-</button>
            <span>${item.quantity}</span>
            <button class="qty-btn" onclick="changeQty(${idx}, 1)">+</button>
          </div>
          <button class="remove-btn" onclick="removeItem(${idx})">Remover</button>
        </div>
      `;
    })
    .join("");

  if (cartTotalVal) {
    cartTotalVal.textContent = `R$ ${total.toFixed(2).replace(".", ",")}`;
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
  showToast(`"${name}" adicionado ao carrinho.`);
}

function changeQty(index, delta) {
  if (cart[index]) {
    cart[index].quantity += delta;
    if (cart[index].quantity <= 0) {
      cart.splice(index, 1);
    }
    saveCart();
  }
}

function removeItem(index) {
  if (cart[index]) {
    cart.splice(index, 1);
    saveCart();
  }
}

function clearCart() {
  cart = [];
  saveCart();
}

// Modals
function openCart() {
  document.getElementById("cartModal").classList.add("active");
  updateCartUI();
}

function closeCart() {
  document.getElementById("cartModal").classList.remove("active");
}

function openCheckout() {
  closeCart();
  const summaryEl = document.getElementById("checkoutSummary");
  let total = 0;
  let summaryHtml = '<ul style="list-style: none; margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;">';
  cart.forEach((i) => {
    const sub = i.price * i.quantity;
    total += sub;
    summaryHtml += `<li style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.35rem;">
      <span>${i.name} (x${i.quantity})</span>
      <span>R$ ${sub.toFixed(2).replace(".", ",")}</span>
    </li>`;
  });
  summaryHtml += `</ul><div style="display:flex; justify-content:space-between; font-weight:700; margin-bottom:1rem;">
    <span>Total:</span>
    <span style="color:var(--accent);">R$ ${total.toFixed(2).replace(".", ",")}</span>
  </div>`;

  summaryEl.innerHTML = summaryHtml;
  document.getElementById("checkoutModal").classList.add("active");
}

function closeCheckout() {
  document.getElementById("checkoutModal").classList.remove("active");
}

// Toast
function showToast(msg) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

// Filter Categories
function filterCategory(category, btnElement) {
  document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
  btnElement.classList.add("active");

  const cards = document.querySelectorAll(".product-card");
  cards.forEach((card) => {
    const c = card.getAttribute("data-category");
    if (category === "todos" || c === category) {
      card.style.display = "flex";
    } else {
      card.style.display = "none";
    }
  });
}

// Submit Order
async function handleCheckout(event) {
  event.preventDefault();
  const btn = document.getElementById("submitOrderBtn");
  btn.disabled = true;
  btn.textContent = "Processando Pedido...";

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
      const errData = await res.json();
      throw new Error(errData.detail || "Erro ao processar pedido");
    }

    const data = await res.json();
    clearCart();
    window.location.href = `/order/${data.order_id}`;
  } catch (err) {
    alert(`Falha no checkout: ${err.message}`);
    btn.disabled = false;
    btn.textContent = "Confirmar e Pagar";
  }
}

// Init
document.addEventListener("DOMContentLoaded", () => {
  updateCartUI();
});
