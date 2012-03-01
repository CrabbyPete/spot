
	var req;
	var url = "/base/ajax/"

	function onPageLoad(func) 
	{
		if(window.addEventListener && !window.opera) 
			window.addEventListener('load', func, false)
		else if(window.attachEvent) 
			window.attachEvent('onload', func)
		else 
		{
			var o=window.onload
			window.onload = function() { o ? o() : o;func() }
		}
		return
	}
	
    function loadJSON()
	{
		if (window.XMLHttpRequest)
		{
			req = new XMLHttpRequest();
			req.onreadystatechange = processReqChange;
			req.open('GET',url, true);
			req.send(null);
		}
		else if (window.ActiveXObject)
		{
			if (req = new ActiveXObject("Microsoft.XMLHTTP") )
			{
				req.onreadystatechange = processReqChange;
				req.open("GET", url, true);
				req.send(null);
			}
        }
    }

	function processReqChange()
	{
		if (req.readyState == 4)
		{
			if (req.status == 200)
				setDataJSON(req)
         }
    }

	function setDataJSON(req)
	{
		var data = eval('(' + req.responseText + ')');
		// <img src="images/user_sent1.jpg" width="253" height="380" />	
		var div = document.getElementById("tourpic")
		var img = document.createElement('img');
		img.src = '/site_media/'+data[0].fields.image;
		img.height = 253
		img.width = 253
		div.appendChild(img)
	}

	onPageLoad( loadJSON );