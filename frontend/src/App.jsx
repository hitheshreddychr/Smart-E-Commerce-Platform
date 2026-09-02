import {
  useEffect,
  useRef,
  useState,
} from "react";

import "./App.css";


const API_URL = "http://127.0.0.1:8000";


function PaymentSuccessPage({ sessionId }) {
  const [paymentStatus, setPaymentStatus] =
    useState("confirming");

  const [paymentError, setPaymentError] =
    useState("");

  const confirmationStarted = useRef(false);


  useEffect(() => {
    if (confirmationStarted.current) {
      return;
    }

    confirmationStarted.current = true;


    const confirmPayment = async () => {
      if (!sessionId) {
        setPaymentStatus("error");

        setPaymentError(
          "Payment session ID was not found."
        );

        return;
      }

      try {
        const response = await fetch(
          `${API_URL}/checkout/confirm/${sessionId}`,
          {
            method: "POST",
          }
        );

        const data =
          await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail ||
              "Unable to confirm payment."
          );
        }

        setPaymentStatus("success");

      } catch (error) {
        console.error(
          "Payment confirmation error:",
          error
        );

        setPaymentStatus("error");

        setPaymentError(
          error.message ||
            "Unable to confirm payment."
        );
      }
    };


    confirmPayment();

  }, [sessionId]);


  if (paymentStatus === "confirming") {
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
          <h1>
            Confirming Payment...
          </h1>

          <p>
            Please wait while your order
            is being processed.
          </p>
        </div>
      </div>
    );
  }


  if (paymentStatus === "error") {
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
            Payment Confirmation Failed
          </h1>

          <p>
            {paymentError}
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
          Your cart has been cleared and
          product stock has been updated.
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



function OrdersPage({
  orders,
  ordersLoading,
  ordersError,
  onRefresh,
  onBackToShop,
  onRequestReturn,
}) {
  return (
    <section
      style={{
        minHeight: "calc(100vh - 90px)",
        background: "#f4f7fb",
        padding: "40px 30px",
      }}
    >
      <div style={{ maxWidth: "1100px", margin: "0 auto" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "15px",
            marginBottom: "30px",
            flexWrap: "wrap",
          }}
        >
          <div>
            <h1 style={{ margin: 0, color: "#111827" }}>
              📦 Your Orders
            </h1>
            <p style={{ color: "#6b7280", marginTop: "8px" }}>
              View your orders and their current status.
            </p>
          </div>

          <div style={{ display: "flex", gap: "10px" }}>
            <button
              onClick={onRefresh}
              style={{
                padding: "11px 18px",
                border: "none",
                borderRadius: "8px",
                background: "#2563eb",
                color: "white",
                cursor: "pointer",
                fontWeight: "600",
              }}
            >
              🔄 Refresh
            </button>

            <button
              onClick={onBackToShop}
              style={{
                padding: "11px 18px",
                border: "1px solid #d1d5db",
                borderRadius: "8px",
                background: "white",
                color: "#374151",
                cursor: "pointer",
                fontWeight: "600",
              }}
            >
              ← Continue Shopping
            </button>
          </div>
        </div>

        {ordersLoading && (
          <div
            style={{
              background: "white",
              padding: "40px",
              borderRadius: "15px",
              textAlign: "center",
              boxShadow: "0 5px 20px rgba(0,0,0,0.08)",
            }}
          >
            <h2>Loading your orders...</h2>
            <p style={{ color: "#6b7280" }}>Please wait.</p>
          </div>
        )}

        {ordersError && !ordersLoading && (
          <div
            style={{
              background: "white",
              padding: "30px",
              borderRadius: "15px",
              textAlign: "center",
              boxShadow: "0 5px 20px rgba(0,0,0,0.08)",
            }}
          >
            <h2 style={{ color: "#dc2626" }}>
              Unable to Load Orders
            </h2>
            <p style={{ color: "#374151" }}>{ordersError}</p>
            <button
              onClick={onRefresh}
              style={{
                marginTop: "15px",
                padding: "12px 25px",
                border: "none",
                borderRadius: "8px",
                background: "#2563eb",
                color: "white",
                cursor: "pointer",
              }}
            >
              Try Again
            </button>
          </div>
        )}

        {!ordersLoading && !ordersError && orders.length === 0 && (
          <div
            style={{
              background: "white",
              padding: "50px",
              borderRadius: "15px",
              textAlign: "center",
              boxShadow: "0 5px 20px rgba(0,0,0,0.08)",
            }}
          >
            <div style={{ fontSize: "55px", marginBottom: "15px" }}>
              📦
            </div>
            <h2>No Orders Yet</h2>
            <p style={{ color: "#6b7280" }}>
              Your completed orders will appear here.
            </p>
            <button
              onClick={onBackToShop}
              style={{
                marginTop: "15px",
                padding: "12px 25px",
                border: "none",
                borderRadius: "8px",
                background: "#2563eb",
                color: "white",
                cursor: "pointer",
              }}
            >
              Start Shopping
            </button>
          </div>
        )}

        {!ordersLoading && !ordersError && orders.length > 0 && (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "20px",
            }}
          >
            {orders.map((order) => (
              <div
                key={order.id}
                style={{
                  background: "white",
                  borderRadius: "15px",
                  padding: "25px",
                  boxShadow: "0 5px 20px rgba(0,0,0,0.08)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    gap: "15px",
                    flexWrap: "wrap",
                    borderBottom: "1px solid #e5e7eb",
                    paddingBottom: "18px",
                    marginBottom: "18px",
                  }}
                >
                  <div>
                    <h2 style={{ margin: 0, color: "#111827" }}>
                      Order #{order.id}
                    </h2>
                    <p style={{ margin: "7px 0 0", color: "#6b7280" }}>
                      Order Total: ₹
                      {Number(order.total_amount || 0).toFixed(2)}
                    </p>
                  </div>

                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "flex-end",
                      gap: "7px",
                    }}
                  >
                    <span
                      style={{
                        display: "inline-block",
                        padding: "7px 14px",
                        borderRadius: "20px",
                        background:
                          order.status === "delivered"
                            ? "#dcfce7"
                            : order.status === "shipped"
                            ? "#dbeafe"
                            : order.status === "return_requested"
                            ? "#fef3c7"
                            : "#f3f4f6",
                        color:
                          order.status === "delivered"
                            ? "#166534"
                            : order.status === "shipped"
                            ? "#1d4ed8"
                            : order.status === "return_requested"
                            ? "#92400e"
                            : "#374151",
                        fontWeight: "700",
                        textTransform: "capitalize",
                      }}
                    >
                      {String(order.status || "unknown").replace(/_/g, " ")}
                    </span>

                    <span style={{ color: "#6b7280", fontSize: "14px" }}>
                      Payment:{" "}
                      {String(order.payment_status || "unknown").replace(
                        /_/g,
                        " "
                      )}
                    </span>

                    {String(order.status || "").toLowerCase() === "delivered" && (
                      <button
                        onClick={() => onRequestReturn(order)}
                        style={{
                          marginTop: "5px",
                          padding: "9px 16px",
                          border: "none",
                          borderRadius: "8px",
                          background: "#dc2626",
                          color: "white",
                          cursor: "pointer",
                          fontWeight: "600",
                        }}
                      >
                        ↩️ Request Return
                      </button>
                    )}
                  </div>
                </div>

                <div>
                  <h3 style={{ marginBottom: "15px", color: "#374151" }}>
                    Order Items
                  </h3>

                  {Array.isArray(order.items) && order.items.length > 0 ? (
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "10px",
                      }}
                    >
                      {order.items.map((item, index) => (
                        <div
                          key={item.id || `${order.id}-${index}`}
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            padding: "12px 15px",
                            background: "#f9fafb",
                            borderRadius: "8px",
                            gap: "15px",
                          }}
                        >
                          <div>
                            <strong>
                              Product #{item.product_id}
                            </strong>
                            <p
                              style={{
                                margin: "4px 0 0",
                                color: "#6b7280",
                                fontSize: "14px",
                              }}
                            >
                              Quantity: {item.quantity}
                            </p>
                          </div>

                          <strong>
                            ₹{Number(item.price || 0).toFixed(2)}
                          </strong>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p style={{ color: "#6b7280" }}>
                      No item details available.
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}


function App() {
  const [products, setProducts] =
    useState([]);

  const [cart, setCart] =
    useState([]);

  const [orders, setOrders] =
    useState([]);

  const [ordersLoading, setOrdersLoading] =
    useState(false);

  const [ordersError, setOrdersError] =
    useState("");

  const [showReturnForm, setShowReturnForm] =
    useState(false);

  const [selectedReturnOrder, setSelectedReturnOrder] =
    useState(null);

  const [returnReason, setReturnReason] =
    useState("");

  const [returnComment, setReturnComment] =
    useState("");

  const [returnLoading, setReturnLoading] =
    useState(false);

  const [showLogin, setShowLogin] =
    useState(false);

  const [showCart, setShowCart] =
    useState(false);

  const [showOrders, setShowOrders] =
    useState(false);

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [loggedIn, setLoggedIn] =
    useState(false);

  const [user, setUser] =
    useState(null);

  const [loginError, setLoginError] =
    useState("");

  const [loading, setLoading] =
    useState(false);


  const pathname =
    window.location.pathname;

  const searchParams =
    new URLSearchParams(
      window.location.search
    );

  const sessionId =
    searchParams.get("session_id");


  const normalizeCart = (data) => {
    if (Array.isArray(data)) {
      return data;
    }

    if (Array.isArray(data?.items)) {
      return data.items;
    }

    if (Array.isArray(data?.cart)) {
      return data.cart;
    }

    if (Array.isArray(data?.data)) {
      return data.data;
    }

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

      const data =
        await response.json();

      setProducts(
        Array.isArray(data)
          ? data
          : []
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
    const token =
      localStorage.getItem(
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
            Authorization:
              `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(
          "Unable to fetch cart"
        );
      }

      const data =
        await response.json();

      setCart(
        normalizeCart(data)
      );

    } catch (error) {
      console.error(
        "Error fetching cart:",
        error
      );

      setCart([]);
    }
  };



  const fetchOrders = async () => {
    const token =
      localStorage.getItem("access_token");

    if (!token) {
      setOrders([]);
      return;
    }

    setOrdersLoading(true);
    setOrdersError("");

    try {
      const response = await fetch(
        `${API_URL}/orders/`,
        {
          headers: {
            Authorization:
              `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Unable to fetch orders."
        );
      }

      setOrders(
        Array.isArray(data)
          ? data
          : []
      );
    } catch (error) {
      console.error(
        "Fetch orders error:",
        error
      );

      setOrders([]);
      setOrdersError(
        error.message ||
          "Unable to fetch orders."
      );
    } finally {
      setOrdersLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);


  useEffect(() => {
    const token =
      localStorage.getItem(
        "access_token"
      );

    if (!token) {
      return;
    }

    fetch(`${API_URL}/auth/me`, {
      headers: {
        Authorization:
          `Bearer ${token}`,
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
        fetchOrders();
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


  const handleLogin = async (
    event
  ) => {
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

      const data =
        await response.json();

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

      const userResponse =
        await fetch(
          `${API_URL}/auth/me`,
          {
            headers: {
              Authorization:
                `Bearer ${data.access_token}`,
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
      await fetchOrders();

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


  const handleRequestReturn = (order) => {
    if (
      !order ||
      String(order.status || "").toLowerCase() !== "delivered"
    ) {
      alert("Return can only be requested for delivered orders.");
      return;
    }

    setSelectedReturnOrder(order);
    setReturnReason("");
    setReturnComment("");
    setShowReturnForm(true);
  };

  const handleSubmitReturnRequest = async (event) => {
    event.preventDefault();

    if (!selectedReturnOrder) {
      return;
    }

    if (!returnReason.trim()) {
      alert("Please enter a return reason.");
      return;
    }

    const token =
      localStorage.getItem("access_token");

    if (!token) {
      alert("Please login before requesting a return.");
      setShowReturnForm(false);
      setShowLogin(true);
      return;
    }

    setReturnLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/orders/${selectedReturnOrder.id}/return`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            reason: returnReason.trim(),
            comment: returnComment.trim() || null,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Unable to submit return request."
        );
      }

      alert(
        `Return request submitted successfully for Order #${selectedReturnOrder.id}.`
      );

      setShowReturnForm(false);
      setSelectedReturnOrder(null);
      setReturnReason("");
      setReturnComment("");

      await fetchOrders();
    } catch (error) {
      console.error(
        "Return request error:",
        error
      );

      alert(
        error.message ||
          "Unable to submit return request."
      );
    } finally {
      setReturnLoading(false);
    }
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
    setOrders([]);

    setShowCart(false);
    setShowOrders(false);
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

    const product =
      products.find(
        (item) =>
          item.id === productId
      );

    if (
      !product ||
      Number(product.stock) <= 0
    ) {
      alert(
        "This product is currently out of stock."
      );

      return;
    }

    const token =
      localStorage.getItem(
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

            Authorization:
              `Bearer ${token}`,
          },

          body: JSON.stringify({
            product_id: productId,
            quantity: 1,
          }),
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        alert(
          data.detail ||
            "Unable to add product to cart."
        );

        return;
      }

      setCart(
        normalizeCart(data)
      );

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


  const handleUpdateQuantity =
    async (
      productId,
      newQuantity
    ) => {
      if (newQuantity <= 0) {
        return;
      }

      const token =
        localStorage.getItem(
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

              Authorization:
                `Bearer ${token}`,
            },

            body: JSON.stringify({
              product_id: productId,
              quantity: newQuantity,
            }),
          }
        );

        const data =
          await response.json();

        if (!response.ok) {
          alert(
            data.detail ||
              "Unable to update quantity."
          );

          return;
        }

        setCart(
          normalizeCart(data)
        );

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


  const handleRemoveFromCart =
    async (productId) => {
      const token =
        localStorage.getItem(
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

              Authorization:
                `Bearer ${token}`,
            },

            body: JSON.stringify({
              product_id: productId,
            }),
          }
        );

        const data =
          await response.json();

        if (!response.ok) {
          alert(
            data.detail ||
              "Unable to remove product."
          );

          return;
        }

        setCart(
          normalizeCart(data)
        );

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

    const token =
      localStorage.getItem(
        "access_token"
      );

    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/checkout`,
        {
          method: "POST",

          headers: {
            Authorization:
              `Bearer ${token}`,

            "Content-Type":
              "application/json",
          },
        }
      );

      const data =
        await response.json();

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
      await fetchOrders();

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


  const getProduct = (
    productId
  ) => {
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


  if (
    pathname ===
    "/payment-success"
  ) {
    return (
      <PaymentSuccessPage
        sessionId={sessionId}
      />
    );
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
            setShowOrders(false);

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
            onClick={() => {
              setShowCart(false);
              setShowOrders(false);
            }}
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


          {loggedIn && (
            <button
              className="nav-button"
              onClick={() => {
                setShowCart(false);
                setShowOrders(true);
                fetchOrders();
              }}
            >
              📦 Orders
            </button>
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

              setShowOrders(false);
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


      {showReturnForm && selectedReturnOrder && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.55)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "20px",
            zIndex: 1000,
          }}
        >
          <div
            style={{
              background: "white",
              width: "100%",
              maxWidth: "520px",
              borderRadius: "16px",
              padding: "30px",
              boxShadow: "0 15px 50px rgba(0,0,0,0.2)",
            }}
          >
            <h2 style={{ marginTop: 0 }}>
              ↩️ Request Return
            </h2>

            <p style={{ color: "#6b7280" }}>
              Order #{selectedReturnOrder.id}
            </p>

            <form onSubmit={handleSubmitReturnRequest}>
              <label
                style={{
                  display: "block",
                  marginBottom: "8px",
                  fontWeight: "600",
                  color: "#374151",
                }}
              >
                Return Reason *
              </label>

              <textarea
                value={returnReason}
                onChange={(event) =>
                  setReturnReason(event.target.value)
                }
                placeholder="Enter the reason for returning this order"
                rows="4"
                required
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  padding: "12px",
                  border: "1px solid #d1d5db",
                  borderRadius: "8px",
                  marginBottom: "18px",
                  fontSize: "15px",
                  resize: "vertical",
                }}
              />

              <label
                style={{
                  display: "block",
                  marginBottom: "8px",
                  fontWeight: "600",
                  color: "#374151",
                }}
              >
                Comment (Optional)
              </label>

              <textarea
                value={returnComment}
                onChange={(event) =>
                  setReturnComment(event.target.value)
                }
                placeholder="Add any additional details"
                rows="4"
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  padding: "12px",
                  border: "1px solid #d1d5db",
                  borderRadius: "8px",
                  marginBottom: "20px",
                  fontSize: "15px",
                  resize: "vertical",
                }}
              />

              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "10px",
                }}
              >
                <button
                  type="button"
                  onClick={() => {
                    if (!returnLoading) {
                      setShowReturnForm(false);
                      setSelectedReturnOrder(null);
                      setReturnReason("");
                      setReturnComment("");
                    }
                  }}
                  disabled={returnLoading}
                  style={{
                    padding: "11px 18px",
                    border: "1px solid #d1d5db",
                    borderRadius: "8px",
                    background: "white",
                    color: "#374151",
                    cursor: returnLoading
                      ? "not-allowed"
                      : "pointer",
                    fontWeight: "600",
                  }}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={
                    returnLoading ||
                    !returnReason.trim()
                  }
                  style={{
                    padding: "11px 18px",
                    border: "none",
                    borderRadius: "8px",
                    background: "#dc2626",
                    color: "white",
                    cursor:
                      returnLoading ||
                      !returnReason.trim()
                        ? "not-allowed"
                        : "pointer",
                    opacity:
                      returnLoading ||
                      !returnReason.trim()
                        ? 0.6
                        : 1,
                    fontWeight: "600",
                  }}
                >
                  {returnLoading
                    ? "Submitting..."
                    : "Submit Return Request"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showOrders ? (

        <OrdersPage
          orders={orders}
          ordersLoading={ordersLoading}
          ordersError={ordersError}
          onRefresh={fetchOrders}
          onRequestReturn={handleRequestReturn}
          onBackToShop={() => {
            setShowOrders(false);
          }}
        />

      ) : showCart ? (

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
                        key={item.id}
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
                              {item.quantity}
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
                                (
                                  product?.stock ||
                                  item.stock ||
                                  0
                                )
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
                    key={product.id}
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
                        {product.name}
                      </h3>


                      <p className="description">
                        {
                          product.description
                        }
                      </p>


                      <p className="price">
                        ₹{product.price}
                      </p>


                      {Number(
                        product.stock
                      ) <= 0 ? (

                        <p
                          className="stock"
                          style={{
                            color: "#dc2626",
                            fontWeight: "700",
                          }}
                        >
                          Out of Stock
                        </p>

                      ) : (

                        <p className="stock">
                          Stock:{" "}
                          {product.stock}
                        </p>

                      )}


                      <button
                        className="add-cart"
                        onClick={() =>
                          handleAddToCart(
                            product.id
                          )
                        }
                        disabled={
                          Number(
                            product.stock
                          ) <= 0
                        }
                        style={{
                          opacity:
                            Number(
                              product.stock
                            ) <= 0
                              ? 0.6
                              : 1,

                          cursor:
                            Number(
                              product.stock
                            ) <= 0
                              ? "not-allowed"
                              : "pointer",
                        }}
                      >
                        {Number(
                          product.stock
                        ) <= 0
                          ? "Out of Stock"
                          : "Add to Cart"}
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