String.prototype.format = function () {
    var args = arguments;
    return this.replace(/\{(\d+)\}/g, function (m, n) { return args[n]; });
};
String.prototype.escape = function () {
    var args = arguments;
    return this.replace(/</g, '').replace(/>/g, '');
};
if (!String.prototype.trim) {
  String.prototype.trim = function () {
    return this.replace(/^\s+|\s+$/g, '');
  };
}
if (typeof String.prototype.endsWith !== 'function') {
    String.prototype.endsWith = function(suffix) {
        return this.indexOf(suffix, this.length - suffix.length) !== -1;
    };
}
if (typeof String.prototype.startsWith != 'function') {
  String.prototype.startsWith = function (str){
    return this.slice(0, str.length) == str;
  };
}

String.prototype.to_date = function () {
    var args = arguments;
    var post_date_str = this.replace(/\-/ig, '/');
    var utc_date = new Date(Date.parse(post_date_str));
    var now = new Date();
    utc_date.setTime(utc_date.getTime() - 60000 * now.getTimezoneOffset());
    return utc_date;
};

RegExp.prototype.exec_all = function(string) {
    var match = null;
    var matches = new Array();
    while (match = this.exec(string)) {
        var matchArray = [];
        for (var i in match) {
            if (parseInt(i) == i) {
                matchArray.push(match[i]);
            }
        }
        matches.push(matchArray);
    }
    return matches;
};

Date.prototype.format = function(format) {
    format = format || "yyyy-MM-dd hh:mm:ss";
    var o = {
        "M+" : this.getMonth()+1, //month
        "d+" : this.getDate(),    //day
        "h+" : this.getHours(),   //hour
        "m+" : this.getMinutes(), //minute
        "s+" : this.getSeconds(), //second
        "q+" : Math.floor((this.getMonth()+3)/3),  //quarter
        "S" : this.getMilliseconds() //millisecond
    };
    if(/(y+)/.test(format)) format=format.replace(RegExp.$1,
    (this.getFullYear()+"").substr(4 - RegExp.$1.length));
    for(var k in o)if(new RegExp("("+ k +")").test(format))
    format = format.replace(RegExp.$1,
      RegExp.$1.length==1 ? o[k] :
        ("00"+ o[k]).substr((""+ o[k]).length));
    return format;
};

;(function($){
    $.json_action = function(action, opt, success, error){
        $.post("/json/"+action,
            opt,
            function(res){
                if (res.status=="ok"){
                    success && success(res.response);
                } else {
                    error && error(res.error);
                }
        }, "json");
    };

    $.json_options = function(inputs){
        var opt = {};
        inputs.each(function(){
            var value;
            if ($(this).attr("type") == "file"){
                return;
            }
            if ($(this).attr("type") == "checkbox"){
                value = $.toJSON($(this).is(":checked"));
            } else if ($(this).is("textarea")){
                value = $.toJSON( $(this).val() );
            } else{
                value = $.toJSON( $.trim($(this).val()) );
            }
            if ($(this).attr("name")){
                opt[$(this).attr("name")] = value;
            }
        });
        return opt;
    };

    var players_settings = {
        youku: {
            link: /<a.+href="http:\/\/v.youku.com\/v_show\/id_(\S+)\.html.*".*>.*<\/a>/gm,
            player: function(match){
                return '<div><iframe class="video_player"' +
                    'src="http://player.youku.com/embed/{0}?wmode=transparent" '.format(match[1]) +
                    'frameborder=0 allowfullscreen wmode="transparent"></iframe></div>'
            }
        },
        xiami: {
            link: /<a.+href="http:\/\/www.xiami.com\/song\/(\d+).*".*>.*<\/a>/gm,
            player: function(match){
                var s = '<div><embed src="http://www.xiami.com/widget/0_{0}/singlePlayer.swf" ' +
                        'type="application/x-shockwave-flash" width="257" height="33" ' +
                        'wmode="transparent"></embed></div>';
                return s.format(match[1])
            }
        },
        xiami_album: {
            link: /<a.+href="http:\/\/www.xiami.com\/album\/(\d+).*".*>.*<\/a>/gm,
            player: function(match){
                var s = '<div><embed src="http://www.xiami.com/widget/' +
                    '0_{0}_235_346_FF8719_494949/albumPlayer.swf" ' +
                    'type="application/x-shockwave-flash" width="235" height="346" ' +
                    'wmode="transparent"></embed></div>';
                return s.format(match[1])
            }
        },
        youtube: {
            link: /<a.+href="http:\/\/www.youtube.com\/watch\?.*v=([^\s&]+).*".*>.*<\/a>/gm,
            player: function(match){
                return '<div><iframe class="video_player" ' +
                    'src="http://www.youtube.com/embed/{0}?wmode=transparent" '.format(match[1]) +
                    'frameborder="0" allowfullscreen wmode="transparent"></iframe></div>'
            }
        },
        ku6: {
            link: /<a.+href="http:\/\/v.ku6.com\/show\/(\S+)\.html.*".*>.*<\/a>/gm,
            player: function(match){
                return '<div><embed src="http://player.ku6.com/refer/{0}/v.swf" '.format(match[1]) +
                'class="video_player" allowscriptaccess="always" wmode="transparent"' +
                'allowfullscreen="true" type="application/x-shockwave-flash" flashvars="from=ku6"></embed></div>'
            }
        },
        qq: {
            link: /<a.+href="http:\/\/v.qq.com\/.+vid=([^\s&\/]+).*".*>.*<\/a>/gm,
            player: function(match){
                return '<div><embed src="http://static.video.qq.com/TPout.swf?vid={0}&auto=0" '.format(match[1]) +
                    'allowFullScreen="true" quality="high"  class="video_player" wmode="transparent"' +
                    'align="middle" allowScriptAccess="always" type="application/x-shockwave-flash"></embed></div>'
            }
        },
        magicycles: {
            link: /<a.+href="http:\/\/www.magicycles.com\/(riders|routes)\/([^\s\/]+)".*>.*<\/a>/gm,
            player: function(match){
                return '<div class="magicycles_widget">' +
                    '<iframe class="magicycles_widget"' +
                    ' src="http://www.magicycles.com/{0}/{1}/widget" '.format(match[1], match[2]) +
                    ' scrolling="no" frameborder="0" allowfullscreen wmode="transparent"></iframe></div>';
            }
        },
        yinyuetai: {
            link: /<a.+href="http:\/\/www.yinyuetai.com\/video\/(\d+).*".*>.*<\/a>/gm,
            player: function(match){
                return '<div><embed src="http://player.yinyuetai.com/video/player/{0}/v_2932937.swf"'.format(match[1]) +
                    ' class="video_player" quality="high" align="middle" wmode="transparent"' +
                    ' allowScriptAccess="sameDomain" allowfullscreen="true" ' +
                    ' type="application/x-shockwave-flash"></embed></div>';
            }
        }
    };
    $.create_player = function(text){
        // replace links with player
        for (var name in players_settings) {
            var player = players_settings[name];
            var links = player.link.exec_all(text);
            $.each(links, function(idx, match){
                text = text.replace(match[0], player.player(match));
            });
        }
        return text;
    };
    window.img_loading = "data:image/gif;base64,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";
    var $loading = $('<span><img src="{0}"></span>'.format(img_loading));
    $.fn.image_box = function(width, height, min_width, min_height){
        width = width || 640;
        height = height || 480;
        min_width = min_width || 160;
        min_height = min_height || 120;

        var $this = $(this);
        // remove non image elem
        $this = $.map($this, function (item, index) {
            var img = $(item);
            if (img.is("img") && img.width()>=min_width && img.height()>=min_height) {
                return item;
            } else {
                return null;
            }
        });

        var total = $this.length;
        $.each($this, function(index, item){
            var img = $(item);

            if($.blockUI) {
                var alt_height = Math.ceil(img.prop("alt").length/70.0) * 20;
                var buildbox = function(){
                    if (width >= $(window).width()){
                        var old_width = width;
                        width = $(window).width() * 0.9;
                        height = height * (width/old_width);
                    }
                    var imgBox = $('<div>' +
                        $loading.html() +
                        '<span class="next"></span>' +
                        '<span class="prev"></span>' +
                        '<a class="imgbox_photo_link search"  title="View Full Size" target="_blank"></a>' +
                        '<div class="imgbox_alt" style="font-size:1.1em; line-height:1.5em; background-color:#fff"></div>' +
                        '<a class="imgbox_close"></a></div>');

                    imgBox.css({
                        width: width+"px", height: height + alt_height + "px", position: "relative",
                        'background-color' : "#ddd",
                        'background-image': "url('/static/images/loading_alpha.gif')",
                        'background-repeat': 'no-repeat',
                        'background-position': '50% 100px',
                        'border-radius': '6px',
                        '-moz-border-radius': '6px',
                        '-webkit-border-radius': '6px',
                        'line-height': height + 'px',
                        'overflow' : 'hidden'
                    });
                    $("img", imgBox).css({
                        'max-width': width + "px", 'max-height': height + "px",
                        'cursor': 'default'
                    });
                    $(".imgbox_close", imgBox).css({
                        position: "absolute", top: "0px", right: "0px",
                        display: "block", width: "32px", height: "32px",
                        cursor: "pointer", 'z-index': '999',
                        'background-image': "url('/static/images/close.png')",
                        'background-repeat': 'no-repeat',
                        'background-position': '50% 50%'
                    });

                    var $search = $(".search", imgBox);
                    $search.css({
                        'width': '100%',
                        'height': '60px',
                        'display': 'block',
                        'position': 'absolute',
                        'top': '0',
                        'left': '0',
                        'background-repeat': 'no-repeat',
                        'background-position': '50% 50%',
                        'background-image': "url('/static/images/search.png')",
                        'cursor': 'url("/static/images/zoom_in.cur"), pointer'
                    });

                    $("span", imgBox).css({
                        'width': '30%',
                        'height': '100%',
                        'display': 'none',
                        'position': 'absolute',
                        'top': '0',
                        'background-repeat': 'no-repeat'
                    });
                    var $prev = $(".prev", imgBox);
                    $prev.css({
                        'background-image': "url('/static/images/prev.png')",
                        'left': '0',
                        'background-position': '2% 50%',
                        'cursor': "url('/static/images/prev.png'), pointer"
                    });
                    var $next = $(".next", imgBox);
                    $next.css({
                        'background-image': "url('/static/images/next.png')",
                        'right': '0',
                        'background-position': '98% 50%',
                        'cursor': "url('/static/images/next.png'), pointer"
                    });

                    var current = index;
                    var show_nav = function(){
                        $prev.hide();
                        $next.hide();
                        $search.hide();
                        if (current > 0) {
                            $prev.fadeIn(1000);
                        }
                        if (current < total-1) {
                            $next.fadeIn(1000);
                        }
                        $search.fadeIn(1000);
                    };
                    var show_photo = function($img){
                        imgBox.css({'background-image': "url('/static/images/loading_alpha.gif')"});
                        var src = $img.attr("src");
                        if ($img.attr("real_src")){
                            src = $img.attr("real_src");
                        }
                        if(src.endsWith("==") || src.endsWith("==/")
                            || src.match(/\.ggpht\.com\/\S+/g)) {
                            if (! src.match(/(=s\d+)$/g)){
                                src = src+"=s0";
                            }
                        }
                        $("img", imgBox).hide();
                        $(".imgbox_photo_link", imgBox).attr("href", src);
                        $("img", imgBox).attr("src", src).fadeIn(500);


                        $img.one('load', function() {
                            imgBox.css({'background-image': "none"});
                        }).each(function() {
                          if(this.complete) $(this).load();
                        });

                        var alt_height = Math.ceil($img.prop("alt").length/70.0) * 20;
                        imgBox.height(height + alt_height);
                        imgBox.parents(".blockMsg").height(height + alt_height);
                        $(".imgbox_alt", imgBox).html($img.prop("alt"));
                    };

                    $next.click(function(){
                        current++;
                        current = current >= total ? total : current;
                        show_nav();
                        show_photo($($this[current]));
                    });
                    $prev.click(function(){
                        current--;
                        current = current < 0 ? 0 : current;
                        show_nav();
                        show_photo($($this[current]));
                    });

                    $(".imgbox_close", imgBox).click(function(){
                        $.unblockUI();
                    });

                    show_nav();
                    show_photo(img);

                    return imgBox;
                };

                img.css("cursor", "pointer");
                img.unbind("click");
                img.click(function() {
                    var imgBox = buildbox();
                    var top = ($(window).height() - height - alt_height) /2;
                    var left = ($(window).width() - width) /2;
                    top = top > 0 ? top : 0;
                    left = left > 0 ? left : 0;
                    var blockUI_css = $.blockUI.defaults.css;
                    $.blockUI.defaults.css['border-radius'] = "6px";
                    $.blockUI.defaults.css['border'] = "5px solid #FFF";
                    $.blockUI({
                        message: imgBox,
                        css: {
                            top:  top + "px",
                            left: left + "px",
                            height: height + alt_height + "px",
                            width: width + "px"
                        },
                        onBlock: function() {
                            $(".blockOverlay").prop("title", "Click to close").click($.unblockUI).css({
                                cursor: 'default'
                            });
                        }
                    });
                    $.blockUI.defaults.css = blockUI_css;
                });
            }
        });
        return $this;
    };

    $.fn.image_info = function(min_width, min_height){
        min_width = min_width || 128;
        min_height = min_height || 128;

        $(this).each(function(index, item){
            var img = $(item);
            var build_info = function(img){
                var info = img.prop("alt");
                if (!info) return;
                if ((img.height() < min_height) || (img.width() < min_width)) return;

                var info_div = $('<p class="img_info"></p>').html(info);
                var img_margin_left = parseInt(img.css("margin-left").replace("px", ""));
                var img_margin_top = parseInt(img.css("margin-top").replace("px", ""));
                var img_info_parent = img.parents(".img_info_parent");
                var parent_scroll_left = img_info_parent.scrollLeft();
                var parent_scroll_top = img_info_parent.scrollTop();

                img.next(".img_info").remove();
                img.after(info_div);
                info_div.css({
                    'background': "rgba(0, 0, 0, 0.5)",
                    'font-size': "90%",
                    'position': "absolute",
                    'color': "#eee",
                    'padding': "6px",
                    'left': img.position().left + parent_scroll_left + img_margin_left + "px",
                    'width': img.outerWidth() - 12 + "px"
                });
                info_div.css({
                    'top': img.position().top + parent_scroll_top + img.height() + img_margin_top -
                        info_div.outerHeight() + "px"
                })
            };

            build_info(img);
        });
        return $(this);
    };

    $.fn.scrollto = function(backoff){
        backoff = backoff || 80;
        var $this = $(this);
        $("html,body").animate({scrollTop: $this.offset().top-backoff}, 500);

        return $this;
    }
})(jQuery);

/*!
 * jQuery throttle / debounce - v1.1 - 3/7/2010
 * http://benalman.com/projects/jquery-throttle-debounce-plugin/
 *
 * Copyright (c) 2010 "Cowboy" Ben Alman
 * Dual licensed under the MIT and GPL licenses.
 * http://benalman.com/about/license/
 */
(function(window,undefined){
  '$:nomunge'; // Used by YUI compressor.

  // Since jQuery really isn't required for this plugin, use `jQuery` as the
  // namespace only if it already exists, otherwise use the `Cowboy` namespace,
  // creating it if necessary.
  var $ = window.jQuery || window.Cowboy || ( window.Cowboy = {} ),

    // Internal method reference.
    jq_throttle;

  $.throttle = jq_throttle = function( delay, no_trailing, callback, debounce_mode ) {
    // After wrapper has stopped being called, this timeout ensures that
    // `callback` is executed at the proper times in `throttle` and `end`
    // debounce modes.
    var timeout_id,

      // Keep track of the last time `callback` was executed.
      last_exec = 0;

    // `no_trailing` defaults to falsy.
    if ( typeof no_trailing !== 'boolean' ) {
      debounce_mode = callback;
      callback = no_trailing;
      no_trailing = undefined;
    }

    // The `wrapper` function encapsulates all of the throttling / debouncing
    // functionality and when executed will limit the rate at which `callback`
    // is executed.
    function wrapper() {
      var that = this,
        elapsed = +new Date() - last_exec,
        args = arguments;

      // Execute `callback` and update the `last_exec` timestamp.
      function exec() {
        last_exec = +new Date();
        callback.apply( that, args );
      };

      // If `debounce_mode` is true (at_begin) this is used to clear the flag
      // to allow future `callback` executions.
      function clear() {
        timeout_id = undefined;
      };

      if ( debounce_mode && !timeout_id ) {
        // Since `wrapper` is being called for the first time and
        // `debounce_mode` is true (at_begin), execute `callback`.
        exec();
      }

      // Clear any existing timeout.
      timeout_id && clearTimeout( timeout_id );

      if ( debounce_mode === undefined && elapsed > delay ) {
        // In throttle mode, if `delay` time has been exceeded, execute
        // `callback`.
        exec();

      } else if ( no_trailing !== true ) {
        // In trailing throttle mode, since `delay` time has not been
        // exceeded, schedule `callback` to execute `delay` ms after most
        // recent execution.
        //
        // If `debounce_mode` is true (at_begin), schedule `clear` to execute
        // after `delay` ms.
        //
        // If `debounce_mode` is false (at end), schedule `callback` to
        // execute after `delay` ms.
        timeout_id = setTimeout( debounce_mode ? clear : exec, debounce_mode === undefined ? delay - elapsed : delay );
      }
    };

    // Set the guid of `wrapper` function to the same of original callback, so
    // it can be removed in jQuery 1.4+ .unbind or .die by using the original
    // callback as a reference.
    if ( $.guid ) {
      wrapper.guid = callback.guid = callback.guid || $.guid++;
    }

    // Return the wrapper function.
    return wrapper;
  };

  $.debounce = function( delay, at_begin, callback ) {
    return callback === undefined
      ? jq_throttle( delay, at_begin, false )
      : jq_throttle( delay, callback, at_begin !== false );
  };

})(this);
