/* 
Radio button javascript. When a user clicks on a button an Ajax request is sent to the server to change how 
the user follows a friend or group: requires Mootools


<div class=tooltip> Follow friend by:
	<center>
		<div class=tootipcontent>
			<form>
				<label>E-mail</label>
				<input class="spacer" name="radiobutton" type="radio" value="email" onclick="radioRequest(this.form,'tip{{friend.friend.pk}}')" {% ifequal friend.follow 'email' %}  checked="true" {% endifequal %}/>
				<label>Phone</label>
				<input  class="spacer" name="radiobutton" type="radio" value="phone" onclick="radioRequest(this.form,'tip{{friend.friend.pk}}')" {% ifequal friend.follow 'phone' %}  checked="true"{% endifequal %}/>
				<label>None</label>
				<input   class="spacer" name="radiobutton" type="radio" value="None" onclick="radioRequest(this.form,'tip{{friend.friend.pk}}')" {% ifequal friend.follow 'None' %}   checked="true"{% endifequal %}/>						
				<input name = "who" type = "hidden", value = "friend" />
				<input name = "follow" type = "hidden", value = "{{friend.friend.pk}}" />
			</form>
		</div>
	</center>
</div>
*/
 
var friendFollow = new Class({
    Implements: [Events],
	radioMenu: new Element('div',{'class':'tooltip'}),
		
	/* Create the menu as a tooltip */
	initialize: function(){
		var form = new Element('form');
		form.adopt( new Element('label',{text:'E-Mail'});
		form.adopt( new Element('input',{'class':'spacer', name:'radiobutton',value:'email'}));
		form.adopt( new Element('label',{text:'Phone'});
		form.adopt( new Element('input',{'class':'spacer', name:'radiobutton',value:'phone'}));
		form.adopt( new Element('label',{text:'Don't'});
		form.adopt( new Element('input',{'class':'spacer', name:'radiobutton',value:'None'}));
		form.adopt( new Element('input',{type:'hidden', name:'who',value:'friend'}));
		form.adopt( new Element('input',{type:'hidden', name:'follow',value:'0'}));
		
		var div = new Element('div',{'class':'tooltipcontent'} );
		div.adopt(form);
		
		var center = new Element('center');
		center.adopt(div);
		this.radioMenu.adopt(center);
	},

	radioToolTip function ( pk, checked ){
		var form = radioMenu.$(form);
		if ( checked == 'email' ){
	},
});

/**


function radioComplete( response ) {
	var x = response;
}
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
**/