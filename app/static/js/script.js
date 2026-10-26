
document.addEventListener("DOMContentLoaded", () => {
    // ==========================================
    // ELEMENTS
    // ==========================================
    const menuToggle = document.getElementById("menuToggle");
    const navigation = document.getElementById("navigation");
    const searchToggle = document.getElementById("searchToggle");
    const searchPanel = document.getElementById("searchPanel");
    const searchInput = document.getElementById("searchInput");
    const cartCount = document.getElementById("cartCount");
    const cartButton = document.getElementById("cartButton");

    const productCards = [
        ...document.querySelectorAll(".product-card")
    ];

    const categoryButtons = [
        ...document.querySelectorAll(".category-pill")
    ];

    const emptyMessage = document.getElementById("emptyMessage");

    // ==========================================
    // PRODUCT CATALOG
    // ==========================================
    let productCatalog = {};

    try {
        productCatalog = JSON.parse(
            localStorage.getItem("sweetHavenProducts") || "{}"
        );
    } catch (error) {
        console.error("Could not load product catalog:", error);
        productCatalog = {};
    }

    // Refresh catalog from the home page.
    // Product IDs are required for checkout.
    productCards.forEach(card => {
        const button = card.querySelector(".add-cart");

        const name = button?.dataset.name;
        const price = Number(button?.dataset.price || 0);
        const stock = Number(button?.dataset.stock);
        const id = Number(card.dataset.id);
        const image =
            card.querySelector("img")?.getAttribute("src") || "";

        if (name && Number.isInteger(id) && id > 0) {
            productCatalog[name] = {
                id,
                name,
                price,
                stock,
                image
            };
        }
    });

    try {
        localStorage.setItem(
            "sweetHavenProducts",
            JSON.stringify(productCatalog)
        );
    } catch (error) {
        console.error("Could not save product catalog:", error);
    }

    // ==========================================
    // LOAD SAVED CART
    // ==========================================
    let cart = {};

    try {
        const savedCart = JSON.parse(
            localStorage.getItem("sweetHavenCart") || "{}"
        );

        if (
            savedCart &&
            typeof savedCart === "object" &&
            !Array.isArray(savedCart)
        ) {
            Object.entries(savedCart).forEach(([name, quantity]) => {
                const qty = Number(quantity);

                if (
                    typeof name === "string" &&
                    Number.isSafeInteger(qty) &&
                    qty > 0
                ) {
                    cart[name] = qty;
                }
            });
        }
    } catch (error) {
        console.error("Could not load saved cart:", error);
        cart = {};
    }

    // ==========================================
    // MOBILE NAVIGATION
    // ==========================================
    if (menuToggle && navigation) {
        menuToggle.addEventListener("click", () => {
            const isOpen = navigation.classList.toggle("open");

            menuToggle.setAttribute(
                "aria-expanded",
                String(isOpen)
            );

            menuToggle.textContent = isOpen ? "✕" : "☰";
        });

        navigation.querySelectorAll("a").forEach(link => {
            link.addEventListener("click", () => {
                navigation.classList.remove("open");

                menuToggle.setAttribute(
                    "aria-expanded",
                    "false"
                );

                menuToggle.textContent = "☰";
            });
        });
    }

    // ==========================================
    // SEARCH PANEL
    // ==========================================
    if (searchToggle && searchPanel && searchInput) {
        searchToggle.addEventListener("click", () => {
            searchPanel.classList.toggle("open");

            if (searchPanel.classList.contains("open")) {
                searchInput.focus();
            }
        });
    }

    // ==========================================
    // PRODUCT FILTERING
    // ==========================================
    function filterProducts(category = "all", search = "") {
        let visibleCount = 0;

        productCards.forEach(card => {
            const cardCategory = (
                card.dataset.category || ""
            ).toLowerCase();

            const cardName = (
                card.dataset.name ||
                card.querySelector(".add-cart")?.dataset.name ||
                ""
            ).toLowerCase();

            const matchesCategory =
                category.toLowerCase() === "all" ||
                cardCategory === category.toLowerCase();

            const matchesSearch =
                cardName.includes(search.toLowerCase());

            const visible = matchesCategory && matchesSearch;

            card.hidden = !visible;

            if (visible) {
                visibleCount++;
            }
        });

        if (emptyMessage) {
            emptyMessage.hidden = visibleCount !== 0;
        }
    }

    function getActiveCategory() {
        return document.querySelector(".category-pill.active")
            ?.dataset.category || "all";
    }

    if (searchPanel && searchInput) {
        searchPanel.addEventListener("submit", event => {
            event.preventDefault();
            alert("Checkout JavaScript is working!");

            filterProducts(
                getActiveCategory(),
                searchInput.value.trim()
            );

            document.getElementById("featured")?.scrollIntoView({
                behavior: "smooth"
            });
        });
    }

    categoryButtons.forEach(button => {
        button.addEventListener("click", () => {
            categoryButtons.forEach(item => {
                item.classList.remove("active");
            });

            button.classList.add("active");

            filterProducts(
                button.dataset.category || "all",
                searchInput?.value.trim() || ""
            );
        });
    });

    // ==========================================
    // SAVE CART
    // ==========================================
    function saveCart() {
        try {
            localStorage.setItem(
                "sweetHavenCart",
                JSON.stringify(cart)
            );
        } catch (error) {
            console.error("Could not save cart:", error);

            alert("Your cart could not be saved in this browser.");
        }
    }

    // ==========================================
    // FORMAT PRICE
    // ==========================================
    function formatPrice(amount) {
        return "₹" + Number(amount).toFixed(2);
    }

    // ==========================================
    // UPDATE HEADER CART COUNT
    // ==========================================
    function updateCartCount() {
        const count = Object.values(cart).reduce(
            (total, quantity) => total + Number(quantity),
            0
        );

        if (cartCount) {
            cartCount.textContent = count;
            cartCount.classList.remove("pop");

            void cartCount.offsetWidth;

            cartCount.classList.add("pop");
        }

        if (cartButton) {
            cartButton.setAttribute(
                "aria-label",
                `Shopping cart, ${count} items`
            );
        }
    }

    // ==========================================
    // RENDER SHOPPING CART PAGE
    // ==========================================
    function renderCartPage() {
        const cartItems = document.getElementById("cartItems");

        if (!cartItems) return;

        const cartEmpty = document.getElementById("cartEmpty");
        const summaryCount = document.getElementById("summaryCount");
        const cartSubtotal = document.getElementById("cartSubtotal");
        const cartTotal = document.getElementById("cartTotal");
        const checkoutButton =
            document.getElementById("checkoutButton");

        cartItems.innerHTML = "";

        let itemCount = 0;
        let subtotal = 0;

        Object.entries(cart).forEach(([name, quantity]) => {
            const product = productCatalog[name];
            const qty = Number(quantity);

            if (
                !product ||
                !Number.isSafeInteger(qty) ||
                qty <= 0
            ) {
                return;
            }

            const price = Number(product.price) || 0;
            const lineTotal = price * qty;

            itemCount += qty;
            subtotal += lineTotal;

            // Cart item
            const item = document.createElement("div");
            item.className = "cart-item";

            // Product image
            const image = document.createElement("img");
            image.className = "cart-item-image";
            image.src = product.image || "";
            image.alt = product.name;

            image.addEventListener("error", () => {
                image.hidden = true;
            });

            // Product details
            const details = document.createElement("div");
            details.className = "cart-item-details";

            const title = document.createElement("h3");
            title.textContent = product.name;

            const priceText = document.createElement("p");
            priceText.textContent = `${formatPrice(price)} each`;

            // Quantity controls
            const controls = document.createElement("div");
            controls.className = "cart-quantity-controls";

            const decrease = document.createElement("button");
            decrease.type = "button";
            decrease.textContent = "−";
            decrease.setAttribute(
                "aria-label",
                `Decrease ${name} quantity`
            );

            const quantityText = document.createElement("span");
            quantityText.textContent = qty;

            const increase = document.createElement("button");
            increase.type = "button";
            increase.textContent = "+";
            increase.setAttribute(
                "aria-label",
                `Increase ${name} quantity`
            );

            decrease.addEventListener("click", () => {
                if (cart[name] > 1) {
                    cart[name]--;
                } else {
                    delete cart[name];
                }

                updateCart();
            });

increase.addEventListener("click", () => {
    const product = productCatalog[name];
    const currentQuantity = Number(cart[name]) || 0;
    const availableStock = Number(product?.stock);

    if (
        !product ||
        !Number.isFinite(availableStock) ||
        availableStock < 0
    ) {
        alert("Unable to check stock. Please refresh the page.");
        return;
    }

    if (currentQuantity >= availableStock) {
        alert(`Only ${availableStock} units of ${name} are available.`);
        return;
    }

    cart[name] = currentQuantity + 1;
    updateCart();
});

            // Remove product
            const remove = document.createElement("button");
            remove.type = "button";
            remove.className = "cart-remove-button";
            remove.textContent = "Remove";

            remove.addEventListener("click", () => {
                delete cart[name];
                updateCart();
            });

            controls.append(decrease, quantityText, increase);

            details.append(
                title,
                priceText,
                controls,
                remove
            );

            // Line total
            const linePrice = document.createElement("strong");
            linePrice.className = "cart-item-total";
            linePrice.textContent = formatPrice(lineTotal);

            item.append(image, details, linePrice);
            cartItems.appendChild(item);
        });

        // Empty cart message
        if (cartEmpty) {
            cartEmpty.hidden = itemCount > 0;
        }

        // Order summary
        if (summaryCount) {
            summaryCount.textContent = itemCount;
        }

        if (cartSubtotal) {
            cartSubtotal.textContent = formatPrice(subtotal);
        }

        if (cartTotal) {
            cartTotal.textContent = formatPrice(subtotal);
        }

        // Checkout navigation
        if (checkoutButton) {
            checkoutButton.disabled = itemCount === 0;

            if (!checkoutButton.dataset.navigationBound) {
                checkoutButton.addEventListener("click", () => {
                    const hasItems = Object.entries(cart).some(
                        ([name, quantity]) =>
                            productCatalog[name] &&
                            Number(quantity) > 0
                    );

                    if (hasItems) {
                        window.location.href = "/checkout";
                    }
                });

                checkoutButton.dataset.navigationBound = "true";
            }
        }
    }

    // ==========================================
    // RENDER CHECKOUT ORDER SUMMARY
    // ==========================================
    function renderCheckoutSummary() {
        const checkoutItems =
            document.getElementById("checkoutItems");

        if (!checkoutItems) return;

        const checkoutItemCount =
            document.getElementById("checkoutItemCount");

        const checkoutSubtotal =
            document.getElementById("checkoutSubtotal");

        const checkoutDelivery =
            document.getElementById("checkoutDelivery");

        const checkoutTotal =
            document.getElementById("checkoutTotal");

        checkoutItems.innerHTML = "";

        let itemCount = 0;
        let subtotal = 0;

        Object.entries(cart).forEach(([name, quantity]) => {
            const product = productCatalog[name];
            const qty = Number(quantity);

            if (
                !product ||
                !Number.isSafeInteger(qty) ||
                qty <= 0
            ) {
                return;
            }

            const price = Number(product.price) || 0;
            const lineTotal = price * qty;

            itemCount += qty;
            subtotal += lineTotal;

            const row = document.createElement("div");
            row.className = "checkout-summary-item";

            const nameText = document.createElement("span");
            nameText.textContent = `${product.name} × ${qty}`;

            const priceText = document.createElement("strong");
            priceText.textContent = formatPrice(lineTotal);

            row.append(nameText, priceText);
            checkoutItems.appendChild(row);
        });

        if (itemCount === 0) {
            const emptyText = document.createElement("p");

            emptyText.textContent =
                "Your cart is empty. Please add sweets before checkout.";

            checkoutItems.appendChild(emptyText);
        }

        if (checkoutItemCount) {
            checkoutItemCount.textContent = itemCount;
        }

        if (checkoutSubtotal) {
            checkoutSubtotal.textContent = formatPrice(subtotal);
        }

        if (checkoutDelivery) {
            checkoutDelivery.textContent = "Calculated at checkout";
        }

        if (checkoutTotal) {
            checkoutTotal.textContent = formatPrice(subtotal);
        }

        const placeOrderButton = document.querySelector(
            '#checkoutForm button[type="submit"], ' +
            '#checkoutForm input[type="submit"]'
        );

        if (placeOrderButton) {
            placeOrderButton.disabled = itemCount === 0;
        }
    }

    // ==========================================
    // CENTRAL CART UPDATE
    // ==========================================
    function updateCart() {
        saveCart();
        updateCartCount();
        renderCartPage();
        renderCheckoutSummary();
    }

    // ==========================================
    // ADD PRODUCTS TO CART
    // ==========================================
   
document.querySelectorAll(".add-cart").forEach(button => {
    button.addEventListener("click", () => {
        const name = button.dataset.name;
        const product = productCatalog[name];

        if (!name || !product) {
            alert("Product details not found. Please refresh the page.");
            return;
        }

        const availableStock = Number(product.stock);
        const currentQuantity = Number(cart[name]) || 0;

        if (!Number.isFinite(availableStock) || availableStock < 0) {
            alert("Unable to check stock. Please refresh the page.");
            return;
        }

        if (currentQuantity >= availableStock) {
            alert(`Only ${availableStock} units of ${name} are available.`);
            return;
        }

        cart[name] = currentQuantity + 1;
        updateCart();

        const originalText = button.innerHTML;
        button.innerHTML = "Added ✓";
        button.disabled = true;

        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 850);
    });
});


    
// ==========================================
// CHECKOUT FORM
// ==========================================
const checkoutForm = document.getElementById("checkoutForm");

if (checkoutForm) {
    checkoutForm.addEventListener("submit", async event => {
        event.preventDefault();

        const cartItems = Object.entries(cart)
            .filter(([name, quantity]) =>
                productCatalog[name] &&
                Number.isSafeInteger(Number(quantity)) &&
                Number(quantity) > 0
            )
            .map(([name, quantity]) => ({
                id: Number(productCatalog[name].id),
                quantity: Number(quantity)
            }));

        if (cartItems.length === 0) {
            alert("Your cart is empty. Please add sweets first.");
            return;
        }

        if (cartItems.some(item =>
            !Number.isInteger(item.id) || item.id <= 0
        )) {
            alert("Product IDs are missing. Please refresh the home page and try again.");
            return;
        }

        const cartItemsInput =
            checkoutForm.querySelector('[name="cart_items"]');

        if (!cartItemsInput) {
            alert('Missing hidden input: name="cart_items".');
            return;
        }

        cartItemsInput.value = JSON.stringify(cartItems);

        console.log("Cart input:", cartItemsInput.value);
        console.log(
            "Form data:",
            [...new FormData(checkoutForm).entries()]
        );

        const message = document.getElementById("checkoutMessage");

        if (message) {
            message.hidden = true;
            message.textContent = "";
        }

        try {
            const response = await fetch(checkoutForm.action, {
                method: "POST",
                body: new FormData(checkoutForm)
            });

            if (response.redirected) {
                window.location.href = response.url;
                return;
            }

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                const detail = data.detail;
                const errorText = Array.isArray(detail)
                    ? detail.map(error => error.msg).join(", ")
                    : detail;

                throw new Error(
                    errorText || "Unable to place your order."
                );
            }

            throw new Error("Unexpected response. Please try again.");
        } catch (error) {
            if (message) {
                message.textContent = error.message;
                message.className = "alert alert-danger";
                message.hidden = false;
                message.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });
            } else {
                alert(error.message);
            }
        }
    });
}


    // ==========================================
    // WISHLIST
    // ==========================================
    document.querySelectorAll(".wishlist").forEach(button => {
        button.addEventListener("click", () => {
            const selected = button.classList.toggle("selected");

            button.textContent = selected ? "♥" : "♡";

            button.setAttribute(
                "aria-pressed",
                String(selected)
            );
        });
    });

    // ==========================================
    // SCROLL REVEAL ANIMATIONS
    // ==========================================
    const revealElements = document.querySelectorAll(".reveal");

    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver(
            (entries, obs) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("visible");
                        obs.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.12 }
        );

        revealElements.forEach(element => {
            observer.observe(element);
        });
    } else {
        revealElements.forEach(element => {
            element.classList.add("visible");
        });
    }

    // ==========================================
    // GENTLE 3D PRODUCT CARD TILT
    // ==========================================
    const canHover = window.matchMedia(
        "(hover: hover) and (pointer: fine)"
    );

    if (canHover.matches) {
        productCards.forEach(card => {
            card.addEventListener("mousemove", event => {
                const rect = card.getBoundingClientRect();

                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;

                const rotateY =
                    ((x / rect.width) - 0.5) * 4;

                const rotateX =
                    (0.5 - (y / rect.height)) * 4;

                card.style.transform =
                    `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            });

            card.addEventListener("mouseleave", () => {
                card.style.transform = "";
            });
        });
    }

    // ==========================================
    // INITIALIZE
    // ==========================================
    updateCart();

    console.log("Sweet Haven initialized successfully.");
});



