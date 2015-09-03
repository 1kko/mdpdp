;(function ($) {
    'use strict';

    var collapser = function(collapsed) {
        var item = $('<span />', {
            'class': 'collapser',
            on: {
                click: function() {
                    var $this = $(this);

                    $this.toggleClass('collapsed');
                    var block = $this.parent().children('.block');
                    var ul = block.children('ul');

                    if ($this.hasClass('collapsed')) {
                        ul.hide();
                        block.children('.dots, .comments').show();
                    } else {
                        ul.show();
                        block.children('.dots, .comments').hide();
                    }
                }
            }
        });

        if (collapsed) {
            item.addClass('collapsed');
        }

        return item;
    };

    var formatter = function(json, opts) {
        var options = $.extend({}, {
            nl2br: true
        }, opts);

        var htmlEncode = function(html) {
            if (!html.toString()) {
                return '';
            }

            return html.toString().replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        };

        var span = function(val, cls) {
            return $('<span />', {
                'class': cls,
                html: htmlEncode(val)
            });
        };

        var parentList=[];
        var genBlock = function(val, level) {
            switch($.type(val)) {
                case 'object':
                    if (!level) {
                        level = 0;
                    }

                    var output = $('<span />', {
                        'class': 'block'
                    });

                    var cnt = Object.keys(val).length;
                    if (!cnt) {
                        return output
                            .append(span('{', 'b'))
                            .append(' ')
                            .append(span('}', 'b'));
                    }

                    output.append(span('{', 'b'));

                    var items = $('<ul />', {
                        'class': 'obj collapsible level' + level
                    });

                    $.each(val, function(key, data) {
                        parentList.push(key);
                        cnt--;
                        var item = $('<li />')
                            .append(span('"', 'q'))
                            .append(key)
                            .append(span('"', 'q'))
                            .append(': ')
                            .append(genBlock(data, level + 1));

                        if (['object', 'array'].indexOf($.type(data)) !== -1 && !$.isEmptyObject(data)) {
                            item.prepend(collapser());
                            parentList.pop();
                        }

                        if (cnt > 0) {
                            item.append(',');
                        }

                        items.append(item);
                    });

                    output.append(items);
                    output.append(span('...', 'dots'));
                    output.append(span('}', 'b'));
                    if (Object.keys(val).length === 1) {
                        output.append(span('// 1 item', 'comments'));
                    } else {
                        output.append(span('// ' + Object.keys(val).length + ' items', 'comments'));
                    }

                    return output;

                case 'array':
                    if (!level) {
                        level = 0;
                    }

                    var cnt = val.length;

                    var output = $('<span />', {
                        'class': 'block'
                    });

                    if (!cnt) {
                        return output
                            .append(span('[', 'b'))
                            .append(' ')
                            .append(span(']', 'b'));
                    }

                    output.append(span('[', 'b'));

                    var items = $('<ul />', {
                        'class': 'obj collapsible level' + level
                    });

                    $.each(val, function(key, data) {
                        // parentList.push(key);
                        cnt--;
                        var item = $('<li />')
                            .append(genBlock(data, level + 1));

                        if (['object', 'array'].indexOf($.type(data)) !== -1 && !$.isEmptyObject(data)) {
                            item.prepend(collapser());
                        }

                        if (cnt > 0) {
                            item.append(',');
                        }

                        items.append(item);
                        // parentList.pop();
                    });

                    output.append(items);
                    output.append(span('...', 'dots'));
                    output.append(span(']', 'b'));
                    if (val.length === 1) {
                        output.append(span('// 1 item', 'comments'));
                    } else {
                        output.append(span('// ' + val.length + ' items', 'comments'));
                    }

                    return output;

                case 'string':
                    val = htmlEncode(val);
                    if (/^(http|https|file):\/\/[^\s]+$/i.test(val)) {
                        return $('<span />')
                            .append(span('"', 'q'))
                            .append($('<a />', {
                                href: val,
                                text: val
                            }))
                            .append(span('"', 'q'));
                    }
                    if (options.nl2br) {
                        var pattern = /\n/g;
                        if (pattern.test(val)) {
                            val = (val + '').replace(pattern, '<br />');
                        }
                    }

                    // console.log(parentList);
                    var parpath=parentList.join(".");
                    parentList.pop();

                    var text = $('<a />', { 'class': 'value str', 'href':'#/', 'path':parpath}).html(val);

                    return $('<span />')
                        .append(span('"', 'q'))
                        .append(text)
                        .append(span('"', 'q'));

                case 'number':
                    // console.log(parentList);
                    var parpath=parentList.join(".");
                    parentList.pop();
                    var retval=$('<a />', {'class':'value  num', 'href':'#/', 'path':parpath}).html(val.toString());
                    // return span(val.toString(), 'num');
                    return retval;

                case 'undefined':
                    // console.log(parentList);
                    var parpath=parentList.join(".");
                    parentList.pop();
                    var retval=$('<a />', {'class':'value  undef', 'href':'#/', 'path':parpath}).html('undefined');
                    // return span('undefined', 'undef');
                    return retval;

                case 'null':
                    // console.log(parentList);
                    var parpath=parentList.join(".");
                    parentList.pop();
                    var retval=$('<a />', {'class':'value  null', 'href':'#/', 'path':parpath}).html('null');
                    // return span('null', 'null');
                    return retval;

                case 'boolean':
                    // console.log(parentList);
                    var parpath=parentList.join(".");
                    parentList.pop();
                    var retval=$('<a />', {'class':'value bool', 'href':'#/', 'path':parpath}).html(val.toString());
                    // return span(val ? 'true' : 'false', 'bool');
                    return retval;
            }
        };

        return genBlock(json);        
    };

    var jsonview = function(json, options) {
        var $this = $(this);

        options = $.extend({}, {
            nl2br: true
        }, options);

        if (typeof json === 'string') {
            try {
                json = JSON.parse(json);
            } catch (err) {
            }
        }

        $this.append($('<div />', {
            class: 'json-view'
        }).append(formatter(json, options)));

        return $this;
    };
    return $.fn.jsonView=jsonview;
})(jQuery);
