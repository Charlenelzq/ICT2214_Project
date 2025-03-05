<?php
session_start();

if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) {
    header('Location: index.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        header {
            background-color: #333;
            color: #fff;
            padding: 1em 0;
            text-align: center;
        }
        nav {
            background-color: #444;
            overflow: hidden;
        }
        nav a {
            float: left;
            display: block;
            color: #fff;
            text-align: center;
            padding: 14px 16px;
            text-decoration: none;
        }
        nav a:hover {
            background-color: #555;
        }
        main {
            padding: 2em;
        }
        section {
            background-color: #fff;
            padding: 2em;
            margin: 2em auto;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            max-width: 600px;
        }
        form div {
            margin-bottom: 1em;
        }
        label {
            display: block;
            margin-bottom: 0.5em;
        }
        textarea {
            width: 100%;
            padding: 0.5em;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        input[type="file"] {
            border: none;
        }
        button {
            background-color: #333;
            color: #fff;
            padding: 0.75em 1.5em;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #555;
        }
        footer {
            text-align: center;
            padding: 1em 0;
            background-color: #333;
            color: #fff;
            position: fixed;
            width: 100%;
            bottom: 0;
        }
    </style>
</head>
<body>
    <header>
        <h1>Welcome to Our Complaint Portal</h1>
    </header>
    <nav>
        <a href="index.php">Home</a>
        <a href="past_complaints.php">Past Complaints</a>
    </nav>
    <main>
        <section>
            <h2>Submit Your Complaint</h2>
            <form action="submit_complaint.php" method="post" enctype="multipart/form-data">
                <div>
                    <label for="complaint">Complaint:</label>
                    <textarea id="complaint" name="complaint" rows="4" ></textarea>
                </div>
                <div>
                    <label for="attachment">Attach a picture:</label>
                    <input type="file" id="attachment" name="attachment" accept="image/*">
                </div>
                <div>
                    <button type="submit">Submit</button>
                </div>
            </form>
        </section>
    </main>
    <footer>
        <p>&copy; 2025 Your Company. All rights reserved.</p>
    </footer>
</body>
</html>