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


function ReviewSection({
  product,
  reviewData,
  loggedIn,
  onLogin,
  reviewForm,
  onRatingChange,
  onCommentChange,
  onSubmit,
  submitting,
}) {
  const [showTopReviews, setShowTopReviews] = useState(false);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewSort, setReviewSort] = useState("highest");

  const averageRating = Number(reviewData?.average_rating || 0);
  const totalReviews = Number(reviewData?.total_reviews || 0);
  const reviews = Array.isArray(reviewData?.reviews)
    ? reviewData.reviews
    : [];

  const sortedReviews = [...reviews].sort((a, b) => {
    if (reviewSort === "highest") {
      if (Number(b.rating) !== Number(a.rating)) {
        return Number(b.rating) - Number(a.rating);
      }
      return String(b.created_at || "").localeCompare(
        String(a.created_at || "")
      );
    }

    if (reviewSort === "lowest") {
      if (Number(a.rating) !== Number(b.rating)) {
        return Number(a.rating) - Number(b.rating);
      }
      return String(b.created_at || "").localeCompare(
        String(a.created_at || "")
      );
    }

    if (reviewSort === "newest") {
      return String(b.created_at || "").localeCompare(
        String(a.created_at || "")
      );
    }

    return String(a.created_at || "").localeCompare(
      String(b.created_at || "")
    );
  });

  const renderStars = (rating) => {
    const numericRating = Math.max(
      0,
      Math.min(5, Math.round(Number(rating) || 0))
    );

    return (
      <span
        aria-label={`${numericRating} out of 5 stars`}
        style={{ letterSpacing: "2px" }}
      >
        {Array.from({ length: 5 }, (_, index) =>
          index < numericRating ? "★" : "☆"
        ).join("")}
      </span>
    );
  };

  return (
    <div
      style={{
        marginTop: "20px",
        paddingTop: "18px",
        borderTop: "1px solid #e5e7eb",
      }}
    >
      {/* Always-visible full rating summary */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "10px",
          flexWrap: "wrap",
          marginBottom: "15px",
        }}
      >
        <div>
          <strong style={{ color: "#111827" }}>
            ⭐ {averageRating.toFixed(1)} / 5
          </strong>
          <span style={{ color: "#6b7280", marginLeft: "8px" }}>
            ({totalReviews} {totalReviews === 1 ? "review" : "reviews"})
          </span>
        </div>
        <div style={{ color: "#f59e0b", fontSize: "18px" }}>
          {renderStars(averageRating)}
        </div>
      </div>

      {/* One expandable Top Reviews section */}
      {reviews.length > 0 && (
        <div style={{ marginBottom: "12px" }}>
          <button
            type="button"
            onClick={() => setShowTopReviews((current) => !current)}
            style={{
              width: "100%",
              textAlign: "left",
              padding: "10px 12px",
              border: "1px solid #e5e7eb",
              borderRadius: showTopReviews ? "8px 8px 0 0" : "8px",
              background: "#f8fafc",
              color: "#111827",
              cursor: "pointer",
              fontWeight: "700",
              fontSize: "13px",
            }}
          >
            {showTopReviews ? "▼" : "▶"} Top Reviews ({reviews.length})
          </button>

          {showTopReviews && (
            <div
              style={{
                background: "#ffffff",
                border: "1px solid #e5e7eb",
                borderTop: "none",
                borderRadius: "0 0 8px 8px",
                padding: "12px",
              }}
            >
              {/* Review sorting */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "8px",
                  marginBottom: "12px",
                  flexWrap: "wrap",
                }}
              >
                <label
                  htmlFor={`review-sort-${product.id}`}
                  style={{
                    color: "#374151",
                    fontWeight: "600",
                    fontSize: "12px",
                  }}
                >
                  Sort Reviews
                </label>
                <select
                  id={`review-sort-${product.id}`}
                  value={reviewSort}
                  onChange={(event) => setReviewSort(event.target.value)}
                  style={{
                    padding: "7px 8px",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    background: "white",
                    color: "#374151",
                    fontSize: "12px",
                  }}
                >
                  <option value="highest">Highest Rating → Lowest</option>
                  <option value="lowest">Lowest Rating → Highest</option>
                  <option value="newest">Newest First</option>
                  <option value="oldest">Oldest First</option>
                </select>
              </div>

              {/* All reviews */}
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "10px",
                }}
              >
                {sortedReviews.map((review, index) => (
                  <div
                    key={review.id}
                    style={{
                      padding: "10px",
                      border: "1px solid #e5e7eb",
                      borderRadius: "7px",
                      background: "#f9fafb",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        gap: "8px",
                        flexWrap: "wrap",
                      }}
                    >
                      <div>
                        <span style={{ color: "#f59e0b", fontSize: "14px" }}>
                          {renderStars(review.rating)}
                        </span>
                        <strong
                          style={{
                            color: "#374151",
                            fontSize: "12px",
                            marginLeft: "7px",
                          }}
                        >
                          Review #{index + 1}
                        </strong>
                      </div>
                      <span style={{ color: "#6b7280", fontSize: "11px" }}>
                        User #{review.user_id}
                      </span>
                    </div>
                    <p
                      style={{
                        margin: "7px 0 0",
                        color: "#374151",
                        lineHeight: "1.5",
                        fontSize: "12px",
                      }}
                    >
                      {review.comment}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {reviews.length === 0 && (
        <p style={{ color: "#6b7280", fontSize: "13px", margin: "0 0 12px" }}>
          No reviews yet.
        </p>
      )}

      {/* Write a Review stays below Top Reviews */}
      <div style={{ marginBottom: "0" }}>
        <button
          type="button"
          onClick={() => setShowReviewForm((current) => !current)}
          style={{
            width: "100%",
            textAlign: "left",
            padding: "10px 12px",
            border: "1px solid #e5e7eb",
            borderRadius: showReviewForm ? "8px 8px 0 0" : "8px",
            background: "#f8fafc",
            color: "#111827",
            cursor: "pointer",
            fontWeight: "700",
            fontSize: "13px",
          }}
        >
          {showReviewForm ? "▼" : "▶"} Write a Review
        </button>

        {showReviewForm && (
          <div
            style={{
              background: "#f8fafc",
              border: "1px solid #e5e7eb",
              borderTop: "none",
              borderRadius: "0 0 8px 8px",
              padding: "12px",
            }}
          >
            {!loggedIn ? (
              <div>
                <p
                  style={{
                    color: "#6b7280",
                    fontSize: "13px",
                    margin: "0 0 10px",
                  }}
                >
                  Login to review {product.name}.
                </p>
                <button
                  type="button"
                  onClick={onLogin}
                  style={{
                    padding: "9px 14px",
                    border: "none",
                    borderRadius: "7px",
                    background: "#2563eb",
                    color: "white",
                    cursor: "pointer",
                    fontWeight: "600",
                  }}
                >
                  Login to Review
                </button>
              </div>
            ) : (
              <form onSubmit={(event) => onSubmit(event, product.id)}>
                <label
                  style={{
                    display: "block",
                    marginBottom: "6px",
                    color: "#374151",
                    fontWeight: "600",
                    fontSize: "13px",
                  }}
                >
                  Rating
                </label>

                <select
                  value={reviewForm.rating}
                  onChange={(event) => onRatingChange(event.target.value)}
                  style={{
                    width: "100%",
                    boxSizing: "border-box",
                    padding: "9px",
                    border: "1px solid #d1d5db",
                    borderRadius: "7px",
                    marginBottom: "10px",
                    background: "white",
                  }}
                >
                  <option value="5">★★★★★ - 5</option>
                  <option value="4">★★★★☆ - 4</option>
                  <option value="3">★★★☆☆ - 3</option>
                  <option value="2">★★☆☆☆ - 2</option>
                  <option value="1">★☆☆☆☆ - 1</option>
                </select>

                <label
                  style={{
                    display: "block",
                    marginBottom: "6px",
                    color: "#374151",
                    fontWeight: "600",
                    fontSize: "13px",
                  }}
                >
                  Comment
                </label>

                <textarea
                  value={reviewForm.comment}
                  onChange={(event) => onCommentChange(event.target.value)}
                  placeholder="Share your experience with this product"
                  rows="3"
                  maxLength="1000"
                  required
                  style={{
                    width: "100%",
                    boxSizing: "border-box",
                    padding: "10px",
                    border: "1px solid #d1d5db",
                    borderRadius: "7px",
                    marginBottom: "10px",
                    fontSize: "14px",
                    resize: "vertical",
                  }}
                />

                <button
                  type="submit"
                  disabled={submitting}
                  style={{
                    padding: "9px 14px",
                    border: "none",
                    borderRadius: "7px",
                    background: submitting ? "#9ca3af" : "#16a34a",
                    color: "white",
                    cursor: submitting ? "not-allowed" : "pointer",
                    fontWeight: "600",
                  }}
                >
                  {submitting ? "Submitting..." : "Submit Review"}
                </button>

                <p
                  style={{
                    color: "#6b7280",
                    fontSize: "12px",
                    margin: "9px 0 0",
                  }}
                >
                  Your review will appear immediately after it is submitted.
                </p>
              </form>
            )}
          </div>
        )}
      </div>
    </div>
  );
}



function RecommendationProductCard({ product, onAddToCart, onViewSimilar }) {
  return (
    <div
      style={{
        background: "white",
        borderRadius: "14px",
        padding: "15px",
        minWidth: "220px",
        maxWidth: "240px",
        flex: "0 0 220px",
        boxShadow: "0 5px 18px rgba(0,0,0,0.08)",
        border: "1px solid #e5e7eb",
      }}
    >
      <img
        src={product.images || "https://via.placeholder.com/220"}
        alt={product.name}
        style={{
          width: "100%",
          height: "170px",
          objectFit: "cover",
          borderRadius: "10px",
          background: "#f3f4f6",
        }}
      />

      <h3
        style={{
          margin: "12px 0 7px",
          color: "#111827",
          fontSize: "17px",
        }}
      >
        {product.name}
      </h3>

      <p
        style={{
          margin: "0 0 8px",
          color: "#2563eb",
          fontWeight: "700",
          fontSize: "16px",
        }}
      >
        ₹{product.price}
      </p>

      <p
        style={{
          margin: "0 0 12px",
          color: "#6b7280",
          fontSize: "13px",
        }}
      >
        {product.category || "General"}
      </p>

      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
        <button
          type="button"
          onClick={() => onViewSimilar(product.id)}
          style={{
            flex: 1,
            minWidth: "100px",
            padding: "9px 10px",
            border: "1px solid #2563eb",
            borderRadius: "7px",
            background: "white",
            color: "#2563eb",
            cursor: "pointer",
            fontWeight: "600",
            fontSize: "12px",
          }}
        >
          Similar
        </button>

        <button
          type="button"
          onClick={() => onAddToCart(product.id)}
          disabled={Number(product.stock) <= 0}
          style={{
            flex: 1,
            minWidth: "100px",
            padding: "9px 10px",
            border: "none",
            borderRadius: "7px",
            background: Number(product.stock) <= 0 ? "#9ca3af" : "#16a34a",
            color: "white",
            cursor: Number(product.stock) <= 0 ? "not-allowed" : "pointer",
            fontWeight: "600",
            fontSize: "12px",
          }}
        >
          {Number(product.stock) <= 0 ? "Out of Stock" : "Add to Cart"}
        </button>
      </div>
    </div>
  );
}


function RecommendationSection({
  title,
  products,
  loading,
  emptyMessage,
  onAddToCart,
  onViewSimilar,
}) {
  return (
    <section
      style={{
        maxWidth: "1200px",
        margin: "0 auto 35px",
        padding: "0 30px",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "15px",
          gap: "10px",
          flexWrap: "wrap",
        }}
      >
        <h2 style={{ margin: 0, color: "#111827" }}>{title}</h2>
        <span style={{ color: "#6b7280", fontSize: "13px" }}>
          Smart recommendations
        </span>
      </div>

      {loading ? (
        <div
          style={{
            background: "white",
            borderRadius: "12px",
            padding: "25px",
            textAlign: "center",
            color: "#6b7280",
          }}
        >
          Loading recommendations...
        </div>
      ) : products.length === 0 ? (
        <div
          style={{
            background: "white",
            borderRadius: "12px",
            padding: "25px",
            textAlign: "center",
            color: "#6b7280",
            border: "1px solid #e5e7eb",
          }}
        >
          {emptyMessage}
        </div>
      ) : (
        <div
          style={{
            display: "flex",
            gap: "16px",
            overflowX: "auto",
            padding: "5px 2px 15px",
          }}
        >
          {products.map((product) => (
            <RecommendationProductCard
              key={product.id}
              product={product}
              onAddToCart={onAddToCart}
              onViewSimilar={onViewSimilar}
            />
          ))}
        </div>
      )}
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

  const [notifications, setNotifications] =
    useState([]);

  const [showNotifications, setShowNotifications] =
    useState(false);

  const [loginError, setLoginError] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [reviewsByProduct, setReviewsByProduct] =
    useState({});

  const [reviewForms, setReviewForms] =
    useState({});

  const [reviewSubmittingProduct, setReviewSubmittingProduct] =
    useState(null);


  const [recommendedProducts, setRecommendedProducts] =
    useState([]);

  const [trendingProducts, setTrendingProducts] =
    useState([]);

  const [similarProducts, setSimilarProducts] =
    useState([]);

  const [similarProductId, setSimilarProductId] =
    useState(null);

  const [recommendationsLoading, setRecommendationsLoading] =
    useState(false);

  const [trendingLoading, setTrendingLoading] =
    useState(false);

  const [similarLoading, setSimilarLoading] =
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
  
  
  const normalizeProductList = (data) => {
    if (Array.isArray(data)) {
      return data;
    }

    if (Array.isArray(data?.products)) {
      return data.products;
    }

    if (Array.isArray(data?.recommendations)) {
      return data.recommendations;
    }

    if (Array.isArray(data?.data)) {
      return data.data;
    }

    return [];
  };


  const fetchRecommendations = async (userId) => {
    if (!userId) {
      setRecommendedProducts([]);
      return;
    }

    setRecommendationsLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/recommendations/${userId}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to fetch recommendations."
        );
      }

      setRecommendedProducts(normalizeProductList(data));
    } catch (error) {
      console.error("Recommendation fetch error:", error);
      setRecommendedProducts([]);
    } finally {
      setRecommendationsLoading(false);
    }
  };


  const fetchTrendingProducts = async () => {
    setTrendingLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/products/trending`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to fetch trending products."
        );
      }

      setTrendingProducts(normalizeProductList(data));
    } catch (error) {
      console.error("Trending products fetch error:", error);
      setTrendingProducts([]);
    } finally {
      setTrendingLoading(false);
    }
  };


  const fetchSimilarProducts = async (productId) => {
    if (!productId) {
      return;
    }

    setSimilarProductId(productId);
    setSimilarLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/products/${productId}/similar`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to fetch similar products."
        );
      }

      setSimilarProducts(normalizeProductList(data));
    } catch (error) {
      console.error("Similar products fetch error:", error);
      setSimilarProducts([]);
    } finally {
      setSimilarLoading(false);
    }
  };


  const recordProductView = async (productId) => {
    if (!loggedIn || !user?.id || !productId) {
      return;
    }

    try {
      await fetch(
        `${API_URL}/products/${productId}/view?user_id=${encodeURIComponent(
          user.id
        )}`,
        {
          method: "POST",
        }
      );
    } catch (error) {
      console.error("Product view tracking error:", error);
    }
  };


  const fetchNotifications = async () => {
    const token =
  localStorage.getItem("access_token");
  
  if (!token) {
    setNotifications([]);
    return;
  }
  
  try {
    const response = await fetch(
      `${API_URL}/notifications`,
      {
        headers: {
          Authorization:
          `Bearer ${token}`,
        },
      }
    );
    if (!response.ok) {
      throw new Error(
        "Unable to fetch notifications"
      );
    }
    
    const data =
    await response.json();
    
    setNotifications(
      Array.isArray(data)
      ? data
      : []
    );
  } catch (error) {
    console.error(
      "Error fetching notifications:",
      error
    );
    
    setNotifications([]);
  }
};


  const markNotificationAsRead = async (
    notificationId
  ) => {
    const token =
      localStorage.getItem("access_token");

    if (!token) {
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/notifications/read`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
            Authorization:
              `Bearer ${token}`,
          },
          body: JSON.stringify({
            notification_ids: [
              notificationId,
            ],
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Unable to mark notification as read"
        );
      }

      setNotifications(
        (currentNotifications) =>
          currentNotifications.map(
            (notification) =>
              notification.id ===
              notificationId
                ? {
                    ...notification,
                    read_status: true,
                  }
                : notification
          )
      );
    } catch (error) {
      console.error(
        "Error marking notification as read:",
        error
      );
    }
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

  const fetchProductReviews = async (productId) => {
    try {
      const response = await fetch(
        `${API_URL}/products/${productId}/reviews`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to fetch product reviews."
        );
      }

      setReviewsByProduct((currentReviews) => ({
        ...currentReviews,
        [productId]: data,
      }));
    } catch (error) {
      console.error(
        `Error fetching reviews for product ${productId}:`,
        error
      );

      setReviewsByProduct((currentReviews) => ({
        ...currentReviews,
        [productId]: {
          product_id: productId,
          average_rating: 0,
          total_reviews: 0,
          reviews: [],
        },
      }));
    }
  };

  const fetchAllProductReviews = async (productList) => {
    if (!Array.isArray(productList) || productList.length === 0) {
      return;
    }

    await Promise.all(
      productList.map((product) =>
        fetchProductReviews(product.id)
      )
    );
  };

  const handleSubmitReview = async (event, productId) => {
    event.preventDefault();

    if (!loggedIn) {
      alert("Please login before submitting a review.");
      setShowLogin(true);
      return;
    }

    const currentReviewForm =
      reviewForms[productId] || { rating: "5", comment: "" };

    const comment = currentReviewForm.comment.trim();
    const rating = Number(currentReviewForm.rating);

    if (!comment) {
      alert("Please enter a review comment.");
      return;
    }

    if (rating < 1 || rating > 5) {
      alert("Please select a rating between 1 and 5.");
      return;
    }

    const token = localStorage.getItem("access_token");

    if (!token) {
      alert("Please login before submitting a review.");
      setShowLogin(true);
      return;
    }

    setReviewSubmittingProduct(productId);

    try {
      const response = await fetch(
        `${API_URL}/reviews?product_id=${encodeURIComponent(
          productId
        )}&rating=${encodeURIComponent(
          rating
        )}&comment=${encodeURIComponent(comment)}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to submit review."
        );
      }

      alert(
        "Review submitted successfully! Refresh the page to see it."
      );

      setReviewForms((currentForms) => ({
        ...currentForms,
        [productId]: { rating: "5", comment: "" },
      }));
      await fetchProductReviews(productId);
    } catch (error) {
      console.error("Submit review error:", error);
      alert(
        error.message || "Unable to submit review."
      );
    } finally {
      setReviewSubmittingProduct(null);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  useEffect(() => {
    fetchAllProductReviews(products);
  }, [products]);


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


  useEffect(() => {
    if (!loggedIn) {
      setNotifications([]);
      return;
    }

    fetchNotifications();
  }, [loggedIn]);


  useEffect(() => {
    fetchTrendingProducts();
  }, []);


  useEffect(() => {
    if (!loggedIn || !user?.id) {
      setRecommendedProducts([]);
      return;
    }

    fetchRecommendations(user.id);
  }, [loggedIn, user?.id]);


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

          {loggedIn && (
            <>
              <button
                className="notification-button"
                onClick={() => {
                  const nextShowNotifications = !showNotifications;
                  setShowNotifications(nextShowNotifications);

                  if (nextShowNotifications) {
                    fetchNotifications();
                  }
                }}
                aria-label="Notifications"
              >
                🔔

                {notifications.filter(
                  (notification) =>
                    !notification.read_status
                ).length > 0 && (
                  <span className="notification-badge">
                    {notifications.filter(
                      (notification) =>
                        !notification.read_status
                    ).length}
                  </span>
                )}
              </button>

              {showNotifications && (
                <div className="notification-dropdown">

                  <div className="notification-header">
                    <strong>
                      Notifications
                    </strong>
                    </div>
                  
                  {notifications.length === 0 ? (
                    <div className="notification-empty">
                      No notifications
                    </div>
                  ) : (
                    notifications.map(
                      (notification) => (
                       <div
  key={notification.id}
  className={
    notification.read_status
      ? "notification-item"
      : "notification-item unread"
  }
  onClick={() =>
    markNotificationAsRead(
      notification.id
    )
  }
  role="button"
  tabIndex={0}
>
  <div className="notification-message">
    {notification.message}
  </div>

  <div className="notification-time">
    {notification.timestamp
      ? new Date(
          notification.timestamp
        ).toLocaleString()
      : ""}
  </div>
</div>
                      )
                    )
                  )}

                </div>
              )}
            </>
          )}

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


          {loggedIn && (
            <RecommendationSection
              title="Recommended For You"
              products={recommendedProducts}
              loading={recommendationsLoading}
              emptyMessage="Browse or purchase a few products and we will personalize recommendations for you."
              onAddToCart={handleAddToCart}
              onViewSimilar={fetchSimilarProducts}
            />
          )}


          <RecommendationSection
            title="You May Also Like"
            products={trendingProducts}
            loading={trendingLoading}
            emptyMessage="Trending products are not available right now."
            onAddToCart={handleAddToCart}
            onViewSimilar={fetchSimilarProducts}
          />


          {similarProductId && (
            <RecommendationSection
              title={`Similar Products${getProduct(similarProductId)?.name ? ` — ${getProduct(similarProductId).name}` : ""}`}
              products={similarProducts}
              loading={similarLoading}
              emptyMessage="No similar products were found for this product."
              onAddToCart={handleAddToCart}
              onViewSimilar={fetchSimilarProducts}
            />
          )}


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
                      onClick={() => {
                        recordProductView(product.id);
                        fetchSimilarProducts(product.id);
                      }}
                      style={{
                        cursor: "pointer",
                      }}
                    />


                    <div className="product-details">

                      <h3
                        onClick={() => {
                          recordProductView(product.id);
                          fetchSimilarProducts(product.id);
                        }}
                        style={{
                          cursor: "pointer",
                        }}
                      >
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

                      <ReviewSection
                        product={product}
                        reviewData={reviewsByProduct[product.id]}
                        loggedIn={loggedIn}
                        onLogin={() => setShowLogin(true)}
                        reviewForm={
                          reviewForms[product.id] || {
                            rating: "5",
                            comment: "",
                          }
                        }
                        onRatingChange={(rating) =>
                          setReviewForms((currentForms) => ({
                            ...currentForms,
                            [product.id]: {
                              ...(currentForms[product.id] || {
                                rating: "5",
                                comment: "",
                              }),
                              rating,
                            },
                          }))
                        }
                        onCommentChange={(comment) =>
                          setReviewForms((currentForms) => ({
                            ...currentForms,
                            [product.id]: {
                              ...(currentForms[product.id] || {
                                rating: "5",
                                comment: "",
                              }),
                              comment,
                            },
                          }))
                        }
                        onSubmit={handleSubmitReview}
                        submitting={reviewSubmittingProduct === product.id}
                      />


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
                        type="button"
                        onClick={() => {
                          recordProductView(product.id);
                          fetchSimilarProducts(product.id);
                        }}
                        style={{
                          width: "100%",
                          marginBottom: "8px",
                          padding: "10px",
                          border: "1px solid #2563eb",
                          borderRadius: "7px",
                          background: "white",
                          color: "#2563eb",
                          cursor: "pointer",
                          fontWeight: "600",
                        }}
                      >
                        View Similar Products
                      </button>

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