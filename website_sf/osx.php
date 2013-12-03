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
    <div class="download-logo"><a href="osx.html"><img src="images/logo_apple.png" width="60" height="60" border="0" /></a></div>
    <div class="download-logo"><a href="http://sourceforge.net/projects/schoolsplay/files/childsplay_sp/">
    <img src="images/logo_linux.png" width="60" height="60" border="0" /></a>
    </div>
    <div class="download-logo"><a href="http://sourceforge.net/projects/schoolsplay/files/childsplay_sp-win32"><img src="images/logo_windows.png" width="60" height="60" border="0" /></a>
    </div><!-- end download-logo -->
</div><!-- end download -->

<div id="breadcrumbs">Home | <?php if(curPageName() != "Home") {echo curPageName();} ?> </div>
<div id="content">

<!-- InstanceBeginEditable name="content" -->
<h1>OSX</h1> 
      <p>Unfortunately there is no OS X package of the new Childsplay (>= 0.99) at the moment. We are working on it.</p>
      <p>However, if you really like to test some activities, you can download the OS X application bundle of the
 'old' Childsplay package at Sourceforge: <a href="http://downloads.sourceforge.net/childsplay/Childsplay-0.85.1_1.dmg?use_mirror= Childsplay-0.85.1_1">Childsplay-0.85.1_1</a></p>
<p>
There are some problems with it, we know ;-)
</p>
<p>
Main problem is that although all languages are in it, they are not displayed.<br>
Easiest solution is to open a terminal in the location where Childsplay is copied and type:
<br>
LANG=nl_BE.utf8 LANGUAGE=nl_BE.utf8 childsplay_sp
<br>
where you replace nl_BE with your locale.
</p>
<p>
If you want to speed up development of Childsplay on OSX, please send me an email to encourage me!
We receive almost no feedback on OSX, so some encouraging words would be nice :-)</p>
<p>
Mails can be send to chris.van.bael@gmail.com
</p><!-- InstanceEndEditable --></div>
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
