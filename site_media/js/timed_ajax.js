var url = 'http://demos111.mootools.net/demos/Ajax_Timed/ajax_timed.php';
 
ar url = "/base/ajax/";
// refresh every 4 seconds
var timer = 4; 
// periodical and dummy variables for later use
var periodical, dummy; 
var start = $('start'), stop = $('stop'), log = $('log_res');
 
/* our ajax istance */
var ajax = new Ajax(url, { 
	update: log,
	method: 'get',
	onComplete: function() {
		// when complete, we remove the spinner
		log.removeClass('ajax-loading'); 
	},
	onCancel: function() {
		// when we stop timed ajax while it's requesting
		// we forse to cancel the request, so here we
		// just remove the spinner
		log.removeClass('ajax-loading'); 
	}
});
 
/* our refresh function: it sets a dummy to prevent 
   caching of php and add the loader class */
var refresh = (function() {
	// dummy to prevent caching of php
	dummy = $time() + $random(0, 100);
	// we add out fancy spinner
	log.empty().addClass('ajax-loading');
	// requests of our php plus dummy as query
	ajax.request(dummy); 
}); 
 
// start and stop click events
start.addEvent('click', function(e) {
	// prevent default
	new Event(e).stop(); 
	// prevent insane clicks to start numerous requests
	$clear(periodical); 
 
	/* a bit of fancy styles */
	stop.setStyle('font-weight', 'normal');
	start.setStyle('font-weight', 'bold');
	log.empty().addClass('ajax-loading'); 
	/* ********************* */
 
	// the periodical starts here, the * 1000 is because milliseconds required
	periodical = refresh.periodical(timer * 1000, this); 
 
	// this is the first only request, later on will be only the periodical and refresh 
	// that do the request. If we don't do this way, we have to wait for 4 seconds before 
	// the first request.
	ajax.request($time()); 
});
 
stop.addEvent('click', function(e) {
	new Event(e).stop(); // prevent default;
 
	/* a bit of fancy styles 
	   note: we do not remove 'ajax-loading' class
             because it is already done by 'onCancel'
			 since we later do 'ajax.cancel()'
	*/
	start.setStyle('font-weight', 'normal');
	stop.setStyle('font-weight', 'bold');
	/* ********************* */
 
	// let's stop our timed ajax
	$clear(periodical); 
	// and let's stop our request in case it was waiting for a response
	ajax.cancel(); 
});
