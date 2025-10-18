/* Upload Page JavaScript - AI Detection Tool */

// API Configuration
const API_BASE_URL = window.location.hostname === 'localhost' && window.location.port === '3000' 
  ? 'http://localhost:8000' 
  : '';

const $ = (s) => document.querySelector(s);
const statusBox = $('#status');
const fileInput = $('#file');
const latexArea = $('#latex');

let selectedFile = null;

fileInput.addEventListener('change', async (e) => {
  selectedFile = e.target.files && e.target.files[0];
  if (!selectedFile) return;
  if (selectedFile.name.toLowerCase().endsWith('.tex')) {
    const text = await selectedFile.text();
    latexArea.value = text;
  }
});

function setStatus(msg, type = '') { 
  statusBox.textContent = msg; 
  statusBox.className = `status-box ${type}`.trim(); 
  statusBox.style.display = 'block'; 
}

async function detect() {
  try {
    setStatus('Detecting AI-likeness…', 'info');
    if (selectedFile && selectedFile.name.toLowerCase().endsWith('.pdf')) {
      const form = new FormData();
      form.append('file', selectedFile);
      const r = await fetch(`${API_BASE_URL}/detect_pdf`, { method: 'POST', body: form });
      const data = await r.json();
      if (!r.ok) throw new Error(data?.detail || 'PDF detection failed');
      setStatus(`🧠 Estimated AI score: ${data.score}%\nReason: ${data.reasoning}`, 'success');
      return;
    }
    const latex = latexArea.value.trim();
    if (latex.length < 50) { 
      setStatus('Please paste at least 50 characters of LaTeX or upload a PDF.', 'error'); 
      return; 
    }
    const res = await fetch(`${API_BASE_URL}/detect_raw`, { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' }, 
      body: JSON.stringify({ latex }) 
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data?.detail || 'Detection failed');
    setStatus(`🧠 Estimated AI score: ${data.score}%\nReason: ${data.reasoning}`, 'success');
  } catch (err) { 
    let errorMsg = err.message;
    
    // Provide user-friendly error messages for common issues
    if (errorMsg.includes('API overloaded') || errorMsg.includes('503')) {
      errorMsg = '🚫 AI service is currently overloaded. Please try again in a few minutes.';
    } else if (errorMsg.includes('rate limit') || errorMsg.includes('429')) {
      errorMsg = '⏳ Rate limit reached. Please wait a moment and try again.';
    } else if (errorMsg.includes('quota') || errorMsg.includes('billing')) {
      errorMsg = '💳 API quota exceeded. Please check your API configuration.';
    } else if (errorMsg.includes('timeout') || errorMsg.includes('TimeoutError')) {
      errorMsg = '⏰ Request timed out. The AI service may be slow. Please try again.';
    } else if (!errorMsg || errorMsg === 'Detection failed' || errorMsg === 'PDF detection failed') {
      errorMsg = '❌ AI detection failed. Please try again or check your input.';
    }
    
    setStatus(errorMsg, 'error'); 
  }
}