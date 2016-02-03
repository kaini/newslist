"use strict"

var API = "_data"
var GLOBAL = {
	items: {},
	sources: {},
	xhrs: {},
}

function set_image_class() {
	var img = $(this)
	if (img.attr("class") == "article-image") {
		if (img.width() > 2 * img.height()) {
			img.attr("class", "article-image-w")
		} else {
			img.attr("class", "article-image-h")
		}
	}
}

function make_item_box(item, source) {
	var image = $("<img>").attr("src", item.image ? API + "/" + item.image + ".png" : "icons/" + source.id + ".png")
		                  .attr("alt", item.image ? item.title : source.name)
		                  .attr("class", item.image ? "article-image" : "article-image-dummy")
		                  .on("load", set_image_class)
    var source_image = null
    if (item.image) {
    	var source_image = $("<img>").attr("src", "icons/" + source.id + ".png")
    	                             .attr("alt", source.name)
    	                             .attr("class", "source-image")
    }
	var imagebox = $("<div>").attr("class", "image")
	                         .append(image)
	if (source_image) {
		imagebox.append(source_image)
	}

	var headera = $("<a>").text(item.title)
	                      .attr("href", item.url)
	var header = $("<h2>").append(headera)
	var summary = $("<p>").text(item.summary)
	var content = $("<div>").attr("class", "content")
	                        .append(header)
	                        .append(summary)

	var article = $("<article>").attr("lang", source.lang)
	                            .append(imagebox)
	                            .append(content)
	return article
}

function refresh_news_display() {
	var keys = []
	for (var key in GLOBAL.items) {
		keys.push(key)
	}
	// TODO sort?

	var item_count = 0
	var i = 0
	var has_hit = false
	var items_box = $("#items")
	items_box.empty()
	do {
		has_hit = false
		for (var k = 0; k < keys.length; ++k) {
			var item = GLOBAL.items[keys[k]][i]
			if (item) {
				has_hit = true
				++item_count
				var box = make_item_box(item, GLOBAL.sources[keys[k]])
				items_box.append(box)
			}
		}
		++i
	} while (has_hit)
	items_box.append($("<div>").attr("class", "clearfix"))
}

function source_changed() {
	var checkbox = $(this)
	var enabled = checkbox.is(":checked")
	var source_id = checkbox.attr("data-source-id")
	if (enabled) {
		console.log("Adding source " + source_id)
		fetch_source(source_id)
	} else {
		console.log("Removing source " + source_id)
		if (GLOBAL.xhrs[source_id]) {
			GLOBAL.xhrs[source_id].abort()
			delete GLOBAL.xhrs[source_id]
		}
		delete GLOBAL.items[source_id]
		refresh_news_display()
	}
}

function fetch_sources() {
	$.get(API + "/sources.json")
		.done(function(result) {
			var ul = $("#sources")
			ul.empty()
			$(result).each(function() {
				var input = $("<input>").attr("type", "checkbox")
				                        .attr("id", "source-" + this.id)
				                        .attr("data-source-id", this.id)
				                        .change(source_changed)
				var label = $("<label>").text(this.name)
				                        .attr("for", "source-" + this.id)
				var li = $("<li>").append(input)
				                  .append(label)
				ul.append(li)
				GLOBAL.sources[this.id] = this
				// TODO sort
			})
		})
}

function fetch_source(source_id) {
	var xhr = $.get(API + "/source_" + source_id + ".json")
		.done(function(result) {
			GLOBAL.items[source_id] = result
			// TODO last update
			refresh_news_display()
		})
		.always(function() {
			delete GLOBAL.xhrs[source_id]
		})
	GLOBAL.xhrs[source_id] = xhr
}

function sources_toggle(open) {
	if (open) {
		$("#sources-button .icon-open").hide()
		$("#sources-button .icon-close").show()
		$("#sources").show()
	} else {
		$("#sources-button .icon-open").show()
		$("#sources-button .icon-close").hide()
		$("#sources").hide()
	}
}

$(document).ready(function() {
	fetch_sources()
	// TODO set interval for sources if fail??

	var sources_open = false
	sources_toggle(false)
	$("#sources-button").click(function() {
		sources_open = !sources_open
		sources_toggle(sources_open)
	})	
})

$(document).ajaxError(function() {
	console.error("AJAX Fail!")
})
