import React, { useState } from "react";
import "./App.css";

const API_BASE = "http://localhost:5000/api";

function App() {
  const [userInput, setUserInput] = useState("");
  const [extractedItems, setExtractedItems] = useState([]);
  const [comparisonData, setComparisonData] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [activeTab, setActiveTab] = useState("compare");
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadedImage(file);

      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const extractFromImage = async () => {
    if (!uploadedImage) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("image", uploadedImage);

      const response = await fetch(`${API_BASE}/extract-from-image`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setExtractedItems(data.items);
      setActiveTab("items");
      setImagePreview(null);
      setUploadedImage(null);
    } catch (error) {
      console.error("Error extracting from image:", error);
      alert("Failed to extract items from image. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const clearImage = () => {
    setUploadedImage(null);
    setImagePreview(null);
  };

  const extractItems = async () => {
    if (!userInput.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/extract-items`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: userInput }),
      });

      const data = await response.json();
      setExtractedItems(data.items);
      setActiveTab("items");
    } catch (error) {
      console.error("Error extracting items:", error);
      alert("Failed to extract items. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const comparePrice = async () => {
    if (extractedItems.length === 0) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/compare-prices`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          items: extractedItems,
          location: "Pune",
        }),
      });

      const data = await response.json();
      setComparisonData(data);
      setInsights(data.insights);
      setActiveTab("results");
    } catch (error) {
      console.error("Error comparing prices:", error);
      alert("Failed to compare prices. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;

    const userMsg = { role: "user", text: chatInput };
    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput("");

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: chatInput,
          context: comparisonData,
        }),
      });

      const data = await response.json();
      const aiMsg = { role: "ai", text: data.answer };
      setChatMessages((prev) => [...prev, aiMsg]);
    } catch (error) {
      console.error("Error sending chat:", error);
    }
  };

  const removeItem = (index) => {
    setExtractedItems((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="app">
      <div className="grain-overlay"></div>

      <header className="header">
        <div className="container">
          <div className="logo-section">
            <div className="logo-icon">₹</div>
            <div>
              <h1 className="logo-title">QuickCompare</h1>
              <p className="logo-subtitle">AI-Powered Price Intelligence</p>
            </div>
          </div>
          <div className="header-stats">
            <div className="stat-item">
              <span className="stat-value">₹200-500</span>
              <span className="stat-label">Avg. Monthly Savings</span>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <span className="stat-value">4</span>
              <span className="stat-label">Platforms Compared</span>
            </div>
          </div>
        </div>
      </header>

      <main className="main-content container">
        <section className="input-section">
          <div className="input-card">
            <h2 className="section-title">What do you need?</h2>
            <p className="section-subtitle">
              Type naturally or upload an image of your shopping list
            </p>

            <div className="input-mode-tabs">
              <button
                className={`mode-tab ${!imagePreview ? "active" : ""}`}
                onClick={clearImage}
              >
                ⌨️ Type Text
              </button>
              <button className="mode-tab">📸 Upload Image</button>
            </div>

            {imagePreview ? (
              <div className="image-upload-section">
                <div className="image-preview-container">
                  <img
                    src={imagePreview}
                    alt="Uploaded"
                    className="image-preview"
                  />
                  <button className="remove-image" onClick={clearImage}>
                    ×
                  </button>
                </div>
                <button
                  className="btn btn-primary"
                  onClick={extractFromImage}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner"></span> Analyzing Image...
                    </>
                  ) : (
                    <>🔍 Extract Items from Image</>
                  )}
                </button>
              </div>
            ) : (
              <>
                <div className="input-group">
                  <textarea
                    className="text-input"
                    placeholder="E.g., Get me 1L Amul milk, brown bread, dozen eggs, and 1kg rice..."
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    rows="3"
                  />
                  <button
                    className="btn btn-primary"
                    onClick={extractItems}
                    disabled={loading || !userInput.trim()}
                  >
                    {loading ? (
                      <>
                        <span className="spinner"></span> Analyzing...
                      </>
                    ) : (
                      <>✨ Extract Items</>
                    )}
                  </button>
                </div>

                <div className="upload-section">
                  <div className="upload-divider">
                    <span>OR</span>
                  </div>
                  <label className="upload-button">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      style={{ display: "none" }}
                    />
                    <span className="upload-icon">📸</span>
                    <span className="upload-text">
                      Upload Shopping List Image
                    </span>
                    <span className="upload-hint">JPG, PNG up to 10MB</span>
                  </label>
                </div>
              </>
            )}

            {!imagePreview && (
              <div className="quick-examples">
                <span className="examples-label">Try:</span>
                <button
                  className="example-chip"
                  onClick={() =>
                    setUserInput("I need milk 1L, bread, and eggs")
                  }
                >
                  Breakfast essentials
                </button>
                <button
                  className="example-chip"
                  onClick={() =>
                    setUserInput("Get me rice 5kg, dal 1kg, oil 1L")
                  }
                >
                  Pantry staples
                </button>
                <button
                  className="example-chip"
                  onClick={() =>
                    setUserInput("Cold coffee, chips, and biscuits")
                  }
                >
                  Snack time
                </button>
              </div>
            )}
          </div>
        </section>

        {extractedItems.length > 0 && (
          <div className="tabs">
            <button
              className={`tab ${activeTab === "items" ? "active" : ""}`}
              onClick={() => setActiveTab("items")}
            >
              📝 Items ({extractedItems.length})
            </button>
            <button
              className={`tab ${activeTab === "results" ? "active" : ""}`}
              onClick={() => setActiveTab("results")}
              disabled={!comparisonData}
            >
              💰 Price Comparison
            </button>
            <button
              className={`tab ${activeTab === "chat" ? "active" : ""}`}
              onClick={() => setActiveTab("chat")}
            >
              💬 AI Assistant
            </button>
          </div>
        )}

        {activeTab === "items" && extractedItems.length > 0 && (
          <section className="items-section">
            <div className="items-header">
              <h3>Extracted Items</h3>
              <button
                className="btn btn-secondary"
                onClick={comparePrice}
                disabled={loading}
              >
                {loading ? "Comparing..." : "🔍 Compare Prices"}
              </button>
            </div>

            <div className="items-grid">
              {extractedItems.map((item, index) => (
                <div key={index} className="item-card">
                  <span className="item-text">{item}</span>
                  <button
                    className="item-remove"
                    onClick={() => removeItem(index)}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </section>
        )}

        {activeTab === "results" && comparisonData && (
          <section className="results-section">
            {insights && (
              <div className="insights-card">
                <h3 className="insights-title">🤖 AI Insights</h3>
                <div className="insights-grid">
                  <div className="insight-item">
                    <span className="insight-icon">💡</span>
                    <div>
                      <div className="insight-label">Recommendation</div>
                      <div className="insight-value">
                        {insights.recommendation}
                      </div>
                    </div>
                  </div>
                  <div className="insight-item">
                    <span className="insight-icon">📈</span>
                    <div>
                      <div className="insight-label">Price Trend</div>
                      <div className="insight-value">
                        {insights.price_trend}
                      </div>
                    </div>
                  </div>
                  <div className="insight-item">
                    <span className="insight-icon">💰</span>
                    <div>
                      <div className="insight-label">Savings Tip</div>
                      <div className="insight-value">
                        {insights.savings_tip}
                      </div>
                    </div>
                  </div>
                  <div className="insight-item">
                    <span className="insight-icon">🎯</span>
                    <div>
                      <div className="insight-label">Smart Suggestion</div>
                      <div className="insight-value">
                        {insights.smart_suggestion}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="platforms-grid">
              {Object.entries(comparisonData.platforms).map(
                ([platform, data]) => {
                  const isCheapest =
                    platform === comparisonData.cheapest_platform;

                  return (
                    <div
                      key={platform}
                      className={`platform-card ${
                        isCheapest ? "cheapest" : ""
                      }`}
                    >
                      {isCheapest && (
                        <div className="cheapest-badge">🏆 Best Deal</div>
                      )}

                      <div className="platform-header">
                        <h4 className="platform-name">{platform}</h4>
                        <div className="platform-total">
                          ₹{data.total.toFixed(2)}
                        </div>
                      </div>

                      <div className="platform-breakdown">
                        <div className="breakdown-row">
                          <span>Items Total</span>
                          <span>₹{data.items_total.toFixed(2)}</span>
                        </div>
                        <div className="breakdown-row">
                          <span>Delivery Fee</span>
                          <span
                            className={data.delivery_fee === 0 ? "free" : ""}
                          >
                            {data.delivery_fee === 0
                              ? "FREE"
                              : `₹${data.delivery_fee}`}
                          </span>
                        </div>
                        <div className="breakdown-row">
                          <span>Platform Fee</span>
                          <span>₹{data.platform_fee}</span>
                        </div>
                      </div>

                      <div className="platform-items">
                        {data.items.map((item, idx) => (
                          <div key={idx} className="platform-item">
                            <span className="item-name">{item.name}</span>
                            <span className="item-price">
                              {item.available ? `₹${item.price}` : "N/A"}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                }
              )}
            </div>
          </section>
        )}

        {activeTab === "chat" && (
          <section className="chat-section">
            <div className="chat-card">
              <div className="chat-header">
                <h3>AI Shopping Assistant</h3>
                <p>Ask me anything about prices, trends, or recommendations</p>
              </div>

              <div className="chat-messages">
                {chatMessages.length === 0 ? (
                  <div className="chat-empty">
                    <span className="chat-empty-icon">💬</span>
                    <p>Start a conversation!</p>
                    <div className="chat-suggestions">
                      <button
                        onClick={() =>
                          setChatInput("Is this a good time to buy rice?")
                        }
                      >
                        Is this a good time to buy rice?
                      </button>
                      <button
                        onClick={() =>
                          setChatInput("Which platform has best delivery?")
                        }
                      >
                        Which platform has best delivery?
                      </button>
                      <button
                        onClick={() =>
                          setChatInput("How can I save more money?")
                        }
                      >
                        How can I save more money?
                      </button>
                    </div>
                  </div>
                ) : (
                  chatMessages.map((msg, idx) => (
                    <div key={idx} className={`chat-message ${msg.role}`}>
                      <div className="message-avatar">
                        {msg.role === "user" ? "👤" : "🤖"}
                      </div>
                      <div className="message-content">{msg.text}</div>
                    </div>
                  ))
                )}
              </div>

              <div className="chat-input">
                <input
                  type="text"
                  placeholder="Ask me anything..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && sendChatMessage()}
                />
                <button onClick={sendChatMessage} disabled={!chatInput.trim()}>
                  Send
                </button>
              </div>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <div className="container">
          <p>Built with ❤️ using React + Flask + Gemini AI</p>
          <p className="footer-note">
            Prices are indicative and may vary. Always verify before purchasing.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
