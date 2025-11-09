let tg = window.Telegram.WebApp;
tg.expand();

let products = [];
let cart = [];
let currentCategory = 'all';

// Загрузка товаров из вашего API или JSON
async function loadProducts() {
    // Здесь должен быть запрос к вашему API
    // Для примера используем статические данные
    products = [
        {
            id: 1,
            name: 'Ромашка аптечная',
            description: 'Натуральная ромашка для чая',
            price: 150,
            category: 'Лекарственные травы',
            image: '🌼',
            in_stock: true
        },
        {
            id: 2,
            name: 'Мята перечная',
            description: 'Свежая мята для напитков',
            price: 120,
            category: 'Чайные сборы',
            image: '🌿',
            in_stock: true
        },
        {
            id: 3,
            name: 'Базилик сушеный',
            description: 'Ароматный базилик',
            price: 180,
            category: 'Специи',
            image: '🌱',
            in_stock: true
        }
    ];
    
    renderProducts();
}

function renderProducts() {
    const container = document.getElementById('products');
    const filtered = currentCategory === 'all' 
        ? products 
        : products.filter(p => p.category === currentCategory);
    
    container.innerHTML = filtered.map(product => `
        <div class="product-card">
            <div class="product-image">${product.image || '🌿'}</div>
            <div class="product-info">
                <div class="product-name">${product.name}</div>
                <div class="product-description">${product.description}</div>
                <div class="product-footer">
                    <div class="product-price">${product.price} ₽</div>
                    <button class="add-btn" onclick="addToCart(${product.id})" 
                            ${!product.in_stock ? 'disabled' : ''}>
                        ${product.in_stock ? '+ В корзину' : 'Нет в наличии'}
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function showTab(category) {
    currentCategory = category;
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.toggle('active', tab.textContent.includes(category) || 
                            (category === 'all' && tab.textContent === 'Все'));
    });
    renderProducts();
}

function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    const existing = cart.find(item => item.id === productId);
    
    if (existing) {
        existing.quantity++;
    } else {
        cart.push({ ...product, quantity: 1 });
    }
    
    updateCart();
    tg.HapticFeedback.impactOccurred('light');
}

function updateCart() {
    document.getElementById('cart-count').textContent = cart.reduce((sum, item) => sum + item.quantity, 0);
    
    const cartItems = document.getElementById('cart-items');
    cartItems.innerHTML = cart.map((item, index) => `
        <div class="cart-item">
            <div>
                <div><strong>${item.name}</strong></div>
                <div>${item.price} ₽ × ${item.quantity}</div>
            </div>
            <div>
                <button onclick="changeQuantity(${index}, -1)">-</button>
                ${item.quantity}
                <button onclick="changeQuantity(${index}, 1)">+</button>
            </div>
        </div>
    `).join('');
    
    const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    document.getElementById('total').textContent = total;
}

function changeQuantity(index, delta) {
    cart[index].quantity += delta;
    if (cart[index].quantity <= 0) {
        cart.splice(index, 1);
    }
    updateCart();
}

function toggleCart() {
    document.getElementById('cart-panel').classList.toggle('active');
}

function checkout() {
    if (cart.length === 0) {
        tg.showAlert('Корзина пуста!');
        return;
    }
    document.getElementById('checkout-modal').classList.add('active');
}

function closeCheckout() {
    document.getElementById('checkout-modal').classList.remove('active');
}

function sendOrder() {
    const contact = document.getElementById('contact').value;
    if (!contact) {
        tg.showAlert('Введите контактные данные!');
        return;
    }
    
    const orderData = {
        type: 'order',
        products: cart,
        total: cart.reduce((sum, item) => sum + item.price * item.quantity, 0),
        contact: contact
    };
    
    tg.sendData(JSON.stringify(orderData));
    tg.close();
}

// Инициализация
loadProducts();
