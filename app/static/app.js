// NovaStore v2.0 - State Management & Client Logic
let cart = JSON.parse(localStorage.getItem("novastore_cart") || "[]");
let currentCategory = "todos";
let currentSearch = "";
let activeProductId = null;

// Checkout dynamic state
let checkoutState = {
  couponCode: null,
  couponPercent: 0,
  freeShippingCoupon: false,
  shippingCost: 0,
  shippingRegion: "Sul (PR/SC)",
  shippingDays: 2,
};

function saveCart() {
  localStorage.setItem("novastore_cart", JSON.stringify(cart));
  renderCartUI();
}

function getCartSubtotal() {
  return cart.reduce((acc, item) => acc + item.price * item.quantity, 0);
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
  const drawer = document.getElementById("cartDrawer");
  if (drawer) {
    drawer.classList.add("active");
    renderCartUI();
  }
}

function closeDrawer() {
  const drawer = document.getElementById("cartDrawer");
  if (drawer) drawer.classList.remove("active");
}

function handleBackdropClick(event) {
  if (event.target.id === "cartDrawer") {
    closeDrawer();
  }
}

// Product Detail & Reviews Modal
async function openProductModal(productId) {
  activeProductId = productId;
  try {
    const [prodRes, revRes] = await Promise.all([
      fetch(`/api/products/${productId}`),
      fetch(`/api/products/${productId}/reviews`),
    ]);
    if (!prodRes.ok) return;
    const prod = await prodRes.json();
    const reviews = revRes.ok ? await revRes.json() : [];

    document.getElementById("pmCategory").textContent = prod.category;
    document.getElementById("pmTitle").textContent = prod.name;
    document.getElementById("pmDesc").textContent = prod.description;
    document.getElementById("pmPrice").textContent = `R$ ${prod.price.toFixed(2).replace(".", ",")}`;

    const specsEl = document.getElementById("pmSpecs");
    if (prod.specs) {
      specsEl.innerHTML = prod.specs
        .split("|")
        .map((s) => `<span class="spec-chip">${s.trim()}</span>`)
        .join("");
    } else {
      specsEl.innerHTML = `<span class="spec-chip">Homologado NovaStore Dev Gear</span>`;
    }

    const addBtn = document.getElementById("pmAddBtn");
    if (prod.stock <= 0) {
      addBtn.disabled = true;
      addBtn.innerHTML = `<span>Esgotado</span>`;
    } else {
      addBtn.disabled = false;
      addBtn.innerHTML = `<span>Adicionar ao Carrinho (${prod.stock} disp.)</span>`;
      addBtn.onclick = () => {
        addToCart(prod.id, prod.name, prod.price);
        closeProductModal();
      };
    }

    renderReviewsList(reviews);
    document.getElementById("productModal").classList.add("active");
  } catch (e) {
    console.error(e);
  }
}

function renderReviewsList(reviews) {
  const listEl = document.getElementById("pmReviewsList");
  if (!listEl) return;
  if (!reviews || reviews.length === 0) {
    listEl.innerHTML = `<p style="color: var(--text-dim); font-size: 0.85rem;">Nenhuma avaliacao registrada ainda. Seja o primeiro a avaliar.</p>`;
    return;
  }
  listEl.innerHTML = reviews
    .map(
      (r) => `
      <div class="review-item">
        <div class="review-head">
          <strong style="color: var(--text-main);">${r.author_name}</strong>
          <span style="color: #fbbf24; font-weight: 700;">${"★".repeat(r.rating)}${"☆".repeat(5 - r.rating)}</span>
        </div>
        <p style="font-size: 0.84rem; color: var(--text-muted); line-height: 1.45;">${r.comment}</p>
      </div>
    `
    )
    .join("");
}

function closeProductModal() {
  const modal = document.getElementById("productModal");
  if (modal) modal.classList.remove("active");
}

async function submitProductReview(event) {
  event.preventDefault();
  if (!activeProductId) return;
  const payload = {
    author_name: document.getElementById("revAuthor").value.trim(),
    rating: parseInt(document.getElementById("revRating").value, 10),
    comment: document.getElementById("revComment").value.trim(),
  };
  try {
    const res = await fetch(`/api/products/${activeProductId}/reviews`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      document.getElementById("revComment").value = "";
      showToast("Avaliacao tecnica registrada!");
      await openProductModal(activeProductId);
    }
  } catch (err) {
    console.error(err);
  }
}

// Modal Checkout Controls
async function openCheckoutModal() {
  closeDrawer();
  await quoteShipping();
  refreshCheckoutTotals();
  document.getElementById("checkoutModal").classList.add("active");
}

function closeCheckoutModal() {
  document.getElementById("checkoutModal").classList.remove("active");
}

async function quoteShipping() {
  const zipInput = document.getElementById("custZip");
  const zip = zipInput ? zipInput.value.trim() : "80010-000";
  const subtotal = getCartSubtotal();
  try {
    const res = await fetch("/api/shipping/quote", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        zip_code: zip.length >= 8 ? zip : "80010-000",
        subtotal: subtotal,
        coupon_code: checkoutState.couponCode,
      }),
    });
    if (res.ok) {
      const data = await res.json();
      checkoutState.shippingCost = data.cost;
      checkoutState.shippingRegion = data.region;
      checkoutState.shippingDays = data.estimated_days;
      refreshCheckoutTotals();
    }
  } catch (e) {
    console.error(e);
  }
}

async function applyCoupon() {
  const input = document.getElementById("custCoupon");
  const fb = document.getElementById("couponFeedback");
  const code = input.value.trim().toUpperCase();
  if (!code) return;

  try {
    const res = await fetch("/api/coupons/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, subtotal: getCartSubtotal() }),
    });
    const data = await res.json();
    fb.style.display = "block";
    if (data.valid) {
      checkoutState.couponCode = data.code;
      checkoutState.couponPercent = data.discount_percent;
      checkoutState.freeShippingCoupon = data.free_shipping;
      fb.style.color = "var(--success)";
      fb.textContent = data.message;
      showToast(data.message);
      await quoteShipping();
    } else {
      checkoutState.couponCode = null;
      checkoutState.couponPercent = 0;
      checkoutState.freeShippingCoupon = false;
      fb.style.color = "var(--danger)";
      fb.textContent = data.message;
      await quoteShipping();
    }
    refreshCheckoutTotals();
  } catch (e) {
    console.error(e);
  }
}

function refreshCheckoutTotals() {
  const summaryEl = document.getElementById("checkoutSummary");
  if (!summaryEl) return;

  const subtotal = getCartSubtotal();
  const couponDisc = +(subtotal * (checkoutState.couponPercent / 100)).toFixed(2);
  const payMethodEl = document.getElementById("custPayment");
  const isPix = payMethodEl && payMethodEl.value === "pix";
  const pixDisc = isPix && checkoutState.couponCode ? +((subtotal - couponDisc) * 0.05).toFixed(2) : 0;
  const totalDiscount = +(couponDisc + pixDisc).toFixed(2);
  const shipping = checkoutState.shippingCost;
  const finalTotal = Math.max(0, +(subtotal - totalDiscount + shipping).toFixed(2));

  let itemsHtml =
    '<div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 1rem;">';

  cart.forEach((i) => {
    const sub = i.price * i.quantity;
    itemsHtml += `
      <div style="display: flex; justify-content: space-between; font-size: 0.84rem; margin-bottom: 0.35rem;">
        <span style="color: var(--text-muted);">${i.name} &times; ${i.quantity}</span>
        <span style="font-weight: 600;">R$ ${sub.toFixed(2).replace(".", ",")}</span>
      </div>
    `;
  });

  itemsHtml += `
    <div style="border-top: 1px solid var(--border-subtle); margin-top: 0.6rem; padding-top: 0.6rem; font-size: 0.84rem; color: var(--text-muted);">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
        <span>Subtotal:</span>
        <span>R$ ${subtotal.toFixed(2).replace(".", ",")}</span>
      </div>
      ${
        totalDiscount > 0
          ? `<div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem; color: var(--success);">
              <span>Descontos (${checkoutState.couponCode || "PIX"}):</span>
              <span>- R$ ${totalDiscount.toFixed(2).replace(".", ",")}</span>
            </div>`
          : ""
      }
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
        <span>Frete (${checkoutState.shippingRegion} - ${checkoutState.shippingDays}d uteis):</span>
        <span>${shipping === 0 ? '<strong style="color: var(--success);">Gratis</strong>' : "R$ " + shipping.toFixed(2).replace(".", ",")}</span>
      </div>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 1.05rem; font-weight: 800; border-top: 1px solid var(--border-subtle); padding-top: 0.6rem; margin-top: 0.5rem;">
      <span>Total a Liquidar:</span>
      <span style="color: var(--primary);">R$ ${finalTotal.toFixed(2).replace(".", ",")}</span>
    </div>
  </div>`;

  summaryEl.innerHTML = itemsHtml;
}

// Filtering, Sorting & Live Search
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

function handleSort(mode) {
  const grid = document.getElementById("productsGrid");
  if (!grid) return;
  const cards = Array.from(grid.querySelectorAll(".card"));

  cards.sort((a, b) => {
    const idA = parseInt(a.getAttribute("data-id") || "0", 10);
    const idB = parseInt(b.getAttribute("data-id") || "0", 10);
    const priceA = parseFloat(a.getAttribute("data-price") || "0");
    const priceB = parseFloat(b.getAttribute("data-price") || "0");
    const ratingA = parseFloat(a.getAttribute("data-rating") || "0");
    const ratingB = parseFloat(b.getAttribute("data-rating") || "0");
    const stockA = parseInt(a.getAttribute("data-stock") || "0", 10);
    const stockB = parseInt(b.getAttribute("data-stock") || "0", 10);
    const titleA = a.getAttribute("data-title") || "";
    const titleB = b.getAttribute("data-title") || "";

    if (mode === "price_asc") return priceA - priceB;
    if (mode === "price_desc") return priceB - priceA;
    if (mode === "rating_desc") return ratingB - ratingA;
    if (mode === "stock_desc") return stockB - stockA;
    if (mode === "name_asc") return titleA.localeCompare(titleB);
    return idA - idB;
  });

  cards.forEach((c) => grid.appendChild(c));
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
  if (!toast) return;
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

  const zipEl = document.getElementById("custZip");
  const payload = {
    customer_name: document.getElementById("custName").value.trim(),
    customer_email: document.getElementById("custEmail").value.trim(),
    customer_address: document.getElementById("custAddress").value.trim(),
    zip_code: zipEl && zipEl.value.trim().length >= 8 ? zipEl.value.trim() : "80000-000",
    payment_method: document.getElementById("custPayment").value,
    coupon_code: checkoutState.couponCode,
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

// Admin Panel Functions
async function updateOrderStatus(orderId, newStatus) {
  try {
    const res = await fetch(`/api/admin/orders/${orderId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });
    if (res.ok) {
      showToast(`Pedido ${orderId} atualizado para "${newStatus}"`);
      setTimeout(() => window.location.reload(), 700);
    }
  } catch (e) {
    console.error(e);
  }
}

async function saveProductQuick(productId) {
  const price = parseFloat(document.getElementById(`price-${productId}`).value);
  const stock = parseInt(document.getElementById(`stock-${productId}`).value, 10);
  try {
    const res = await fetch(`/api/admin/products/${productId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ price, stock }),
    });
    if (res.ok) {
      showToast(`Produto #${productId} atualizado com sucesso.`);
      setTimeout(() => window.location.reload(), 600);
    }
  } catch (e) {
    console.error(e);
  }
}

async function createNewProduct(event) {
  event.preventDefault();
  const payload = {
    name: document.getElementById("newProdName").value.trim(),
    category: document.getElementById("newProdCat").value.trim(),
    price: parseFloat(document.getElementById("newProdPrice").value),
    stock: parseInt(document.getElementById("newProdStock").value, 10),
    badge: document.getElementById("newProdBadge").value.trim() || null,
    description: document.getElementById("newProdDesc").value.trim(),
    specs: document.getElementById("newProdSpecs").value.trim() || null,
  };
  try {
    const res = await fetch("/api/admin/products", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      showToast("Novo produto adicionado ao catalogo!");
      setTimeout(() => window.location.reload(), 600);
    }
  } catch (e) {
    console.error(e);
  }
}

async function deleteProduct(productId) {
  try {
    const res = await fetch(`/api/admin/products/${productId}`, {
      method: "DELETE",
    });
    if (res.ok) {
      showToast(`Produto #${productId} removido.`);
      setTimeout(() => window.location.reload(), 600);
    }
  } catch (e) {
    console.error(e);
  }
}

async function saveCoupon(event) {
  event.preventDefault();
  const payload = {
    code: document.getElementById("cpCode").value.trim().toUpperCase(),
    discount_percent: parseFloat(document.getElementById("cpDiscount").value),
    free_shipping: document.getElementById("cpFreeShip").checked,
    active: true,
  };
  try {
    const res = await fetch("/api/admin/coupons", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      showToast(`Cupom ${payload.code} salvo!`);
      setTimeout(() => window.location.reload(), 600);
    }
  } catch (e) {
    console.error(e);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  renderCartUI();
});
