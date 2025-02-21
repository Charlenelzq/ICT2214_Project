<html>
<body>
<?php
session_start();

if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) {
    header('Location: index.php');
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


$username = $_SESSION['username'];


$sql = "SELECT complaintID FROM user_complaints WHERE user = ?";
$stmt1 = $conn->prepare($sql);
$stmt1->bind_param("s", $username);
$stmt1->execute();
$result = $stmt1->get_result();


if ($result->num_rows > 0) {
    echo "<table>";
    echo "<tr><th>Complaint ID</th><th>Complaint</th></tr>";
    while ($row = $result->fetch_assoc()) {
        # Use the complaintID to get the complaint text
        $sql2 = "SELECT Complaint, File FROM complaints WHERE idcomplaints = ?";
        $stmt2 = $conn->prepare($sql2);
        $stmt2->bind_param("i", $row['complaintID']);
        $stmt2->execute();
        $complaint_info = $stmt2->get_result();
        $complaint = $complaint_info->fetch_assoc();

        echo "<tr>";
        echo "<td>" . $row['complaintID'] . "</td>";
        echo "<td><a href='complaint.php?file=" . $complaint['File'] . "'>" . $complaint['Complaint'] . "</a></td>";
        echo "</tr>";
    }
    echo "</table>";
} else {
    echo "No complaints found.";
}

$stmt1->close();
$stmt2->close();
$conn->close();
?>
</body>
</html>