odoo.define('vpcs_survey_fields.survey', function (require) {
'use strict';

var survey = require('survey.survey');
/*
 * This file is intended to add interactivity to survey forms
 */
var the_form = $('.js_surveyform');
if(!the_form.length) {
    return $.Deferred().reject("DOM doesn't contain '.js_surveyform' - Translator");
}

var cprefill_controller = the_form.attr("data-prefill").replace('prefill', 'cprefill');
var submit_controller = the_form.attr("data-submit");
var print_mode = false;

if (_.isUndefined(submit_controller)) {
    print_mode = true;
    $('#js_add_item').parents('tr').remove();
}

var index = 1;

function cprefill(){
    var prefill_def = $.ajax(cprefill_controller, {dataType: "json"})
        .done(function(json_data){
            _.each(json_data, function(value, prefix){
                var input = the_form.find(".form-control[name='" + prefix + "'], img[name='"+prefix+"']");
                if (input.length){
                    if (input[0].type == 'file'){
                        input.replaceWith("<input type='text' readonly='readonly' class='form-control' value='"+value+"' disabled='disabled'/>");
                    }
                    else if (input.length > 0 && input[0].nodeName == "IMG"){
                        input.attr('src', "data:image/png;base64," + value);
                    }
                    else {
                        input.val(value);
                    }
                }
                else if(_.isObject(value)){
                    _.each(value, function(v, k){
                        the_form.find(".form-control[name='" + k + "'], select[name='" + k + "']").val(v);
                    });
                }
            });
        })
        .fail(function(){
            console.warn("[survey] CPrefill failed to load data");
        });
    return prefill_def;
}

if (! _.isUndefined(cprefill_controller)) {
    cprefill();
}

});
