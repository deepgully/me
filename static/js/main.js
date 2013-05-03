String.prototype.format = function () {
    var args = arguments;
    return this.replace(/\{(\d+)\}/g, function (m, n) { return args[n]; });
};

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
                var alt_height = Math.ceil(img.attr("alt").length/70.0) * 20;

                var buildbox = function(){
                    var imgBox = $('<div>' +
                        '<img src="/static/images/loading.gif"/>' +
                        '<span class="next"></span>' +
                        '<span class="prev"></span>' +
                        '<a class="imgbox_photo_link search"  title="View Full Size" target="_blank"></a>' +
                        '<div class="imgbox_alt"></div>' +
                        '<a class="imgbox_close"></a></div>');

                    imgBox.css({
                        width: width+"px", height: height + alt_height + "px", position: "relative",
                        'background-color' : "#f1f1f1",
                        'background-image': "url('/static/images/loading_alpha.gif')",
                        'background-repeat': 'no-repeat',
                        'background-position': '50% 36%',
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
                        'width': '50%',
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
                        var src = $img.attr("src");
                        if ($img.attr("real_src")){
                            src = $img.attr("real_src");
                        }
                        $("img", imgBox).hide();
                        $(".imgbox_photo_link", imgBox).attr("href", src);
                        $("img", imgBox).attr("src", src).fadeIn(500);

                        $(".imgbox_alt", imgBox).html($img.attr("alt"));
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
                            $(".blockOverlay").attr("title", "Click to close").click($.unblockUI).css({
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
                var info = img.attr("alt");
                if (!info) return;
                if ((img.height() < min_height) || (img.width() < min_width)) return;

                var info_div = $('<p class="img_info"></p>').html(info);
                var img_margin_left = parseInt(img.css("margin-left").replace("px", ""));
                var img_margin_top = parseInt(img.css("margin-top").replace("px", ""));

                img.next(".img_info").remove();
                img.after(info_div);
                info_div.css({
                    'background': "rgba(0, 0, 0, 0.5)",
                    'font-size': "90%",
                    'position': "absolute",
                    'color': "#eee",
                    'padding': "6px",
                    'left': img.position().left + img_margin_left + "px",
                    'width': img.outerWidth() - 12 + "px"
                });
                info_div.css({
                    'top': img.position().top + img.height() + img_margin_top -
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
