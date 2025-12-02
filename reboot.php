<?php
session_start();
if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
  header('Location: /login');
  exit;
}

// Handle reboot request
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['confirm_reboot'])) {
    // Log the reboot action
    $log_file = '/var/www/gsmdialler-data/log.txt';
    $timestamp = date('Y-m-d H:i:s');
    file_put_contents($log_file, "[$timestamp] System reboot initiated by user.\n", FILE_APPEND);
    
    // Execute reboot command (requires sudo permissions)
    // Note: www-data user needs passwordless sudo for /sbin/reboot
    exec('sudo /sbin/reboot 2>&1', $output, $return_var);
    
    // If reboot command fails, show error
    if ($return_var !== 0) {
        header('Location: /?error=reboot_failed');
        exit;
    }
    
    // Reboot initiated successfully
    header('Location: /?reboot_initiated=1');
    exit;
}

// Show confirmation page
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Reboot System - GSM Dialler</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: #f5f7fa;
      font-family: 'Inter', sans-serif;
    }
    .container {
      max-width: 500px;
      margin-top: 100px;
    }
    .card {
      border: none;
      border-radius: 16px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="card p-4">
      <h4 class="mb-4">⚠️ Reboot System</h4>
      <p>Are you sure you want to reboot the Raspberry Pi?</p>
      <p class="text-muted small">This will restart the entire system. The web interface will be unavailable for about 1-2 minutes.</p>
      
      <form method="post">
        <input type="hidden" name="confirm_reboot" value="1">
        <div class="d-flex gap-2 mt-4">
          <button type="submit" class="btn btn-danger flex-fill">Yes, Reboot Now</button>
          <a href="/" class="btn btn-outline-secondary flex-fill">Cancel</a>
        </div>
      </form>
    </div>
  </div>
</body>
</html>




