<nav class="navbar navbar-default navbar-fixed-top">
	<div class="container-fluid">
		<!-- Brand and toggle get grouped for better mobile display -->
		<div class="navbar-header">

			<a class="navbar-brand" rel="home" href="index.php" title="MDPDP">
			    <img src="android-chrome-36x36.png" class="navbar-brand" style="padding:0px 0px 32px 15px;">
					DPDP <small style="font-size:7px;">designed by ikko</small>
			</a>
		</div>

		<!-- Collect the nav links, forms, and other content for toggling -->
		<ul class="nav navbar-nav">
			<?php if (basename($_SERVER['PHP_SELF'],'.php')=='index'){echo "<li class='active'>"; } else { echo "<li>"; } ?>
			<a href="index.php">Dashboard <span class="sr-only">(current)</span></a></li>
			<li><a href="http://<?php echo $_SERVER['SERVER_ADDR']; ?>:5000/">Analysis</a></li>

			<?php if (basename($_SERVER['PHP_SELF'],'.php')=='uploader'){echo "<li class='active'>"; } else {echo "<li>"; } ?>
			<a href="uploader.php">Upload CSV</a></li>
		</ul>
		<div class="navbar-right navbar-form">
 			<form role='search' method='get' action='search.php'>
				<i class="axi axi-calendar"></i>
				<div class='form-group'>
					<input type='text' name='daterange' id='daterange' class='form-control'>
				</div>
			</form>
		</div>

	</div><!-- /.container-fluid -->
</nav>
