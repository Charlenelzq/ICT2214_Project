<?php
session_start();

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $user = $_POST['username'];
    $pass = $_POST['password'];
    $pass = hash('sha256', $pass);

    // Database connection parameters
    $servername = "localhost";
    $username = "admin";
    $password = "password123";
    $dbname = "app_db";

    // Create connection
    $conn = new mysqli($servername, $username, $password, $dbname);

    // Check connection
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    // Prepare and bind
    $stmt = $conn->prepare("SELECT password FROM users WHERE username = ?");
    $stmt->bind_param("s", $user);
    $stmt->execute();
    $stmt->bind_result($hashed_password);
    $stmt->fetch();
    $stmt->close();
    $conn->close();

    // Verify password
    if ($pass == $hashed_password) {
        $_SESSION['username'] = $user;
        $_SESSION['loggedin'] = true;
        header("Location: home.php");
    } else {
        header("Location: index.php?error=1");
    }
}
?>