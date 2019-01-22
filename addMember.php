<?php
//this file is only for building test subjects  messy but useful
 error_reporting( E_ALL );
$servername = "127.0.0.1";
	$username = "root";
	$password = "";
	$dbname = "members";

 
// Create connection
$conn = mysqli_connect($servername, $username, $password, $dbname);
// Check connection
if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}

$id1 = "741";
$last_name1 = "JustaTest";
$first_name1 = "Anyone";
$postal_code1 = "3122";
$membshipnum1 = "36654";
$end_date1 = "2018-01-01";
$status_id1 ="Disabled";
$status_name1 ="";

$sql = "INSERT INTO memberlocal (id, last_name, first_name, postal_code, membshipnum, end_date, status_id, status_name)
VALUES ('$id1','$last_name1','$first_name1','$postal_code1','$membshipnum1','$end_date1','$status_id1','$status_name1')";
//mysql_query($sql) or trigger_error(mysql_error()." in ".$sql);
if (mysqli_query($conn, $sql)) {
    echo "New record created successfully";
} else {
    echo "Error: " . $sql . "<br>" . mysqli_error($conn);
}


mysqli_close($conn);
?> 