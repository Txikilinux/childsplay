<?php include("breadcrumbs.php"); ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"><!-- InstanceBegin template="/Templates/template.dwt" codeOutsideHTMLIsLocked="false" -->
<head>
<!--<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />--> 
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1 "> 
<meta name="author" content="Stas Zytkiewicz">

<meta name="description" content="Childsplay is a collection of educational activities for young children and runs on Windows, OSX, and Linux. Childsplay can be used at home, kindergartens and pre-schools.">

<meta name="keyword" content="educational, activity, games, young, children, windows, mac, osx, linux, ubuntu, redhat, suse, fun, learning, math, spelling, language, schools, kindergarten, pre-schools">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<!-- InstanceBeginEditable name="doctitle" -->
<title>Childsplay</title>
<link href="css/stylesheet.css" rel="stylesheet" type="text/css" /> 
<!-- InstanceEndEditable -->
<!-- InstanceBeginEditable name="head" -->
<!-- InstanceEndEditable -->
<link href="css/stylesheet.css" rel="stylesheet" type="text/css" />
</head>

<body>
<div id="wrapper">
	<div id="center">
    	<div id="header-wrapper">
            <div id="header"></div>  
            <div id="menu">
                <div class="menu-item"><a href="index.php">Home</a></div>
                <div class="divider"><img src="images/clear.gif" width="1" height="1" /></div>
                <div class="menu-item"><a href="screenshots.php">Screenshots</a></div>
                 <div class="divider"><img src="images/clear.gif" width="1" height="1" /></div>
                <div class="menu-item"><a href="translations.php">Translations</a></div>
                 <div class="divider"><img src="images/clear.gif" width="1" height="1" /></div>
                <div class="menu-item"><a href="wiki.php">Wiki</a></div>
                <div class="divider"><img src="images/clear.gif" width="1" height="1" /></div>
                <div class="menu-item"><a href="contact.php">Contact</a></div>
            </div>
         </div><!-- end header wrapper -->





<div id="download">
    <div class="download-logo"><a href="osx.php"><img src="images/logo_apple.png" width="60" height="60" border="0" /></a></div>
    <div class="download-logo"><a href="http://sourceforge.net/projects/schoolsplay/files/childsplay_sp/">
    <img src="images/logo_linux.png" width="60" height="60" border="0" /></a>
    </div>
    <div class="download-logo"><a href="http://sourceforge.net/projects/schoolsplay/files/childsplay_sp-win32"><img src="images/logo_windows.png" width="60" height="60" border="0" /></a>
    </div><!-- end download-logo -->
</div><!-- end download -->

<div id="breadcrumbs">Home | <?php if(curPageName() != "Home") {echo curPageName();} ?> </div>
<div id="content">

<!-- InstanceBeginEditable name="content" -->
<h1>What's Childsplay</h1> 
<p>Childsplay is a collection of educational activities for young children and runs on Windows, OSX, and Linux.</p>
<p>Childsplay can be used at home, kindergartens and pre-schools.</p>
<p>Childsplay is a fun and save way to let young children use the computer and at the same time teach them a little math, letters of the alphabeth, spelling, eye-hand coordination etc.</b>
</p>
<p>Childsplay is part of the schoolsplay.org project.</p>
<p><b>Main menu</b><br>
<a href="images/screenshots/CP_menu_big.gif"><img src="images/screenshots/CP_menu_small.gif"/></a>
</p>
<h2 id="toc2"><span>Features</span></h2>
<p>Childsplay provides several features for users and developers of activities:</p>
<ul>
<li>memory activities that are fun to play and at the same time learn sounds, images, letters and numbers.</li>
<li>activities that train the child to use the mouse and keyboard.</li>
<li>pure game activities like puzzles, pong, pacman and billiards.</li>
<li>multilingual support, even right to left languages (via <a href="http://www.pango.org/" onclick="window.open(this.href, '_blank'); return false;">Pango</a>).</li>
<li>solid data logging to monitor the children's progress; locally (<a href="http://www.sqlite.org/" onclick="window.open(this.href, '_blank'); return false;">SQLite</a>) or over network (<a href="http://www.mysql.com/" onclick="window.open(this.href, '_blank'); return false;">MySQL</a> or any other db supported by <a href="http://www.sqlalchemy.org/" onclick="window.open(this.href, '_blank'); return false;">SQLAlchemy</a>).</li>
<li>set of <a href="http://www.openoffice.org/" onclick="window.open(this.href, '_blank'); return false;">OpenOffice</a> reports to print this data (still in development state).</li>
<li>object oriented framework for easy activity development in Python/PyGame.</li>
<li>good support by the developers and translators.</li>
</ul>

<!-- InstanceEndEditable --></div>
<div id="donate">
	<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
	<input type="hidden" name="cmd" value="_s-xclick">
	<input type="hidden" name="hosted_button_id" value="4DMCUYT3NPJEJ">
	<input type="image" src="https://www.paypalobjects.com/en_US/NL/i/btn/btn_donateCC_LG.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
	<img alt="" border="0" src="https://www.paypalobjects.com/nl_NL/i/scr/pixel.gif" width="1" height="1">
	</form>
	<div id="donate-text"><p>Support is voluntary, after all the Schoolsplay project is completely free-software!
    If you want to support us, please make a donation with PayPal.</p></div>
    <!-- end donate text -->
</div><!-- end donate -->

<div id="footer">
<img style="margin-left:70px;" src="images/liner.png" width="540" height="12" /><br />Schoolsplay.org 2011
<a href="http://sourceforge.net/projects/schoolsplay"><img src="http://sflogo.sourceforge.net/sflogo.php?group_id=181294&amp;type=8" width="80" height="15" alt="Get schoolsplay at SourceForge.net. Fast, secure and Free Open Source software downloads" /></a></div><!-- end footer -->

</div><!-- end center div -->
</div>
</body>
<!-- InstanceEnd --></html>
