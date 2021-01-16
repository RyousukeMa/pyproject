$(function() {
	console.log('script.js');
	console.log('------------------------signin.html-------------------------');
	$('#signinbutton').on('click', function(){
		$('#signinbox, #background').fadeIn();
	});
	$('#closebutton, #background').on('click', function(){
		$('#signinbox, #background').fadeOut();
	});
	console.log('------------------------work.html---------------------------');
	//--------------------------------------------------------------------------
	//
	// ajax勉強
	//
	var data_ary;
	$.ajax({
		url: "/open_warehouse.json",
		type: "get",
		datatype: "json",
		success : function(data) {
			// data_ary = data.split(":");
			// data = JSON.parse(data);
			// console.log(data);
		},
		error:function(XMLHttpRequest, textStatus, errorThrown){
			alert("ajax通信失敗 やり直し");
			// console.log("XMLHttpRequest : " + XMLHttpRequest.status);
			// console.log("textStatus     : " + textStatus);
			// console.log("errorThrown    : " + errorThrown.message);
		}
	})
	// console.log('↓data_ary');
	// console.log(data_ary);
	$("#display").click(function() {
		$(".result").empty();
		var totalNumber = data_ary.length;
		var count = 0;
		for(var i = 0; i < totalNumber-1; i++) {
			var row = data_ary[i];
			var cell = row.split("\t");
			// console.log(row);
			$(".result").append("<tr><td>" + cell[0] + "</td><td>" + cell[1] + "</td></tr>");
			count = count + 1;
		}
		$(".hit").text(count + "件のデータを表示しました。");
		// console.log(data_ary);
	});
	//
	// workspace ajaxTest
	//
	// var ajaxTest;
	// $.ajax({
	// 	url: "open_warehouse.py",
	// 	type: "get",
	// 	success : function(data) {
	// 		ajaxTest = data.split("\n");
	// 	},
	// 	error:function(data) {
	// 		alert("失敗")
	// 	}
	// })
	//

	//--------------------------------------------------------------------------
	// indy
	//--------------------------------------------------------------------------
	//
	// drawermenu
	//
	$('.icon').on('click', function() {
		$(this).addClass('open');
		$('.hamburger_list').addClass('open');
		$("#overlay").fadeIn("slow");
	});
	$("#overlay").on('click',function() {
		$('.icon,.hamburger_list').removeClass('open');
		$('#overlay,.dialog').fadeOut();
	});
	//
	// dialog
	//
	$('#dialogbutton').on('click', function() {
		$('.dialog,#overlay').fadeIn();
	});
	$('#closebutton').on('click', function() {
		$('#overlay,.dialog').fadeOut();
	});
	//
	// dialogタグ
	//
	var element = document.getElementById("hoge");
	console.log(element);
	$('#foo').on('click',function(){
		console.log('------');
		console.log(element);
		$('#hoge').fadeIn();
	});
	$('#close').on('click',function(){
		$('#hoge').fadeOut();
	});
	// element.showModal();
	//
	// タブ切り替え
	//
	$('.left').on('click', function() {
		$(this).addClass('selected');
		$('.center,.right').removeClass('selected');
	});
	$('.center').on('click', function() {
		$(this).addClass('selected');
		$('.left,.right').removeClass('selected');
	});
	$('.right').on('click', function() {
		$(this).addClass('selected');
		$('.left,.center').removeClass('selected');
	});
	//
	// タブ切り替え(admin/users)
	//
	$('.user_tab').on('click', function(){
		$(this).addClass('selected');
		$('.delete_tab').removeClass('selected');
	});
	$('.delete_tab').on('click', function(){
		$(this).addClass('selected');
		$('.user_tab').removeClass('selected');
	});
	//
	// ajax
	//
	var indy_ajax;
	$.ajax({
		url: "data/test.json",
		type: "get",
		datatype: "json",
		success : function(data) {
			// data_ary = data.split(":");
			// data = JSON.parse(data);
			// data_ary = data.split(":");
			// console.log(JSON.parse(data));
			// console.log(data);
			var indy_ajax = data;
		},
		error:function(XMLHttpRequest, textStatus, errorThrown){
			alert("ajax通信失敗 やり直し");
			// console.log("XMLHttpRequest : " + XMLHttpRequest.status);
			// console.log("textStatus     : " + textStatus);
			// console.log("errorThrown    : " + errorThrown.message);
		}
	});
	$(".left").click(function() {
		$(".tub_content").empty().append("<p>" + indy_ajax + "</p>");
		// var totalNumber = data_ary.length;
		// var count = 0;
		// for(var i = 0; i < totalNumber-1; i++) {
		// 	var row = data_ary[i];
		// 	var cell = row.split("\t");
		// 	// console.log(row);
		// 	$(".result").append("<tr><td>" + cell[0] + "</td><td>" + cell[1] + "</td></tr>");
		// 	count = count + 1;
		// }
		// $(".hit").text(count + "件のデータを表示しました。");
		// console.log(data_ary);
	});
});
