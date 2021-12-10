// Servo values
var slider = document.getElementById("servoRange");
var output = document.getElementById("servo");
output.innerHTML = slider.value;

slider.oninput = function() {
  output.innerHTML = this.value;
};
var slider2 = document.getElementById("servoRange2");
var output2 = document.getElementById("servo2");
output2.innerHTML = slider2.value;

slider2.oninput = function() {
  output2.innerHTML = this.value;
};

// PWM values
var slider3 = document.getElementById("pwmRange");
var output3 = document.getElementById("pwm");
output3.innerHTML = slider3.value;

slider3.oninput = function() {
  output3.innerHTML = this.value;
};
var slider4 = document.getElementById("pwmRange2");
var output4 = document.getElementById("pwm2");
output4.innerHTML = slider4.value;

slider4.oninput = function() {
  output4.innerHTML = this.value;
}

// Torvalds movement
$('#north').on('mousedown', function(){
	$.get('/north');
	});
$('#north').on('mouseup', function(){
	$.get('/stoptwo');
	});
$('#south').on('mousedown', function(){
	$.get('/south');
	});
$('#south').on('mouseup', function(){
	$.get('/stoptwo');
	});
$('#west').on('mousedown', function(){
	$.get('/west');
	});
$('#west').on('mouseup', function(){
	$.get('/stoptwo');
	});
$('#east').on('mousedown', function(){
	$.get('/east');
	});
$('#east').on('mouseup', function(){
	$.get('/stoptwo');
	});
$('#torvalds').on('mousedown', function(){
	$.get('/torvaldson');
	});
$('#torvalds').on('mouseup', function(){
	$.get('/torvaldsoff');
	});

// Linus movement
$('#linus').on('mousedown', function(){
	$.get('/linuson');
	});
$('#linus').on('mouseup', function(){
	$.get('/linusoff');
	});
$('#forward').on('mousedown', function(){
	$.get('/forward');
	});
$('#forward').on('mouseup', function(){
	$.get('/stop');
	});
$('#backward').on('mousedown', function(){
	$.get('/backward');
	});
$('#backward').on('mouseup', function(){
	$.get('/stop');
	});
$('#left').on('mousedown', function(){
	$.get('/left');
	});
$('#left').on('mouseup', function(){
	$.get('/stop');
	});
$('#right').on('mousedown', function(){
	$.get('/right');
	});
$('#right').on('mouseup', function(){
	$.get('/stop');
    });
