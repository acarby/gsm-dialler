<?php
// GPIO Status endpoint - returns JSON with GPIO17 state
header('Content-Type: application/json');

$status_file = '/var/www/gsmdialler-data/gpio_status.json';

// Read status from file (updated by gpio_trigger.py)
if (file_exists($status_file)) {
    $data = json_decode(file_get_contents($status_file), true);
    if ($data && isset($data['status'])) {
        echo json_encode($data);
    } else {
        echo json_encode([
            "status" => "error",
            "error" => "Invalid status file format"
        ]);
    }
} else {
    echo json_encode([
        "status" => "error",
        "error" => "Status file not found - GPIO trigger may not be running"
    ]);
}
?>

