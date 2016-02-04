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
	var image = $("<img>").attr("src", item.image ? API + "/" + item.image + ".png" : "icons/" + source.master_id + ".png")
		                  .attr("alt", item.image ? item.title : source.name)
		                  .attr("class", item.image ? "article-image" : "article-image-dummy")
		                  .on("load", set_image_class)
    var source_image = null
    if (item.image) {
    	var source_image = $("<img>").attr("src", "icons/" + source.master_id + ".png")
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
	                            .attr("id", "article-" + item.id)
	                            .append(imagebox)
	                            .append(content)
	return article
}

function refresh_news_display() {
	var keys = []
	for (var key in GLOBAL.items) {
		keys.push(key)
	}
	keys.sort(function(a, b) {
		var akey = GLOBAL.sources[a].name.toLowerCase()
		var bkey = GLOBAL.sources[b].name.toLowerCase()
		return (akey < bkey ? -1 : (akey > bkey ? 1 : 0))
	})

	var i = 0
	var insert_anchor = $("#anchor")
	$("#items article").attr("data-delete", "data-delete")
	do {
		var has_hit = false
		var retry = 0
		for (var k = 0; k < keys.length; ++k) {
			var item = GLOBAL.items[keys[k]][i + retry]
			if (item) {
				has_hit = true

				var box = $("#article-" + item.id)
				if (box.length && !box.attr("data-delete")) {
					// article already in DOM because item is a duplicate
					// retry with next article
					--k
					++retry
					continue
				} else if (box.length) {
					// article already in DOM
					box.attr("data-delete", null)
				} else {
					// article not added yet
					box = make_item_box(item, GLOBAL.sources[keys[k]])
				}
				insert_anchor.before(box)
			}
			retry = 0
		}
		++i
	} while (has_hit)

	$("#items article[data-delete]").remove()

	$("#lastupdate").text(new Date().toLocaleString(
		window.navigator.userLanguage || window.navigator.language, {
		weekday: "long",
		year: "numeric",
		month: "long",
		day: "numeric",
		hour: "numeric",
		minute: "numeric",
	}))
}

function source_changed() {
	var checkbox = $(this)
	var enabled = checkbox.is(":checked")
	var source_id = checkbox.attr("data-source-id")
	if (enabled) {
		console.log("Adding source " + source_id)
		fetch_source(source_id)
		localStorage.setItem("source-" + source_id, "1")
	} else {
		console.log("Removing source " + source_id)
		if (GLOBAL.xhrs[source_id]) {
			GLOBAL.xhrs[source_id].abort()
			delete GLOBAL.xhrs[source_id]
		}
		delete GLOBAL.items[source_id]
		refresh_news_display()
		localStorage.removeItem("source-" + source_id)
	}
}

function fetch_sources() {
	$.get({url: API + "/sources.json", cache: false})
		.done(function(result) {
			var ul = $("#sources")
			ul.empty()
			result.sort(function(a, b) {
				var akey = a.name.toLowerCase()
				var bkey = b.name.toLowerCase()
				return (akey < bkey ? -1 : (akey > bkey ? 1 : 0))
			})
			$(result).each(function() {
				var input = $("<input>").attr("type", "checkbox")
				                        .attr("id", "source-" + this.id)
				                        .attr("data-source-id", this.id)
				                        .change(source_changed)
				if (localStorage.getItem("source-" + this.id)) {
					input.attr("checked", "checked")
					input.change()
				}
				var label = $("<label>").text(this.name)
				                        .attr("for", "source-" + this.id)
				var li = $("<li>").append(input)
				                  .append(label)
				ul.append(li)
				GLOBAL.sources[this.id] = this
			})
		})
}

function fetch_source(source_id) {
	var xhr = $.get({url: API + "/source_" + source_id + ".json", cache: false})
		.done(function(result) {
			GLOBAL.items[source_id] = result
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
	window.setInterval(function() {
		console.log("Update")
		fetch_sources()
	}, 5 * 60 * 1000)

	var sources_open = false
	sources_toggle(false)
	$("#sources-button").click(function() {
		sources_open = !sources_open
		sources_toggle(sources_open)
	})
})

$(document).ajaxError(function() {
	console.error("AJAX Fail!")
	// TODO ??
})
