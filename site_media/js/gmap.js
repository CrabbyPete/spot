
var geocoder;
var marker;
var map;

function form_coord(lat, lng) {
    var la = document.getElementsByName('lati');
    la[0].value = lat;
    var ln = document.getElementsByName('lngi');
    ln[0].value = lng;
}


function dragend_handle() {
    var point = marker.getPoint();
    map.panTo(point);
    document.getElementById("lat").innerHTML = point.lat().toFixed(5);
    document.getElementById("lng").innerHTML = point.lng().toFixed(5);
    form_coord(point.lat().toFixed(5), point.lng().toFixed(5));
 }

function moveend_handle() {
    map.clearOverlays();
    var center = map.getCenter();
    marker = new GMarker(center, {draggable: true});

    map.addOverlay(marker);
    document.getElementById("lat").innerHTML = center.lat().toFixed(5);
    document.getElementById("lng").innerHTML = center.lng().toFixed(5);

    GEvent.addListener(marker, "dragend", dragend_handle);
	form_coord(point.lat().toFixed(5), point.lng().toFixed(5));
}

function showLatLong( latitude, longitude ) {
	mp = document.getElementById("map")
    map = new GMap2(mp);
    map.addControl(new GSmallMapControl());
    map.addControl(new GMapTypeControl());

    var point = new GLatLng(latitude, longitude);
    map.setCenter(point, 14);
    marker = new GMarker(point, {draggable: true});

    document.getElementById("lat").innerHTML = point.lat().toFixed(5);
    document.getElementById("lng").innerHTML = point.lng().toFixed(5);
    map.addOverlay(marker);

    GEvent.addListener(marker, "dragend", dragend_handle );
    GEvent.addListener(map, "moveend", moveend_handle );
}


function showAddress(address, zoom) {
    if (zoom === undefined)
		zoom = 14;
	map = new GMap2(document.getElementById("map"));
    map.addControl(new GSmallMapControl());
    map.addControl(new GMapTypeControl());
    geocoder = new GClientGeocoder();
    geocoder.getLatLng( address,
            function(point)
            {
                if (!point) {
                    alert(address + " not found");
                }
                else {
                    document.getElementById("lat").innerHTML = point.lat().toFixed(5);
                    document.getElementById("lng").innerHTML = point.lng().toFixed(5);
                    map.clearOverlays()
                    map.setCenter(point, zoom);
                    marker = new GMarker(point, {draggable: true});
                    map.addOverlay(marker);

                    GEvent.addListener(marker, "dragend", dragend_handle );
                    GEvent.addListener(map, "moveend", moveend_handle );
                }
            }
    );
}