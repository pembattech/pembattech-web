jQuery(window).on('scroll', function() {
	// stop telling people to scroll when they're scrolled
	var window_offset = jQuery(window).scrollTop() - jQuery('body').offset().top;

	if (window_offset > 10) {

		jQuery('.scroll-indicator').addClass('off');

	} else {

		jQuery('.scroll-indicator').removeClass('off');

	}

});