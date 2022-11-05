jQuery(document).ready(function($){"use strict";$('form.contactForm').submit(function(){var f=$(this).find('.form-group'),ferror=!1,emailExp=/^[^\s()<>@,;:\/]+@\w[\w\.-]+\.[a-z]{2,}$/i;f.children('input').each(function(){var i=$(this);var rule=i.attr('data-rule');if(rule!==undefined){var ierror=!1;var pos=rule.indexOf(':',0);if(pos>=0){var exp=rule.substr(pos+1,rule.length);rule=rule.substr(0,pos)}else{rule=rule.substr(pos+1,rule.length)}
switch(rule){case 'required':if(i.val()===''){ferror=ierror=!0}
break;case 'minlen':if(i.val().length<parseInt(exp)){ferror=ierror=!0}
break;case 'email':if(!emailExp.test(i.val())){ferror=ierror=!0}
break;case 'checked':if(!i.is(':checked')){ferror=ierror=!0}
break;case 'regexp':exp=new RegExp(exp);if(!exp.test(i.val())){ferror=ierror=!0}
break}
i.next('.validation').html((ierror?(i.attr('data-msg')!==undefined?i.attr('data-msg'):'wrong Input'):'')).show('blind')}});f.children('textarea').each(function(){var i=$(this);var rule=i.attr('data-rule');if(rule!==undefined){var ierror=!1;var pos=rule.indexOf(':',0);if(pos>=0){var exp=rule.substr(pos+1,rule.length);rule=rule.substr(0,pos)}else{rule=rule.substr(pos+1,rule.length)}
switch(rule){case 'required':if(i.val()===''){ferror=ierror=!0}
break;case 'minlen':if(i.val().length<parseInt(exp)){ferror=ierror=!0}
break}
i.next('.validation').html((ierror?(i.attr('data-msg')!=undefined?i.attr('data-msg'):'wrong Input'):'')).show('blind')}});if(ferror)return!1;else var str=$(this).serialize();var action=$(this).attr('action');if(!action){action='contactform/contactform.php'}
$.ajax({type:"POST",url:action,data:str,success:function(msg){if(msg=='OK'){$("#sendmessage").addClass("show");$("#errormessage").removeClass("show");$('.contactForm').find("input, textarea").val("")}else{$("#sendmessage").removeClass("show");$("#errormessage").addClass("show");$('#errormessage').html(msg)}}});return!1})})