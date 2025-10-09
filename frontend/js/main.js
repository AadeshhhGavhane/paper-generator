/* Main Page JavaScript - Research Paper Generator */

const $ = (sel) => document.querySelector(sel);
const statusBox = $('#status');
const downloadsBox = $('#downloads');
const dlTex = $('#dlTex');
const dlPdf = $('#dlPdf');
const generateBtn = $('#generateBtn');

const detectRow = $('#detectRow');
const detectBtn = $('#detectBtn');
const detectStatus = $('#detectStatus');

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
  detectRow.style.display = 'none';
  detectStatus.style.display = 'none';
  detectStatus.textContent = '';
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
    const res = await fetch('/generate', {
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

    if (tex_filename) {
      dlTex.href = `/download/tex/${encodeURIComponent(run_id)}`;
      dlTex.setAttribute('download', tex_filename);
    }
    if (pdf_filename) {
      dlPdf.href = `/download/pdf/${encodeURIComponent(run_id)}`;
      dlPdf.setAttribute('download', pdf_filename);
    }

    downloadsBox.style.display = 'grid';
    detectRow.style.display = 'flex';
  } catch (err) {
    let errorMsg = err.message;
    
    // Provide user-friendly error messages for common issues
    if (errorMsg.includes('API overloaded') || errorMsg.includes('503')) {
      errorMsg = '🚫 AI service is currently overloaded. Please try again in a few minutes, or switch to a different AI provider.';
    } else if (errorMsg.includes('rate limit') || errorMsg.includes('429')) {
      errorMsg = '⏳ Rate limit reached. Please wait a moment and try again.';
    } else if (errorMsg.includes('quota') || errorMsg.includes('billing')) {
      errorMsg = '💳 API quota exceeded. Please check your API billing or try a different provider.';
    } else if (errorMsg.includes('timeout') || errorMsg.includes('TimeoutError')) {
      errorMsg = '⏰ Request timed out. The AI service may be slow. Please try again.';
    } else if (!errorMsg || errorMsg === 'Generation failed') {
      errorMsg = '❌ Generation failed. Please try again with a different topic or AI provider.';
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
    const res = await fetch('/detect', {
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