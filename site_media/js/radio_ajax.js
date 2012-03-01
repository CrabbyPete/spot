/* 
Radio button javascript. When a user clicks on a button an Ajax request is sent to the server to change how 
the user follows a friend or group: requires Mootools
*/
function radioToolTip( el ){
	var form = $(el)
	form.set('style', { 'display': 'block' } );
  
	return form;
}

function radioComplete( response ) {
	var x = response;
}

var TRUE = '/true/';
var FALSE = '/false/'
function radioRequest(form, el) {
	var xhr = new Request (
			{
				url: '/base/ajaxradio/',
				method: 'POST',
				onComplete: radioComplete
			}
		);
		
		xhr.send(whatButton(form));
		var element = $(el)
		var oldForm = $(el).getElement('form');

		for (var i = 0; i < form.radiobutton.length; i++) {
			oldForm.radiobutton[i].checked = form.radiobutton[i].checked;
		}
		
		var inner = oldForm.get('html');
		oldForm.set('html',inner);
	
		return;
}

function whatButton(form) {
	var local;
	for (var i = 0; i < form.radiobutton.length; i++) {
		if(form.radiobutton[i].checked) {
		    local = form.radiobutton[i].value;
            break;
        }
	}
	who = '&' + escape(form.who.value) + '=';
	qstr = 'button=' + escape(local)+ who + escape(form.follow.value);

   return qstr;
}
