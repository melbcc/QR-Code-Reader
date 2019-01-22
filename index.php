<?php
//debugging use only strip out before launch!!
error_reporting( E_ALL );
/*
To Do List
Create html pretty output
-Gain string ???
//-Get no. from string
//-Look up database
//-Get user values from database
//Compare end date
-Format and display values -- add user to meeting table
*/
	
$string = 'https://melbpc.com.au/QRcheck/client_id=517';
//strip out all that is not decimal
$newstr = preg_replace('/[^0-9]/', '', $string);
echo $newstr;
echo "</br>";
//need year month day -matchy matchy
$todayD = date("Y\-m\-d ");
echo $todayD;
echo "</br>";


  //test purposes, uses localhost - would store this in diff file and call if security concerns!!
	$servername = "127.0.0.1";
	$username = "root";
	$password = "";
	$dbname = "members";
	
//mysqli for php5
   $conn = new mysqli($servername, $username, $password, $dbname);

   
   if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

//select all from database where qrID number exists
  $query = "SELECT * FROM memberlocal WHERE id ='$newstr'";
$res = mysqli_query($conn, $query); 
  if(mysqli_num_rows($res)>0) {
	while ($row = mysqli_fetch_array($res))  {
                     //echo $row[0];
					  echo "</br>";
					  
                      $qrID = $row[0];
					  echo $qrID;
					  echo "</br>";
					  //echo $CompanyID;
                      $lName = $row[1];
					  echo $lName ;
					  echo "</br>";
                      $fName = $row[2];
					  echo $fName;
					  echo "</br>";
                      $pCode = $row[3];
					  echo $pCode;
					  echo "</br>";
                      $mNo = $row[4];
					  echo $mNo;
					  echo "</br>";
                      $memEnd = $row[5];
					  echo $memEnd;
					  echo "</br>";
                      $StatID = $row[6];
					  echo $StatID;
					  echo "</br>";
					  $StatName = $row[7];
					  echo $StatName;
					  echo "</br>";
					   echo "</br>";
                    } 
          //check membership status by date compare  - did not really know what would be in database e.g. member status
		if(strtotime($memEnd) < strtotime($todayD)){
			echo "Membership is not current";
		}
		}
		else {
			echo "</br>";
	echo "Sorry no result could be found for this member";
}
		
		echo "</br>";
		//dump memory and connection  --Avoid using session due to possible memory constraints
		mysqli_free_result($res);
        $conn->close();   
	
	
?>