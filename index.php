<?php
session_start();

// Handle log download FIRST - before any other processing
if (isset($_GET['action']) && $_GET['action'] === 'download_log') {
  // Check if user is logged in
  if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header('Location: /login');
    exit;
  }
  
  $log_file = '/var/www/gsmdialler-data/log.txt';
  if (file_exists($log_file)) {
    header('Content-Type: text/plain');
    header('Content-Disposition: attachment; filename="gsm_dialler_log_' . date('Y-m-d_His') . '.txt"');
    header('Content-Length: ' . filesize($log_file));
    readfile($log_file);
    exit;
  } else {
    header("Location: index.php?error=log_not_found");
    exit;
  }
}

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
  header('Location: /login');
  exit;
}

$call_list_file = '/var/www/gsmdialler-data/call_list.txt';
$message_file = '/var/www/gsmdialler-data/message.txt';
$log_file = '/var/www/gsmdialler-data/log.txt';

$call_list = file_exists($call_list_file) ? file($call_list_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) : [];
$message = file_exists($message_file) ? file_get_contents($message_file) : '';

// Read log and reverse order (newest first)
$log_contents = '';
if (file_exists($log_file)) {
    $log_lines = file($log_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    $log_lines = array_reverse($log_lines); // Reverse to show newest first
    $log_contents = implode("\n", $log_lines);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
  if (isset($_POST['call_list'], $_POST['message'])) {
    file_put_contents($call_list_file, $_POST['call_list']);
    file_put_contents($message_file, $_POST['message']);
    $timestamp = date('Y-m-d H:i:s');
    file_put_contents($log_file, "[$timestamp] Updated call list and message.\n", FILE_APPEND);
    header("Location: index.php?success=1");
    exit;
  }
  
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>GSM Dialler</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
  body {
    background: #f5f7fa;
    font-family: 'Inter', sans-serif;
    color: #333;
  }
  .container {
    max-width: 880px;
    margin-top: 40px;
  }
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }
  .header h3 {
    margin: 0;
    font-weight: 600;
    font-size: 1.5rem;
  }
  .card {
    border: 1px solid #e3e6ec;
    border-radius: 14px;
    padding: 2rem;
    background-color: #fff;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    margin-bottom: 2rem;
  }
  textarea.form-control {
    font-size: 0.95rem;
    background-color: #fafbfc;
    border-radius: 10px;
    border: 1px solid #ced4da;
  }
  button {
    border-radius: 8px;
  }
  .btn-save {
    font-weight: 500;
    padding: 0.75rem 1.5rem;
  }
  pre {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    max-height: 300px;
    overflow-y: auto;
  }
  .alert {
    font-size: 0.95rem;
  }
  #test-result, #sms-result {
    font-size: 0.9rem;
    margin-top: 1rem;
    padding: 1rem;
    border-radius: 8px;
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    min-height: 50px;
    max-height: 400px;
    overflow-y: auto;
    white-space: pre-wrap;
    font-family: 'Courier New', monospace;
  }
  .result-loading {
    color: #0d6efd;
    font-style: italic;
  }
  .result-success {
    color: #198754;
  }
  .result-error {
    color: #dc3545;
  }
  .result-timeout {
    color: #ffc107;
  }
  .call-entry {
    margin-bottom: 1rem;
    padding: 0.75rem;
    background-color: #fff;
    border-left: 4px solid #0d6efd;
    border-radius: 4px;
  }
  .call-entry.error {
    border-left-color: #dc3545;
  }
  .call-entry.timeout {
    border-left-color: #ffc107;
  }
  .call-entry.completed {
    border-left-color: #198754;
  }
  
  /* Modal Overlay Styles */
  .test-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.6);
    z-index: 9999;
    backdrop-filter: blur(4px);
  }
  .test-overlay.active {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .test-modal {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    animation: slideIn 0.3s ease-out;
  }
  @keyframes slideIn {
    from {
      transform: translateY(-20px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }
  .test-modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #e3e6ec;
  }
  .test-modal-header h5 {
    margin: 0;
    font-weight: 600;
    font-size: 1.25rem;
  }
  .test-status {
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    text-align: center;
  }
  .test-status.progress {
    background-color: #e7f3ff;
    color: #0d6efd;
  }
  .test-status.success {
    background-color: #d1e7dd;
    color: #198754;
  }
  .test-status.error {
    background-color: #f8d7da;
    color: #dc3545;
  }
  .spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(13, 110, 253, 0.3);
    border-radius: 50%;
    border-top-color: #0d6efd;
    animation: spin 1s linear infinite;
    margin-right: 0.5rem;
    vertical-align: middle;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  .call-progress-item {
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    border-radius: 8px;
    background-color: #f8f9fa;
    border-left: 4px solid #0d6efd;
  }
  .call-progress-item.active {
    background-color: #e7f3ff;
    border-left-color: #0d6efd;
  }
  .call-progress-item.completed {
    background-color: #d1e7dd;
    border-left-color: #198754;
  }
  .call-progress-item.error {
    background-color: #f8d7da;
    border-left-color: #dc3545;
  }
  .call-progress-item.timeout {
    background-color: #fff3cd;
    border-left-color: #ffc107;
  }
  .btn-close-modal {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #6c757d;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.2s;
  }
  .btn-close-modal:hover {
    background-color: #f0f0f0;
    color: #000;
  }
  
  /* GPIO Status Styles */
  .gpio-status-box {
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
    border: 2px solid;
    transition: all 0.3s ease;
  }
  .gpio-status-box.normal {
    background-color: #d1e7dd;
    border-color: #198754;
    color: #0f5132;
  }
  .gpio-status-box.alarm {
    background-color: #f8d7da;
    border-color: #dc3545;
    color: #842029;
    animation: pulse-alarm 2s infinite;
  }
  @keyframes pulse-alarm {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
  }
  .gpio-status-icon {
    font-size: 3rem;
    margin-bottom: 0.5rem;
  }
  .gpio-status-text {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
  }
  .gpio-status-details {
    font-size: 0.9rem;
    color: #666;
    margin-top: 0.5rem;
  }
  .gpio-status-error {
    padding: 1rem;
    background-color: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 8px;
    color: #856404;
    text-align: center;
  }
  </style>
</head>
<body>

  <div class="container">
  <div class="header">
    <h3>📞 GSM Dialler Dashboard</h3>
    <div>
      <a href="/reboot" class="btn btn-outline-warning btn-sm me-2">🔄 Reboot</a>
      <a href="/logout" class="btn btn-outline-dark btn-sm">Logout</a>
    </div>
  </div>

  <?php if (isset($_GET['success'])): ?>
    <div class="alert alert-success">✅ Settings updated successfully.</div>
  <?php endif; ?>

  <form method="post">
    <div class="card">
    <div class="row g-4">
      <div class="col-md-6">
      <label class="form-label fw-medium">📋 Call List</label>
      <textarea name="call_list" rows="7" class="form-control" placeholder="One number per line"><?= htmlspecialchars(implode("\n", $call_list)) ?></textarea>
      </div>
      <div class="col-md-6">
      <label class="form-label fw-medium">💬 Message to Send</label>
      <textarea name="message" rows="7" class="form-control" placeholder="Enter message to send"><?= htmlspecialchars($message) ?></textarea>
      </div>
    </div>
     <div class="text-end mt-4">
     <button type="submit" class="btn btn-dark btn-save">💾 Save Settings</button>
     <button type="button" class="btn btn-outline-primary btn-save" onclick="triggerTestCall()" id="btn-test-call">📞 Run Test Call</button>
     <button type="button" class="btn btn-outline-success btn-save" onclick="triggerTestSMS()" id="btn-test-sms">📩 Run Test SMS</button>
     </div>
    </div>
    
  </form>

  <!-- GPIO Status Card -->
  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
      <h6 class="mb-0 fw-medium">🔥 Fire Alarm Panel Status</h6>
      <button type="button" class="btn btn-sm btn-outline-secondary" onclick="refreshGPIOStatus(); return false;" id="btn-refresh-gpio">🔄 Refresh</button>
    </div>
    <div id="gpio-status-container">
      <div class="d-flex align-items-center justify-content-center" style="min-height: 80px;">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <span class="ms-3">Loading GPIO status...</span>
      </div>
    </div>
  </div>

  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
      <h6 class="mb-0 fw-medium">📑 Log</h6>
      <div>
        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="refreshLog()">🔄 Refresh</button>
        <button type="button" class="btn btn-sm btn-outline-primary" onclick="downloadLog()">📥 Download</button>
        <button type="button" class="btn btn-sm btn-outline-danger" onclick="clearLog()" id="btn-clear-log">🗑️ Clear</button>
      </div>
    </div>
    <pre id="log-content"><?= htmlspecialchars($log_contents) ?></pre>
  </div>
  </div>

  <!-- Test Call Overlay Modal -->
  <div class="test-overlay" id="test-call-overlay">
    <div class="test-modal">
      <div class="test-modal-header">
        <h5>📞 Test Call in Progress</h5>
        <button class="btn-close-modal" onclick="closeTestCallModal()" id="btn-close-test">×</button>
      </div>
      <div id="test-status" class="test-status progress">
        <span class="spinner"></span>
        <strong>Initializing call...</strong>
      </div>
      <div id="test-call-details"></div>
    </div>
  </div>

  <!-- Test SMS Overlay Modal -->
  <div class="test-overlay" id="test-sms-overlay">
    <div class="test-modal">
      <div class="test-modal-header">
        <h5>📩 Test SMS</h5>
        <button class="btn-close-modal" onclick="closeTestSMSModal()">×</button>
      </div>
      <div id="sms-status" class="test-status progress">
        <span class="spinner"></span>
        <strong>Sending SMS...</strong>
      </div>
      <div id="sms-details"></div>
    </div>
  </div>

<script>
  function showTestCallModal() {
    const overlay = document.getElementById('test-call-overlay');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    document.getElementById('btn-close-test').style.display = 'none'; // Hide close button during test
  }
  
  function closeTestCallModal() {
    const overlay = document.getElementById('test-call-overlay');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }
  
  function showTestSMSModal() {
    const overlay = document.getElementById('test-sms-overlay');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
  
  function closeTestSMSModal() {
    const overlay = document.getElementById('test-sms-overlay');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }
  
  // Close modal when clicking outside
  document.getElementById('test-call-overlay').addEventListener('click', function(e) {
    if (e.target === this) {
      closeTestCallModal();
    }
  });
  
  document.getElementById('test-sms-overlay').addEventListener('click', function(e) {
    if (e.target === this) {
      closeTestSMSModal();
    }
  });

  function logEvent(message) {
    const formData = new FormData();
    formData.append('action', 'log');
    formData.append('message', message);
    
    fetch('log_actions.php', {
      method: 'POST',
      body: formData
    }).catch(err => console.error('Log error:', err));
  }
  
  function triggerTestCall() {
    const btn = document.getElementById('btn-test-call');
    const statusDiv = document.getElementById('test-status');
    const detailsDiv = document.getElementById('test-call-details');
    
    // Log the test call event
    logEvent('Test Call triggered');
    
    // Show modal and reset
    showTestCallModal();
    btn.disabled = true;
    btn.textContent = '⏳ Calling...';
    detailsDiv.innerHTML = '';
    statusDiv.className = 'test-status progress';
    statusDiv.innerHTML = '<span class="spinner"></span><strong>Connecting to modem...</strong>';
    
    fetch('test_call.py')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.text();
      })
      .then(data => {
        try {
          // Try to parse as JSON
          const json = JSON.parse(data);
          displayCallResultsInModal(json);
          
          // Log the result
          const successCount = json.calls ? json.calls.filter(c => c.status === 'completed').length : 0;
          const totalCount = json.calls ? json.calls.length : 0;
          logEvent(`Test Call completed: ${successCount}/${totalCount} calls successful`);
        } catch (e) {
          // If not JSON, display as text
          statusDiv.className = 'test-status error';
          statusDiv.innerHTML = '<strong>❌ Error parsing response</strong>';
          detailsDiv.innerHTML = '<pre>' + data + '</pre>';
        }
      })
      .catch(err => {
        statusDiv.className = 'test-status error';
        statusDiv.innerHTML = '<strong>❌ Error: ' + err.message + '</strong>';
        detailsDiv.innerHTML = '<p>Please check the modem connection and try again.</p>';
        logEvent(`Test Call failed: ${err.message}`);
      })
      .finally(() => {
        btn.disabled = false;
        btn.textContent = '📞 Run Test Call';
        document.getElementById('btn-close-test').style.display = 'block'; // Show close button
      });
  }
  
  function displayCallResultsInModal(data) {
    const statusDiv = document.getElementById('test-status');
    const detailsDiv = document.getElementById('test-call-details');
    
    if (data.error) {
      statusDiv.className = 'test-status error';
      statusDiv.innerHTML = '<strong>❌ ' + data.error + '</strong>';
      return;
    }
    
    if (!data.calls || data.calls.length === 0) {
      statusDiv.className = 'test-status error';
      statusDiv.innerHTML = '<strong>⚠️ No calls were made.</strong>';
      return;
    }
    
    // Update status based on results
    const hasErrors = data.calls.some(c => c.status === 'error');
    const hasTimeouts = data.calls.some(c => c.status === 'timeout');
    const allCompleted = data.calls.every(c => c.status === 'completed');
    
    if (allCompleted) {
      statusDiv.className = 'test-status success';
      statusDiv.innerHTML = '<strong>✅ All calls completed successfully!</strong>';
    } else if (hasErrors) {
      statusDiv.className = 'test-status error';
      statusDiv.innerHTML = '<strong>❌ Some calls failed</strong>';
    } else if (hasTimeouts) {
      statusDiv.className = 'test-status error';
      statusDiv.innerHTML = '<strong>⚠️ Some calls timed out</strong>';
    } else {
      statusDiv.className = 'test-status progress';
      statusDiv.innerHTML = '<strong>📞 Calls processed</strong>';
    }
    
    // Display call details
    let html = '<div style="margin-top: 1rem;"><strong>Call Details:</strong></div>';
    data.calls.forEach((call, index) => {
      const statusClass = call.status === 'completed' ? 'completed' : 
                         call.status === 'error' ? 'error' : 
                         call.status === 'timeout' ? 'timeout' : 'active';
      
      const statusIcon = call.status === 'completed' ? '✅' : 
                        call.status === 'error' ? '❌' : 
                        call.status === 'timeout' ? '⏱️' : '📞';
      
      html += `<div class="call-progress-item ${statusClass}">`;
      html += `<strong>${statusIcon} Call ${index + 1}: ${call.number}</strong><br>`;
      html += `<span>Status: <strong>${call.status.toUpperCase()}</strong></span>`;
      
      if (call.duration_s) {
        html += ` | Duration: <strong>${call.duration_s}s</strong>`;
      }
      
      if (call.error) {
        html += `<br><span style="color: #dc3545;">Error: ${call.error}</span>`;
      }
      
      if (call.log && call.log.length > 0) {
        html += '<details style="margin-top: 0.5rem;"><summary style="cursor: pointer; color: #0d6efd; font-size: 0.9rem;">View Modem Log</summary><pre style="margin-top: 0.5rem; font-size: 0.8rem; background: #f8f9fa; padding: 0.5rem; border-radius: 4px; max-height: 200px; overflow-y: auto;">';
        call.log.forEach(line => {
          html += line + '\n';
        });
        html += '</pre></details>';
      }
      
      html += '</div>';
    });
    
    detailsDiv.innerHTML = html;
  }
  
  function triggerTestSMS() {
    const btn = document.getElementById('btn-test-sms');
    const statusDiv = document.getElementById('sms-status');
    const detailsDiv = document.getElementById('sms-details');
    
    // Log the test SMS event
    logEvent('Test SMS triggered');
    
    // Show modal and reset
    showTestSMSModal();
    btn.disabled = true;
    btn.textContent = '⏳ Sending...';
    detailsDiv.innerHTML = '';
    statusDiv.className = 'test-status progress';
    statusDiv.innerHTML = '<span class="spinner"></span><strong>Connecting to modem...</strong>';
    
    fetch('test_sms.py')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.text();
      })
      .then(data => {
        try {
          // Try to parse as JSON
          const json = JSON.parse(data);
          displaySMSResultsInModal(json);
          
          // Log the result
          const successCount = json.sms_messages ? json.sms_messages.filter(s => s.status === 'completed').length : 0;
          const totalCount = json.sms_messages ? json.sms_messages.length : 0;
          logEvent(`Test SMS completed: ${successCount}/${totalCount} messages sent successfully`);
        } catch (e) {
          // If not JSON, display as text
          statusDiv.className = 'test-status error';
          statusDiv.innerHTML = '<strong>❌ Error parsing response</strong>';
          detailsDiv.innerHTML = '<pre style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-top: 1rem;">' + data + '</pre>';
        }
      })
      .catch(err => {
        if (err.message.includes('404')) {
          statusDiv.className = 'test-status error';
          statusDiv.innerHTML = '<strong>⚠️ SMS functionality not available</strong>';
          detailsDiv.innerHTML = '<p style="margin-top: 1rem;">test_sms.py not found. SMS functionality not implemented yet.</p>';
        } else {
          statusDiv.className = 'test-status error';
          statusDiv.innerHTML = '<strong>❌ Error: ' + err.message + '</strong>';
          detailsDiv.innerHTML = '<p style="margin-top: 1rem;">Please check the modem connection and try again.</p>';
          logEvent(`Test SMS failed: ${err.message}`);
        }
      })
      .finally(() => {
        btn.disabled = false;
        btn.textContent = '📩 Run Test SMS';
      });
  }
  
  function displaySMSResultsInModal(data) {
    const statusDiv = document.getElementById('sms-status');
    const detailsDiv = document.getElementById('sms-details');
    
    if (data.error) {
      statusDiv.className = 'test-status error';
      statusDiv.innerHTML = '<strong>❌ ' + data.error + '</strong>';
      return;
    }
    
    if (!data.sms_messages || data.sms_messages.length === 0) {
      statusDiv.className = 'test-status error';
      statusDiv.innerHTML = '<strong>⚠️ No SMS messages were sent.</strong>';
      return;
    }
    
    // Update status based on results
    const hasErrors = data.sms_messages.some(s => s.status === 'error');
    const hasTimeouts = data.sms_messages.some(s => s.status === 'timeout');
    const allCompleted = data.sms_messages.every(s => s.status === 'completed');
    
    if (allCompleted) {
      statusDiv.className = 'test-status success';
      statusDiv.innerHTML = '<strong>✅ All SMS messages sent successfully!</strong>';
    } else if (hasErrors) {
      statusDiv.className = 'test-status error';
      statusDiv.innerHTML = '<strong>❌ Some SMS messages failed</strong>';
    } else if (hasTimeouts) {
      statusDiv.className = 'test-status error';
      statusDiv.innerHTML = '<strong>⚠️ Some SMS messages timed out</strong>';
    } else {
      statusDiv.className = 'test-status progress';
      statusDiv.innerHTML = '<strong>📩 SMS messages processed</strong>';
    }
    
    // Display message that was sent
    let html = '';
    if (data.message) {
      html += '<div style="margin-bottom: 1rem; padding: 0.75rem; background: #e7f3ff; border-radius: 8px; border-left: 4px solid #0d6efd;">';
      html += '<strong>Message sent:</strong><br>';
      html += '<span style="font-style: italic;">' + data.message.replace(/\n/g, '<br>') + '</span>';
      html += '</div>';
    }
    
    // Display SMS details
    html += '<div style="margin-top: 1rem;"><strong>SMS Details:</strong></div>';
    data.sms_messages.forEach((sms, index) => {
      const statusClass = sms.status === 'completed' ? 'completed' : 
                         sms.status === 'error' ? 'error' : 
                         sms.status === 'timeout' ? 'timeout' : 'active';
      
      const statusIcon = sms.status === 'completed' ? '✅' : 
                        sms.status === 'error' ? '❌' : 
                        sms.status === 'timeout' ? '⏱️' : '📩';
      
      html += `<div class="call-progress-item ${statusClass}">`;
      html += `<strong>${statusIcon} SMS ${index + 1}: ${sms.number}</strong><br>`;
      html += `<span>Status: <strong>${sms.status.toUpperCase()}</strong></span>`;
      
      if (sms.duration_s) {
        html += ` | Duration: <strong>${sms.duration_s}s</strong>`;
      }
      
      if (sms.error) {
        html += `<br><span style="color: #dc3545;">Error: ${sms.error}</span>`;
      }
      
      if (sms.log && sms.log.length > 0) {
        html += '<details style="margin-top: 0.5rem;"><summary style="cursor: pointer; color: #0d6efd; font-size: 0.9rem;">View Modem Log</summary><pre style="margin-top: 0.5rem; font-size: 0.8rem; background: #f8f9fa; padding: 0.5rem; border-radius: 4px; max-height: 200px; overflow-y: auto;">';
        sms.log.forEach(line => {
          html += line + '\n';
        });
        html += '</pre></details>';
      }
      
      html += '</div>';
    });
    
    detailsDiv.innerHTML = html;
  }
  
  function refreshLog() {
    // Reload the page to get updated log
    window.location.reload();
  }
  
  function downloadLog() {
    // Download log file - create a temporary link to trigger download
    const link = document.createElement('a');
    link.href = 'index.php?action=download_log';
    link.download = 'gsm_dialler_log_' + new Date().toISOString().slice(0,19).replace(/:/g, '-') + '.txt';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
  
  function clearLog() {
    if (!confirm('Are you sure you want to clear the log? This action cannot be undone.')) {
      return;
    }
    
    const btn = document.getElementById('btn-clear-log');
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = '⏳ Clearing...';
    
    const formData = new FormData();
    formData.append('action', 'clear_log');
    
    fetch('log_actions.php', {
      method: 'POST',
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          // Refresh the log display
          refreshLog();
        } else {
          alert('Error clearing log: ' + (data.error || 'Unknown error'));
          btn.disabled = false;
          btn.textContent = originalText;
        }
      })
      .catch(err => {
        alert('Error clearing log: ' + err.message);
        btn.disabled = false;
        btn.textContent = originalText;
      });
  }
  
  function updateGPIOStatus() {
    fetch('gpio_status.php')
      .then(res => res.json())
      .then(data => {
        const container = document.getElementById('gpio-status-container');
        
        if (data.status === 'error') {
          container.innerHTML = `
            <div class="gpio-status-error">
              <strong>⚠️ Error reading GPIO status</strong><br>
              <small>${data.error || 'Unknown error'}</small>
            </div>
          `;
          return;
        }
        
        const isAlarm = data.is_alarm;
        const statusClass = isAlarm ? 'alarm' : 'normal';
        const statusIcon = isAlarm ? '🔥' : '✅';
        const statusText = data.status_text;
        const stateText = `GPIO${data.gpio_pin}: ${data.state} (${data.value})`;
        
        container.innerHTML = `
          <div class="gpio-status-box ${statusClass}">
            <div class="gpio-status-icon">${statusIcon}</div>
            <div class="gpio-status-text">${statusText}</div>
            <div class="gpio-status-details">
              ${stateText}<br>
              <small>Last updated: ${new Date().toLocaleTimeString()}</small>
            </div>
          </div>
        `;
      })
      .catch(err => {
        const container = document.getElementById('gpio-status-container');
        container.innerHTML = `
          <div class="gpio-status-error">
            <strong>⚠️ Failed to fetch GPIO status</strong><br>
            <small>${err.message}</small>
          </div>
        `;
      });
  }
  
  function refreshGPIOStatus() {
    try {
      // Show loading state
      const container = document.getElementById('gpio-status-container');
      if (!container) {
        console.error('GPIO status container not found');
        return;
      }
      
      container.innerHTML = `
        <div class="d-flex align-items-center justify-content-center" style="min-height: 80px;">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <span class="ms-3">Refreshing...</span>
        </div>
      `;
      
      // Update the status
      updateGPIOStatus();
    } catch (err) {
      console.error('Error in refreshGPIOStatus:', err);
      alert('Error refreshing GPIO status: ' + err.message);
    }
    return false;
  }
  
  // Also add event listener as backup
  document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('btn-refresh-gpio');
    if (btn) {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        refreshGPIOStatus();
      });
    }
  });
  
  // Update GPIO status on page load
  updateGPIOStatus();
  
  // Auto-refresh GPIO status every 2 seconds
  setInterval(updateGPIOStatus, 2000);
  
  // Auto-refresh log every 5 seconds
  setInterval(function() {
    fetch('index.php')
      .then(res => res.text())
      .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newLogContent = doc.getElementById('log-content');
        if (newLogContent) {
          document.getElementById('log-content').textContent = newLogContent.textContent;
        }
      })
      .catch(err => console.error('Log refresh error:', err));
  }, 5000);
  </script>
  
  


</body>
</html>
