
function scriptInit() {
if (!document.getElementById) {
	return;
	}
}

// Set up Event Listener - the script that allows us to use the addEvent call below

function addEvent(elm, evType, fn, useCapture) {
	if (elm.addEventListener) {
	elm.addEventListener(evType, fn, useCapture);
	return true;
	} else if (elm.attachEvent) {
	var r = elm.attachEvent('on' + evType, fn);
	return r;
	} else {
	elm['on' + evType] = fn;
	}
}

// Start Column Script

function setTall() {
	if (document.getElementById) {
		// the divs array contains references to each column's div element.  
		// Replace 'center' 'right' and 'left' with your own.  
		// Or remove the last one entirely if you've got 2 columns.  Or add another if you've got 4!
		var divs = new Array(document.getElementById('rightPanel'), document.getElementById('leftPanel'));
		
		// Let's determine the maximum height out of all columns specified
		var maxHeight = 0;
		for (var i = 0; i < divs.length; i++) {
			if (divs[i].offsetHeight > maxHeight) maxHeight = divs[i].offsetHeight;
		}
		
		// Let's set all columns to that maximum height
		for (var i = 0; i < divs.length; i++) {
			divs[i].style.height = maxHeight + 'px';

			// Now, if the browser's in standards-compliant mode, the height property
			// sets the height excluding padding, so we figure the padding out by subtracting the
			// old maxHeight from the new offsetHeight, and compensate!  So it works in Safari AND in IE 5.x
			if (divs[i].offsetHeight > maxHeight) {
				divs[i].style.height = (maxHeight - (divs[i].offsetHeight - maxHeight)) + 'px';
			}
		}
	}
}

/*
	Fire Events - you can add other scripts here and call them using the following method.  
	This one balances the columns when the page loads, and again when the window is resized
	Some have asked about users changing text size, because this script won't fire and your page can look weird.  If you were resizing text via a script, we could run this script when the user calls that script.  However, if you're relying on browser methods for text resizing, I'm not aware of a method to watch for that kind of an event.  If someone smarter than me knows of one, please let me know!  If you don't understand what I mean, then pretend I didn't say anything...
*/

addEvent(window, 'load', setTall, false);