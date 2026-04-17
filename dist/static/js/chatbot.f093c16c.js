/**
 * Portfolio AI Chatbot Widget
 * Floating chat button with streaming responses via SSE.
 */
(function () {
  const API_URL = window.CHATBOT_API_URL || 'https://chinmaya7077-portfolio-chatbot.hf.space';
  let sessionId = localStorage.getItem('chatbot_session') || crypto.randomUUID();
  localStorage.setItem('chatbot_session', sessionId);

  // ---- CREATE WIDGET HTML ----
  const widget = document.createElement('div');
  widget.id = 'chatbot-widget';
  widget.innerHTML = `
    <button id="chatbot-toggle" aria-label="Open AI Chat">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
    </button>
    <div id="chatbot-panel" class="chatbot-hidden">
      <div id="chatbot-header">
        <div class="chatbot-header-info">
          <span class="chatbot-avatar">AI</span>
          <div>
            <strong>Portfolio Assistant</strong>
            <small>Ask me about Chinmaya's work</small>
          </div>
        </div>
        <button id="chatbot-close" aria-label="Close chat">&times;</button>
      </div>
      <div id="chatbot-messages"></div>
      <div id="chatbot-suggestions"></div>
      <div id="chatbot-input-area">
        <input type="text" id="chatbot-input" placeholder="Ask about projects, skills, experience..." autocomplete="off" />
        <button id="chatbot-send" aria-label="Send">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
    </div>
  `;
  document.body.appendChild(widget);

  const toggle = document.getElementById('chatbot-toggle');
  const panel = document.getElementById('chatbot-panel');
  const closeBtn = document.getElementById('chatbot-close');
  const messagesEl = document.getElementById('chatbot-messages');
  const suggestionsEl = document.getElementById('chatbot-suggestions');
  const input = document.getElementById('chatbot-input');
  const sendBtn = document.getElementById('chatbot-send');

  let isOpen = false;
  let isLoading = false;

  // ---- TOGGLE ----
  toggle.addEventListener('click', () => {
    isOpen = true;
    panel.classList.remove('chatbot-hidden');
    toggle.classList.add('chatbot-active');
    if (messagesEl.children.length === 0) {
      showWelcome();
      loadSuggestions();
    }
    input.focus();
  });

  closeBtn.addEventListener('click', () => {
    isOpen = false;
    panel.classList.add('chatbot-hidden');
    toggle.classList.remove('chatbot-active');
  });

  function showWelcome() {
    addMessage('assistant', "Hi! I'm Chinmaya's AI assistant. Ask me about his projects, skills, experience, or tech stack.");
  }

  // ---- SUGGESTIONS ----
  async function loadSuggestions() {
    const defaults = [
      "What projects have you built?",
      "What is your tech stack?",
      "Tell me about your experience",
      "What is your education?",
    ];
    try {
      const res = await fetch(API_URL + '/chat/suggestions');
      if (res.ok) {
        const data = await res.json();
        renderSuggestions(data.suggestions.slice(0, 4));
        return;
      }
    } catch (e) {}
    renderSuggestions(defaults);
  }

  function renderSuggestions(items) {
    suggestionsEl.innerHTML = '';
    items.forEach(text => {
      const btn = document.createElement('button');
      btn.className = 'chatbot-suggestion';
      btn.textContent = text;
      btn.addEventListener('click', () => {
        sendMessage(text);
        suggestionsEl.innerHTML = '';
      });
      suggestionsEl.appendChild(btn);
    });
  }

  // ---- MESSAGES ----
  function addMessage(role, content) {
    const div = document.createElement('div');
    div.className = 'chatbot-msg chatbot-msg-' + role;
    const bubble = document.createElement('div');
    bubble.className = 'chatbot-bubble';
    bubble.textContent = content;
    div.appendChild(bubble);
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return bubble;
  }

  function addLoading() {
    const div = document.createElement('div');
    div.className = 'chatbot-msg chatbot-msg-assistant';
    div.id = 'chatbot-loading';
    const bubble = document.createElement('div');
    bubble.className = 'chatbot-bubble chatbot-typing';
    bubble.innerHTML = '<span></span><span></span><span></span>';
    div.appendChild(bubble);
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function removeLoading() {
    const el = document.getElementById('chatbot-loading');
    if (el) el.remove();
  }

  // ---- SEND MESSAGE ----
  async function sendMessage(text) {
    if (!text.trim() || isLoading) return;
    isLoading = true;
    input.value = '';
    sendBtn.disabled = true;

    addMessage('user', text);
    addLoading();

    try {
      // Use non-streaming for reliability
      const res = await fetch(API_URL + '/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: text,
          session_id: sessionId,
          stream: false,
        }),
      });

      removeLoading();

      if (!res.ok) {
        addMessage('assistant', 'Sorry, something went wrong. Please try again.');
        isLoading = false;
        sendBtn.disabled = false;
        return;
      }

      const data = await res.json();
      addMessage('assistant', data.response || "I couldn't generate a response.");
      if (data.session_id) sessionId = data.session_id;

    } catch (e) {
      removeLoading();
      addMessage('assistant', 'Connection error. The AI service might be starting up — please try again in a moment.');
    }

    isLoading = false;
    sendBtn.disabled = false;
    input.focus();
  }

  // ---- INPUT ----
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage(input.value);
  });
  sendBtn.addEventListener('click', () => sendMessage(input.value));
})();
