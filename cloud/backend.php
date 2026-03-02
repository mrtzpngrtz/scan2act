<?php
// backend.php - Handles token generation, prompt submission, and polling.

$data_file = 'data.json';

// Initialize data file if it doesn't exist
if (!file_exists($data_file)) {
    file_put_contents($data_file, json_encode([
        'active_token' => null,
        'token_expiry' => 0,
        'pending_prompt' => null,
        'mode' => 1
    ]));
}

// Function to get current data
function get_data() {
    global $data_file;
    $content = file_get_contents($data_file);
    return json_decode($content, true);
}

// Function to save data
function save_data($data) {
    global $data_file;
    file_put_contents($data_file, json_encode($data, JSON_PRETTY_PRINT));
}

$action = $_GET['action'] ?? '';

// CORS headers for local polling script
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json");

if ($action === 'generate_token') {
    // Determine the mode
    $mode = isset($_GET['mode']) ? (int)$_GET['mode'] : 1;
    
    // Generate a new random token
    $token = bin2hex(random_bytes(16));
    // Set expiry to 5 minutes from now
    $expiry = time() + (5 * 60);
    
    $data = get_data();
    $data['active_token'] = $token;
    $data['token_expiry'] = $expiry;
    $data['mode'] = $mode;
    // We do NOT clear the pending_prompt here, only when it's fetched by the local poller
    save_data($data);
    
    echo json_encode(['success' => true, 'token' => $token, 'expiry' => $expiry, 'mode' => $mode]);
    exit;
}

if ($action === 'check_token') {
    $token = $_GET['token'] ?? '';
    $data = get_data();
    
    if ($token && $token === $data['active_token']) {
        if (time() <= $data['token_expiry']) {
            echo json_encode(['valid' => true, 'mode' => $data['mode'] ?? 1]);
            exit;
        } else {
            // Expired
            $data['active_token'] = null;
            save_data($data);
            echo json_encode(['valid' => false, 'error' => 'Token expired']);
            exit;
        }
    }
    echo json_encode(['valid' => false, 'error' => 'Invalid token']);
    exit;
}

if ($action === 'submit_prompt') {
    // Expecting POST data
    $input = json_decode(file_get_contents('php://input'), true);
    $token = $input['token'] ?? '';
    $prompt = $input['prompt'] ?? '';
    
    $data = get_data();
    
    if ($token && $token === $data['active_token'] && time() <= $data['token_expiry']) {
        if (!empty($prompt)) {
            $data['pending_prompt'] = $prompt;
            // Invalidate the token after successful submission
            $data['active_token'] = null;
            $data['token_expiry'] = 0;
            save_data($data);
            echo json_encode(['success' => true]);
            exit;
        } else {
            echo json_encode(['success' => false, 'error' => 'Empty prompt']);
            exit;
        }
    } else {
        echo json_encode(['success' => false, 'error' => 'Invalid or expired token']);
        exit;
    }
}

if ($action === 'poll_prompt') {
    // Local script calls this to check if a prompt was submitted
    $data = get_data();
    if (!empty($data['pending_prompt'])) {
        $prompt = $data['pending_prompt'];
        // Clear it so we don't process it twice
        $data['pending_prompt'] = null;
        save_data($data);
        echo json_encode(['has_prompt' => true, 'prompt' => $prompt]);
        exit;
    }
    echo json_encode(['has_prompt' => false]);
    exit;
}

echo json_encode(['error' => 'Invalid action']);
?>