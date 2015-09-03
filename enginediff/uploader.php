<?php
include_once("common/lib.php");
?>



<!DOCTYPE html>

<html>
<head>
	<?php include ('common/headers.php'); ?>
</head>
<body>
<?php include ('common/nav.php'); ?>
<div class="container">
	<div class="row">
		<div class="col-xs-12">
			<h2><i class="axi axi-upload"></i> Upload CSV</h2>
		</div>
		<div class="col-xs-6 col-xs-offset-3">
			<!-- Progress-bar is supported in FF3.6+, Chrome6+, Safari4+ -->
			<div id="file-uploader">		
				<noscript>			
					<p>Please enable JavaScript to use file uploader.</p>
					<!-- or put a simple form for upload here -->
				</noscript>         
			</div>
			<h6>Drag-and-drop is supported in FF, Chrome.</h6>
		</div>
	</div>
	<div class="row">
		<div class="col-xs-12">
			<pre id="result">Converted JSON Data will be displayed here.</pre>
		</div>
	</div>

	<div class="row">
		<div class="col-xs-12">
			<h2><i class="axi axi-frown-o"></i> Drop all data</h2>
		</div>
		<div class="col-xs-12">
			<p class=" text-align-cetner">
				<button class="btn btn-danger" id='resetBtn'><i class="axi axi-ion-fireball"></i> Clean up all data</button>
			</p>
			<div id="alertMessage"></div>
		</div>
	</div>
</div> <!-- end of container-->
<script src="js/fileuploader.js" type="text/javascript"></script>
<script>        

	// function ajax_on_complete_handler(data, status) {
	// 	if(status == "success" && data!="") {
	// 		//$("#result").text(data.replace(/\r\n/g,EOL));
	// 	}		
	// }

	function createUploader(){
		var uploader = new qq.FileUploader({
			element: document.getElementById('file-uploader'),
			action: 'uploader/upload.php',
			debug: false,
			onComplete: function(id, fileName, responseJson) {
				// console.log(id);
				// console.log(fileName);
				console.log(responseJson);
				if(responseJson["success"]==true) {
					console.log("success");

					//document.getElementById('result').innerHTML=JSON.stringify(responseJson['contents'],undefined,2);//.replace(/\r\n/g,EOL));
					$('#result').html(JSON.stringify(responseJson['contents']));
					// $.get("dynamic_update.php?id="+$("#user_file_list>tbody>tr>td").first().html(), ajax_on_complete_handler);
				}
			},
		});     
	};

	// in your app create uploader as soon as the DOM is ready
	// don't wait for the window to load  
	window.onload = createUploader;

	$(document).ready(function(){
		$('#resetBtn').on('click',function() {
			if(confirm("This will DESTROY all data.\nAre you sure?")){
				$.ajax({
					url:"clear.php?confirm=true",
					dataType:"json",
					success: function(data) {
						if (data.ok==1) {
							console.log(data);
							$('#alertMessage').attr('class', 'alert alert-success alert-dismissible');
							// $('#alertMessage').html(data.nIndexesWas.toString()+" "+data.msg);
							$('#alertMessage').html("Data is dropped successfully.");
						} else {
							$('#alertMessage').attr('class', 'alert alert-warning alert-dismissible');
							$('#alertMessage').html(data.errmsg);
						}
					}
				});
			}
		});
	});

   </script>
   <?php include('common/footer.php'); ?>
</body>
</html>
