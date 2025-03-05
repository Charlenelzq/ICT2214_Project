<?php
session_start();

// Check if the user is logged in
if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) {
    header("Location: index.php");
    exit;
}

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

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $complaint_text = $_POST['complaint'];
    $target_dir = '/var/www/uploads/';
    $target_file = $target_dir . basename($_FILES["attachment"]["name"]);
    $uploadOk = 1;
    $imageFileType = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));

    // Check if image file is a actual image or fake image
    $check = getimagesize($_FILES["attachment"]["tmp_name"]);
    if ($check !== false) {
        $uploadOk = 1;
    } else {
        echo "File is not an image.";
        $uploadOk = 0;
    }

    // Check file size
    if ($_FILES["attachment"]["size"] > 500000) {
        echo "Sorry, your file is too large.";
        $uploadOk = 0;
    }

    // Allow certain file formats
    if ($imageFileType != "jpg" && $imageFileType != "png" && $imageFileType != "jpeg" && $imageFileType != "gif") {
        echo "Sorry, only JPG, JPEG, PNG & GIF files are allowed.";
        $uploadOk = 0;
    }

    // Check if $uploadOk is set to 0 by an error
    if ($uploadOk == 0) {
        echo "Sorry, your file was not uploaded.";
    } else {
        echo "Target file: " . $target_file . "<br>";

        if (move_uploaded_file($_FILES["attachment"]["tmp_name"], $target_file)) {
            // Prepare an insert statement
            $sql = "INSERT INTO complaints (Complaint, File) VALUES (?, ?)";

            if ($stmt = $conn->prepare($sql)) {
                // Bind variables to the prepared statement as parameters
                $stmt->bind_param("ss", $param_complaint_text, $param_complaint_image);

                // Set parameters
                $param_complaint_text = $complaint_text;
                $param_complaint_image = basename($_FILES["attachment"]["name"]);

                // Attempt to execute the prepared statement
                if ($stmt->execute()) {
                    echo "Complaint submitted successfully.";
                    echo "<br><a href='home.php'>Back to Home</a>";
                } else {
                    echo "Something went wrong. Please try again later.";
                }

                // Close statement
                $stmt->close();
            }

            # get the complaintID of the complaint that was just inserted
            $sql = "SELECT idcomplaints FROM complaints WHERE Complaint = ? AND File = ?";
            if ($stmt = $conn->prepare($sql)) {
                $stmt->bind_param("ss", $param_complaint_text, $param_complaint_image);
                $stmt->execute();
                $stmt->bind_result($complaintID);
                $stmt->fetch();
                $stmt->close();
            }

            # insert into user_complaints table
            $sql = "INSERT INTO user_complaints (user, complaintID) VALUES (?, ?)";
            if ($stmt = $conn->prepare($sql)) {
                $stmt->bind_param("si", $param_user, $param_complaintID);
                $param_user = $_SESSION['username'];
                $param_complaintID = $complaintID;
                $stmt->execute();
                $stmt->close();
            }

        } else {
            echo "Sorry, there was an error uploading your file.";
        }
    }

    // Close connection
    $conn->close();
}
?>