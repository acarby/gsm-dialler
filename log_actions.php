<?php
session_start();
header('Content-Type: application/json');

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
  http_response_code(403);
  echo json_encode(["status" => "error", "error" => "Unauthorized"]);
  exit;
}

$log_file = '/var/www/gsmdialler-data/log.txt';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
  echo json_encode(["status" => "error", "error" => "Invalid request method"]);
  exit;
}

$action = $_POST['action'] ?? '';

if ($action === 'log') {
  $log_message = trim($_POST['message'] ?? '');
  if ($log_message === '') {
    echo json_encode(["status" => "error", "error" => "No message provided"]);
    exit;
  }
  $timestamp = date('Y-m-d H:i:s');
  file_put_contents($log_file, "[$timestamp] $log_message\n", FILE_APPEND);
  echo json_encode(["status" => "success"]);
  exit;
}

if ($action === 'clear_log') {
  if (file_exists($log_file)) {
    file_put_contents($log_file, "");
    $timestamp = date('Y-m-d H:i:s');
    file_put_contents($log_file, "[$timestamp] Log cleared by user.\n", FILE_APPEND);
    echo json_encode(["status" => "success", "message" => "Log cleared successfully"]);
  } else {
    echo json_encode(["status" => "error", "error" => "Log file not found"]);
  }
  exit;
}

echo json_encode(["status" => "error", "error" => "Unknown action"]);
?>



