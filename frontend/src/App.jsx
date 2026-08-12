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

  // -----------------------------------------
  // Get Products
  // -----------------------------------------

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${API_URL}/products/`);

      if (!response.ok) {
        throw new Error("Unable to fetch products");
      }

      const data = await response.json();

      setProducts(data);
    } catch (error) {
      console.error("Error fetching products:", error);
    }
  };

  // -----------------------------------------
  // Get Cart
  // -----------------------------------------

  const fetchCart = async () => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setCart([]);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/cart/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Unable to fetch cart");
      }

      const data = await response.json();

      setCart(data);
    } catch (error) {
      console.error("Error fetching cart:", error);
    }
  };

  // -----------------------------------------
  // Initial Products
  // -----------------------------------------

  useEffect(() => {
    fetchProducts();
  }, []);

  // -----------------------------------------
  // Check Existing Login
  // -----------------------------------------

  useEffect(() => {
    const token = localStorage.getItem("access_token");

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
          throw new Error("Token expired");
        }

        return response.json();
      })
      .then((data) => {
        setUser(data);
        setLoggedIn(true);

        fetchCart();
      })
      .catch(() => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");

        setUser(null);
        setLoggedIn(false);
        setCart([]);
      });
  }, []);

  // -----------------------------------------
  // Login
  // -----------------------------------------

  const handleLogin = async (event) => {
    event.preventDefault();

    setLoginError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          name: "SmartShop User",
          email: email,
          password: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setLoginError(data.detail || "Login failed");
        setLoading(false);
        return;
      }

      // Save tokens
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      // Get current user
      const userResponse = await fetch(`${API_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${data.access_token}`,
        },
      });

      const userData = await userResponse.json();

      setUser(userData);
      setLoggedIn(true);
      setShowLogin(false);

      setEmail("");
      setPassword("");

      // Get cart after login
      await fetchCart();
    } catch (error) {
      console.error("Login error:", error);

      setLoginError("Unable to connect to the server");
    }

    setLoading(false);
  };

  // -----------------------------------------
  // Logout
  // -----------------------------------------

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    setUser(null);
    setLoggedIn(false);
    setCart([]);

    setShowCart(false);
  };

  // -----------------------------------------
  // Add Product To Cart
  // -----------------------------------------

  const handleAddToCart = async (productId) => {
    if (!loggedIn) {
      alert("Please login before adding products to cart.");
      setShowLogin(true);
      return;
    }

    const token = localStorage.getItem("access_token");

    try {
      const response = await fetch(`${API_URL}/cart/`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },

        body: JSON.stringify({
          product_id: productId,
          quantity: 1,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.detail || "Unable to add product to cart.");
        return;
      }

      await fetchCart();

      alert("Product added to cart successfully! 🛒");
    } catch (error) {
      console.error("Add to cart error:", error);

      alert("Unable to connect to the server.");
    }
  };

  // -----------------------------------------
  // Checkout
  // -----------------------------------------

  const handleCheckout = async () => {
    if (!loggedIn) {
      alert("Please login before checkout.");
      setShowLogin(true);
      return;
    }

    if (cart.length === 0) {
      alert("Your cart is empty.");
      return;
    }

    const token = localStorage.getItem("access_token");

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/orders/checkout`, {
        method: "POST",

        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (!response.ok) {
        console.error("Checkout failed:", data);

        alert(data.detail || "Checkout failed.");
        setLoading(false);
        return;
      }

      console.log("Checkout successful:", data);

      // Refresh cart from backend
      await fetchCart();

      alert(
        `Order placed successfully! 🎉\n\n${
          data.order_id
            ? `Order ID: ${data.order_id}`
            : "Thank you for shopping with SmartShop!"
        }`
      );

      setShowCart(false);
    } catch (error) {
      console.error("Checkout error:", error);

      alert("Unable to connect to the checkout server.");
    }

    setLoading(false);
  };

  // -----------------------------------------
  // Calculate Cart
  // -----------------------------------------

  const getProduct = (productId) => {
    return products.find((product) => product.id === productId);
  };

  const getCartTotal = () => {
    return cart.reduce((total, item) => {
      const product = getProduct(item.product_id);

      if (!product) {
        return total;
      }

      return total + Number(product.price) * item.quantity;
    }, 0);
  };

  // -----------------------------------------
  // Cart Count
  // -----------------------------------------

  const getCartCount = () => {
    return cart.reduce((total, item) => {
      return total + item.quantity;
    }, 0);
  };

  // -----------------------------------------
  // Return UI
  // -----------------------------------------

  return (
    <div className="app">

      {/* ----------------------------------------- */}
      {/* Navbar */}
      {/* ----------------------------------------- */}

      <nav className="navbar">

        <div
          className="logo"
          onClick={() => {
            setShowCart(false);
            window.scrollTo(0, 0);
          }}
          style={{ cursor: "pointer" }}
        >
          SmartShop
        </div>

        <div className="nav-links">

          <a
            href="#"
            onClick={() => setShowCart(false)}
          >
            Home
          </a>

          <a
            href="#products"
            onClick={() => setShowCart(false)}
          >
            Products
          </a>

          {!loggedIn ? (

            <button
              className="nav-button"
              onClick={() => setShowLogin(true)}
            >
              Login
            </button>

          ) : (

            <>
              <span className="welcome-user">
                Hi, {user?.email}
              </span>

              <button
                className="nav-button"
                onClick={handleLogout}
              >
                Logout
              </button>
            </>

          )}

          <a href="#">
            Register
          </a>

          <button
            className="cart-button"
            onClick={() => {
              if (!loggedIn) {
                alert("Please login to view your cart.");
                setShowLogin(true);
                return;
              }

              setShowCart(true);

              fetchCart();
            }}
          >
            🛒 Cart ({getCartCount()})
          </button>

        </div>

      </nav>


      {/* ----------------------------------------- */}
      {/* Login */}
      {/* ----------------------------------------- */}

      {showLogin && !loggedIn && (

        <section className="login-section">

          <div className="login-card">

            <h2>
              Login to SmartShop
            </h2>

            <form onSubmit={handleLogin}>

              <label>
                Email
              </label>

              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
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
                onChange={(event) =>
                  setPassword(event.target.value)
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
                disabled={loading}
              >
                {loading ? "Logging in..." : "Login"}
              </button>

            </form>

            <button
              className="cancel-login"
              onClick={() => {
                setShowLogin(false);
                setLoginError("");
              }}
            >
              Cancel
            </button>

          </div>

        </section>

      )}


      {/* ----------------------------------------- */}
      {/* Cart Page */}
      {/* ----------------------------------------- */}

      {showCart ? (

        <section className="cart-page">

          <h1>
            🛒 Your Cart
          </h1>

          {cart.length === 0 ? (

            <div className="empty-cart">

              <h2>
                Your cart is empty
              </h2>

              <p>
                Add some products to your cart.
              </p>

              <button
                className="shop-button"
                onClick={() => setShowCart(false)}
              >
                Continue Shopping
              </button>

            </div>

          ) : (

            <>

              {/* Cart Items */}

              <div className="cart-items">

                {cart.map((item) => {

                  const product = getProduct(item.product_id);

                  if (!product) {
                    return null;
                  }

                  const itemTotal =
                    Number(product.price) * item.quantity;

                  return (

                    <div
                      className="cart-item"
                      key={item.id}
                    >

                      <img
                        src={product.images}
                        alt={product.name}
                        className="cart-image"
                      />

                      <div className="cart-details">

                        <h2>
                          {product.name}
                        </h2>

                        <p>
                          {product.description}
                        </p>

                        <p>
                          Price: ₹{product.price}
                        </p>

                        <p>
                          Quantity: {item.quantity}
                        </p>

                        <h3>
                          Item Total: ₹{itemTotal}
                        </h3>

                      </div>

                    </div>

                  );

                })}

              </div>


              {/* Cart Summary */}

              <div className="cart-summary">

                <h2>
                  Cart Summary
                </h2>

                <p>
                  Total Items: {getCartCount()}
                </p>

                <h2>
                  Total: ₹{getCartTotal()}
                </h2>

                <button
                  className="checkout-button"
                  onClick={handleCheckout}
                  disabled={loading}
                >
                  {loading
                    ? "Processing..."
                    : "Proceed to Checkout"}
                </button>

              </div>

            </>

          )}

        </section>

      ) : (

        /* ----------------------------------------- */
        /* Home Page */
        /* ----------------------------------------- */

        <>

          {/* Hero */}

          <section className="hero">

            <div>

              <h1>
                Welcome to SmartShop
              </h1>

              <p>
                Discover amazing products at great prices.
              </p>

              <button
                className="shop-button"
                onClick={() => {
                  document
                    .getElementById("products")
                    ?.scrollIntoView({
                      behavior: "smooth",
                    });
                }}
              >
                Shop Now
              </button>

            </div>

          </section>


          {/* Products */}

          <section
            className="products-section"
            id="products"
          >

            <h2>
              Our Products
            </h2>

            <div className="product-grid">

              {products.map((product) => (

                <div
                  className="product-card"
                  key={product.id}
                >

                  <img
                    src={product.images}
                    alt={product.name}
                    className="product-image"
                  />

                  <div className="product-details">

                    <h3>
                      {product.name}
                    </h3>

                    <p className="description">
                      {product.description}
                    </p>

                    <p className="price">
                      ₹{product.price}
                    </p>

                    <p className="stock">
                      Stock: {product.stock}
                    </p>

                    <button
                      className="add-cart"
                      onClick={() =>
                        handleAddToCart(product.id)
                      }
                    >
                      Add to Cart
                    </button>

                  </div>

                </div>

              ))}

            </div>

          </section>

        </>

      )}


      {/* ----------------------------------------- */}
      {/* Footer */}
      {/* ----------------------------------------- */}

      <footer>

        <p>
          © 2026 SmartShop. All rights reserved.
        </p>

      </footer>

    </div>
  );
}

export default App;