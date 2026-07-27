document.addEventListener('DOMContentLoaded', () => {
  const chatLauncher = document.getElementById('chatLauncher');
  const chatWindow = document.getElementById('chatWindow');
  const closeWidgetBtn = document.getElementById('closeWidgetBtn');
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

  function addMessage(text, sender) {
    const row = document.createElement('div');
    row.className = `msg-row ${sender}`;

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.innerText = text;

    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-icon-btn';
    copyBtn.setAttribute('onclick', 'copyMessageText(this)');
    copyBtn.setAttribute('title', 'Copy message');
    copyBtn.innerHTML = `<i class="fa-regular fa-copy"></i>`;

    row.appendChild(bubble);
    row.appendChild(copyBtn);
    chatBody.appendChild(row);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function showTypingIndicator() {
    const row = document.createElement('div');
    row.className = 'msg-row bot typing-row';

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.innerHTML = `
      <div class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    `;

    row.appendChild(bubble);
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
        <div class="msg-bubble">
          Conversation reset! How can I help you today?
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

  window.loadRecentTopic = function (topicTitle) {
    resetConversation();
    addMessage(`Loaded topic: ${topicTitle}. How can I assist you with this?`, 'bot');
  };
});
