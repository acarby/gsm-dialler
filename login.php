<?php
session_start();
$correct_user = 'admin';
$correct_pass = 'dialler123';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if ($_POST['username'] === $correct_user && $_POST['password'] === $correct_pass) {
        $_SESSION['logged_in'] = true;
        header("Location: /");
        exit;
    } else {
        $error = "Invalid login details.";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Login - GSM Dialler</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background-color: #f9f9fb;
      font-family: 'Inter', sans-serif;
    }
    .card {
      border: none;
      border-radius: 16px;
      padding: 2rem;
      max-width: 400px;
      width: 100%;
      box-shadow: 0 12px 24px rgba(0, 0, 0, 0.06);
    }
    .btn-primary {
      background-color: #000;
      border: none;
      border-radius: 8px;
    }
    .btn-primary:hover {
      background-color: #222;
    }
    .form-control {
      border-radius: 8px;
    }
    .form-label {
      font-weight: 500;
    }
  </style>
</head>
<body class="d-flex justify-content-center align-items-center vh-100">
  <div class="card shadow bg-white">
    <h4 class="text-center mb-4">🔒 <strong>GSM Dialler Login</strong></h4>
    <?php if (!empty($error)): ?>
      <div class="alert alert-danger"><?= htmlspecialchars($error) ?></div>
    <?php endif; ?>
    <form method="post" autocomplete="off">
      <div class="mb-3">
        <label class="form-label">Username</label>
        <input type="text" name="username" class="form-control" required autofocus>
      </div>
      <div class="mb-3">
        <label class="form-label">Password</label>
        <input type="password" name="password" class="form-control" required>
      </div>
      <button class="btn btn-primary w-100 mt-2" type="submit">Log In</button>
    </form>
  </div>
</body>
</html>
