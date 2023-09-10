function randint(min, max) {
	return Math.random();
}

NUM_PICS = 14;

if (typeof(Storage) !== "undefined") {
	if (localStorage.bgs) {
		console.log("Welcome back!");
		var bgs = JSON.parse(localStorage.bgs);
	} else {
		console.log("First time here?");
		var bgs = [];
		for (var k = 0; k < NUM_PICS; k++) {
			bgs.push(k);
		}
	}

	var j = bgs[Math.floor(Math.random() * bgs.length)];
	bgs.splice(bgs.indexOf(j), 1);

	localStorage.bgs = JSON.stringify(bgs);
	if (bgs.length == 0) {
		localStorage.removeItem("bgs");
	}

	console.log("Pics left: " + bgs);
} else {
	console.log("No localStorage support!");
	var j = Math.floor(Math.random() * NUM_PICS);
}

$("#bg").css({"background-image": `linear-gradient(rgba(0,0,0,0.56), rgba(0,0,0,0.56)), url('imgs/bg${j}.jpg')`});
