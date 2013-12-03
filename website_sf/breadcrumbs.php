<?php
function curPageName() {
 $page = substr($_SERVER["SCRIPT_NAME"],strrpos($_SERVER["SCRIPT_NAME"],"/")+1);
	if( $page == "screenshots.php")
	{
		return "Screenshots";
		
	}
	if( $page == "translations.php")
	{
		return "Translations";
	}
	if( $page == "wiki.php")
	{
		return "Wiki";
	}
	if( $page == "contact.php")
	{
		return "Contact";
	}
	if($page == "index.php")
	{
		return "Home";
	}
}
?>
