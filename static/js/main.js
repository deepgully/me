/* Bootstrap growl */
(function(){var t;t=jQuery,t.bootstrapGrowl=function(e,s){var a,o,l;switch(s=t.extend({},t.bootstrapGrowl.default_options,s),a=t("<div>"),a.attr("class","bootstrap-growl alert"),s.type&&a.addClass("alert-"+s.type),s.allow_dismiss&&a.append('<a class="close" data-dismiss="alert" href="#">&times;</a>'),a.append(e),s.top_offset&&(s.offset={from:"top",amount:s.top_offset}),l=s.offset.amount,t(".bootstrap-growl").each(function(){return l=Math.max(l,parseInt(t(this).css(s.offset.from))+t(this).outerHeight()+s.stackup_spacing)}),o={position:"body"===s.ele?"fixed":"absolute",margin:0,"z-index":"9999",display:"none"},o[s.offset.from]=l+"px",a.css(o),"auto"!==s.width&&a.css("width",s.width+"px"),t(s.ele).append(a),s.align){case"center":a.css({left:"50%","margin-left":"-"+a.outerWidth()/2+"px"});break;case"left":a.css("left","20px");break;default:a.css("right","20px")}return a.fadeIn(),s.delay>0&&a.delay(s.delay).fadeOut(function(){return t(this).alert("close")}),a},t.bootstrapGrowl.default_options={ele:"body",type:null,offset:{from:"top",amount:20},align:"right",width:250,delay:4e3,allow_dismiss:!0,stackup_spacing:10}}).call(this);
/*!
 * bootstrap-tags 1.1.5
 * https://github.com/maxwells/bootstrap-tags
 * Copyright 2013 Max Lahey; Licensed MIT
 */
!function(a){!function(){window.Tags||(window.Tags={}),jQuery(function(){return a.tags=function(b,c){var d,e,f,g,h,i,j,k=this;null==c&&(c={});for(d in c)g=c[d],this[d]=g;if(this.bootstrapVersion||(this.bootstrapVersion="3"),this.readOnly||(this.readOnly=!1),this.suggestOnClick||(this.suggestOnClick=!1),this.suggestions||(this.suggestions=[]),this.restrictTo=null!=c.restrictTo?c.restrictTo.concat(this.suggestions):!1,this.exclude||(this.exclude=!1),this.displayPopovers=null!=c.popovers?!0:null!=c.popoverData,this.popoverTrigger||(this.popoverTrigger="hover"),this.tagClass||(this.tagClass="btn-info"),this.tagSize||(this.tagSize="md"),this.promptText||(this.promptText="Enter tags..."),this.caseInsensitive||(this.caseInsensitive=!1),this.readOnlyEmptyMessage||(this.readOnlyEmptyMessage="No tags to display..."),this.maxNumTags||(this.maxNumTags=-1),this.beforeAddingTag||(this.beforeAddingTag=function(){}),this.afterAddingTag||(this.afterAddingTag=function(){}),this.beforeDeletingTag||(this.beforeDeletingTag=function(){}),this.afterDeletingTag||(this.afterDeletingTag=function(){}),this.definePopover||(this.definePopover=function(a){return'associated content for "'+a+'"'}),this.excludes||(this.excludes=function(){return!1}),this.tagRemoved||(this.tagRemoved=function(){}),this.pressedReturn||(this.pressedReturn=function(){}),this.pressedDelete||(this.pressedDelete=function(){}),this.pressedDown||(this.pressedDown=function(){}),this.pressedUp||(this.pressedUp=function(){}),this.$element=a(b),null!=c.tagData?this.tagsArray=c.tagData:(f=a(".tag-data",this.$element).html(),this.tagsArray=null!=f?f.split(","):[]),c.popoverData)this.popoverArray=c.popoverData;else for(this.popoverArray=[],j=this.tagsArray,h=0,i=j.length;i>h;h++)e=j[h],this.popoverArray.push(null);return this.getTags=function(){return k.tagsArray},this.getTagsContent=function(){return k.popoverArray},this.getTagsWithContent=function(){var a,b,c,d;for(a=[],b=c=0,d=k.tagsArray.length-1;d>=0?d>=c:c>=d;b=d>=0?++c:--c)a.push({tag:k.tagsArray[b],content:k.popoverArray[b]});return a},this.getTag=function(a){var b;return b=k.tagsArray.indexOf(a),b>-1?k.tagsArray[b]:null},this.getTagWithContent=function(a){var b;return b=k.tagsArray.indexOf(a),{tag:k.tagsArray[b],content:k.popoverArray[b]}},this.hasTag=function(a){return k.tagsArray.indexOf(a)>-1},this.removeTagClicked=function(b){return"A"===b.currentTarget.tagName&&(k.removeTag(a("span",b.currentTarget.parentElement).html()),a(b.currentTarget.parentNode).remove()),k},this.removeLastTag=function(){return k.tagsArray.length>0&&(k.removeTag(k.tagsArray[k.tagsArray.length-1]),k.canAddByMaxNum()&&k.enableInput()),k},this.removeTag=function(a){if(k.tagsArray.indexOf(a)>-1){if(k.beforeDeletingTag(a)===!1)return;k.popoverArray.splice(k.tagsArray.indexOf(a),1),k.tagsArray.splice(k.tagsArray.indexOf(a),1),k.renderTags(),k.afterDeletingTag(a),k.canAddByMaxNum()&&k.enableInput()}return k},this.canAddByRestriction=function(a){return this.restrictTo===!1||-1!==this.restrictTo.indexOf(a)},this.canAddByExclusion=function(a){return(this.exclude===!1||-1===this.exclude.indexOf(a))&&!this.excludes(a)},this.canAddByMaxNum=function(){return-1===this.maxNumTags||this.tagsArray.length<this.maxNumTags},this.addTag=function(a){var b;if(k.canAddByRestriction(a)&&!k.hasTag(a)&&a.length>0&&k.canAddByExclusion(a)&&k.canAddByMaxNum()){if(k.beforeAddingTag(a)===!1)return;b=k.definePopover(a),k.popoverArray.push(b||null),k.tagsArray.push(a),k.afterAddingTag(a),k.renderTags(),k.canAddByMaxNum()||k.disableInput()}return k},this.addTagWithContent=function(a,b){if(k.canAddByRestriction(a)&&!k.hasTag(a)&&a.length>0){if(k.beforeAddingTag(a)===!1)return;k.tagsArray.push(a),k.popoverArray.push(b),k.afterAddingTag(a),k.renderTags()}return k},this.renameTag=function(a,b){return k.tagsArray[k.tagsArray.indexOf(a)]=b,k.renderTags(),k},this.setPopover=function(a,b){return k.popoverArray[k.tagsArray.indexOf(a)]=b,k.renderTags(),k},this.clickHandler=function(a){return k.makeSuggestions(a,!0)},this.keyDownHandler=function(a){var b,c;switch(b=null!=a.keyCode?a.keyCode:a.which){case 13:return a.preventDefault(),k.pressedReturn(a),e=a.target.value,-1!==k.suggestedIndex&&(e=k.suggestionList[k.suggestedIndex]),k.addTag(e),a.target.value="",k.renderTags(),k.hideSuggestions();case 46:case 8:if(k.pressedDelete(a),""===a.target.value&&k.removeLastTag(),1===a.target.value.length)return k.hideSuggestions();break;case 40:if(k.pressedDown(a),""!==k.input.val()||-1!==k.suggestedIndex&&null!=k.suggestedIndex||k.makeSuggestions(a,!0),c=k.suggestionList.length,k.suggestedIndex=k.suggestedIndex<c-1?k.suggestedIndex+1:c-1,k.selectSuggested(k.suggestedIndex),k.suggestedIndex>=0)return k.scrollSuggested(k.suggestedIndex);break;case 38:if(k.pressedUp(a),k.suggestedIndex=k.suggestedIndex>0?k.suggestedIndex-1:0,k.selectSuggested(k.suggestedIndex),k.suggestedIndex>=0)return k.scrollSuggested(k.suggestedIndex);break;case 9:case 27:return k.hideSuggestions(),k.suggestedIndex=-1}},this.keyUpHandler=function(a){var b;return b=null!=a.keyCode?a.keyCode:a.which,40!==b&&38!==b&&27!==b?k.makeSuggestions(a,!1):void 0},this.getSuggestions=function(b,c){var d=this;return this.suggestionList=[],this.caseInsensitive&&(b=b.toLowerCase()),a.each(this.suggestions,function(a,e){var f;return f=d.caseInsensitive?e.substring(0,b.length).toLowerCase():e.substring(0,b.length),d.tagsArray.indexOf(e)<0&&f===b&&(b.length>0||c)?d.suggestionList.push(e):void 0}),this.suggestionList},this.makeSuggestions=function(b,c,d){return null==d&&(d=null!=b.target.value?b.target.value:b.target.textContent),k.suggestedIndex=-1,k.$suggestionList.html(""),a.each(k.getSuggestions(d,c),function(a,b){return k.$suggestionList.append(k.template("tags_suggestion",{suggestion:b}))}),k.$(".tags-suggestion").mouseover(k.selectSuggestedMouseOver),k.$(".tags-suggestion").click(k.suggestedClicked),k.suggestionList.length>0?k.showSuggestions():k.hideSuggestions()},this.suggestedClicked=function(a){return e=a.target.textContent,-1!==k.suggestedIndex&&(e=k.suggestionList[k.suggestedIndex]),k.addTag(e),k.input.val(""),k.makeSuggestions(a,!1,""),k.input.focus(),k.hideSuggestions()},this.hideSuggestions=function(){return k.$(".tags-suggestion-list").css({display:"none"})},this.showSuggestions=function(){return k.$(".tags-suggestion-list").css({display:"block"})},this.selectSuggestedMouseOver=function(b){return a(".tags-suggestion").removeClass("tags-suggestion-highlighted"),a(b.target).addClass("tags-suggestion-highlighted"),a(b.target).mouseout(k.selectSuggestedMousedOut),k.suggestedIndex=k.$(".tags-suggestion").index(a(b.target))},this.selectSuggestedMousedOut=function(b){return a(b.target).removeClass("tags-suggestion-highlighted")},this.selectSuggested=function(b){var c;return a(".tags-suggestion").removeClass("tags-suggestion-highlighted"),c=k.$(".tags-suggestion").eq(b),c.addClass("tags-suggestion-highlighted")},this.scrollSuggested=function(a){var b,c,d,e;return c=k.$(".tags-suggestion").eq(a),d=k.$(".tags-suggestion").eq(0),b=c.position(),e=d.position(),null!=b?k.$(".tags-suggestion-list").scrollTop(b.top-e.top):void 0},this.adjustInputPosition=function(){var b,c,d,e,f,g;return f=k.$(".tag").last(),g=f.position(),c=null!=g?g.left+f.outerWidth(!0):0,d=null!=g?g.top:0,e=k.$element.width()-c,a(".tags-input",k.$element).css({paddingLeft:Math.max(c,0),paddingTop:Math.max(d,0),width:e}),b=null!=g?g.top+f.outerHeight(!0):22,k.$element.css({paddingBottom:b-k.$element.height()})},this.renderTags=function(){var b;return b=k.$(".tags"),b.html(""),k.input.attr("placeholder",0===k.tagsArray.length?k.promptText:""),a.each(k.tagsArray,function(c,d){return d=a(k.formatTag(c,d)),a("a",d).click(k.removeTagClicked),a("a",d).mouseover(k.toggleCloseColor),a("a",d).mouseout(k.toggleCloseColor),k.displayPopovers&&k.initializePopoverFor(d,k.tagsArray[c],k.popoverArray[c]),b.append(d)}),k.adjustInputPosition()},this.renderReadOnly=function(){var b;return b=k.$(".tags"),b.html(0===k.tagsArray.length?k.readOnlyEmptyMessage:""),a.each(k.tagsArray,function(c,d){return d=a(k.formatTag(c,d,!0)),k.displayPopovers&&k.initializePopoverFor(d,k.tagsArray[c],k.popoverArray[c]),b.append(d)})},this.disableInput=function(){return this.$("input").prop("disabled",!0)},this.enableInput=function(){return this.$("input").prop("disabled",!1)},this.initializePopoverFor=function(b,d,e){return c={title:d,content:e,placement:"bottom"},"hoverShowClickHide"===k.popoverTrigger?(a(b).mouseover(function(){return a(b).popover("show"),a(".tag").not(b).popover("hide")}),a(document).click(function(){return a(b).popover("hide")})):c.trigger=k.popoverTrigger,a(b).popover(c)},this.toggleCloseColor=function(b){var c,d;return d=a(b.currentTarget),c=d.css("opacity"),c=.8>c?1:.6,d.css({opacity:c})},this.formatTag=function(a,b,c){var d;return null==c&&(c=!1),d=b.replace("<","&lt;").replace(">","&gt;"),k.template("tag",{tag:d,tagClass:k.tagClass,isPopover:k.displayPopovers,isReadOnly:c,tagSize:k.tagSize})},this.addDocumentListeners=function(){return a(document).mouseup(function(a){var b;return b=k.$(".tags-suggestion-list"),0===b.has(a.target).length?k.hideSuggestions():void 0})},this.template=function(a,b){return Tags.Templates.Template(this.getBootstrapVersion(),a,b)},this.$=function(b){return a(b,this.$element)},this.getBootstrapVersion=function(){return Tags.bootstrapVersion||this.bootstrapVersion},this.initializeDom=function(){return this.$element.append(this.template("tags_container"))},this.init=function(){return this.$element.addClass("bootstrap-tags").addClass("bootstrap-"+this.getBootstrapVersion()),this.initializeDom(),this.readOnly?(this.renderReadOnly(),this.removeTag=function(){},this.removeTagClicked=function(){},this.removeLastTag=function(){},this.addTag=function(){},this.addTagWithContent=function(){},this.renameTag=function(){},this.setPopover=function(){}):(this.input=a(this.template("input",{tagSize:this.tagSize})),this.suggestOnClick&&this.input.click(this.clickHandler),this.input.keydown(this.keyDownHandler),this.input.keyup(this.keyUpHandler),this.$element.append(this.input),this.$suggestionList=a(this.template("suggestion_list")),this.$element.append(this.$suggestionList),this.renderTags(),this.canAddByMaxNum()||this.disableInput(),this.addDocumentListeners())},this.init(),this},a.fn.tags=function(b){var c,d;return d={},c="number"==typeof b?b:-1,this.each(function(e,f){var g;return g=a(f),null==g.data("tags")&&g.data("tags",new a.tags(this,b)),c===e||0===e?d=g.data("tags"):void 0}),d}})}.call(this),function(){window.Tags||(window.Tags={}),Tags.Helpers||(Tags.Helpers={}),Tags.Helpers.addPadding=function(a,b,c){return null==b&&(b=1),null==c&&(c=!0),c?0===b?a:Tags.Helpers.addPadding("&nbsp"+a+"&nbsp",b-1):a}}.call(this),function(){var a;window.Tags||(window.Tags={}),Tags.Templates||(Tags.Templates={}),(a=Tags.Templates)["2"]||(a["2"]={}),Tags.Templates["2"].input=function(a){var b;return null==a&&(a={}),b=function(){switch(a.tagSize){case"sm":return"small";case"md":return"medium";case"lg":return"large"}}(),"<input type='text' class='tags-input input-"+b+"' />"}}.call(this),function(){var a;window.Tags||(window.Tags={}),Tags.Templates||(Tags.Templates={}),(a=Tags.Templates)["2"]||(a["2"]={}),Tags.Templates["2"].tag=function(a){return null==a&&(a={}),"<div class='tag label "+a.tagClass+" "+a.tagSize+"' "+(a.isPopover?"rel='popover'":"")+">    <span>"+Tags.Helpers.addPadding(a.tag,2,a.isReadOnly)+"</span>    "+(a.isReadOnly?"":"<a><i class='remove icon-remove-sign icon-white' /></a>")+"  </div>"}}.call(this),function(){var a;window.Tags||(window.Tags={}),Tags.Templates||(Tags.Templates={}),(a=Tags.Templates)["3"]||(a["3"]={}),Tags.Templates["3"].input=function(a){return null==a&&(a={}),"<input type='text' class='form-control tags-input input-"+a.tagSize+"' />"}}.call(this),function(){var a;window.Tags||(window.Tags={}),Tags.Templates||(Tags.Templates={}),(a=Tags.Templates)["3"]||(a["3"]={}),Tags.Templates["3"].tag=function(a){return null==a&&(a={}),"<div class='tag label "+a.tagClass+" "+a.tagSize+"' "+(a.isPopover?"rel='popover'":"")+">    <span>"+Tags.Helpers.addPadding(a.tag,2,a.isReadOnly)+"</span>    "+(a.isReadOnly?"":"<a><i class='remove fa fa-times-circle-o' /></a>")+"  </div>"}}.call(this),function(){var a;window.Tags||(window.Tags={}),Tags.Templates||(Tags.Templates={}),(a=Tags.Templates).shared||(a.shared={}),Tags.Templates.shared.suggestion_list=function(a){return null==a&&(a={}),'<ul class="tags-suggestion-list dropdown-menu"></ul>'}}.call(this),function(){var a;window.Tags||(window.Tags={}),Tags.Templates||(Tags.Templates={}),(a=Tags.Templates).shared||(a.shared={}),Tags.Templates.shared.tags_container=function(a){return null==a&&(a={}),'<div class="tags"></div>'}}.call(this),function(){var a;window.Tags||(window.Tags={}),Tags.Templates||(Tags.Templates={}),(a=Tags.Templates).shared||(a.shared={}),Tags.Templates.shared.tags_suggestion=function(a){return null==a&&(a={}),"<li class='tags-suggestion'>"+a.suggestion+"</li>"}}.call(this),function(){window.Tags||(window.Tags={}),Tags.Templates||(Tags.Templates={}),Tags.Templates.Template=function(a,b,c){return null!=Tags.Templates[a]&&null!=Tags.Templates[a][b]?Tags.Templates[a][b](c):Tags.Templates.shared[b](c)}}.call(this)}(window.jQuery);

/*!
 * bootbox.js v4.2.0
 *
 * http://bootboxjs.com/license.txt
 */
!function(a,b){"use strict";"function"==typeof define&&define.amd?define(["jquery"],b):"object"==typeof exports?module.exports=b(require("jquery")):a.bootbox=b(a.jQuery)}(this,function a(b,c){"use strict";function d(a){var b=q[o.locale];return b?b[a]:q.en[a]}function e(a,c,d){a.stopPropagation(),a.preventDefault();var e=b.isFunction(d)&&d(a)===!1;e||c.modal("hide")}function f(a){var b,c=0;for(b in a)c++;return c}function g(a,c){var d=0;b.each(a,function(a,b){c(a,b,d++)})}function h(a){var c,d;if("object"!=typeof a)throw new Error("Please supply an object of options");if(!a.message)throw new Error("Please specify a message");return a=b.extend({},o,a),a.buttons||(a.buttons={}),a.backdrop=a.backdrop?"static":!1,c=a.buttons,d=f(c),g(c,function(a,e,f){if(b.isFunction(e)&&(e=c[a]={callback:e}),"object"!==b.type(e))throw new Error("button with key "+a+" must be an object");e.label||(e.label=a),e.className||(e.className=2>=d&&f===d-1?"btn-primary":"btn-default")}),a}function i(a,b){var c=a.length,d={};if(1>c||c>2)throw new Error("Invalid argument length");return 2===c||"string"==typeof a[0]?(d[b[0]]=a[0],d[b[1]]=a[1]):d=a[0],d}function j(a,c,d){return b.extend(!0,{},a,i(c,d))}function k(a,b,c,d){var e={className:"bootbox-"+a,buttons:l.apply(null,b)};return m(j(e,d,c),b)}function l(){for(var a={},b=0,c=arguments.length;c>b;b++){var e=arguments[b],f=e.toLowerCase(),g=e.toUpperCase();a[f]={label:d(g)}}return a}function m(a,b){var d={};return g(b,function(a,b){d[b]=!0}),g(a.buttons,function(a){if(d[a]===c)throw new Error("button key "+a+" is not allowed (options are "+b.join("\n")+")")}),a}var n={dialog:"<div class='bootbox modal' tabindex='-1' role='dialog'><div class='modal-dialog'><div class='modal-content'><div class='modal-body'><div class='bootbox-body'></div></div></div></div></div>",header:"<div class='modal-header'><h4 class='modal-title'></h4></div>",footer:"<div class='modal-footer'></div>",closeButton:"<button type='button' class='bootbox-close-button close' data-dismiss='modal' aria-hidden='true'>&times;</button>",form:"<form class='bootbox-form'></form>",inputs:{text:"<input class='bootbox-input bootbox-input-text form-control' autocomplete=off type=text />",textarea:"<textarea class='bootbox-input bootbox-input-textarea form-control'></textarea>",email:"<input class='bootbox-input bootbox-input-email form-control' autocomplete='off' type='email' />",select:"<select class='bootbox-input bootbox-input-select form-control'></select>",checkbox:"<div class='checkbox'><label><input class='bootbox-input bootbox-input-checkbox' type='checkbox' /></label></div>",date:"<input class='bootbox-input bootbox-input-date form-control' autocomplete=off type='date' />",time:"<input class='bootbox-input bootbox-input-time form-control' autocomplete=off type='time' />",number:"<input class='bootbox-input bootbox-input-number form-control' autocomplete=off type='number' />",password:"<input class='bootbox-input bootbox-input-password form-control' autocomplete='off' type='password' />"}},o={locale:"en",backdrop:!0,animate:!0,className:null,closeButton:!0,show:!0,container:"body"},p={};p.alert=function(){var a;if(a=k("alert",["ok"],["message","callback"],arguments),a.callback&&!b.isFunction(a.callback))throw new Error("alert requires callback property to be a function when provided");return a.buttons.ok.callback=a.onEscape=function(){return b.isFunction(a.callback)?a.callback():!0},p.dialog(a)},p.confirm=function(){var a;if(a=k("confirm",["cancel","confirm"],["message","callback"],arguments),a.buttons.cancel.callback=a.onEscape=function(){return a.callback(!1)},a.buttons.confirm.callback=function(){return a.callback(!0)},!b.isFunction(a.callback))throw new Error("confirm requires a callback");return p.dialog(a)},p.prompt=function(){var a,d,e,f,h,i,k;f=b(n.form),d={className:"bootbox-prompt",buttons:l("cancel","confirm"),value:"",inputType:"text"},a=m(j(d,arguments,["title","callback"]),["cancel","confirm"]),i=a.show===c?!0:a.show;var o=["date","time","number"],q=document.createElement("input");if(q.setAttribute("type",a.inputType),o[a.inputType]&&(a.inputType=q.type),a.message=f,a.buttons.cancel.callback=a.onEscape=function(){return a.callback(null)},a.buttons.confirm.callback=function(){var c;switch(a.inputType){case"text":case"textarea":case"email":case"select":case"date":case"time":case"number":case"password":c=h.val();break;case"checkbox":var d=h.find("input:checked");c=[],g(d,function(a,d){c.push(b(d).val())})}return a.callback(c)},a.show=!1,!a.title)throw new Error("prompt requires a title");if(!b.isFunction(a.callback))throw new Error("prompt requires a callback");if(!n.inputs[a.inputType])throw new Error("invalid prompt type");switch(h=b(n.inputs[a.inputType]),a.inputType){case"text":case"textarea":case"email":case"date":case"time":case"number":case"password":h.val(a.value);break;case"select":var r={};if(k=a.inputOptions||[],!k.length)throw new Error("prompt with select requires options");g(k,function(a,d){var e=h;if(d.value===c||d.text===c)throw new Error("given options in wrong format");d.group&&(r[d.group]||(r[d.group]=b("<optgroup/>").attr("label",d.group)),e=r[d.group]),e.append("<option value='"+d.value+"'>"+d.text+"</option>")}),g(r,function(a,b){h.append(b)}),h.val(a.value);break;case"checkbox":var s=b.isArray(a.value)?a.value:[a.value];if(k=a.inputOptions||[],!k.length)throw new Error("prompt with checkbox requires options");if(!k[0].value||!k[0].text)throw new Error("given options in wrong format");h=b("<div/>"),g(k,function(c,d){var e=b(n.inputs[a.inputType]);e.find("input").attr("value",d.value),e.find("label").append(d.text),g(s,function(a,b){b===d.value&&e.find("input").prop("checked",!0)}),h.append(e)})}return a.placeholder&&h.attr("placeholder",a.placeholder),a.pattern&&h.attr("pattern",a.pattern),f.append(h),f.on("submit",function(a){a.preventDefault(),e.find(".btn-primary").click()}),e=p.dialog(a),e.off("shown.bs.modal"),e.on("shown.bs.modal",function(){h.focus()}),i===!0&&e.modal("show"),e},p.dialog=function(a){a=h(a);var c=b(n.dialog),d=c.find(".modal-body"),f=a.buttons,i="",j={onEscape:a.onEscape};if(g(f,function(a,b){i+="<button data-bb-handler='"+a+"' type='button' class='btn "+b.className+"'>"+b.label+"</button>",j[a]=b.callback}),d.find(".bootbox-body").html(a.message),a.animate===!0&&c.addClass("fade"),a.className&&c.addClass(a.className),a.title&&d.before(n.header),a.closeButton){var k=b(n.closeButton);a.title?c.find(".modal-header").prepend(k):k.css("margin-top","-10px").prependTo(d)}return a.title&&c.find(".modal-title").html(a.title),i.length&&(d.after(n.footer),c.find(".modal-footer").html(i)),c.on("hidden.bs.modal",function(a){a.target===this&&c.remove()}),c.on("shown.bs.modal",function(){c.find(".btn-primary:first").focus()}),c.on("escape.close.bb",function(a){j.onEscape&&e(a,c,j.onEscape)}),c.on("click",".modal-footer button",function(a){var d=b(this).data("bb-handler");e(a,c,j[d])}),c.on("click",".bootbox-close-button",function(a){e(a,c,j.onEscape)}),c.on("keyup",function(a){27===a.which&&c.trigger("escape.close.bb")}),b(a.container).append(c),c.modal({backdrop:a.backdrop,keyboard:!1,show:!1}),a.show&&c.modal("show"),c},p.setDefaults=function(){var a={};2===arguments.length?a[arguments[0]]=arguments[1]:a=arguments[0],b.extend(o,a)},p.hideAll=function(){b(".bootbox").modal("hide")};var q={br:{OK:"OK",CANCEL:"Cancelar",CONFIRM:"Sim"},da:{OK:"OK",CANCEL:"Annuller",CONFIRM:"Accepter"},de:{OK:"OK",CANCEL:"Abbrechen",CONFIRM:"Akzeptieren"},en:{OK:"OK",CANCEL:"Cancel",CONFIRM:"OK"},es:{OK:"OK",CANCEL:"Cancelar",CONFIRM:"Aceptar"},fi:{OK:"OK",CANCEL:"Peruuta",CONFIRM:"OK"},fr:{OK:"OK",CANCEL:"Annuler",CONFIRM:"D'accord"},he:{OK:"?????",CANCEL:"?????",CONFIRM:"?????"},it:{OK:"OK",CANCEL:"Annulla",CONFIRM:"Conferma"},lt:{OK:"Gerai",CANCEL:"At?aukti",CONFIRM:"Patvirtinti"},lv:{OK:"Labi",CANCEL:"Atcelt",CONFIRM:"Apstiprināt"},nl:{OK:"OK",CANCEL:"Annuleren",CONFIRM:"Accepteren"},no:{OK:"OK",CANCEL:"Avbryt",CONFIRM:"OK"},pl:{OK:"OK",CANCEL:"Anuluj",CONFIRM:"Potwierd?"},ru:{OK:"OK",CANCEL:"Отмена",CONFIRM:"Применить"},sv:{OK:"OK",CANCEL:"Avbryt",CONFIRM:"OK"},tr:{OK:"Tamam",CANCEL:"?ptal",CONFIRM:"Onayla"},zh_CN:{OK:"OK",CANCEL:"取消",CONFIRM:"确认"},zh_TW:{OK:"OK",CANCEL:"取消",CONFIRM:"確認"}};return p.init=function(c){return a(c||b)},p});

// jquery.imagesloaded.min.js
(function(c,q){var m="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==";c.fn.imagesLoaded=function(f){function n(){var b=c(j),a=c(h);d&&(h.length?d.reject(e,b,a):d.resolve(e));c.isFunction(f)&&f.call(g,e,b,a)}function p(b){k(b.target,"error"===b.type)}function k(b,a){b.src===m||-1!==c.inArray(b,l)||(l.push(b),a?h.push(b):j.push(b),c.data(b,"imagesLoaded",{isBroken:a,src:b.src}),r&&d.notifyWith(c(b),[a,e,c(j),c(h)]),e.length===l.length&&(setTimeout(n),e.unbind(".imagesLoaded",
p)))}var g=this,d=c.isFunction(c.Deferred)?c.Deferred():0,r=c.isFunction(d.notify),e=g.find("img").add(g.filter("img")),l=[],j=[],h=[];c.isPlainObject(f)&&c.each(f,function(b,a){if("callback"===b)f=a;else if(d)d[b](a)});e.length?e.bind("load.imagesLoaded error.imagesLoaded",p).each(function(b,a){var d=a.src,e=c.data(a,"imagesLoaded");if(e&&e.src===d)k(a,e.isBroken);else if(a.complete&&a.naturalWidth!==q)k(a,0===a.naturalWidth||0===a.naturalHeight);else if(a.readyState||a.complete)a.src=m,a.src=d}):
n();return d?d.promise(g):g}})(jQuery);

/*! jQuery JSON plugin 2.4.0 | code.google.com/p/jquery-json */
(function($){'use strict';var escape=/["\\\x00-\x1f\x7f-\x9f]/g,meta={'\b':'\\b','\t':'\\t','\n':'\\n','\f':'\\f','\r':'\\r','"':'\\"','\\':'\\\\'},hasOwn=Object.prototype.hasOwnProperty;$.toJSON=typeof JSON==='object'&&JSON.stringify?JSON.stringify:function(o){if(o===null){return'null';}
var pairs,k,name,val,type=$.type(o);if(type==='undefined'){return undefined;}
if(type==='number'||type==='boolean'){return String(o);}
if(type==='string'){return $.quoteString(o);}
if(typeof o.toJSON==='function'){return $.toJSON(o.toJSON());}
if(type==='date'){var month=o.getUTCMonth()+1,day=o.getUTCDate(),year=o.getUTCFullYear(),hours=o.getUTCHours(),minutes=o.getUTCMinutes(),seconds=o.getUTCSeconds(),milli=o.getUTCMilliseconds();if(month<10){month='0'+month;}
if(day<10){day='0'+day;}
if(hours<10){hours='0'+hours;}
if(minutes<10){minutes='0'+minutes;}
if(seconds<10){seconds='0'+seconds;}
if(milli<100){milli='0'+milli;}
if(milli<10){milli='0'+milli;}
return'"'+year+'-'+month+'-'+day+'T'+
hours+':'+minutes+':'+seconds+'.'+milli+'Z"';}
pairs=[];if($.isArray(o)){for(k=0;k<o.length;k++){pairs.push($.toJSON(o[k])||'null');}
return'['+pairs.join(',')+']';}
if(typeof o==='object'){for(k in o){if(hasOwn.call(o,k)){type=typeof k;if(type==='number'){name='"'+k+'"';}else if(type==='string'){name=$.quoteString(k);}else{continue;}
type=typeof o[k];if(type!=='function'&&type!=='undefined'){val=$.toJSON(o[k]);pairs.push(name+':'+val);}}}
return'{'+pairs.join(',')+'}';}};$.evalJSON=typeof JSON==='object'&&JSON.parse?JSON.parse:function(str){return eval('('+str+')');};$.secureEvalJSON=typeof JSON==='object'&&JSON.parse?JSON.parse:function(str){var filtered=str.replace(/\\["\\\/bfnrtu]/g,'@').replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,']').replace(/(?:^|:|,)(?:\s*\[)+/g,'');if(/^[\],:{}\s]*$/.test(filtered)){return eval('('+str+')');}
throw new SyntaxError('Error parsing JSON, source is not valid.');};$.quoteString=function(str){if(str.match(escape)){return'"'+str.replace(escape,function(a){var c=meta[a];if(typeof c==='string'){return c;}
c=a.charCodeAt();return'\\u00'+Math.floor(c/16).toString(16)+(c%16).toString(16);})+'"';}
return'"'+str+'"';};}(jQuery));

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

    $.fn.image_box = function(min_width, min_height, gallery, parent){
        min_width = min_width || 160;
        min_height = min_height || 120;

        var $this = $(this);
        // remove non image elem
        var $this = $.map($this, function (item, index) {
            var $img = $(item);
            if ($img.is("img") && $img.width()>=min_width && $img.height()>=min_height) {
                return item;
            } else {
                return null;
            }
        });

        var total = $this.length;
        $.each($this, function(index, item){
            var $img = $(item);
            var src = $img.attr("src");
            if ($img.attr("real_src")){
                src = $img.attr("real_src");
            }
            if(src.endsWith("==") || src.endsWith("==/") || src.match(/\.ggpht\.com\/\S+/g)
                || src.match(/\.googleusercontent\.com\/\S+/g)) {
                if (! src.match(/(=s\d+)$/g)) {
                    src = src+"=s0";
                }
            }
            $img.attr("data-toggle", "lightbox").attr("href", src)
                .attr("data-gallery", gallery || "")
                .attr("data-parent", parent || "")
                .attr("data-type", "image")
                .attr("data-title", $img.prop("alt"));
        });
        return $(this);
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
                var img_padding_top = parseInt(img.css("padding-top").replace("px", ""));
                var img_padding_bottom = parseInt(img.css("padding-bottom").replace("px", ""));
                var img_info_parent = img.parents(".img_info_parent");
                var parent_scroll_left = img_info_parent.scrollLeft();
                var parent_scroll_top = img_info_parent.scrollTop();

                img.next(".img_info").remove();
                img.after(info_div);
                info_div.css({
                    'background': "rgba(0, 0, 0, 0.5)",
                    'font-size': '1.4em',
                    'position': "absolute",
                    'color': "#eee",
                    'padding': "10px",
                    'left': img.position().left + parent_scroll_left + img_margin_left + "px",
                    'width': img.outerWidth() + "px"
                });
                info_div.css({
                    'top': img.position().top + parent_scroll_top + img.height() + img_margin_top -
                        info_div.outerHeight() + img_padding_bottom + img_padding_top + "px"
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
