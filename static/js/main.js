document.addEventListener('DOMContentLoaded', () => {
  const chatLauncher = document.getElementById('chatLauncher');
  const chatWindow = document.getElementById('chatWindow');
  const closeWidgetBtn = document.getElementById('closeWidgetBtn');
  const resetChatHeaderBtn = document.getElementById('resetChatHeaderBtn');
  const menuToggleBtn = document.getElementById('menuToggleBtn');
  const menuDrawer = document.getElementById('menuDrawer');
  const newChatDrawerBtn = document.getElementById('newChatDrawerBtn');
  const clearHistoryBtn = document.getElementById('clearHistoryBtn');
  const chatBody = document.getElementById('chatBody');
  const userInput = document.getElementById('userInput');
  const sendBtn = document.getElementById('sendBtn');
  const quickSuggestions = document.getElementById('quickSuggestions');
  const copyToast = document.getElementById('copyToast');

  let history = [];

  // Set initial message timestamp
  const initialTime = document.getElementById('initialTime');
  if (initialTime) {
    initialTime.innerText = getCurrentTimeString();
  }

  function getCurrentTimeString() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  // Open Chat Window with Animation & Hide Launcher Icon
  function openChatWindow() {
    chatWindow.classList.add('active');
    chatLauncher.classList.add('hidden');
    userInput.focus();
  }

  // Close Chat Window & Restore Launcher Icon
  function closeChatWindow() {
    chatWindow.classList.remove('active');
    chatLauncher.classList.remove('hidden');
    if (menuDrawer) menuDrawer.classList.remove('open');
  }

  if (chatLauncher) chatLauncher.addEventListener('click', openChatWindow);
  if (closeWidgetBtn) closeWidgetBtn.addEventListener('click', closeChatWindow);
  if (resetChatHeaderBtn) resetChatHeaderBtn.addEventListener('click', resetConversation);

  // Toggle Top Menu Drawer
  if (menuToggleBtn) {
    menuToggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      menuDrawer.classList.toggle('open');
    });
  }

  document.addEventListener('click', (e) => {
    if (menuDrawer && !menuDrawer.contains(e.target) && e.target !== menuToggleBtn) {
      menuDrawer.classList.remove('open');
    }
  });

  // PURE COPY ICON ONLY (NO TEXT)
  window.copyMessageText = function (btnElement) {
    const msgRow = btnElement.closest('.msg-row');
    const bubble = msgRow.querySelector('.msg-bubble');
    const textToCopy = bubble.innerText.trim();

    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(textToCopy).then(() => {
        showCopySuccess(btnElement);
      }).catch(() => {
        fallbackCopyText(textToCopy, btnElement);
      });
    } else {
      fallbackCopyText(textToCopy, btnElement);
    }
  };

  function fallbackCopyText(text, btnElement) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand('copy');
      showCopySuccess(btnElement);
    } catch (err) {
      console.error('Copy failed', err);
    }
    document.body.removeChild(textArea);
  }

  function showCopySuccess(btnElement) {
    btnElement.classList.add('copied');
    btnElement.innerHTML = `<i class="fa-solid fa-check"></i>`;

    if (copyToast) {
      copyToast.classList.add('show');
      setTimeout(() => {
        copyToast.classList.remove('show');
      }, 1500);
    }

    setTimeout(() => {
      btnElement.classList.remove('copied');
      btnElement.innerHTML = `<i class="fa-regular fa-copy"></i>`;
    }, 1500);
  }

  function parseSimpleMarkdown(text) {
    if (!text) return '';
    let html = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // Bold text **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Code inline `code`
    html = html.replace(/`(.*?)`/g, '<code style="background:#e2e8f0; padding:2px 6px; border-radius:6px; font-size:13px; font-family:monospace;">$1</code>');

    // Bullet list items
    html = html.replace(/^- (.*$)/gim, '• $1');

    // Newlines to <br>
    html = html.replace(/\n/g, '<br>');
    return html;
  }

  function addMessage(text, sender) {
    const row = document.createElement('div');
    row.className = `msg-row ${sender}`;

    if (sender === 'bot') {
      const avatar = document.createElement('div');
      avatar.className = 'bot-avatar-small';
      avatar.innerHTML = `<i class="fa-solid fa-robot"></i>`;
      row.appendChild(avatar);
    }

    const wrapper = document.createElement('div');
    wrapper.className = 'msg-content-wrapper';

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.innerHTML = parseSimpleMarkdown(text);

    const timestamp = document.createElement('span');
    timestamp.className = 'msg-timestamp';
    timestamp.innerText = getCurrentTimeString();

    wrapper.appendChild(bubble);
    wrapper.appendChild(timestamp);

    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-icon-btn';
    copyBtn.setAttribute('onclick', 'copyMessageText(this)');
    copyBtn.setAttribute('title', 'Copy message');
    copyBtn.innerHTML = `<i class="fa-regular fa-copy"></i>`;

    row.appendChild(wrapper);
    row.appendChild(copyBtn);

    chatBody.appendChild(row);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function showTypingIndicator() {
    const row = document.createElement('div');
    row.className = 'msg-row bot typing-row';

    const avatar = document.createElement('div');
    avatar.className = 'bot-avatar-small';
    avatar.innerHTML = `<i class="fa-solid fa-robot"></i>`;
    row.appendChild(avatar);

    const wrapper = document.createElement('div');
    wrapper.className = 'msg-content-wrapper';

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.innerHTML = `
      <div class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    `;

    wrapper.appendChild(bubble);
    row.appendChild(wrapper);

    chatBody.appendChild(row);
    chatBody.scrollTop = chatBody.scrollHeight;
    return row;
  }

  async function handleSend(textToSend) {
    const text = textToSend || userInput.value.trim();
    if (!text) return;

    if (quickSuggestions) {
      quickSuggestions.style.display = 'none';
    }

    addMessage(text, 'user');
    if (!textToSend) userInput.value = '';
    sendBtn.disabled = true;

    const typingRow = showTypingIndicator();

    try {
      const res = await fetch('/api/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history: history })
      });
      const data = await res.json();

      typingRow.remove();

      if (data.reply) {
        addMessage(data.reply, 'bot');
        history.push({ role: 'user', content: text });
        history.push({ role: 'assistant', content: data.reply });
      } else {
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
      }
    } catch (err) {
      typingRow.remove();
      addMessage('Network connection error. Please try again.', 'bot');
    } finally {
      sendBtn.disabled = false;
      userInput.focus();
    }
  }

  window.sendQuickPrompt = function (promptText) {
    userInput.value = promptText;
    handleSend(promptText);
  };

  if (sendBtn) sendBtn.addEventListener('click', () => handleSend());
  if (userInput) {
    userInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleSend();
    });
  }

  function resetConversation() {
    history = [];
    chatBody.innerHTML = `
      <div class="msg-row bot">
        <div class="bot-avatar-small"><i class="fa-solid fa-robot"></i></div>
        <div class="msg-content-wrapper">
          <div class="msg-bubble">
            Conversation reset! 👋 How can I assist you with Smart Electronics today?
          </div>
          <span class="msg-timestamp">${getCurrentTimeString()}</span>
        </div>
        <button class="copy-icon-btn" onclick="copyMessageText(this)" title="Copy message">
          <i class="fa-regular fa-copy"></i>
        </button>
      </div>
    `;
    if (menuDrawer) menuDrawer.classList.remove('open');
  }

  if (newChatDrawerBtn) newChatDrawerBtn.addEventListener('click', resetConversation);
  if (clearHistoryBtn) clearHistoryBtn.addEventListener('click', resetConversation);
});
