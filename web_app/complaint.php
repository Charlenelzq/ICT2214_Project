<?php
session_start();

if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) {
    header('Location: index.php');
    exit;
}

// Get the file from URL parameter without any validation
$filename = $_GET['file'];

// Directly use the filename from the URL parameter
$filepath = "/var/www/uploads/" . $filename;

// Check if file exists
if (file_exists($filepath)) {
    // Check if the file is an image
    $file_info = finfo_open(FILEINFO_MIME_TYPE);
    $mime_type = finfo_file($file_info, $filepath);
    finfo_close($file_info);

    if (strpos($mime_type, 'image') === 0) {
        // Set the appropriate content-type header for images
        header('Content-Type: ' . $mime_type);
        // Get the file content
        readfile($filepath);
    } else {
        // Include the file content for other types (e.g., PHP files)
        include($filepath);
    }
    exit;
} else {
    echo "File not found.";
}

?>