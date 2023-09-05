$(window).on("load", function() {
	IN_DELAY = 250;

	$('body').animate({"opacity": "1"}, IN_DELAY);

	$(".main").delay(IN_DELAY).animate({"opacity": "1"}, 750);
	//for (var i = 7; i >= 1; i--) {
	//	$(`.main> :nth-child(${i})`).delay(IN_DELAY + 125*i).animate({"opacity": "1"}, 500);
	//}
});
