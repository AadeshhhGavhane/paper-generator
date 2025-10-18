/* Main Page JavaScript - Research Paper Generator */

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

const $ = (sel) => document.querySelector(sel);
const statusBox = $('#status');
const downloadsBox = $('#downloads');
const dlTex = $('#dlTex');
const dlPdf = $('#dlPdf');
const generateBtn = $('#generateBtn');

let currentRunId = null;

function setStatus(msg, type = '') {
  statusBox.textContent = msg;
  statusBox.className = `status-box ${type}`.trim();
  statusBox.style.display = 'block';
}

function clearDownloads() {
  downloadsBox.style.display = 'none';
  dlTex.href = '#';
  dlPdf.href = '#';
  dlTex.style.display = 'none';
  dlPdf.style.display = 'none';
  currentRunId = null;
}

async function generatePaper() {
  const topic = $('#topic').value.trim();
  const provider = $('#provider').value;

  clearDownloads();

  if (!topic || topic.length < 3) {
    setStatus('Please enter a topic (at least 3 characters).', 'error');
    return;
  }

  generateBtn.disabled = true;
  setStatus(`Generating with ${provider}... This may take a moment.`, 'info');

  try {
    const res = await fetch(`${API_BASE_URL}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, provider })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data?.detail || 'Generation failed');
    }

    const { run_id, tex_filename, pdf_filename } = data;
    currentRunId = run_id;
    setStatus('✅ Generated successfully. You can download your files below.', 'success');

    // Always show LaTeX download
    if (tex_filename) {
      dlTex.href = `${API_BASE_URL}/download/tex/${encodeURIComponent(run_id)}`;
      dlTex.setAttribute('download', tex_filename);
      dlTex.style.display = 'inline-block';
    }

    // Show PDF download if available
    if (pdf_filename) {
      dlPdf.href = `${API_BASE_URL}/download/pdf/${encodeURIComponent(run_id)}`;
      dlPdf.setAttribute('download', pdf_filename);
      dlPdf.style.display = 'inline-block';
    } else {
      // Show PDF button but with helpful message
      dlPdf.href = '#';
      dlPdf.onclick = (e) => {
        e.preventDefault();
        alert('PDF compilation failed. Try again or use the LaTeX file with Overleaf.');
      };
      dlPdf.style.display = 'inline-block';
    }

    downloadsBox.style.display = 'block';
    detectRow.style.display = 'flex';  // Show the AI detection button
  } catch (err) {
    let errorMsg = err.message;
    
    if (errorMsg.includes('API overloaded') || errorMsg.includes('503')) {
      errorMsg = '🚫 AI service is currently overloaded. Please try again in a few minutes.';
    } else if (errorMsg.includes('rate limit') || errorMsg.includes('429')) {
      errorMsg = '⏳ Rate limit reached. Please wait a moment and try again.';
    } else if (errorMsg.includes('quota') || errorMsg.includes('billing')) {
      errorMsg = '💳 API quota exceeded. Please check your API billing.';
    } else if (!errorMsg || errorMsg === 'Generation failed') {
      errorMsg = '❌ Generation failed. Please try again.';
    }
    
    setStatus(errorMsg, 'error');
  } finally {
    generateBtn.disabled = false;
  }
}

async function detectAI() {
  if (!currentRunId) {
    detectStatus.textContent = 'No run available to detect.';
    detectStatus.className = 'status-box error';
    detectStatus.style.display = 'block';
    return;
  }

  detectBtn.disabled = true;
  detectStatus.textContent = 'Detecting AI-likeness…';
  detectStatus.className = 'status-box info';
  detectStatus.style.display = 'block';

  try {
    const res = await fetch(`${API_BASE_URL}/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ run_id: currentRunId })
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data?.detail || 'Detection failed');
    }
    detectStatus.textContent = `🧠 Estimated AI score: ${data.score}%\nReason: ${data.reasoning}`;
    detectStatus.className = 'status-box success';
  } catch (err) {
    detectStatus.textContent = `❌ ${err.message}`;
    detectStatus.className = 'status-box error';
  } finally {
    detectBtn.disabled = false;
  }
}