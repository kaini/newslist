"use strict"

var $ = require("jquery")

var API = "data"

var GLOBAL = {
	items: {},
	sources: {},
	xhrs: {},
}

function toplevel_parent(source) {
	if (source.parent_id) {
		return toplevel_parent(GLOBAL.sources[source.parent_id])
	} else {
		return source
	}
}

function cmp(a, b) {
	return (a < b ? -1 : (a == b ? 0 : 1))
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

function make_item_box(item) {
	var source = item.source
	var image = $("<img>").attr("src", item.image ? API + "/" + item.image + ".jpg" : "icons/" + toplevel_parent(source).id + ".png")
		                  .attr("alt", item.image ? item.title : source.name)
		                  .attr("class", item.image ? "article-image" : "article-image-dummy")
		                  .on("load", set_image_class)
    var source_image = null
    if (item.image) {
    	var source_image = $("<img>").attr("src", "icons/" + toplevel_parent(source).id + ".png")
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

// Collect all items in a news layer and merge and order them zip-like.
function news_items(parent) {
	// Child sources
	var sources = []
	for (var key in GLOBAL.sources) {
		var source = GLOBAL.sources[key]
		if (source.parent_id === (parent ? parent.id : null)) {
			sources.push(source)
		}
	}
	sources.sort(function(a, b) {
		return cmp(a.order, b.order)
	})

	// Get this items and child sources items
	var itemss = parent ? [GLOBAL.items[parent.id] || []] : []
	$(sources).each(function() {
		itemss.push(news_items(this))
	})

	// Merge the items zip-like
	var items = []
	var item_ids = {}
	var idxs = []
	for (var i = 0; i < itemss.length; ++i) {
		idxs.push(0)
	}
	do {
		var hit = false
		for (var i = 0; i < itemss.length; ++i) {
			if (idxs[i] < itemss[i].length) {
				var item = itemss[i][idxs[i]]
				++idxs[i]
				hit = true
				if (!item_ids[item.id]) {
					items.push(item)
					item_ids[item.id] = true
				} else {
					--i
				}
			}
		}
	} while (hit)

	// Done
	return items
}

function refresh_news_display() {
	console.log("Refresh display")
	var items = news_items(null)
	var insert_anchor = $("#anchor")
	$("#items article").attr("data-delete", "data-delete")
	$(items).each(function() {
		var box = $("#article-" + this.id)
		if (box.length) {
			// article already in DOM
			box.attr("data-delete", null)
		} else {
			// article not added yet
			box = make_item_box(this)
		}
		insert_anchor.before(box)
	})
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
			// throw away old sources
			var ul = $("#sources")
			ul.empty()
			GLOBAL.sources = {}

			// group by parent (root === "")
			var sources_by_parent_id = {}
			$(result).each(function() {
				var key = this.parent_id || ""
				sources_by_parent_id[key] = sources_by_parent_id[key] || []
				sources_by_parent_id[key].push(this)
			})

			// sort each group by name
			for (var key in sources_by_parent_id) {
				sources_by_parent_id[key].sort(function(a, b) {
					var akey = a.name.toLowerCase()
					var bkey = b.name.toLowerCase()
					return cmp(akey, bkey)
				})
			}

			// create new sources in DOM (recursive)
			create_sources(ul, "", sources_by_parent_id)
			refresh_showhides()
		})
}

function create_sources(ul, key, sources_by_parent_id) {
	var sources = sources_by_parent_id[key]
	var i = 0
	$(sources).each(function() {
		GLOBAL.sources[this.id] = this
		this.order = i++
		Object.freeze(this)

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
		if (sources_by_parent_id[this.id]) {
			var sid = "source-sub-" + this.id
			var show_text = $("<span>").text(" show ressorts")
			                           .attr("data-closed", sid)
			var hide_text = $("<span>").text(" hide ressorts")
			                           .attr("data-open", sid)
			var a = $("<a>").attr("href", "#")
			                .attr("data-showhide", "closed")
			                .attr("id", sid)
			                .attr("class", "sub")
			                .append(show_text)
			                .append(hide_text)
			var sub_ul = $("<ul>").attr("data-open", sid)
			create_sources(sub_ul, this.id, sources_by_parent_id)
			li.append(a)
			li.append(sub_ul)
		}
		ul.append(li)
	})
}

function fetch_source(source_id) {
	var xhr = $.get({url: API + "/source_" + source_id + ".json", cache: false})
		.done(function(result) {
			GLOBAL.items[source_id] = result
			Object.freeze(result)
			$(result).each(function() {
				this.source = GLOBAL.sources[source_id]
				Object.freeze(this)
			})
			refresh_news_display()
		})
		.always(function() {
			delete GLOBAL.xhrs[source_id]
		})
	GLOBAL.xhrs[source_id] = xhr
}

function refresh_showhides() {
	$("[data-closed]").each(function() {
		var state = $("#" + $(this).attr("data-closed")).attr("data-showhide")
		if (state === "closed") {
			$(this).show()
		} else {
			$(this).hide()
		}
	})
	$("[data-open]").each(function() {
		var state = $("#" + $(this).attr("data-open")).attr("data-showhide")
		if (state === "open") {
			$(this).show()
		} else {
			$(this).hide()
		}
	})
}

function main() {
	console.log("App init")

	$(document).ready(function() {
		fetch_sources()
		window.setInterval(function() {
			console.log("Update")
			fetch_sources()
		}, 5 * 60 * 1000)

		// Show/Hide toggle feature
		$(document).on("click", "[data-showhide]", function() {
			var elem = $(this)
			if (elem.attr("data-showhide") === "closed") {
				elem.attr("data-showhide", "open")
				$("[data-open='" + elem.attr("id") + "']").each(function() {
					$(this).show()
				})
				$("[data-closed='" + elem.attr("id") + "']").each(function() {
					$(this).hide()
				})
			} else {
				elem.attr("data-showhide", "closed")
				$("[data-open='" + elem.attr("id") + "']").each(function() {
					$(this).hide()
				})
				$("[data-closed='" + elem.attr("id") + "']").each(function() {
					$(this).show()
				})
			}
		})
		refresh_showhides()
	})

	$(document).ajaxError(function() {
		console.error("AJAX Fail!")
		// TODO ??
	})
}

module.exports = {
	main: main
}
