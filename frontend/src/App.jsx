import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);

  const [showLogin, setShowLogin] = useState(false);
  const [showCart, setShowCart] = useState(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loggedIn, setLoggedIn] = useState(false);
  const [user, setUser] = useState(null);

  const [loginError, setLoginError] = useState("");
  const [loading, setLoading] = useState(false);

  const pathname = window.location.pathname;
  const searchParams = new URLSearchParams(window.location.search);
  const sessionId = searchParams.get("session_id");

  const normalizeCart = (data) => {
    if (Array.isArray(data)) return data;

    if (Array.isArray(data?.items)) return data.items;

    if (Array.isArray(data?.cart)) return data.cart;

    if (Array.isArray(data?.data)) return data.data;

    return [];
  };

  const fetchProducts = async () => {
    try {
      const response = await fetch(
        `${API_URL}/products/`
      );

      if (!response.ok) {
        throw new Error(
          "Unable to fetch products"
        );
      }

      const data = await response.json();

      setProducts(
        Array.isArray(data) ? data : []
      );
    } catch (error) {
      console.error(
        "Error fetching products:",
        error
      );

      setProducts([]);
    }
  };

  const fetchCart = async () => {
    const token = localStorage.getItem(
      "access_token"
    );

    if (!token) {
      setCart([]);
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/cart`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(
          "Unable to fetch cart"
        );
      }

      const data = await response.json();

      setCart(normalizeCart(data));
    } catch (error) {
      console.error(
        "Error fetching cart:",
        error
      );

      setCart([]);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  useEffect(() => {
    const token = localStorage.getItem(
      "access_token"
    );

    if (!token) {
      return;
    }

    fetch(`${API_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            "Token expired"
          );
        }

        return response.json();
      })
      .then((data) => {
        setUser(data);
        setLoggedIn(true);

        fetchCart();
      })
      .catch(() => {
        localStorage.removeItem(
          "access_token"
        );

        localStorage.removeItem(
          "refresh_token"
        );

        setUser(null);
        setLoggedIn(false);
        setCart([]);
      });
  }, []);

  const handleLogin = async (event) => {
    event.preventDefault();

    setLoginError("");
    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/auth/login`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            name: "SmartShop User",
            email: email,
            password: password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setLoginError(
          data.detail ||
            "Login failed"
        );

        setLoading(false);
        return;
      }

      localStorage.setItem(
        "access_token",
        data.access_token
      );

      localStorage.setItem(
        "refresh_token",
        data.refresh_token
      );

      const userResponse = await fetch(
        `${API_URL}/auth/me`,
        {
          headers: {
            Authorization: `Bearer ${data.access_token}`,
          },
        }
      );

      const userData =
        await userResponse.json();

      setUser(userData);

      setLoggedIn(true);

      setShowLogin(false);

      setEmail("");

      setPassword("");

      await fetchCart();
    } catch (error) {
      console.error(
        "Login error:",
        error
      );

      setLoginError(
        "Unable to connect to the server"
      );
    }

    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "refresh_token"
    );

    setUser(null);

    setLoggedIn(false);

    setCart([]);

    setShowCart(false);
  };

  const handleAddToCart = async (
    productId
  ) => {
    if (!loggedIn) {
      alert(
        "Please login before adding products to cart."
      );

      setShowLogin(true);

      return;
    }

    const token = localStorage.getItem(
      "access_token"
    );

    try {
      const response = await fetch(
        `${API_URL}/cart/add`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            Authorization: `Bearer ${token}`,
          },

          body: JSON.stringify({
            product_id: productId,
            quantity: 1,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert(
          data.detail ||
            "Unable to add product to cart."
        );

        return;
      }

      setCart(normalizeCart(data));

      alert(
        "Product added to cart successfully!"
      );
    } catch (error) {
      console.error(
        "Add to cart error:",
        error
      );

      alert(
        "Unable to connect to the server."
      );
    }
  };

  const handleUpdateQuantity = async (
    productId,
    newQuantity
  ) => {
    if (newQuantity <= 0) {
      return;
    }

    const token = localStorage.getItem(
      "access_token"
    );

    try {
      const response = await fetch(
        `${API_URL}/cart/update`,
        {
          method: "PUT",

          headers: {
            "Content-Type":
              "application/json",

            Authorization: `Bearer ${token}`,
          },

          body: JSON.stringify({
            product_id: productId,
            quantity: newQuantity,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert(
          data.detail ||
            "Unable to update quantity."
        );

        return;
      }

      setCart(normalizeCart(data));
    } catch (error) {
      console.error(
        "Update quantity error:",
        error
      );

      alert(
        "Unable to update cart."
      );
    }
  };

  const handleRemoveFromCart = async (
    productId
  ) => {
    const token = localStorage.getItem(
      "access_token"
    );

    try {
      const response = await fetch(
        `${API_URL}/cart/remove`,
        {
          method: "DELETE",

          headers: {
            "Content-Type":
              "application/json",

            Authorization: `Bearer ${token}`,
          },

          body: JSON.stringify({
            product_id: productId,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert(
          data.detail ||
            "Unable to remove product."
        );

        return;
      }

      setCart(normalizeCart(data));
    } catch (error) {
      console.error(
        "Remove cart item error:",
        error
      );

      alert(
        "Unable to remove product from cart."
      );
    }
  };

  const handleCheckout = async () => {
    if (!loggedIn) {
      alert(
        "Please login before checkout."
      );

      setShowLogin(true);

      return;
    }

    if (
      !Array.isArray(cart) ||
      cart.length === 0
    ) {
      alert(
        "Your cart is empty."
      );

      return;
    }

    const token = localStorage.getItem(
      "access_token"
    );

    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/checkout`,
        {
          method: "POST",

          headers: {
            Authorization: `Bearer ${token}`,

            "Content-Type":
              "application/json",
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert(
          data.detail ||
            "Checkout failed."
        );

        setLoading(false);

        return;
      }

      if (data.checkout_url) {
        window.location.href =
          data.checkout_url;

        return;
      }

      alert(
        "Checkout created successfully."
      );

      await fetchCart();

      setShowCart(false);
    } catch (error) {
      console.error(
        "Checkout error:",
        error
      );

      alert(
        "Unable to connect to the checkout server."
      );
    }

    setLoading(false);
  };

  const getProduct = (productId) => {
    return products.find(
      (product) =>
        product.id === productId
    );
  };

  const getCartTotal = () => {
    return cart.reduce(
      (total, item) => {
        return (
          total +
          Number(
            item.item_total || 0
          )
        );
      },
      0
    );
  };

  const getCartCount = () => {
    return cart.reduce(
      (total, item) => {
        return (
          total +
          Number(
            item.quantity || 0
          )
        );
      },
      0
    );
  };

  function PaymentSuccessPage() {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          background: "#f4f7fb",
          padding: "30px",
        }}
      >
        <div
          style={{
            background: "white",
            padding: "50px",
            borderRadius: "20px",
            textAlign: "center",
            maxWidth: "600px",
            width: "100%",
            boxShadow:
              "0 10px 40px rgba(0,0,0,0.12)",
          }}
        >
          <div
            style={{
              width: "80px",
              height: "80px",
              borderRadius: "50%",
              background: "#22c55e",
              color: "white",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "40px",
              margin:
                "0 auto 25px",
            }}
          >
            ✓
          </div>

          <h1
            style={{
              color: "#16a34a",
              fontSize: "42px",
              marginBottom: "15px",
            }}
          >
            Payment Successful!
          </h1>

          <p
            style={{
              fontSize: "18px",
              color: "#374151",
            }}
          >
            Your payment has been completed
            successfully.
          </p>

          <p
            style={{
              fontSize: "16px",
              color: "#16a34a",
              fontWeight: "600",
              marginTop: "20px",
            }}
          >
            Your order has been processed.
          </p>

          {sessionId && (
            <>
              <p
                style={{
                  fontSize: "14px",
                  color: "#6b7280",
                  marginTop: "25px",
                }}
              >
                Payment Session
              </p>

              <p
                style={{
                  fontSize: "13px",
                  color: "#374151",
                  wordBreak: "break-all",
                  background: "#f3f4f6",
                  padding: "12px",
                  borderRadius: "8px",
                }}
              >
                {sessionId}
              </p>
            </>
          )}

          <button
            onClick={() => {
              window.location.href =
                "/";
            }}
            style={{
              marginTop: "20px",
              padding: "14px 30px",
              border: "none",
              borderRadius: "8px",
              background: "#2563eb",
              color: "white",
              fontSize: "16px",
              cursor: "pointer",
            }}
          >
            Continue Shopping
          </button>
        </div>
      </div>
    );
  }

  if (
    pathname ===
    "/payment-success"
  ) {
    return <PaymentSuccessPage />;
  }

  if (
    pathname ===
    "/payment-cancelled"
  ) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          background: "#f4f7fb",
          padding: "30px",
        }}
      >
        <div
          style={{
            background: "white",
            padding: "50px",
            borderRadius: "20px",
            textAlign: "center",
            maxWidth: "600px",
            width: "100%",
            boxShadow:
              "0 10px 40px rgba(0,0,0,0.12)",
          }}
        >
          <h1
            style={{
              color: "#dc2626",
            }}
          >
            Payment Cancelled
          </h1>

          <p
            style={{
              fontSize: "18px",
              color: "#374151",
            }}
          >
            Your Stripe payment was
            cancelled.
          </p>

          <button
            onClick={() => {
              window.location.href =
                "/";
            }}
            style={{
              marginTop: "20px",
              padding: "14px 30px",
              border: "none",
              borderRadius: "8px",
              background: "#2563eb",
              color: "white",
              fontSize: "16px",
              cursor: "pointer",
            }}
          >
            Return to Shop
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <nav className="navbar">
        <div
          className="logo"
          onClick={() => {
            setShowCart(false);

            window.scrollTo(
              0,
              0
            );
          }}
          style={{
            cursor: "pointer",
          }}
        >
          SmartShop
        </div>

        <div className="nav-links">
          <a
            href="#"
            onClick={() =>
              setShowCart(false)
            }
          >
            Home
          </a>

          <a
            href="#products"
            onClick={() =>
              setShowCart(false)
            }
          >
            Products
          </a>

          {!loggedIn ? (
            <button
              className="nav-button"
              onClick={() =>
                setShowLogin(true)
              }
            >
              Login
            </button>
          ) : (
            <>
              <span className="welcome-user">
                Hi, {user?.name}
              </span>

              <button
                className="nav-button"
                onClick={
                  handleLogout
                }
              >
                Logout
              </button>
            </>
          )}

          <button
            className="cart-button"
            onClick={() => {
              if (!loggedIn) {
                alert(
                  "Please login to view your cart."
                );

                setShowLogin(true);

                return;
              }

              setShowCart(true);

              fetchCart();
            }}
          >
            🛒 Cart (
            {getCartCount()})
          </button>
        </div>
      </nav>

      {showLogin &&
        !loggedIn && (
          <section className="login-section">
            <div className="login-card">
              <h2>
                Login to SmartShop
              </h2>

              <form
                onSubmit={
                  handleLogin
                }
              >
                <label>
                  Email
                </label>

                <input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(
                    event
                  ) =>
                    setEmail(
                      event.target.value
                    )
                  }
                  required
                />

                <label>
                  Password
                </label>

                <input
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(
                    event
                  ) =>
                    setPassword(
                      event.target.value
                    )
                  }
                  required
                />

                {loginError && (
                  <p className="login-error">
                    {loginError}
                  </p>
                )}

                <button
                  type="submit"
                  className="login-submit"
                  disabled={
                    loading
                  }
                >
                  {loading
                    ? "Logging in..."
                    : "Login"}
                </button>
              </form>

              <button
                className="cancel-login"
                onClick={() => {
                  setShowLogin(
                    false
                  );

                  setLoginError(
                    ""
                  );
                }}
              >
                Cancel
              </button>
            </div>
          </section>
        )}

      {showCart ? (
        <section className="cart-page">
          <h1>
            🛒 Your Cart
          </h1>

          {!Array.isArray(
            cart
          ) ||
          cart.length === 0 ? (
            <div className="empty-cart">
              <h2>
                Your cart is empty
              </h2>

              <p>
                Add some products to
                your cart.
              </p>

              <button
                className="shop-button"
                onClick={() =>
                  setShowCart(false)
                }
              >
                Continue Shopping
              </button>
            </div>
          ) : (
            <div className="cart-layout">
              <div className="cart-items">
                {cart.map(
                  (item) => {
                    const product =
                      getProduct(
                        item.product_id
                      );

                    return (
                      <div
                        className="cart-item"
                        key={
                          item.id
                        }
                      >
                        <img
                          src={
                            product?.images ||
                            "https://via.placeholder.com/150"
                          }
                          alt={
                            item.product_name ||
                            product?.name
                          }
                          className="cart-image"
                        />

                        <div className="cart-item-details">
                          <h3>
                            {item.product_name ||
                              product?.name}
                          </h3>

                          <p>
                            {product?.description ||
                              "Product added to your cart."}
                          </p>

                          <p className="cart-price">
                            ₹{item.price}
                          </p>

                          <div className="quantity-controls">
                            <button
                              onClick={() =>
                                handleUpdateQuantity(
                                  item.product_id,
                                  item.quantity -
                                    1
                                )
                              }
                              disabled={
                                item.quantity <=
                                1
                              }
                            >
                              −
                            </button>

                            <span>
                              {
                                item.quantity
                              }
                            </span>

                            <button
                              onClick={() =>
                                handleUpdateQuantity(
                                  item.product_id,
                                  item.quantity +
                                    1
                                )
                              }
                              disabled={
                                item.quantity >=
                                item.stock
                              }
                            >
                              +
                            </button>
                          </div>

                          <button
                            className="remove-button"
                            onClick={() =>
                              handleRemoveFromCart(
                                item.product_id
                              )
                            }
                          >
                            Delete
                          </button>
                        </div>

                        <div className="cart-item-total">
                          ₹
                          {Number(
                            item.item_total
                          ).toFixed(2)}
                        </div>
                      </div>
                    );
                  }
                )}
              </div>

              <div className="cart-summary">
                <h2>
                  Order Summary
                </h2>

                <p>
                  Total Items:{" "}
                  {getCartCount()}
                </p>

                <div className="summary-total">
                  <span>
                    Total
                  </span>

                  <strong>
                    ₹
                    {getCartTotal().toFixed(
                      2
                    )}
                  </strong>
                </div>

                <button
                  className="checkout-button"
                  onClick={
                    handleCheckout
                  }
                  disabled={
                    loading
                  }
                >
                  {loading
                    ? "Processing..."
                    : "Proceed to Checkout"}
                </button>

                <button
                  className="continue-shopping"
                  onClick={() =>
                    setShowCart(false)
                  }
                >
                  Continue Shopping
                </button>
              </div>
            </div>
          )}
        </section>
      ) : (
        <>
          <section className="hero">
            <div>
              <h1>
                Welcome to SmartShop
              </h1>

              <p>
                Discover amazing
                products at great
                prices.
              </p>

              <button
                className="shop-button"
                onClick={() => {
                  document
                    .getElementById(
                      "products"
                    )
                    ?.scrollIntoView({
                      behavior:
                        "smooth",
                    });
                }}
              >
                Shop Now
              </button>
            </div>
          </section>

          <section
            className="products-section"
            id="products"
          >
            <h2>
              Our Products
            </h2>

            <div className="product-grid">
              {products.map(
                (product) => (
                  <div
                    className="product-card"
                    key={
                      product.id
                    }
                  >
                    <img
                      src={
                        product.images
                      }
                      alt={
                        product.name
                      }
                      className="product-image"
                    />

                    <div className="product-details">
                      <h3>
                        {
                          product.name
                        }
                      </h3>

                      <p className="description">
                        {
                          product.description
                        }
                      </p>

                      <p className="price">
                        ₹
                        {
                          product.price
                        }
                      </p>

                      <p className="stock">
                        Stock:{" "}
                        {
                          product.stock
                        }
                      </p>

                      <button
                        className="add-cart"
                        onClick={() =>
                          handleAddToCart(
                            product.id
                          )
                        }
                      >
                        Add to Cart
                      </button>
                    </div>
                  </div>
                )
              )}
            </div>
          </section>
        </>
      )}

      <footer>
        <p>
          © 2026 SmartShop.
          All rights reserved.
        </p>
      </footer>
    </div>
  );
}

export default App;