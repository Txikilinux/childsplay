

// (c) dynarch.com 2003
// Author: Mihai Bazon, http://dynarch.com/mishoo/

if (/MSIE [56].*Windows/.test(navigator.userAgent)) (function() {
	var blank = new Image;


// OPGELET: DE PLAATSING VAN DE SPACER.GIF MOET NAAR EEN ABSOLUUT PAD VERWIJZEN

	blank.src = 'http://www.mintjens.be/website/images/spacer.gif';

	var imgs = document.getElementsByTagName("img");
	for (var i = imgs.length; --i >= 0;) {
		var img = imgs[i];
		var src = img.src;

		if (!/\.png$/.test(src))
			continue;
		var s = img.runtimeStyle;
		s.width = img.offsetWidth + "px";
		s.height = img.offsetHeight + "px";
		s.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + src + "',sizingMethod='scale')";
		img.src = blank.src;
	}
})();

