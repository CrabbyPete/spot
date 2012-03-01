	function jsonComplete( json ) {
		path = '/site_media/'+ json[0].fields.image;
		photo = new Element( 'img',{'src': path} );
		var picture = $('bigpicture');
		if ( picture.getElement('img') ){
			var img = picture.getElement('img');
			img.src = path;
		}
		else	
			picture.adopt(photo);
	}
	
	function jsonRequest() {
		var xhr = new Request.JSON
		(
			{
				url: '/base/ajax/',
				method: 'GET',
				onComplete: jsonComplete
			}
		);
		xhr.send(null);
	}
	
	window.addEvent('domready', function(){ jsonRequest(); jsonRequest.periodical(60000)} );