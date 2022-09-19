odoo.define('vitalpet_onboarding', function (require) {
	"use strict";

	var core = require('web.core');
	var SystrayMenu = require('web.SystrayMenu');
	var Widget = require('web.Widget');
	var tree=require('web.TreeView');
	var QWeb = core.qweb;
	var Model = require('web.Model');
	var web_client = require('web.web_client');
	var utils = require('web.utils');

var GetStarted = Widget.extend ({
		init: function() {
			
			var arg1=$(".form_id").text();			
		    var self = this;
			var hr_onboarding = new Model('hr.employee.onboarding');
			hr_onboarding.call('get_started_info', [[1], arg1])
			.then(function(get_started_dict) {
					if(get_started_dict){
						$(".smart_buttons_list").each(function(){
							$(this).find("button").eq(0).find("span.o_form_field_number").text(parseFloat(get_started_dict.score).toFixed(2));
						});
						if(get_started_dict.priority == 0){
							$('.good').attr("class","o_priority_star fa fa-star-o priority_very_good good");
							$('.very_good').attr("class","o_priority_star fa fa-star-o priority_very_good very_good");
							$('.excellent').attr("class",'o_priority_star fa fa-star-o priority_excellent excellent');
							$('.good').attr("style","color: #666666 !important;");
							$('.very_good').attr("style","color: #666666 !important;");
							$('.excellent').attr("style","color: #666666 !important;");
						}
						if(get_started_dict.priority == 1){
							$('.very_good').attr("class","o_priority_star fa fa-star-o priority_very_good very_good");
							$('.excellent').attr("class",'o_priority_star fa fa-star-o priority_excellent excellent');
							$('.very_good').attr("style","color: #666666 !important;");
							$('.excellent').attr("style","color: #666666 !important;");
						}
						if(get_started_dict.priority == 2){
							$('.excellent').attr("class",'o_priority_star fa fa-star-o priority_excellent excellent');
							$('.excellent').attr("style","color: #666666 !important;");
						}
						$(".form_name").html(get_started_dict.name);
						$(".form_phone").html(get_started_dict.phone);
						$(".form_email").html(get_started_dict.mail);
						$(".form_applied_job").html(get_started_dict.applied_job);
						$(".form_applicant_id").html(get_started_dict.applicant_id);
						$(".form_company").html(get_started_dict.company);
						$(".form_responsible").html(get_started_dict.responsible);
						$(".form_expected_salary").html(get_started_dict.expected_salary);
						$(".form_proposed_salary").html(get_started_dict.proposed_salary);
						$(".form_availability").html(get_started_dict.available);
						$(".form_pay_type").val(get_started_dict.pay_type);
						
						$(".form_contract_type").html("<option value=''></option>");
						$.each(get_started_dict.contract_type_disp, function(key,val) {
							$(".form_contract_type").append("<option value='"+key+"'>"+val+"</option>");
						});
						$(".form_contract_type").val(get_started_dict.contract_type);
						var name = get_started_dict.name
						$(".emp_name").text(get_started_dict.name+' has been Successfully Onboarded.');
						
					}
			});
	   }
});

var InsertValsGetStarted = Widget.extend ({
		init: function() {
			var arg1=$(".form_id").text();
			var get_started = {con_typ:$(".form_contract_type").val(), pay_typ:$(".form_pay_type").val()};
			var hr_onboarding = new Model('hr.employee.onboarding');
			hr_onboarding.call('insert_records_get_started', [[1], arg1,get_started])
			.then(function(result_vals) {		
				if(result_vals=='started'){
					alert('Please send the PID document');
				}
				else{
					$(".btn-next").click();
				}
			});
		}
});

var PersonalInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('personalinfo', [[1], arg1])
		.then(function(personal_info_dict) {
				if(personal_info_dict){
					$(".form_pob").val(personal_info_dict.place_of_birth);
					$(".form_id_no").val(personal_info_dict.id_no);
					$(".form_passport_no").val(personal_info_dict.passport_no);
					$(".form_driving_license_no").val(personal_info_dict.dl_no);
					$(".form_street").val(personal_info_dict.street);
					$(".form_street2").val(personal_info_dict.street2);
					$(".form_city").val(personal_info_dict.city);
					// $(".form_bio").val(personal_info_dict.notes);


					$(".form_state").html("<option value=''></option>");
					$.each(personal_info_dict.state_dict, function(key,val) {
						$(".form_state").append("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_state").val(personal_info_dict.state);

					$(".form_zip").val(personal_info_dict.zip);
					$(".form_first_name_alias").val(personal_info_dict.first_name_alias);
					$(".form_middle_name_alias").val(personal_info_dict.middle_name_alias);
					$(".form_last_name_alias").val(personal_info_dict.last_name_alias);
					$(".form_gender").val(personal_info_dict.gender);
					$(".form_marital_status").val(personal_info_dict.marital_status);
					$(".form_filing_status").val(personal_info_dict.filing_staus);
					$(".form_children").val(personal_info_dict.children);
					$(".form_ethnic_id").val(personal_info_dict.ethnic_id);
					$(".form_smoker").val(personal_info_dict.smoker);
					$(".form_dob").val(personal_info_dict.dob);
					$(".form_age").val(personal_info_dict.age);
					$(".form_emergency_name").val(personal_info_dict.emergency_contact_name);
					$(".form_relationship").val(personal_info_dict.emergency_contact_relationship);
					$(".form_emergency_phone").val(personal_info_dict.emergency_contact_phone);

					$(".form_birth_country").html("<option value=''></option>");
					$(".form_country").html("<option value=''></option>");
					$(".form_nationality").html("<option value=''></option>");
					$.each(personal_info_dict.country, function(key,val) {
						$(".form_country").append("<option value='"+key+"'>"+val+"</option>");
						$(".form_nationality").append("<option value='"+key+"'>"+val+"</option>");
						$(".form_birth_country").append("<option value='"+key+"'>"+val+"</option>");
						
					});
					$(".form_country").val(personal_info_dict.country_id);
					$(".form_nationality").val(personal_info_dict.nationality);
					$(".form_birth_country").val(personal_info_dict.birth_country);
				}
		});
   }
});

var ChangeState = Widget.extend ({
	init: function() {
		var country_id=$(".form_country").val();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('change_state_name', [[1], country_id]).then(function(state_dict) {
			if(state_dict){
				var old_val=$(".form_state").val();
				$(".form_state").html("<option value=''></option>");
				$.each(state_dict, function(key,val) {
					$(".form_state").append("<option value='"+key+"'>"+val+"</option>");
				});
				$(".form_state").val(old_val);
			}				
		});
   }
});

var ChangeCountry = Widget.extend ({
	init: function() {
		var state_id=$(".form_state").val();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('change_country_name', [[1], state_id]).then(function(result_vals) {
			if(result_vals){
				$(".form_country").val(result_vals);
			}				
		});
   }
});

var InsertValsPersonalInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var personal_info = {
				id_no:$(".form_id_no").val(), 
				passport_no:$(".form_passport_no").val(),
				dl_no:$(".form_driving_license_no").val(),
				street:$(".form_street").val(),
				street2:$(".form_street2").val(),
				city:$(".form_city").val(),
				state:$(".form_state").val(),
				country:$(".form_country").val(),
				zip:$(".form_zip").val(),
				fst_name_alias:$(".form_first_name_alias").val(),
				mid_name_alias:$(".form_middle_name_alias").val(),
				lst_name_alias:$(".form_last_name_alias").val(),
				emergency_contact_name:$(".form_emergency_name").val(),
				emergency_contact_relationship:$(".form_relationship").val(),
				emergency_contact_phone:$(".form_emergency_phone").val(),
				gender:$(".form_gender").val(),
				nationality:$(".form_nationality").val(),
				birth_country:$(".form_birth_country").val(),
				marital_sts:$(".form_marital_status").val(),
				filing_sts:$(".form_filing_status").val(),
				noc:$(".form_children").val(),
				ethnic:$(".form_ethnic_id").val(),
				smoker:$(".form_smoker").val(),
				dob:$(".form_dob").val(),
				age:$(".form_age").val(),
				place_of_birth:$(".form_pob").val(),
			};
		var hr_onboarding = new Model('hr.employee.onboarding');
		console.log(hr_onboarding);
		hr_onboarding.call('insert_records_personal_info', [[1], arg1,personal_info])
		.then(function(result_vals) {
			// alert(result_vals);
			if(result_vals == 'experience'){
				$(".btn-next").click();
			}
			else{
			}
		});
   }
});

var ExperienceInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('experienceinfo', [[1], arg1])
		.then(function(experience_info_dict) {
				if(experience_info_dict){
					$.each(experience_info_dict.state_dict, function(key,val) {
						$(".form_certification_exp_state_issued").append("<option value='"+key+"'>"+val+"</option>");
					});
					$.each(experience_info_dict, function(key_main,exp_val) { 
					
					if(key_main=='exp_academic_list'){		
						var i=0;
							$.each(exp_val, function(key,aca_val) {
								if(i==0){
									$(".form_academic_exp_tree_id").val(aca_val['academic_tree_id']);
									$(".form_academic_exp").val(aca_val['academic_experience']);
									$(".form_academic_institution").val(aca_val['institute']);
									$(".form_academic_diploma").val(aca_val['diploma']);
									$(".form_academic_fos").val(aca_val['field_of_study']);
									$(".form_academic_start_date").val(aca_val['start_date']);
									$(".form_academic_end_date").val(aca_val['end_date']);
									i++;
								}else{
									if(i==1){
										$(".academic_exp_offer_accepted tbody").find("tr:gt(1)").remove();
									}
									$(".academic_exp_offer_accepted tbody").append("<tr class='inc"+i+"'>"+$(".academic_exp_offer_accepted tr").eq(1).html()+"</tr>");
									
									$(".inc"+i+" .form_academic_exp_tree_id").val(aca_val['academic_tree_id']);								
									$(".inc"+i+" .form_academic_exp").val(aca_val['academic_experience']);
									$(".inc"+i+" .form_academic_institution").val(aca_val['institute']);
									$(".inc"+i+" .form_academic_diploma").val(aca_val['diploma']);
									$(".inc"+i+" .form_academic_fos").val(aca_val['field_of_study']);
									$(".inc"+i+" .form_academic_start_date").val(aca_val['start_date']);
									$(".inc"+i+" .form_academic_end_date").val(aca_val['end_date']);
									i++;
								}
							});									
						}
					if(key_main=='exp_professional_list'){
						var i=0;
						$.each(exp_val, function(key,pro_val) {
							if(i==0){
								$(".form_professional_exp_tree_id").val(pro_val['professional_tree_id']);
								$(".form_professional_exp_position").val(pro_val['position']);
								$(".form_professional_exp_employer").val(pro_val['employer']);
								$(".form_professional_exp_start_date").val(pro_val['start_date']);
								$(".form_professional_exp_end_date").val(pro_val['end_date']);
								i++;
							}else{
								if(i==1){
									$(".professional_exp_offer_accepted tbody").find("tr:gt(1)").remove();
								}
								$(".professional_exp_offer_accepted tbody").append("<tr class='inc"+i+"'>"+$(".professional_exp_offer_accepted tr").eq(1).html()+"</tr>");
								$(".inc"+i+" .form_professional_exp_tree_id").val(pro_val['professional_tree_id']);											
								$(".inc"+i+" .form_professional_exp_position").val(pro_val['position']);
								$(".inc"+i+" .form_professional_exp_employer").val(pro_val['employer']);
								$(".inc"+i+" .form_professional_exp_start_date").val(pro_val['start_date']);
								$(".inc"+i+" .form_professional_exp_end_date").val(pro_val['end_date']);
								i++;
							}
						});
						
						}
					if(key_main=='exp_certificate_list'){
						var i=0;
						$.each(exp_val, function(key,aca_val) {
							if(i==0){
								$(".form_certification_exp_tree_id").val(aca_val['certification_tree_id']);
								$(".form_certification_exp_certificate").val(aca_val['certifications']);
								$(".form_certification_exp_certificate_code").val(aca_val['certificate_code']);
								$(".form_certification_exp_issued_by").val(aca_val['issued_by']);
								if (aca_val['professional_license'] == true){
									$(".form_certification_exp_professional_license").attr('checked','checked');
								}
								$(".form_certification_exp_state_issued").val(aca_val['state_issued_id']);
								$(".form_certification_exp_start_date").val(aca_val['start_date']);
								$(".form_certification_exp_end_date").val(aca_val['end_date']);
								i++;
							}else{
								if(i==1){
									$(".certification_exp_offer_accepted tbody").find("tr:gt(1)").remove();
								}
								$(".certification_exp_offer_accepted tbody").append("<tr class='inc"+i+"'>"+$(".certification_exp_offer_accepted tr").eq(1).html()+"</tr>");
								$(".inc"+i+" .form_certification_exp_tree_id").val(aca_val['certification_tree_id']);											
								$(".inc"+i+" .form_certification_exp_certificate").val(aca_val['certifications']);
								$(".inc"+i+" .form_certification_exp_certificate_code").val(aca_val['certificate_code']);
								$(".inc"+i+" .form_certification_exp_issued_by").val(aca_val['issued_by']);
								if (aca_val['professional_license'] == true){
									$(".inc"+i+" .form_certification_exp_professional_license").attr('checked','checked');
								}
								$(".inc"+i+" .form_certification_exp_state_issued").val(aca_val['state_issued_id']);
								$(".inc"+i+" .form_certification_exp_start_date").val(aca_val['start_date']);
								$(".inc"+i+" .form_certification_exp_end_date").val(aca_val['end_date']);
								i++;
							}
						});
						
						}
							
			        });   
					
				}else{

				}
		});
   }
});

var InsertValsExpirenceInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var n=0;
		$('.academic_exp_offer_accepted tr').each(function(){
			if(n>=1){
				var offer_accepted_academic_info = {
					academic_tree_id:$(this).find('.form_academic_exp_tree_id').val(), 
					academic_exp:$(this).find('.form_academic_exp').val(),
					academic_institution:$(this).find('.form_academic_institution').val(),
					academic_diploma:$(this).find('.form_academic_diploma').val(),
					academic_fos:$(this).find('.form_academic_fos').val(),
					academic_start:$(this).find('.form_academic_start_date').val(),
					academic_end:$(this).find('.form_academic_end_date').val(),
				};
			    var hr_onboarding = new Model('hr.employee.onboarding');
				hr_onboarding.call('insert_records_experience_academic_info', [[1], arg1,offer_accepted_academic_info])
				.then(function() {
				});
			}
			n++;
		});
		var m=0;
		$('.professional_exp_offer_accepted tr').each(function(){
			if(m>=1){
				var offer_accepted_professional_info = {
					professional_tree_id:$(this).find('.form_professional_exp_tree_id').val(), 
					position:$(this).find('.form_professional_exp_position').val(),
					employer:$(this).find('.form_professional_exp_employer').val(),
					professional_start:$(this).find('.form_professional_exp_start_date').val(),
					professional_end:$(this).find('.form_professional_exp_end_date').val(),
				};
			    var hr_onboarding = new Model('hr.employee.onboarding');
				hr_onboarding.call('insert_records_experience_professional_info', [[1], arg1,offer_accepted_professional_info])
				.then(function() {
				});
			}
			m++;
		});
		var p=0;
		$('.certification_exp_offer_accepted tr').each(function(){
			var req = 0;
			if(p>=1){
				var professional_license_val = ''
				if($(this).find('.form_certification_exp_professional_license').is(':checked')){
					professional_license_val = true
				}
				var offer_accepted_certificate_info = {
					certificate_tree_id:$(this).find('.form_certification_exp_tree_id').val(), 
					certificate:$(this).find('.form_certification_exp_certificate').val(),
					certificate_no:$(this).find('.form_certification_exp_certificate_code').val(),
					issued_by:$(this).find('.form_certification_exp_issued_by').val(),
					professional_license:professional_license_val,
					state_issued_id:$(this).find('.form_certification_exp_state_issued').val(),
					certificate_start:$(this).find('.form_certification_exp_start_date').val(),
					certificate_end:$(this).find('.form_certification_exp_end_date').val(),
				};
				if (offer_accepted_certificate_info['certificate'] && offer_accepted_certificate_info['certificate_no'] && offer_accepted_certificate_info['issued_by'] && offer_accepted_certificate_info['state_issued_id'] && offer_accepted_certificate_info['certificate_start'] && offer_accepted_certificate_info['certificate_end']) {
					req=0;
//							alert('Please Complete the details');
				}
				else if (offer_accepted_certificate_info['certificate'] || offer_accepted_certificate_info['certificate_no'] || offer_accepted_certificate_info['issued_by'] || offer_accepted_certificate_info['state_issued_id'] || offer_accepted_certificate_info['certificate_start'] || offer_accepted_certificate_info['certificate_end']) {
					req=1;
//					alert('Please Complete the details');
				}
				if(req==1) {
					if (offer_accepted_certificate_info['certificate'] == '') {
						$(this).find(".form_certification_exp_certificate").attr("style","border-bottom: 2px solid #f00 !important;");
						
					}
					else {
						
						$(this).find(".form_certification_exp_certificate").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (offer_accepted_certificate_info['certificate_no'] == '') {
						$(this).find(".form_certification_exp_certificate_code").attr("style","border-bottom: 2px solid #f00 !important;");
						
					}
					else {
						
						$(this).find(".form_certification_exp_certificate_code").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (offer_accepted_certificate_info['issued_by'] == '') {
						$(this).find(".form_certification_exp_issued_by").attr("style","border-bottom: 2px solid #f00 !important;");
						
					}
					else {
						
						$(this).find(".form_certification_exp_issued_by").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (offer_accepted_certificate_info['state_issued_id'] == '') {
						$(this).find(".form_certification_exp_state_issued").attr("style","border-bottom: 2px solid #f00 !important;");
						
					}
					else {
						
						$(this).find(".form_certification_exp_state_issued").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (offer_accepted_certificate_info['certificate_start'] == '') {
						$(this).find(".form_certification_exp_start_date").attr("style","border-bottom: 2px solid #f00 !important;");
						
					}
					else {
						
						$(this).find(".form_certification_exp_start_date").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (offer_accepted_certificate_info['certificate_end'] == '') {
						$(this).find(".form_certification_exp_end_date").attr("style","border-bottom: 2px solid #f00 !important;");
						
					}
					else {
						
						$(this).find(".form_certification_exp_end_date").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
//					alert('Please Complete the details');
				}
				if(req==1) {
				
					alert('Please Complete the details');
				}
				else{
					    var hr_onboarding = new Model('hr.employee.onboarding');
						hr_onboarding.call('insert_records_experience_certification_info', [[1], arg1,offer_accepted_certificate_info])
						.then(function() {
						});
						var substate_name = 'employement';
						var state_name = 'offer';
					    var hr_onboarding_state = new Model('hr.employee.onboarding');
						hr_onboarding_state.call('change_status', [[1], arg1,substate_name,state_name])
						.then(function() {
						});
						$(".btn-next").click();
					}
			}
			p++;
		});

		// var substate_name = 'employement';
		// var state_name = 'offer';
	 //    var hr_onboarding_state = new Model('hr.employee.onboarding');
		// hr_onboarding_state.call('change_status', [[1], arg1,substate_name,state_name])
		// .then(function() {
		// });

   }
}); 

var EmployementInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('employementinfo', [[1], arg1])
		.then(function(employement_info_dict) {
			if(employement_info_dict){
				$(".form_contract_type").val(employement_info_dict.contract_type)
				$(".form_start_date").val(employement_info_dict.emp_start_date);					
				$(".form_benefits_seniority_date").val(employement_info_dict.benifits_seniority_date);


				$(".form_job_seniority_title").html("<option value=''></option>");
				$.each(employement_info_dict.job_seniority_title_disp, function(job_key,job_val) {
					$(".form_job_seniority_title").append("<option value='"+job_key+"'>"+job_val+"</option>");
				});					
				$(".form_job_seniority_title").val(employement_info_dict.job_seniority_title);

			}
		});
   }
});

var InsertValsEmployementInfo = Widget.extend ({
	init: async function() {
		var arg1=$(".form_id").text();
		var employement_info = {
			job_seniority_title:$(".form_job_seniority_title").val(), 
			start_date:$(".form_start_date").val()
		};
		let promise = new Promise((resolve, reject) => {
			// setTimeout(function(){
				var hr_onboarding = new Model('hr.employee.onboarding');
				hr_onboarding.call('insert_records_employement_info', [[1], arg1,employement_info])
				.then(function(result_vals) {
					resolve(result_vals);
				});
			// },10000);
		});
		let result = await promise;
		if(result){
			$(".btn-next").click();
		}
   	}
});

var OfferSummary = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();			
	    var self = this;
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('offer_summary', [[1], arg1])
		.then(function(offer_summary_dict) {
				if(offer_summary_dict){
					$(".form_summary_name").val(offer_summary_dict.name);
					$(".form_summary_phone").val(offer_summary_dict.phone);
					$(".form_summary_mail").val(offer_summary_dict.mail);
					$(".form_summary_applied_job").val(offer_summary_dict.applied_job);
					$(".form_summary_applicant_id").val(offer_summary_dict.applicant_id);
					$(".form_summary_company").val(offer_summary_dict.company);
					$(".form_summary_responsible").val(offer_summary_dict.responsible);
					$(".form_summary_id_number").val(offer_summary_dict.id_no);
					$(".form_summary_passport_number").val(offer_summary_dict.passport_no);
					$(".form_street").val(offer_summary_dict.street);
					$(".form_street2").val(offer_summary_dict.street2);
					$(".form_city").val(offer_summary_dict.city);
					$(".form_summary_state").val(offer_summary_dict.state);
					$(".form_summary_country").val(offer_summary_dict.country_id);
					$(".form_zip").val(offer_summary_dict.zip);
					$(".form_summary_gender").val(offer_summary_dict.gender);
					$(".form_summary_marital_status").val(offer_summary_dict.marital_status);
					$(".form_summary_filing_status").val(offer_summary_dict.filing_status);
					$(".form_summary_noc").val(offer_summary_dict.children);
					$(".form_summary_dob").val(offer_summary_dict.dob);
					$(".form_summary_age").val(offer_summary_dict.age);
					$(".form_summary_scheduled_hours").val(offer_summary_dict.scheduled_hours);
					$(".form_summary_pay_rate").val(offer_summary_dict.pay_rate);
					$(".form_summary_start_date").val(offer_summary_dict.emp_start_date);		
					$(".form_job_seniority_title").val(offer_summary_dict.job_seniority_title);
					$(".form_summary_ben_sen_date").val(offer_summary_dict.benifits_seniority_date);
					$(".form_summary_country").val(offer_summary_dict.nationality);
					$(".form_summary_nationality").val(offer_summary_dict.nationality);
					$(".form_summary_birth_country").val(offer_summary_dict.birth_country);	

					$(".form_summary_employment_status").html("<option value=''></option>");
					$.each(offer_summary_dict.emp_sts_disp, function(job_key,job_val) {
						$(".form_summary_employment_status").append("<option value='"+job_key+"'>"+job_val+"</option>");
					});	
					$(".form_summary_employment_status").val(offer_summary_dict.emp_status);

					$(".form_summary_pob").val(offer_summary_dict.place_of_birth);
					$.each(offer_summary_dict, function(key_main,exp_val) { 
						
						if(key_main=='exp_academic_list'){		
							var i=0;
								$.each(exp_val, function(key,aca_val) {
									if(i==0){
										$(".form_academic_exp_tree_id").val(aca_val['academic_tree_id']);
										$(".form_academic_exp").val(aca_val['academic_experience']);
										$(".form_academic_institution").val(aca_val['institute']);
										$(".form_academic_diploma").val(aca_val['diploma']);
										$(".form_academic_fos").val(aca_val['field_of_study']);
										$(".form_academic_start_date").val(aca_val['start_date']);
										$(".form_academic_end_date").val(aca_val['end_date']);
										i++;
									}else{
										if(i==1){
											$(".academic_exp_offer_accepted_summary tbody").find("tr:gt(1)").remove();
										}
										$(".academic_exp_offer_accepted_summary tbody").append("<tr class='inc"+i+"'>"+$(".academic_exp_offer_accepted_summary tr").eq(1).html()+"</tr>");
										
										$(".inc"+i+" .form_academic_exp_tree_id").val(aca_val['academic_tree_id']);								
										$(".inc"+i+" .form_academic_exp").val(aca_val['academic_experience']);
										$(".inc"+i+" .form_academic_institution").val(aca_val['institute']);
										$(".inc"+i+" .form_academic_diploma").val(aca_val['diploma']);
										$(".inc"+i+" .form_academic_fos").val(aca_val['field_of_study']);
										$(".inc"+i+" .form_academic_start_date").val(aca_val['start_date']);
										$(".inc"+i+" .form_academic_end_date").val(aca_val['end_date']);
										i++;
									}
								});									
							}
						if(key_main=='exp_professional_list'){

							var i=0;
							$.each(exp_val, function(key,pro_val) {
								if(i==0){
									$(".form_professional_exp_tree_id").val(pro_val['professional_tree_id']);
									$(".form_professional_exp_position").val(pro_val['position']);
									$(".form_professional_exp_employer").val(pro_val['employer']);
									$(".form_professional_exp_start_date").val(pro_val['start_date']);
									$(".form_professional_exp_end_date").val(pro_val['end_date']);
									i++;
								}else{
									if(i==1){
										$(".professional_exp_offer_accepted_summary tbody").find("tr:gt(1)").remove();
									}
									$(".professional_exp_offer_accepted_summary tbody").append("<tr class='inc"+i+"'>"+$(".professional_exp_offer_accepted_summary tr").eq(1).html()+"</tr>");
									$(".inc"+i+" .form_professional_exp_tree_id").val(pro_val['professional_tree_id']);											
									$(".inc"+i+" .form_professional_exp_position").val(pro_val['position']);
									$(".inc"+i+" .form_professional_exp_employer").val(pro_val['employer']);
									$(".inc"+i+" .form_professional_exp_start_date").val(pro_val['start_date']);
									$(".inc"+i+" .form_professional_exp_end_date").val(pro_val['end_date']);
									i++;
								}
							});
							
							}
						if(key_main=='exp_certificate_list'){
							var i=0;
							$.each(exp_val, function(key,aca_val) {
								if(i==0){
									$(".form_certification_exp_tree_id").val(aca_val['certification_tree_id']);
									$(".form_certification_exp_certificate").val(aca_val['certifications']);
									$(".form_certification_exp_certificate_code").val(aca_val['certificate_code']);
									$(".form_certification_exp_issued_by").val(aca_val['issued_by']);
									if (aca_val['professional_license'] == true){
										$(".form_certification_exp_professional_license").attr('checked','checked');
									}
									$(".form_certification_exp_state_issued").val(aca_val['state_issued_id']);
									$(".form_certification_exp_start_date").val(aca_val['start_date']);
									$(".form_certification_exp_end_date").val(aca_val['end_date']);
									i++;
								}else{
									if(i==1){
										$(".certification_exp_offer_accepted_summary tbody").find("tr:gt(1)").remove();
									}
									$(".certification_exp_offer_accepted_summary tbody").append("<tr class='inc"+i+"'>"+$(".certification_exp_offer_accepted_summary tr").eq(1).html()+"</tr>");
									$(".inc"+i+" .form_certification_exp_tree_id").val(aca_val['certification_tree_id']);											
									$(".inc"+i+" .form_certification_exp_certificate").val(aca_val['certifications']);
									$(".inc"+i+" .form_certification_exp_certificate_code").val(aca_val['certificate_code']);
									$(".inc"+i+" .form_certification_exp_issued_by").val(aca_val['issued_by']);
									if (aca_val['professional_license'] == true){
										$(".inc"+i+" .form_certification_exp_professional_license").attr('checked','checked');
									}
									$(".inc"+i+" .form_certification_exp_state_issued").val(aca_val['state_issued_id']);
									$(".inc"+i+" .form_certification_exp_start_date").val(aca_val['start_date']);
									$(".inc"+i+" .form_certification_exp_end_date").val(aca_val['end_date']);
									i++;
								}
							});
							
							}
						
		        });   
				}
		});
   }
});

var InsertValsOfferSummary = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var summary_info = {
				summary_employment_status:$(".form_summary_employment_status").val(), 
				summary_scheduled_hours:$(".form_summary_scheduled_hours").val(), 
				summary_pay_rate:$(".form_summary_pay_rate").val(),
				};
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('summary_state', [[1], arg1,summary_info])
		.then(function() {
		});
   }
});

var BackgroundiNine = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('inineinfo', [[1], arg1])
		.then(function(inine_info_dict) {

			var doc_val_list = '';
			
			if(inine_info_dict){
			$.each(inine_info_dict, function(key_main,inine_val) { 
				if (key_main=='doc_disp'){
					$.each(inine_val, function(key,val) {
						doc_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_applicant_documents").html("<option value=''></option>");
					$(".form_applicant_documents").append(doc_val_list);
					$(".form_employer_documents").html("<option value=''></option>");
					$(".form_employer_documents").append(doc_val_list);
				}
			});

			$.each(inine_info_dict, function(key_main,inine_val) { 
				if(key_main=='applicant_list'){		
					var i=0;

						$(".i9_applicant_table tbody").find("tr:gt(1)").remove();	
						$.each(inine_val, function(app_key,app_val) {
							
							if(i==0){
								if(app_val['status_id'] != ''){
									$(".btn_sent.btn_applicant").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');

									$(".i9_send_all").text("Resend All");
									$(".i9_send_all").attr("style","background:#e2e2e2;");
									$(".i9_send_all").attr("class","btn btn-default i9_send_all");

									
									$(".i9_applicant_table .onboard_trash").hide();
								}
								$(".applicant_tree_id").val(app_val['applicant_tree_id']);
								$(".form_applicant_documents").val(app_val['document']);
								$(".applicant_link").attr("href",app_val['doc_link']);
								$(".applicant_status").val(app_val['status_id']);
								$(".applicant_date_sent").val(app_val['date_sent']);
								$(".applicant_expiration").val(app_val['expiration']);
								i++;
							}else{
								if(i==1){
									$(".i9_applicant_table tbody").find("tr:gt(1)").remove();
								}
								$(".i9_applicant_table tbody").append("<tr class='inc"+i+"'>"+$(".i9_applicant_table tr").eq(1).html()+"</tr>");
								
								if(app_val['status_id'] != ''){
									$(".inc"+i+" .btn_sent.btn_applicant").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');

									$(".i9_send_all").text("Resend All");
									$(".i9_send_all").attr("style","background:#e2e2e2;");
									$(".i9_send_all").attr("class","btn btn-default i9_send_all");

									
									$(".inc"+i+" .i9_applicant_table .onboard_trash").hide();
								}else{
									$(".inc"+i+" .btn_sent.btn_applicant").html('<button class="btn btn-primary">Send</button>');
								}

								$(".inc"+i+" .applicant_tree_id").val(app_val['applicant_tree_id']);	
								$(".inc"+i+" .form_applicant_documents").append(doc_val_list);
								$(".inc"+i+" .form_applicant_documents").val(app_val['document']);
								$(".inc"+i+" .applicant_link").attr("href",app_val['doc_link']);
								$(".inc"+i+" .applicant_status").val(app_val['status_id']);
								$(".inc"+i+" .applicant_date_sent").val(app_val['date_sent']);
								$(".inc"+i+" .applicant_expiration").val(app_val['expiration']);
								i++;
							}
						});									
					}
					if(key_main=='employer_list'){
						var i=0;
						$.each(inine_val, function(emp_key,emp_val) {
							
							if(i==0){
								if(emp_val['status_id'] != ''){
									$(".btn_sent.btn_employer").html('<button class="btn btn-default " style="background:#e2e2e2;">Resend</button>');

									$(".i9_send_all").text("Resend All");
									$(".i9_send_all").attr("style","background:#e2e2e2;");
									$(".i9_send_all").attr("class","btn btn-default i9_send_all");

									
									$(".i9_employer_table .onboard_trash").hide();
								}
								$(".employer_tree_id").val(emp_val['employer_tree_id']);
								$(".form_employer_documents").val(emp_val['document']);
								$(".employer_link").attr("href",emp_val['doc_link']);
								$(".employer_status").val(emp_val['status_id']);
								$(".employer_date_sent").val(emp_val['date_sent']);
								$(".employer_expiration").val(emp_val['expiration']);
								i++;
							}else{
								if(i==1){
									$(".i9_employer_table tbody").find("tr:gt(1)").remove();
								}
								$(".i9_employer_table tbody").append("<tr class='inc"+i+"'>"+$(".i9_employer_table tr").eq(1).html()+"</tr>");
								
								if(emp_val['status_id'] != ''){
									$(".inc"+i+" .btn_sent.btn_employer").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');

									$(".i9_send_all").text("Resend All");
									$(".i9_send_all").attr("style","background:#e2e2e2;");
									$(".i9_send_all").attr("class","btn btn-default i9_send_all");

									
									$(".inc"+i+" .i9_employer_table.onboard_trash").hide();
								}else{
									$(".inc"+i+" .btn_sent.btn_employer").html('<button class="btn btn-primary">Send</button>');
								}

								$(".inc"+i+" .employer_tree_id").val(emp_val['employer_tree_id']);						
								$(".inc"+i+" .form_employer_documents").val(emp_val['document']);
								$(".inc"+i+" .employer_link").attr("href",emp_val['doc_link']);
								$(".inc"+i+" .employer_status").val(emp_val['status_id']);
								$(".inc"+i+" .employer_date_sent").val(emp_val['date_sent']);
								$(".inc"+i+" .employer_expiration").val(emp_val['expiration']);
								i++;
							}
						});
					
					}
					if(key_main=='everify_case_result_list'){
						var i=0;
						$.each(inine_val, function(emp_key,emp_val) {
							
							if(i==0){
								$(".everify_case_result_tree_id").val(emp_val['everify_case_result_tree_id']);
								$(".everify_case_result_case_number").val(emp_val['case_number']);
								$(".everify_case_result_status").val(emp_val['status']);
								$(".everify_case_result_message_code").val(emp_val['message_code']);
								$(".everify_case_result_eligiblity_statement").val(emp_val['eligiblity_statement']);
								$(".everify_case_result_statement_details").val(emp_val['statement_details']);
								$(".everify_case_result_date_sent").val(emp_val['date_sent']);
								$(".everify_case_result_date_received").val(emp_val['date_received']);
								$(".everify_case_result_case_status").val(emp_val['case_status']);
								$(".everify_case_result_download_URL").val(emp_val['everify_download_url']);
								i++;								
							}else{
								if(i==1){
									$(".everify_case_result tbody").find("tr:gt(1)").remove();
								}
								$(".everify_case_result tbody").append("<tr class='inc"+i+"'>"+$(".everify_case_result tr").eq(1).html()+"</tr>");
								
								$(".inc"+i+" .everify_case_result_tree_id").val(emp_val['everify_case_result_tree_id']);						
								$(".inc"+i+" .everify_case_result_case_number").val(emp_val['case_number']);					
								$(".inc"+i+" .everify_case_result_status").val(emp_val['status']);
								$(".inc"+i+" .everify_case_result_message_code").val(emp_val['message_code']);
								$(".inc"+i+" .everify_case_result_eligiblity_statement").val(emp_val['eligiblity_statement']);
								$(".inc"+i+" .everify_case_result_statement_details").val(emp_val['statement_details']);
								$(".inc"+i+" .everify_case_result_date_sent").val(emp_val['date_sent']);
								$(".inc"+i+" .everify_case_result_date_received").val(emp_val['date_received']);
								$(".inc"+i+" .everify_case_result_case_status").val(emp_val['case_status']);
								$(".inc"+i+" .everify_case_result_download_URL").val(emp_val['everify_download_url']);
								i++;

							}

						});
						
					}
					if(key_main=='everify_case_result_url'){
						var i=0;
						$.each(inine_val, function(emp_key,emp_val) {
							if(i==0){
								$(".everify_download_url").attr("href",emp_val['everify_download_url']);
							}else{
								if(i==1){
									$(".everify_case_result_download_table tbody").find("tr:gt(0)").remove();
								}
								$(".everify_case_result_download_table tbody").append("<tr class='inc"+i+"'>"+$(".everify_case_result_download_table tr").eq(0).html()+"</tr>");
								
								$(".inc"+i+" .everify_download_url").attr("href",emp_val['everify_download_url']);
							}
							i++;
						});
					}
        		});   
			}else{

			}
		});
   }
});

var InsertValsInineInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var n=0;
		$('.i9_applicant_table tr').each(function(){
			if(n>=1){
				var inine_applicant_info_vals = {
						applicant_tree_id:$(this).find('.applicant_tree_id').val(), 
						form_applicant_documents:$(this).find('.form_applicant_documents').val(),
						applicant_link:$(this).find('.applicant_link').val(),
						applicant_status:$(this).find('.applicant_status').val(),
						applicant_date_sent:$(this).find('.applicant_date_sent').val(),
						applicant_expiration:$(this).find('.applicant_expiration').val(),
					};
			    var hr_onboarding = new Model('hr.employee.onboarding');
				hr_onboarding.call('insert_records_inine_applicant_info', [[1], arg1,inine_applicant_info_vals])
				.then(function() {
				});
			}
			n++;
		});
		var m=0;
		$('.i9_employer_table tr').each(function(){
			if(m>=1){
				var inine_employer_info_vals = {
						employer_tree_id:$(this).find('.employer_tree_id').val(), 
						form_employer_documents:$(this).find('.form_employer_documents').val(),
						employer_link:$(this).find('.employer_link').val(),
						employer_status:$(this).find('.employer_status').val(),
						employer_date_sent:$(this).find('.employer_date_sent').val(),
						employer_expiration:$(this).find('.employer_expiration').val(),
					};
			    var hr_onboarding = new Model('hr.employee.onboarding');
				hr_onboarding.call('insert_records_inine_employer_info', [[1], arg1,inine_employer_info_vals])
				.then(function() {
				});
			}
			m++;
		});
		
		var substate_name = 'everify';
		var state_name = 'to_approve';
	    var hr_onboarding_state = new Model('hr.employee.onboarding');
		hr_onboarding_state.call('change_status', [[1], arg1,substate_name,state_name])
		.then(function() {
		});
		
   }
});

var ConsentForm = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('consentinfo', [[1], arg1])
		.then(function(consent_info_dict) {

			var doc_val_list = ['']
			if(consent_info_dict){
			$.each(consent_info_dict, function(key_main,val_main) { 
				if (key_main=='doc_disp'){
					$.each(val_main, function(key,val) {
						doc_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_consent_documents").html("<option value=''></option>");
					$(".form_consent_documents").append(doc_val_list);
				}
			});
			$.each(consent_info_dict, function(key_main,val_main) { 
				if(key_main=='consent_list'){		
					var i=0;
						$.each(val_main, function(consent_key,consent_val) {
							if(i==0){
								if(consent_val['status_id'] != ''){
									$(".btn_sent.btn_consent").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');

									$(".consent_send_all").text("Resend All");
									$(".consent_send_all").attr("style","background:#e2e2e2;");
									$(".consent_send_all").attr("class","btn btn-default consent_send_all");

									
									$(".background_check_consent_form_table .onboard_trash").hide();
								}
								$(".consent_form_tree_id").val(consent_val['consent_tree_id']);
								$(".form_consent_documents").append(doc_val_list);
								$(".form_consent_documents").val(consent_val['document']);
								$(".background_check_consent_form_link").attr("href",consent_val['doc_link']);
								$(".background_check_consent_form_status").val(consent_val['status_id']);
								$(".background_check_consent_form_date_sent").val(consent_val['date_sent']);
								$(".background_check_consent_form_expiration").val(consent_val['expiration']);
								i++;
							}else{
								if(i==1){
									$(".background_check_consent_form_table tbody").find("tr:gt(1)").remove();
								}
								$(".background_check_consent_form_table tbody").append("<tr class='inc"+i+"'>"+$(".background_check_consent_form_table tr").eq(1).html()+"</tr>");
								
								if(consent_val['status_id'] != ''){
									$(".inc"+i+" .btn_sent.btn_consent").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');

									$(".consent_send_all").text("Resend All");
									$(".consent_send_all").attr("style","background:#e2e2e2;");
									$(".consent_send_all").attr("class","btn btn-default consent_send_all");

									
									$(".inc"+i+" .background_check_consent_form_table .onboard_trash").hide();
								}else{
									$(".inc"+i+" .btn_sent.btn_consent").html('<button class="btn btn-primary">Send</button>');
								}

								$(".inc"+i+" .consent_form_tree_id").val(consent_val['consent_tree_id']);	
								$(".inc"+i+" .form_consent_documents").append(doc_val_list);
								$(".inc"+i+" .form_consent_documents").val(consent_val['document']);
								$(".inc"+i+" .background_check_consent_form_link").attr("href",consent_val['doc_link']);
								$(".inc"+i+" .background_check_consent_form_status").val(consent_val['status_id']);
								$(".inc"+i+" .background_check_consent_form_date_sent").val(consent_val['date_sent']);
								$(".inc"+i+" .background_check_consent_form_expiration").val(consent_val['expiration']);
								i++;
							}
						});									
					}
				
				});   
				}else{

				}
		});
   }
});

var InsertValsConsentInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var n=0;
		$('.background_check_consent_form_table tr').each(function(){
			if(n>=1){
				var background_consent_info_vals = {
						consent_form_tree_id:$(this).find('.consent_form_tree_id').val(), 
						form_consent_documents:$(this).find('.form_consent_documents').val(),
						background_check_consent_form_link:$(this).find('.background_check_consent_form_link').val(),
						background_check_consent_form_status:$(this).find('.background_check_consent_form_status').val(),
						background_check_consent_form_date_sent:$(this).find('.background_check_consent_form_date_sent').val(),
						background_check_consent_form_expiration:$(this).find('.background_check_consent_form_expiration').val(),
					};
			    var hr_onboarding = new Model('hr.employee.onboarding');
				hr_onboarding.call('insert_records_background_consent_info', [[1], arg1,background_consent_info_vals])
				.then(function() {
				});
			}
			n++;
		});

		var substate_name = 'background';
		var state_name = 'background';
	    var hr_onboarding_state = new Model('hr.employee.onboarding');
		hr_onboarding_state.call('change_status', [[1], arg1,substate_name,state_name])
		.then(function() {
		});
   }
});

var BackgroundCheck = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('backgroundinfo', [[1], arg1])
		.then(function(background_info_dict) {
			var doc_val_list = ['']
			var background_val_list = ['']
			var background_package_val_list = ['']
			if(background_info_dict){
			$.each(background_info_dict, function(key_main,val_main) { 
				if (key_main=='doc_disp'){
					$.each(val_main, function(key,val) {
						doc_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_applicant_documents").html("<option value=''></option>");
					$(".form_applicant_documents").append(doc_val_list);
					$(".form_employer_documents").html("<option value=''></option>");
					$(".form_employer_documents").append(doc_val_list);
				}
			});

			$.each(background_info_dict, function(key_main,val_main) { 
				if (key_main=='background_dict'){
					$.each(val_main, function(key ,val) {
						background_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_background_check_items").html("<option value=''></option>");
					$(".form_background_check_items").append(background_val_list);
				}
			});

			$.each(background_info_dict, function(key_main,val_main) { 
				if (key_main=='background_package_dict'){
					$.each(val_main, function(key ,val) {
						background_package_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_background_check_package_items").html("<option value=''></option>");
					$(".form_background_check_package_items").append(background_package_val_list);
				}
			});

			$.each(background_info_dict, function(key_main,val_main) { 
				if(key_main=='background_list'){		
					var i=0;
						$.each(val_main, function(bg_key,bg_val) {
							if(i==0){
								$(".background_check_table tbody").find("tr:gt(1)").remove();			
								$(".background_check_tree_id").val(bg_val['background_tree_id']);
								$(".form_background_check_items").val(bg_val['document']);
								$(".background_check_status").val(bg_val['status_id']);
								i++;
							}else{
								if(i==1){
									$(".background_check_table tbody").find("tr:gt(1)").remove();
								}
								$(".background_check_table tbody").append("<tr class='inc"+i+"'>"+$(".background_check_table tr").eq(1).html()+"</tr>");
								$(".inc"+i+" .background_check_tree_id").val(bg_val['background_tree_id']);	
								$(".inc"+i+" .form_background_check_items").val(bg_val['document']);
								$(".inc"+i+" .background_check_status").val(bg_val['status_id']);
								i++;
							}
						});									
					}
				}); 

			$.each(background_info_dict, function(key_main,val_main) { 
				if(key_main=='background_package_list'){		
					var i=0;
						$.each(val_main, function(bg_key,bg_val) {
							if(i==0){
								$(".background_check_package_table tbody").find("tr:gt(1)").remove();
								$(".background_check_package_tree_id").val(bg_val['background_package_tree_id']);
								$(".form_background_check_package_items").val(bg_val['document']);
								i++;
							}else{
								if(i==1){
									$(".background_check_package_table tbody").find("tr:gt(1)").remove();
								}
								$(".background_check_package_table tbody").append("<tr class='inc"+i+"'>"+$(".background_check_package_table tr").eq(1).html()+"</tr>");
								$(".inc"+i+" .background_check_package_tree_id").val(bg_val['background_package_tree_id']);	
								$(".inc"+i+" .form_background_check_package_items").val(bg_val['document']);
								i++;
							}
						});									
					}
				});   
			}
		});
   }
});

var InsertValsBackgroundcheckInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var i=0;
		$('.background_check_table tr').each(function(){
			if(i>=1){
				var background_check_info_vals = {
						background_check_tree_id:$(this).find('.background_check_tree_id').val(), 
						form_background_check_documents:$(this).find('.form_background_check_items').val(),
						background_check_status:$(this).find('.background_check_status').val(),
					};
			    var hr_onboarding = new Model('hr.employee.onboarding');
				hr_onboarding.call('insert_records_background_check_info', [[1], arg1,background_check_info_vals])
				.then(function() {
				});
			}
			i++;
		});

		var j=0;
		$('.background_check_package_table tr').each(function(){
			if(j>=1){
				var background_check_package_info_vals = {
						background_check_package_tree_id:$(this).find('.background_check_package_tree_id').val(), 
						form_background_check_package_items:$(this).find('.form_background_check_package_items').val(),
					};
			    var hr_onboarding = new Model('hr.employee.onboarding');
				hr_onboarding.call('insert_records_background_check_package_info', [[1], arg1,background_check_package_info_vals])
				.then(function() {
				});
			}
			j++;
		});

		var substate_name = 'back_summary';
		var state_name = 'background';
	    var hr_onboarding_state = new Model('hr.employee.onboarding');
		hr_onboarding_state.call('change_status', [[1], arg1,substate_name,state_name])
		.then(function(result_vals) {
			if (result_vals != 'Initiated'){
				alert('Please Initiate the Background Process');
			}
			else{
				$(".btn-next").click();
			}
		});
   }
});

var BackgroundSummary = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('backgroundsummaryinfo', [[1], arg1])
		.then(function(background_summary_info_dict) {

			var doc_val_list = ['']
			var background_val_list = ['']
			var background_download_val_list = ['']
			var background_package_val_list = ['']
			if(background_summary_info_dict){
				
			$.each(background_summary_info_dict, function(key_main,val_main) { 
				if (key_main=='doc_disp'){
					$.each(val_main, function(key,val) {
						doc_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_applicant_documents").html("<option value=''></option>");
					$(".form_applicant_documents").append(doc_val_list);
					$(".form_employer_documents").html("<option value=''></option>");
					$(".form_employer_documents").append(doc_val_list);
				}
			});

			$.each(background_summary_info_dict, function(key_main,val_main) { 
				if (key_main=='background_dict'){
					$.each(val_main, function(key ,val) {
						background_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_background_check_items").html("<option value=''></option>");
					$(".form_background_check_items").append(background_val_list);
					$(".form_background_check_download_items").html("<option value=''></option>");
					$(".form_background_check_download_items").append(background_val_list);

				}
			});

			$.each(background_summary_info_dict, function(key_main,val_main) { 
		
				if (key_main=='background_package_dict'){

					$.each(val_main, function(key ,val) {
						background_package_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_background_check_summary_package_items").html("<option value=''></option>");
					$(".form_background_check_summary_package_items").append(background_package_val_list);
				}
			});

			$.each(background_summary_info_dict, function(key_main,val_main) { 
				if (key_main=='background_download_dict'){
					$.each(val_main, function(key ,val) {
						background_download_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_background_check_download_items").html("<option value=''></option>");
					$(".form_background_check_download_items").append(background_download_val_list);

				}
			});

			$.each(background_summary_info_dict, function(key_main,val_main) {
				if(key_main=='background_list'){		
					var i=0;
					$.each(val_main, function(bg_key,bg_val) {
						if(i==0){
							$(".background_check_summary_table tbody").find("tr:gt(1)").remove();
							if(bg_val['status_id'] != ''){
								$(".btn_background_check_initiate").text("Resend");
								$(".btn_background_check_initiate").attr("style","background:#e2e2e2;");
								$(".btn_background_check_initiate").attr("class","btn btn-default btn_background_check_initiate");
							}
							
							$(".background_check_tree_id").val(bg_val['background_tree_id']);
							$(".form_background_check_items").val(bg_val['document']);

							$(".background_check_status").val(bg_val['status_id']);
							i++;
						}else{
							if(bg_val['status_id'] != ''){
								$(".btn_background_check_initiate").text("Resend");
								$(".btn_background_check_initiate").attr("style","background:#e2e2e2;");
								$(".btn_background_check_initiate").attr("class","btn btn-default btn_background_check_initiate");
							}
							$(".background_check_summary_table tbody").append("<tr class='inc"+i+"'>"+$(".background_check_summary_table tr").eq(1).html()+"</tr>");
							$(".inc"+i+" .background_check_tree_id").val(bg_val['background_tree_id']);	
							$(".inc"+i+" .form_background_check_items").val(bg_val['document']);

							$(".inc"+i+" .background_check_status").val(bg_val['status_id']);
							i++;
						}
					});									
				}
				if(key_main=='background_download_list'){		
					var i=0;
					$.each(val_main, function(bgd_key,bgd_val) {
						if(i==0){
							$(".background_check_download_summary_table tbody").find("tr:gt(1)").remove();
							$(".background_check_download_tree_id").val(bgd_val['background_tree_id']);
							$(".form_background_check_download_items").val(bgd_val['document']);
							$(".background_check_download_url").attr("href",bgd_val['link']);
							i++;
						}else{
							// if(i==1){
							// 	$(".background_check_download_summary_table tbody").find("tr:gt(1)").remove();
							// }
							$(".background_check_download_summary_table tbody").append("<tr class='inc"+i+"'>"+$(".background_check_download_summary_table tr").eq(1).html()+"</tr>");
							$(".inc"+i+" .background_check_download_tree_id").val(bgd_val['background_tree_id']);	
							$(".inc"+i+" .form_background_check_download_items").val(bgd_val['document']);	
							$(".inc"+i+" .background_check_download_url").attr("href",bgd_val['link']);
							i++;
						}
					});									
				}
				if(key_main=='background_package_list'){	
					var i=0;
					$.each(val_main, function(bgp_key,bgp_val) {
						if(i==0){
							$(".background_check_summary_package_table tbody").find("tr:gt(1)").remove();
							$(".background_check_summary_package_tree_id").val(bgp_val['background_package_tree_id']);
							$(".form_background_check_summary_package_items").val(bgp_val['document']);
							i++;
						}else{
							// if(i==1){
							// 	$(".background_check_summary_package_table tbody").find("tr:gt(1)").remove();
							// }
							$(".background_check_summary_package_table tbody").append("<tr class='inc"+i+"'>"+$(".background_check_summary_package_table tr").eq(1).html()+"</tr>");
							$(".inc"+i+" .background_check_summary_package_tree_id").val(bgp_val['background_package_tree_id']);	
							$(".inc"+i+" .form_background_check_summary_package_items").val(bgp_val['document']);
							i++;
						}
					});									
				}
			}); 

			}
		});
   }
});

var InsertValsBackgroundSummaryInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
	    var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('insert_records_background_summary_info', [[1], arg1])
		.then(function(result_vals) {
			if(result_vals == 'back_summary'){
				alert("Background check process is not completed yet")
			}else{
		
				var substate_name = 'adverse';
				var state_name = 'background';
			    var hr_onboarding_state = new Model('hr.employee.onboarding');
				hr_onboarding_state.call('change_status', [[1], arg1,substate_name,state_name])
				.then(function() {
				});
				$(".btn-next").click();
			}
		});

		// var i=0;
		// $('.background_check_summary_table tr').each(function(){
		// 	if(i>=1){
		// 		var background_summary_info_vals = {
		// 				background_check_tree_id:$(this).find('.background_check_tree_id').val(), 
		// 				form_background_check_documents:$(this).find('.form_background_check_items').val(),
		// 				background_check_status:$(this).find('.background_check_status').val(),
		// 				form_drug_test:$(".form_drug_test").val()
		// 			};
		// 	    var hr_onboarding = new Model('hr.employee.onboarding');
		// 		hr_onboarding.call('insert_records_background_summary_info', [[1], arg1,background_summary_info_vals])
		// 		.then(function(result_vals) {
		// 			alert(result_vals);
		// 			if(result_vals == 'back_summary'){
		// 				alert("Background check process is not completed yet")
		// 			}else{
		// 				$(".btn-next").click();
		// 			}
		// 		});
		// 	}
		// 	i++;
		// });
   }
});

var AdverseAction = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('adverseinfo', [[1], arg1])
		.then(function(adverse_info_dict) {

			var doc_val_list = ['']
			if(adverse_info_dict){
			$.each(adverse_info_dict, function(key_main,val_main) { 
				if (key_main=='doc_disp'){
					$.each(val_main, function(key,val) {
						doc_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_adverse_documents").html("<option value=''></option>");
					$(".form_adverse_documents").append(doc_val_list);
				}
			});
			$.each(adverse_info_dict, function(key_main,val_main) { 
				if(key_main=='adverse_list'){		
					var i=0;
						$.each(val_main, function(adverse_key,adverse_val) {
							if(i==0){
								if(adverse_val['status_id'] != ''){
									$(".btn_sent.btn_adverse").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
									$(".adverse_action_table .onboard_trash").hide();
								}
								$(".adverse_action_tree_id").val(adverse_val['adverse_tree_id']);
								$(".form_adverse_documents").append(doc_val_list);
								$(".form_adverse_documents").val(adverse_val['document']);
								$(".adverse_action_link").attr("href",adverse_val['doc_link']);
								$(".adverse_action_status").val(adverse_val['status_id']);
								$(".adverse_action_date_sent").val(adverse_val['date_sent']);
								$(".adverse_action_expiration").val(adverse_val['expiration']);
								i++;
							}else{
								if(i==1){
									$(".adverse_action_table tbody").find("tr:gt(1)").remove();
								}
								$(".adverse_action_table tbody").append("<tr class='inc"+i+"'>"+$(".adverse_action_table tr").eq(1).html()+"</tr>");
								
								if(adverse_val['status_id'] != ''){
									$(".inc"+i+" .btn_sent.btn_adverse").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
									$(".inc"+i+" .adverse_action_table .onboard_trash").hide();
								}else{
									$(".inc"+i+" .btn_sent.btn_adverse").html('<button class="btn btn-primary">Send</button>');
								}

								$(".inc"+i+" .adverse_action_tree_id").val(adverse_val['adverse_tree_id']);	
								$(".inc"+i+" .form_adverse_documents").append(doc_val_list);
								$(".inc"+i+" .form_adverse_documents").val(adverse_val['document']);
								$(".inc"+i+" .adverse_action_link").attr("href",adverse_val['doc_link']);
								$(".inc"+i+" .adverse_action_status").val(adverse_val['status_id']);
								$(".inc"+i+" .adverse_action_date_sent").val(adverse_val['date_sent']);
								$(".inc"+i+" .adverse_action_expiration").val(adverse_val['expiration']);
								i++;
							}
						});									
					}
				});   
				}else{

				}
		});
   }
});

var InsertValsAdverseActionInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var n=0;
		$('.adverse_action_table tr').each(function(){
			if(n>=1){
				var adverse_action_info_vals = {
						adverse_action_tree_id:$(this).find('.adverse_action_tree_id').val(), 
						form_adverse_documents:$(this).find('.form_adverse_documents').val(),
						adverse_action_link:$(this).find('.adverse_action_link').val(),
						adverse_action_status:$(this).find('.adverse_action_status').val(),
						adverse_action_date_sent:$(this).find('.adverse_action_date_sent').val(),
						adverse_action_expiration:$(this).find('.adverse_action_expiration').val(),
					};
			    var hr_onboarding = new Model('hr.employee.onboarding');
				hr_onboarding.call('insert_records_adverse_action_info', [[1], arg1,adverse_action_info_vals])
				.then(function() {
				});
			}
			n++;
		});
		
		var substate_name = 'inine';
		var state_name = 'to_approve';
	    var hr_onboarding_state = new Model('hr.employee.onboarding');
		hr_onboarding_state.call('change_status', [[1], arg1,substate_name,state_name])
		.then(function() {
		});
   }
});

var HireEverify = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('hireeverifyinfo', [[1], arg1])
		.then(function(hire_everify_info_dict) {

			var doc_val_list = ['']
			var background_val_list = ['']
			var background_package_val_list = ['']
			if(hire_everify_info_dict){
			$.each(hire_everify_info_dict, function(key_main,val_main) { 
				if (key_main=='doc_disp'){
					$.each(val_main, function(key,val) {
						doc_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_applicant_documents").html("<option value=''></option>");
					$(".form_applicant_documents").append(doc_val_list);
					$(".form_employer_documents").html("<option value=''></option>");
					$(".form_employer_documents").append(doc_val_list);
				}
			});

			$.each(hire_everify_info_dict, function(key_main,val_main) { 
				if (key_main=='background_dict'){
					$.each(val_main, function(key ,val) {
						background_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_background_check_items").html("<option value=''></option>");
					$(".form_background_check_items").append(background_val_list);
				}
			});
			
			$.each(hire_everify_info_dict, function(key_main,val_main) { 
		
				if (key_main=='background_package_dict'){

					$.each(val_main, function(key ,val) {
						background_package_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_background_check_everify_package_items").html("<option value=''></option>");
					$(".form_background_check_everify_package_items").append(background_package_val_list);
				}
			});
			
			// if($('.everify_value').val()=='completed'){
			// 	$(".btn_everify").text("Re-Initiate");
			// 	$(".btn_everify").attr("style","background:#e2e2e2;");
			// 	$(".btn_everify").attr("class","btn btn-default btn_everify");
			// }

			if(hire_everify_info_dict['e_verify'] == 'completed'){
				$(".btn_everify").text("Re-Initiate");
				$(".btn_everify").attr("style","background:#e2e2e2;");
				$(".btn_everify").attr("class","btn btn-default btn_everify");	
				$('.everify_value').val('completed');			
			}
				
			$.each(hire_everify_info_dict, function(key_main,val_main) { 
				if(key_main=='applicant_list'){		
					var i=0;
						$.each(val_main, function(app_key,app_val) {
							if(i==0){
								if(app_val['status_id'] != ''){
									$(".btn_sent.btn_applicant").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
									$(".e_verify_applicant_table .onboard_trash").hide();
								}
								$(".applicant_tree_id").val(app_val['applicant_tree_id']);
								$(".form_applicant_documents").val(app_val['document']);
								$(".applicant_link").attr("href",app_val['doc_link']);
								$(".applicant_status").val(app_val['status_id']);
								$(".applicant_date_sent").val(app_val['date_sent']);
								$(".applicant_expiration").val(app_val['expiration']);
								i++;
							}else{
								if(i==1){
									$(".e_verify_applicant_table tbody").find("tr:gt(1)").remove();
								}
								$(".e_verify_applicant_table tbody").append("<tr class='inc"+i+"'>"+$(".e_verify_applicant_table tr").eq(1).html()+"</tr>");
								
								if(app_val['status_id'] != ''){
									$(".inc"+i+" .btn_sent.btn_applicant").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
									$(".inc"+i+" .e_verify_applicant_table .onboard_trash").hide();
								}else{
									$(".inc"+i+" .btn_sent.btn_applicant").html('<button class="btn btn-primary" >Send</button>');
								}

								$(".inc"+i+" .applicant_tree_id").val(app_val['applicant_tree_id']);	
								$(".inc"+i+" .form_applicant_documents").append(doc_val_list);
								$(".inc"+i+" .form_applicant_documents").val(app_val['document']);
								$(".inc"+i+" .applicant_link").attr("href",app_val['doc_link']);
								$(".inc"+i+" .applicant_status").val(app_val['status_id']);
								$(".inc"+i+" .applicant_date_sent").val(app_val['date_sent']);
								$(".inc"+i+" .applicant_expiration").val(app_val['expiration']);
								i++;
							}
						});									
					}
				if(key_main=='employer_list'){

					var i=0;
					$.each(val_main, function(emp_key,emp_val) {
						if(i==0){
							if(emp_val['status_id'] != ''){
								$(".btn_sent.btn_employer").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
								$(".e_verify_employer_table .onboard_trash").hide();
							}
							$(".employer_tree_id").val(emp_val['employer_tree_id']);
							$(".form_employer_documents").val(emp_val['document']);
							$(".employer_link").attr("href",emp_val['doc_link']);
							$(".employer_status").val(emp_val['status_id']);
							$(".employer_date_sent").val(emp_val['date_sent']);
							$(".employer_expiration").val(emp_val['expiration']);
							i++;
						}else{
							if(i==1){
								$(".e_verify_employer_table tbody").find("tr:gt(1)").remove();
							}
							$(".e_verify_employer_table tbody").append("<tr class='inc"+i+"'>"+$(".e_verify_employer_table tr").eq(1).html()+"</tr>");
							
							if(emp_val['status_id'] != ''){
								$(".inc"+i+" .btn_sent.btn_employer").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
								$(".inc"+i+" .e_verify_employer_table .onboard_trash").hide();
							}else{
								$(".inc"+i+" .btn_sent.btn_employer").html('<button class="btn btn-primary" >Send</button>');
							}

							$(".inc"+i+" .employer_tree_id").val(emp_val['employer_tree_id']);						
							$(".inc"+i+" .form_employer_documents").val(emp_val['document']);
							$(".inc"+i+" .employer_link").attr("href",emp_val['doc_link']);
							$(".inc"+i+" .employer_status").val(emp_val['status_id']);
							$(".inc"+i+" .employer_date_sent").val(emp_val['date_sent']);
							$(".inc"+i+" .employer_expiration").val(emp_val['expiration']);
							i++;
						}
					});
					
					}
				if(key_main=='background_list'){		
					var i=0;
						$.each(val_main, function(bg_key,bg_val) {
							if(i==0){
								$(".background_check_tree_id").val(bg_val['background_tree_id']);
								$(".form_background_check_items").val(bg_val['document']);
								$(".background_check_status").val(bg_val['status_id']);
								i++;
							}else{
								if(i==1){
									$(".e_verify_background_check_table tbody").find("tr:gt(1)").remove();
								}
								$(".e_verify_background_check_table tbody").append("<tr class='inc"+i+"'>"+$(".e_verify_background_check_table tr").eq(1).html()+"</tr>");
								$(".inc"+i+" .background_check_tree_id").val(bg_val['background_tree_id']);	
								$(".inc"+i+" .form_background_check_items").val(bg_val['document']);
								$(".inc"+i+" .background_check_status").val(bg_val['status_id']);
								i++;
							}
						});									
					}

				if(key_main=='background_package_list'){	
					var i=0;
					$.each(val_main, function(bgp_key,bgp_val) {
						if(i==0){
							$(".background_check_everify_package_tree_id").val(bgp_val['background_package_tree_id']);
							$(".form_background_check_everify_package_items").val(bgp_val['document']);
							i++;
						}else{
							if(i==1){
								$(".background_check_everify_package_table tbody").find("tr:gt(1)").remove();
							}
							$(".background_check_everify_package_table tbody").append("<tr class='inc"+i+"'>"+$(".background_check_everify_package_table tr").eq(1).html()+"</tr>");
							$(".inc"+i+" .background_check_everify_package_tree_id").val(bgp_val['background_package_tree_id']);	
							$(".inc"+i+" .form_background_check_everify_package_items").val(bgp_val['document']);
							i++;
						}
					});									
				}
				
				});   
				}
		});
   }
});

var InsertValsEverifyInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var n=0;
		$('.e_verify_applicant_table tr').each(function(){
			if(n>=1){
				var everify_applicant_info_vals = {
						applicant_tree_id:$(this).find('.applicant_tree_id').val(), 
						form_applicant_documents:$(this).find('.form_applicant_documents').val(),
						applicant_link:$(this).find('.applicant_link').val(),
						applicant_status:$(this).find('.applicant_status').val(),
						applicant_date_sent:$(this).find('.applicant_date_sent').val(),
						applicant_expiration:$(this).find('.applicant_expiration').val(),
					};
			    var hr_onboarding = new Model('hr.employee.onboarding');
				hr_onboarding.call('insert_records_everify_applicant_info', [[1], arg1,everify_applicant_info_vals])
				.then(function() {
				});
			}
			n++;
		});
		var m=0;
		$('.e_verify_employer_table tr').each(function(){
			if(m>=1){
				var everify_employer_info_vals = {
						employer_tree_id:$(this).find('.employer_tree_id').val(), 
						form_employer_documents:$(this).find('.form_employer_documents').val(),
						employer_link:$(this).find('.employer_link').val(),
						employer_status:$(this).find('.employer_status').val(),
						employer_date_sent:$(this).find('.employer_date_sent').val(),
						employer_expiration:$(this).find('.employer_expiration').val(),
					};
			    var hr_onboarding = new Model('hr.employee.onboarding');
				hr_onboarding.call('insert_records_everify_employer_info', [[1], arg1,everify_employer_info_vals])
				.then(function() {
				});
			}
			m++;
		});
		var i=0;
		$('.e_verify_background_check_table tr').each(function(){
			if(i>=1){
				var everify_background_info_vals = {
						background_check_tree_id:$(this).find('.background_check_tree_id').val(), 
						form_background_check_documents:$(this).find('.form_background_check_items').val(),
						background_check_status:$(this).find('.background_check_status').val(),
						form_everify_test:$(".form_drug_test").val()
					};
			    var hr_onboarding = new Model('hr.employee.onboarding');
				hr_onboarding.call('insert_records_everify_background_info', [[1], arg1,everify_background_info_vals])
				.then(function() {					
				});
			}
			i++;
		});
		if($('.everify_value').val()=='completed'){
		
			var substate_name = 'app_summary';
			var state_name = 'to_approve';
		    var hr_onboarding_state = new Model('hr.employee.onboarding');
			hr_onboarding_state.call('change_status', [[1], arg1,substate_name,state_name])
			.then(function() {
			});
			
			$(".btn-next").click();
		}else{
			alert("Please complete the E-Verify process by clicking 'Initiate'");
		}
   }
});

var HireSummary = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();			
	    var self = this;
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('hire_summary', [[1], arg1])
		.then(function(hire_summary_dict) {
				if(hire_summary_dict){
					$(".form_summary_name").val(hire_summary_dict.name);
					$(".form_summary_phone").val(hire_summary_dict.phone);
					$(".form_summary_mail").val(hire_summary_dict.mail);
					$(".form_summary_applied_job").val(hire_summary_dict.applied_job);
					$(".form_summary_applicant_id").val(hire_summary_dict.applicant_id);
					$(".form_summary_company").val(hire_summary_dict.company);
					$(".form_summary_responsible").val(hire_summary_dict.responsible);
					$(".form_summary_id_number").val(hire_summary_dict.id_no);
					$(".form_summary_passport_number").val(hire_summary_dict.passport_no);
					$(".form_street").val(hire_summary_dict.street);
					$(".form_street2").val(hire_summary_dict.street2);
					$(".form_city").val(hire_summary_dict.city);
					$(".form_summary_state").val(hire_summary_dict.state);
					$(".form_summary_country").val(hire_summary_dict.country_id);
					$(".form_zip").val(hire_summary_dict.zip);
					$(".form_summary_gender").val(hire_summary_dict.gender);
					$(".form_summary_marital_status").val(hire_summary_dict.marital_status);
					$(".form_summary_filing_status").val(hire_summary_dict.filing_status);
					$(".form_summary_noc").val(hire_summary_dict.children);
					$(".form_summary_dob").val(hire_summary_dict.dob);
					$(".form_summary_age").val(hire_summary_dict.age);
					$(".form_summary_scheduled_hours").val(hire_summary_dict.scheduled_hours);
					$(".form_summary_pay_rate").val(hire_summary_dict.pay_rate);
					$(".form_summary_start_date").val(hire_summary_dict.emp_start_date);				
					$(".form_summary_job_sen_title").val(hire_summary_dict.job_seniority_title);
					$(".form_summary_ben_sen_date").val(hire_summary_dict.benifits_seniority_date);
					$(".form_summary_country").val(hire_summary_dict.nationality);
					$(".form_summary_nationality").val(hire_summary_dict.nationality);
					$(".form_summary_birth_country").val(hire_summary_dict.birth_country);		
					$(".form_summary_employment_status").val(hire_summary_dict.emp_status);
					$(".form_summary_pob").val(hire_summary_dict.place_of_birth);
					$(".form_bio").val(hire_summary_dict.notes);
					
					$.each(hire_summary_dict, function(key_main,val_main) { 
						if (key_main=='e_verify'){
							$(".form_everify_test").val(val_main);
						}
					});
					
					var doc_val_list = ['']
					var background_val_list = ['']
					var background_download_val_list = ['']
					var background_package_val_list = ['']
					$.each(hire_summary_dict, function(key_main,val_main) { 
						if (key_main=='doc_disp'){
							$.each(val_main, function(key,val) {
								doc_val_list += ("<option value='"+key+"'>"+val+"</option>");
							});
							$(".form_applicant_documents").html("<option value=''></option>");
							$(".form_applicant_documents").append(doc_val_list);
							$(".form_employer_documents").html("<option value=''></option>");
							$(".form_employer_documents").append(doc_val_list);
						}
					});

					$.each(hire_summary_dict, function(key_main,val_main) { 
						if (key_main=='background_dict'){
							$.each(val_main, function(key ,val) {
								background_val_list += ("<option value='"+key+"'>"+val+"</option>");
							});
							$(".form_background_check_items").html("<option value=''></option>");
							$(".form_background_check_items").append(background_val_list);
						}
					});
			
					$.each(hire_summary_dict, function(key_main,val_main) { 
				
						if (key_main=='background_package_dict'){

							$.each(val_main, function(key ,val) {
								background_package_val_list += ("<option value='"+key+"'>"+val+"</option>");
							});
							$(".form_background_check_everify_summary_package_items").html("<option value=''></option>");
							$(".form_background_check_everify_summary_package_items").append(background_package_val_list);
						}
					});

					$.each(hire_summary_dict, function(key_main,val_main) { 
						if (key_main=='background_download_dict'){
							$.each(val_main, function(key ,val) {
								background_download_val_list += ("<option value='"+key+"'>"+val+"</option>");
							});
							$(".form_everify_download_items").html("<option value=''></option>");
							$(".form_everify_download_items").append(background_download_val_list);

						}
					});

					$.each(hire_summary_dict.state_dict, function(key,val) {
						$(".form_certification_exp_state_issued").append("<option value='"+key+"'>"+val+"</option>");
					});
					
					$.each(hire_summary_dict, function(key_main,val_main) { 
						if (key_main=='drug_test'){
							$(".form_drug_test").val(val_main);
						}
					});
						
					$.each(hire_summary_dict, function(key_main,val_main) { 
						if(key_main=='applicant_list'){		
							var i=0;
								$.each(val_main, function(app_key,app_val) {
									if(i==0){
										if(app_val['status_id'] != ''){
											$(".btn_sent.btn_applicant").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
											$(".e_verify_applicant_table_summary .onboard_trash").hide();
										}
										$(".applicant_tree_id").val(app_val['applicant_tree_id']);
										$(".form_applicant_documents").val(app_val['document']);
										$(".applicant_link").attr("href",app_val['doc_link']);
										$(".applicant_status").val(app_val['status_id']);
										$(".applicant_date_sent").val(app_val['date_sent']);
										$(".applicant_expiration").val(app_val['expiration']);
										i++;
									}else{
										if(i==1){
											$(".e_verify_applicant_table_summary tbody").find("tr:gt(1)").remove();
										}
										$(".e_verify_applicant_table_summary tbody").append("<tr class='inc"+i+"'>"+$(".e_verify_applicant_table_summary tr").eq(1).html()+"</tr>");
										
										if(app_val['status_id'] != ''){
											$(".inc"+i+" .btn_sent.btn_applicant").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
											$(".inc"+i+" .e_verify_applicant_table_summary .onboard_trash").hide();
										}else{
											$(".inc"+i+" .btn_sent.btn_applicant").html('<button class="btn btn-primary" >Send</button>');
										}

										$(".inc"+i+" .applicant_tree_id").val(app_val['applicant_tree_id']);	
										$(".inc"+i+" .form_applicant_documents").append(doc_val_list);
										$(".inc"+i+" .form_applicant_documents").val(app_val['document']);
										$(".inc"+i+" .applicant_link").attr("href",app_val['doc_link']);
										$(".inc"+i+" .applicant_status").val(app_val['status_id']);
										$(".inc"+i+" .applicant_date_sent").val(app_val['date_sent']);
										$(".inc"+i+" .applicant_expiration").val(app_val['expiration']);
										i++;
									}
								});									
							}
						if(key_main=='employer_list'){
							var i=0;
							$.each(val_main, function(emp_key,emp_val) {
								if(i==0){
									if(emp_val['status_id'] != ''){
										$(".btn_sent.btn_employer").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
										$(".e_verify_employer_table_summary .onboard_trash").hide();
									}
									$(".employer_tree_id").val(emp_val['employer_tree_id']);
									$(".form_employer_documents").val(emp_val['document']);
									$(".employer_link").attr("href",emp_val['doc_link']);
									$(".employer_status").val(emp_val['status_id']);
									$(".employer_date_sent").val(emp_val['date_sent']);
									$(".employer_expiration").val(emp_val['expiration']);
									i++;
								}else{
									if(i==1){
										$(".e_verify_employer_table_summary tbody").find("tr:gt(1)").remove();
									}
									$(".e_verify_employer_table_summary tbody").append("<tr class='inc"+i+"'>"+$(".e_verify_employer_table_summary tr").eq(1).html()+"</tr>");
									
									if(emp_val['status_id'] != ''){
										$(".inc"+i+" .btn_sent.btn_employer").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
										$(".inc"+i+" .e_verify_employer_table_summary .onboard_trash").hide();
									}else{
										$(".inc"+i+" .btn_sent.btn_employer").html('<button class="btn btn-primary" >Send</button>');
									}

									$(".inc"+i+" .employer_tree_id").val(emp_val['employer_tree_id']);						
									$(".inc"+i+" .form_employer_documents").val(emp_val['document']);
									$(".inc"+i+" .employer_link").attr("href",emp_val['doc_link']);
									$(".inc"+i+" .employer_status").val(emp_val['status_id']);
									$(".inc"+i+" .employer_date_sent").val(emp_val['date_sent']);
									$(".inc"+i+" .employer_expiration").val(emp_val['expiration']);
									i++;
								}
							});
							
							}
						if(key_main=='background_list'){		
							var i=0;
								$.each(val_main, function(bg_key,bg_val) {
									if(i==0){
										$(".background_check_tree_id").val(bg_val['background_tree_id']);
										$(".form_background_check_items").val(bg_val['document']);
										$(".background_check_status").val(bg_val['status_id']);
										i++;
									}else{
										if(i==1){
											$(".e_verify_table_summary tbody").find("tr:gt(1)").remove();
										}
										$(".e_verify_table_summary tbody").append("<tr class='inc"+i+"'>"+$(".e_verify_table_summary tr").eq(1).html()+"</tr>");
										$(".inc"+i+" .background_check_tree_id").val(bg_val['background_tree_id']);	
										$(".inc"+i+" .form_background_check_items").val(bg_val['document']);
										$(".inc"+i+" .background_check_status").val(bg_val['status_id']);
										i++;
									}
								});									
							} 

						if(key_main=='background_download_list'){		
							var i=0;
							$.each(val_main, function(bgd_key,bgd_val) {
								if(i==0){
									$(".everify_download_tree_id").val(bgd_val['background_tree_id']);
									$(".form_everify_download_items").val(bgd_val['document']);
									$(".everify_download_url").attr("href",bgd_val['link']);
									i++;
								}else{
									if(i==1){
										$(".everify_download_summary_table tbody").find("tr:gt(1)").remove();
									}
									$(".everify_download_summary_table tbody").append("<tr class='inc"+i+"'>"+$(".everify_download_summary_table tr").eq(1).html()+"</tr>");
									$(".inc"+i+" .everify_download_tree_id").val(bgd_val['background_tree_id']);	
									$(".inc"+i+" .form_everify_download_items").val(bgd_val['document']);	
									$(".inc"+i+" .everify_download_url").attr("href",bgd_val['link']);
									i++;
								}
							});									
						}
						

						if(key_main=='background_package_list'){	
							var i=0;
							$.each(val_main, function(bgp_key,bgp_val) {
								if(i==0){
									$(".background_check_everify_summary_package_tree_id").val(bgp_val['background_package_tree_id']);
									$(".form_background_check_everify_summary_package_items").val(bgp_val['document']);
									i++;
								}else{
									if(i==1){
										$(".background_check_everify_package_table tbody").find("tr:gt(1)").remove();
									}
									$(".background_check_everify_package_table tbody").append("<tr class='inc"+i+"'>"+$(".background_check_everify_package_table tr").eq(1).html()+"</tr>");
									$(".inc"+i+" .background_check_everify_summary_package_tree_id").val(bgp_val['background_package_tree_id']);	
									$(".inc"+i+" .form_background_check_everify_summary_package_items").val(bgp_val['document']);
									i++;
								}
							});									
						}
						
						}); 
					
					$.each(hire_summary_dict, function(key_main,exp_val) { 
						
						if(key_main=='exp_academic_list'){		
							var i=0;
								$.each(exp_val, function(key,aca_val) {
									if(i==0){
										$(".form_academic_exp_tree_id").val(aca_val['academic_tree_id']);
										$(".form_academic_exp").val(aca_val['academic_experience']);
										$(".form_academic_institution").val(aca_val['institute']);
										$(".form_academic_diploma").val(aca_val['diploma']);
										$(".form_academic_fos").val(aca_val['field_of_study']);
										$(".form_academic_start_date").val(aca_val['start_date']);
										$(".form_academic_end_date").val(aca_val['end_date']);
										i++;
									}else{
										if(i==1){
											$(".academic_exp_e_verify_summary tbody").find("tr:gt(1)").remove();
										}
										$(".academic_exp_e_verify_summary tbody").append("<tr class='inc"+i+"'>"+$(".academic_exp_e_verify_summary tr").eq(1).html()+"</tr>");
										
										$(".inc"+i+" .form_academic_exp_tree_id").val(aca_val['academic_tree_id']);								
										$(".inc"+i+" .form_academic_exp").val(aca_val['academic_experience']);
										$(".inc"+i+" .form_academic_institution").val(aca_val['institute']);
										$(".inc"+i+" .form_academic_diploma").val(aca_val['diploma']);
										$(".inc"+i+" .form_academic_fos").val(aca_val['field_of_study']);
										$(".inc"+i+" .form_academic_start_date").val(aca_val['start_date']);
										$(".inc"+i+" .form_academic_end_date").val(aca_val['end_date']);
										i++;
									}
								});									
							}
						if(key_main=='exp_professional_list'){
							var i=0;
							$.each(exp_val, function(key,pro_val) {
								if(i==0){
									$(".form_professional_exp_tree_id").val(pro_val['professional_tree_id']);
									$(".form_professional_exp_position").val(pro_val['position']);
									$(".form_professional_exp_employer").val(pro_val['employer']);
									$(".form_professional_exp_start_date").val(pro_val['start_date']);
									$(".form_professional_exp_end_date").val(pro_val['end_date']);
									i++;
								}else{
									if(i==1){
										$(".professional_exp_e_verify_summary tbody").find("tr:gt(1)").remove();
									}
									$(".professional_exp_e_verify_summary tbody").append("<tr class='inc"+i+"'>"+$(".professional_exp_e_verify_summary tr").eq(1).html()+"</tr>");
									$(".inc"+i+" .form_professional_exp_tree_id").val(pro_val['professional_tree_id']);											
									$(".inc"+i+" .form_professional_exp_position").val(pro_val['position']);
									$(".inc"+i+" .form_professional_exp_employer").val(pro_val['employer']);
									$(".inc"+i+" .form_professional_exp_start_date").val(pro_val['start_date']);
									$(".inc"+i+" .form_professional_exp_end_date").val(pro_val['end_date']);
									i++;
								}
							});
							
							}
						if(key_main=='exp_certificate_list'){
							var i=0;
							$.each(exp_val, function(key,aca_val) {
								if(i==0){
									$(".form_certification_exp_tree_id").val(aca_val['certification_tree_id']);
									$(".form_certification_exp_certificate").val(aca_val['certifications']);
									$(".form_certification_exp_certificate_code").val(aca_val['certificate_code']);
									$(".form_certification_exp_issued_by").val(aca_val['issued_by']);
									if (aca_val['professional_license'] == true){
										$(".form_certification_exp_professional_license").attr('checked','checked');
									}
									$(".form_certification_exp_state_issued").val(aca_val['state_issued_id']);
									$(".form_certification_exp_start_date").val(aca_val['start_date']);
									$(".form_certification_exp_end_date").val(aca_val['end_date']);
									i++;
								}else{
									if(i==1){
										$(".certification_exp_e_verify_summary tbody").find("tr:gt(1)").remove();
									}
									$(".certification_exp_e_verify_summary tbody").append("<tr class='inc"+i+"'>"+$(".certification_exp_e_verify_summary tr").eq(1).html()+"</tr>");
									$(".inc"+i+" .form_certification_exp_tree_id").val(aca_val['certification_tree_id']);											
									$(".inc"+i+" .form_certification_exp_certificate").val(aca_val['certifications']);
									$(".inc"+i+" .form_certification_exp_certificate_code").val(aca_val['certificate_code']);
									$(".inc"+i+" .form_certification_exp_issued_by").val(aca_val['issued_by']);
									if (aca_val['professional_license'] == true){
										$(".inc"+i+" .form_certification_exp_professional_license").attr('checked','checked');
									}
									$(".inc"+i+" .form_certification_exp_state_issued").val(aca_val['state_issued_id']);
									$(".inc"+i+" .form_certification_exp_start_date").val(aca_val['start_date']);
									$(".inc"+i+" .form_certification_exp_end_date").val(aca_val['end_date']);
									i++;
								}
							});
							
							}
						
		        });   
				}
		});
   }
});

var InsertValsHireInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();

		var bio = $(".form_bio").val();
		var image = $(".image_value").val();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('hire_applicant', [[1], arg1,bio,image])
		.then(function() {
		});
		
		var substate_name = 'ben_eligiblity';
		var state_name = 'hire';
	    var hr_onboarding_state = new Model('hr.employee.onboarding');
		hr_onboarding_state.call('change_status', [[1], arg1,substate_name,state_name])
		.then(function() {
		});
   }
});

var BenefitsEligibility = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();			
	    var self = this;
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('benefits_eligibility_info', [[1], arg1])
		.then(function(benefits_eligibility_dict) {
				if(benefits_eligibility_dict){
					$(".form_enrollment_delay").val(benefits_eligibility_dict.enrollment_delay);
					if(benefits_eligibility_dict.elegible_for_benefits == 'eligible'){
						$(".eligible_for_benefits").attr('checked','checked');
					}
				}
		});
   }
});

var InsrtValsBenefitsEligibility = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		if($('input.eligible_for_benefits').is(':checked')){
			var ban_obj = 'checked'
		}
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('insert_vals_benefits_eligibility', [[1], arg1,ban_obj])
		.then(function() {
		});
		
		var substate_name = 'welcome';
		var state_name = 'hire';
	    var hr_onboarding_state = new Model('hr.employee.onboarding');
		hr_onboarding_state.call('change_status', [[1], arg1,substate_name,state_name])
		.then(function() {
		});
   }
});

var WelcomeMail = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('welcomemailinfo', [[1], arg1])
		.then(function(welcome_info_dict) {

			var doc_val_list = ['']
			var survey_val_list = ['']
			if(welcome_info_dict){
			$.each(welcome_info_dict, function(key_main,val_main) { 
				if (key_main=='doc_disp'){
					$.each(val_main, function(key,val) {
						doc_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_welcome_applicant_documents").html("<option value=''></option>");
					$(".form_welcome_applicant_documents").append(doc_val_list);
				}
			});	
			$.each(welcome_info_dict, function(key_main,val_main) { 
				if(key_main=='welcome_list'){		
					var i=0;
						$.each(val_main, function(welcome_key,welcome_val) {
							if(i==0){
								if(welcome_val['status_id'] != ''){
									$(".btn_sent.btn_welcome").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');

									$(".welcome_mail_send_all").text("Resend All");
									$(".welcome_mail_send_all").attr("style","background:#e2e2e2;");
									$(".welcome_mail_send_all").attr("class","btn btn-default welcome_mail_send_all");

									
									$(".welcome_mail_applicant_table .onboard_trash").hide();
								}
								$(".welcome_applicant_tree_id").val(welcome_val['welcome_tree_id']);
								$(".form_welcome_applicant_documents").append(doc_val_list);
								$(".form_welcome_applicant_documents").val(welcome_val['document']);
								$(".welcome_applicant_link").attr("href",welcome_val['doc_link']);
								$(".welcome_applicant_status").val(welcome_val['status_id']);
								$(".welcome_applicant_date_sent").val(welcome_val['date_sent']);
								$(".welcome_applicant_expiration").val(welcome_val['expiration']);
								i++;
							}else{
								if(i==1){
									$(".welcome_mail_applicant_table tbody").find("tr:gt(1)").remove();
								}
								$(".welcome_mail_applicant_table tbody").append("<tr class='inc"+i+"'>"+$(".welcome_mail_applicant_table tr").eq(1).html()+"</tr>");
								
								if(welcome_val['status_id'] != ''){
									$(".inc"+i+" .btn_sent.btn_welcome").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');

									$(".welcome_mail_send_all").text("Resend All");
									$(".welcome_mail_send_all").attr("style","background:#e2e2e2;");
									$(".welcome_mail_send_all").attr("class","btn btn-default welcome_mail_send_all");

									
									$(".inc"+i+" .welcome_mail_applicant_table .onboard_trash").hide();
								}else{
									$(".inc"+i+" .btn_sent.btn_welcome").html('<button class="btn btn-primary">Send</button>');
								}

								$(".inc"+i+" .welcome_applicant_tree_id").val(welcome_val['welcome_tree_id']);	
								$(".inc"+i+" .form_welcome_applicant_documents").append(doc_val_list);
								$(".inc"+i+" .form_welcome_applicant_documents").val(welcome_val['document']);
								$(".inc"+i+" .welcome_applicant_link").attr("href",welcome_val['doc_link']);
								$(".inc"+i+" .welcome_applicant_status").val(welcome_val['status_id']);
								$(".inc"+i+" .welcome_applicant_date_sent").val(welcome_val['date_sent']);
								$(".inc"+i+" .welcome_applicant_expiration").val(welcome_val['expiration']);
								i++;
							}

										
						});									
					}
				});  

			$.each(welcome_info_dict, function(key_main,val_main) { 
				if (key_main=='survey_dict'){
					$.each(val_main, function(key,val) {
						survey_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_welcome_survey").html("<option value=''></option>");
					$(".form_welcome_survey").append(survey_val_list);
				}
			});	
			
			
			$.each(welcome_info_dict, function(key_main,val_main) { 
				if(key_main=='survey_list'){		
					var i=0;
					$.each(val_main, function(welcome_key,welcome_val) {
						if(i==0){
							if(welcome_val['status_id'] != ''){
								$(".btn_sent.btn_survey").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');

								$(".welcome_mail_send_all").text("Resend All");
								$(".welcome_mail_send_all").attr("style","background:#e2e2e2;");
								$(".welcome_mail_send_all").attr("class","btn btn-default welcome_mail_send_all");

								
								$(".welcome_mail_survey_table .onboard_trash").hide();
							}
							$(".welcome_survey_tree_id").val(welcome_val['survey_tree_id']);
							$(".form_welcome_survey").val(welcome_val['survey']);
							$(".welcome_survey_link").attr("href",welcome_val['survey_link']);
							$(".welcome_survey_status").val(welcome_val['status_id']);
							$(".welcome_survey_date_sent").val(welcome_val['date_sent']);
							$(".welcome_survey_expiration").val(welcome_val['expiration']);
							i++;
						}else{
							if(i==1){
								$(".welcome_mail_survey_table tbody").find("tr:gt(1)").remove();
							}
							$(".welcome_mail_survey_table tbody").append("<tr class='inc"+i+"'>"+$(".welcome_mail_survey_table tr").eq(1).html()+"</tr>");
							
							if(welcome_val['status_id'] != ''){
								$(".inc"+i+" .btn_sent.btn_survey").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');

								$(".welcome_mail_send_all").text("Resend All");
								$(".welcome_mail_send_all").attr("style","background:#e2e2e2;");
								$(".welcome_mail_send_all").attr("class","btn btn-default welcome_mail_send_all");

								
								$(".inc"+i+" .welcome_mail_survey_table .onboard_trash").hide();
							}else{
								$(".inc"+i+" .btn_sent.btn_survey").html('<button class="btn btn-primary">Send</button>');
							}

							$(".inc"+i+" .welcome_survey_tree_id").val(welcome_val['survey_tree_id']);
							$(".inc"+i+" .form_welcome_survey").val(welcome_val['survey']);
							$(".inc"+i+" .welcome_survey_link").attr("href",welcome_val['survey_link']);
							$(".inc"+i+" .welcome_survey_status").val(welcome_val['status_id']);
							$(".inc"+i+" .welcome_survey_date_sent").val(welcome_val['date_sent']);
							$(".inc"+i+" .welcome_survey_expiration").val(welcome_val['expiration']);
							i++;
						}		
					});									
					}
				});   
			}
		});
   }
});

var InsertValsWelcomeEmailInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var n=0;
		$('.welcome_mail_applicant_table tr').each(function(){
			if(n>=1){
				var welcome_email_info_vals = {
						welcome_applicant_tree_id:$(this).find('.welcome_applicant_tree_id').val(), 
						form_welcome_applicant_documents:$(this).find('.form_welcome_applicant_documents').val(),
						welcome_applicant_link:$(this).find('.welcome_applicant_link').val(),
						welcome_applicant_status:$(this).find('.welcome_applicant_status').val(),
						welcome_applicant_date_sent:$(this).find('.welcome_applicant_date_sent').val(),
						welcome_applicant_expiration:$(this).find('.welcome_applicant_expiration').val(),
					};
			    var hr_onboarding = new Model('hr.employee.onboarding');
				hr_onboarding.call('insert_records_welcome_email_info', [[1], arg1,welcome_email_info_vals])
				.then(function() {
				});
			}
			n++;
		});
		var m=0;
		$('.welcome_mail_survey_table tr').each(function(){
			if(m>=1){
				var survey_welcome_email_info_vals = {
						welcome_survey_tree_id:$(this).find('.welcome_survey_tree_id').val(), 
						form_welcome_survey:$(this).find('.form_welcome_survey').val(),
						welcome_survey_link:$(this).find('.welcome_survey_link').val(),
						welcome_survey_status:$(this).find('.welcome_survey_status').val(),
						welcome_survey_date_sent:$(this).find('.welcome_survey_date_sent').val(),
						welcome_survey_expiration:$(this).find('.welcome_survey_expiration').val(),
					};
			    var hr_onboarding = new Model('hr.employee.onboarding');
				hr_onboarding.call('insert_records_survey_welcome_email_info', [[1], arg1,survey_welcome_email_info_vals])
				.then(function() {
				});
			}
			m++;
		});

		
		var substate_name = 'appraisal';
		var state_name = 'hire';
	    var hr_onboarding_state = new Model('hr.employee.onboarding');
		hr_onboarding_state.call('change_status', [[1], arg1,substate_name,state_name])
		.then(function() {
		});
   }
});

var AppraisalInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('appraisal_info', [[1], arg1])
		.then(function(appraisal_info_dict) {
				if(appraisal_info_dict){
					if(appraisal_info_dict.appraisal_by_short == 1){
						$(".days_appraisal").attr('checked','checked');
					}
					if(appraisal_info_dict.appraisal_by_manager == 1){
						$(".manager").attr('checked','checked');
					}
					if(appraisal_info_dict.appraisal_self == 1){
						$(".employee").attr('checked','checked');
					}
					if(appraisal_info_dict.appraisal_by_collaborators == 1){
						$(".direct_report").attr('checked','checked');
					}
					if(appraisal_info_dict.direct_report_anonymous == 1){
						$(".direct_report_anonymous").attr('checked','checked');
					}
					if(appraisal_info_dict.appraisal_by_colleagues == 1){
						$(".colleagues").attr('checked','checked');
					}
					if(appraisal_info_dict.colleague_report_anonymous == 1){
						$(".colleagues_anonymous").attr('checked','checked');
					}
					if(appraisal_info_dict.appraisal_by_coach == 1){
						$(".coach").attr('checked','checked');
					}
					if(appraisal_info_dict.periodic_appraisal == 1){
						$(".periodic_appraisal").attr('checked','checked');
					}
					if(appraisal_info_dict.auto_send_appraisals == 1){
						$(".auto_send_appraisal").attr('checked','checked');
					}
					$(".repeat_period").val(appraisal_info_dict.appraisal_frequency);
					$(".period").val(appraisal_info_dict.appraisal_frequency_unit);
					$(".next_appraisal_date").val(appraisal_info_dict.appraisal_date);
				}
		});
   }
});

var InsertValsAppraisalInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var days_appraisal='';
		if($('input.days_appraisal').is(':checked')){
			days_appraisal=$(".days_appraisal").val();
		}
		var manager='';
		if($('input.manager').is(':checked')){
			manager=$(".manager").val();
		}
		var employee='';
		if($('input.employee').is(':checked')){
			employee=$(".employee").val();
		}
		var direct_report='';
		if($('input.direct_report').is(':checked')){
			direct_report=$(".direct_report").val();
		}
		var direct_report_anonymous='';
		if($('input.direct_report_anonymous').is(':checked')){
			direct_report_anonymous=$(".direct_report_anonymous").val();
		}
		var colleagues='';
		if($('input.colleagues').is(':checked')){
			colleagues=$(".colleagues").val();
		}
		var colleagues_anonymous='';
		if($('input.colleagues_anonymous').is(':checked')){
			colleagues_anonymous=$(".colleagues_anonymous").val();
		}
		var coach='';
		if($('input.coach').is(':checked')){
			coach=$(".coach").val();
		}
		var periodic_appraisal='';
		if($('input.periodic_appraisal').is(':checked')){
			periodic_appraisal=$(".periodic_appraisal").val();
		}
		var auto_send_appraisal='';
		if($('input.auto_send_appraisal').is(':checked')){
			auto_send_appraisal=$(".auto_send_appraisal").val();
		}
		var appraisal_plan_info = {	
				days_appraisal : days_appraisal,
				manager : manager,
				employee : employee,
				direct_report : direct_report,
				direct_report_anonymous : direct_report_anonymous,
				colleagues : colleagues,
				colleagues_anonymous : colleagues_anonymous,
				coach : coach,
				periodic_appraisal : periodic_appraisal,
				repeat_period : $(".repeat_period").val(), 
				period : $(".period").val(),
				next_appraisal_date : $(".next_appraisal_date").val(),
				auto_send_appraisal : auto_send_appraisal
			};
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('insert_records_appraisal_info', [[1], arg1,appraisal_plan_info])
		.then(function() {
		});
		
		
		var substate_name = 'hire_summary';
		var state_name = 'hire';
	    var hr_onboarding_state = new Model('hr.employee.onboarding');
		hr_onboarding_state.call('change_status', [[1], arg1,substate_name,state_name])
		.then(function() {
		});
   }
});

var welcomeSummary = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('welcome_summary', [[1], arg1])
		.then(function(welcome_summary_dict) {


			var doc_val_list = ['']
			var survey_val_list = ['']
			$.each(welcome_summary_dict, function(key_main,val_main) { 
				if (key_main=='document_dict'){
					$.each(val_main, function(key,val) {
						doc_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_welcome_everify_documents").html("<option value=''></option>");
					$(".form_welcome_everify_documents").append(doc_val_list);
				}
			});	

			$.each(welcome_summary_dict, function(key_main,val_main) { 
				if (key_main=='survey_dict'){
					$.each(val_main, function(key,val) {
						survey_val_list += ("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_everify_welcome_survey").html("<option value=''></option>");
					$(".form_everify_welcome_survey").append(survey_val_list);
				}
			});	

			$.each(welcome_summary_dict, function(key_main,val_main) { 
				if(key_main=='welcome_list'){		
					var i=0;
						$.each(val_main, function(welcome_key,welcome_val) {
							if(i==0){
								if(welcome_val['status_id'] != ''){
									$(".btn_sent.btn_welcome").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
									$(".welcome_mail_everify_table .onboard_trash").hide();
								}
								$(".welcome_everify_tree_id").val(welcome_val['welcome_tree_id']);
								$(".form_welcome_everify_documents").val(welcome_val['document']);
								$(".welcome_everify_link").attr("href",welcome_val['doc_link']);
								$(".welcome_everify_status").val(welcome_val['status_id']);
								$(".welcome_everify_date_sent").val(welcome_val['date_sent']);
								$(".welcome_everify_expiration").val(welcome_val['expiration']);
								i++;
							}else{
								if(i==1){
									$(".welcome_mail_everify_table tbody").find("tr:gt(1)").remove();
								}
								$(".welcome_mail_everify_table tbody").append("<tr class='inc"+i+"'>"+$(".welcome_mail_everify_table tr").eq(1).html()+"</tr>");
								
								if(welcome_val['status_id'] != ''){
									$(".inc"+i+" .btn_sent.btn_welcome").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
									$(".inc"+i+" .welcome_mail_everify_table .onboard_trash").hide();
								}else{
									$(".inc"+i+" .btn_sent.btn_welcome").html('<button class="btn btn-primary">Send</button>');
								}

								$(".inc"+i+" .welcome_everify_tree_id").val(welcome_val['welcome_tree_id']);
								$(".inc"+i+" .form_welcome_everify_documents").val(welcome_val['document']);
								$(".inc"+i+" .welcome_everify_link").attr("href",welcome_val['doc_link']);
								$(".inc"+i+" .welcome_everify_status").val(welcome_val['status_id']);
								$(".inc"+i+" .welcome_everify_date_sent").val(welcome_val['date_sent']);
								$(".inc"+i+" .welcome_everify_expiration").val(welcome_val['expiration']);
								i++;
							}

										
						});									
					}
				});  
			
			$.each(welcome_summary_dict, function(key_main,val_main) { 
				if(key_main=='survey_list'){		
					var i=0;
						$.each(val_main, function(welcome_key,welcome_val) {
							if(i==0){
								if(welcome_val['status_id'] != ''){
									$(".btn_sent.btn_survey").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
									$(".welcome_mail_everify_table_summary .onboard_trash").hide();
								}
								$(".welcome_everify_survey_tree_id").val(welcome_val['survey_tree_id']);
								$(".form_everify_welcome_survey").val(welcome_val['survey']);
								$(".welcome_everify_survey_link").attr("href",welcome_val['survey_link']);
								$(".welcome_everify_survey_status").val(welcome_val['status_id']);
								$(".welcome_everify_survey_date_sent").val(welcome_val['date_sent']);
								$(".welcome_everify_survey_expiration").val(welcome_val['expiration']);
								i++;
							}else{
								if(i==1){
									$(".welcome_mail_everify_table_summary tbody").find("tr:gt(1)").remove();
								}
								$(".welcome_mail_everify_table_summary tbody").append("<tr class='inc"+i+"'>"+$(".welcome_mail_everify_table_summary tr").eq(1).html()+"</tr>");
								
								if(welcome_val['status_id'] != ''){
									$(".inc"+i+" .btn_sent.btn_welcome").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
									$(".inc"+i+" .welcome_mail_everify_table_summary .onboard_trash").hide();
								}else{
									$(".inc"+i+" .btn_sent.btn_welcome").html('<button class="btn btn-primary">Send</button>');
								}

								$(".inc"+i+" .welcome_everify_survey_tree_id").val(welcome_val['survey_tree_id']);
								$(".inc"+i+" .form_everify_welcome_survey").val(welcome_val['survey']);
								$(".inc"+i+" .welcome_everify_survey_link").attr("href",welcome_val['survey_link']);
								$(".inc"+i+" .welcome_everify_survey_status").val(welcome_val['status_id']);
								$(".inc"+i+" .welcome_everify_survey_date_sent").val(welcome_val['date_sent']);
								$(".inc"+i+" .welcome_everify_survey_expiration").val(welcome_val['expiration']);
								i++;
							}

										
						});									
					}
				}); 
			$.each(welcome_summary_dict, function(key_main,val_main) {   
				if(welcome_summary_dict){
					$(".e_verify").val(welcome_summary_dict.everify);
				}		
			});	
		});
   }
});

var InsertValsHireSummary = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('send_benefit_survey', [[1], arg1]).then(function() {
		});
   }
});

var InsertValsBenefitsState = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var substate_name = 'ben_survey';
		var state_name = 'benefits';
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('change_status', [[1], arg1,substate_name,state_name]).then(function() {
		});
   }
});
var InsertValsEmployeeSummaryState = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var substate_name = 'emp_summary';
		var state_name = 'contract';
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('change_status', [[1], arg1,substate_name,state_name]).then(function() {
		});
   }
});


var InsertValsContract = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var substate_name = 'contract';
		var state_name = 'contract';
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('change_status', [[1], arg1,substate_name,state_name]).then(function() {
		});
   }
});

var BenifitsSurveyInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('benifits_survey_link', [[1], arg1])
		.then(function(benifits_survey_info) {
			if(benifits_survey_info){
				$(".not_eligible").attr("style","display : none;");
				$(".benefits_survey_link").attr("href",benifits_survey_info);
			}else{
				$(".eligible").attr("style","display : none;");
			}
		});
   }
});

var BenifitsSurveyResultsInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('benifits_survey_results_info', [[1], arg1])
		.then(function(benifits_survey_results_info) {
			if(benifits_survey_results_info != 0){
				$(".not_eligible").attr("style","display : none;");
				$(".benefits_survey_link").attr("href",benifits_survey_results_info);
			}else{
				$(".eligible").attr("style","display : none;");
			}
		});
   }
});

var EmployeeInfo = Widget.extend ({
		init: function() {
			var arg1=$(".form_id").text();			
		    var self = this;
			var hr_onboarding = new Model('hr.employee.onboarding');
			hr_onboarding.call('employee_info', [[1], arg1])
			.then(function(employee_info_dict) {
				if(employee_info_dict){
					$(".form_employee_summary_name").val(employee_info_dict.name);
					$(".work_address").val(employee_info_dict.address_id);
					$(".work_street2").val(employee_info_dict.street2);
					$(".work_city").val(employee_info_dict.city);
					$(".work_state").val(employee_info_dict.state);
					$(".work_country").val(employee_info_dict.country);
					$(".work_mobile").val(employee_info_dict.mobile_phone);
					$(".work_email").val(employee_info_dict.work_email);
					$(".work_phone").val(employee_info_dict.work_phone);
					$(".primary_job").val(employee_info_dict.job_id);
					$(".job_seniority_title").val(employee_info_dict.job_seniority_title);
					$(".contract_type").val(employee_info_dict.employment_status);
					$(".manager").val(employee_info_dict.parent_id);
					$(".coach").val(employee_info_dict.coach_id);
					if(employee_info_dict.manager_checkbox == 1){
						$(".is_a_manager").attr('checked','checked');
					}
					$(".nationality").val(employee_info_dict.country_id);
					$(".identification_no").val(employee_info_dict.identification_id);
					$(".passport_no").val(employee_info_dict.passport_id);
					$(".home_address").val(employee_info_dict.address_home_id);
					$(".location_id").val(employee_info_dict.location_id);
					$(".gender").val(employee_info_dict.gender);
					$(".marital_status").val(employee_info_dict.marital);
					$(".no_of_child").val(employee_info_dict.children);
					$(".ethnic_id").val(employee_info_dict.ethnic_id);
					$(".smoker").val(employee_info_dict.smoker);
					$(".date_of_birth").val(employee_info_dict.birthday);
					$(".place_of_birth").val(employee_info_dict.place_of_birth);
					$(".birth_country").val(employee_info_dict.birth_country);
					$(".age").val(employee_info_dict.age);
					if(employee_info_dict.verify_checkbox == 1){
						$(".verified").attr('checked','checked');
					}
					$(".work_authorization").val(employee_info_dict.work_authorization);
					$(".document_no").val(employee_info_dict.document_no);
					$(".expiration_date").val(employee_info_dict.expiration_date);
					$(".document_a").val(employee_info_dict.document_A);
					$(".document_b").val(employee_info_dict.document_B);
					$(".document_c").val(employee_info_dict.document_C);
					$(".visa_type").val(employee_info_dict.visa_type);
					$(".visa_expiration").val(employee_info_dict.visa_exp);
					$(".visa_country").val(employee_info_dict.country);
					$(".ref_id").val(employee_info_dict.ref_id);
					$(".application_date").val(employee_info_dict.application_date);
					$(".approval_date").val(employee_info_dict.approval_date);
					$(".expiration_date_visa").val(employee_info_dict.exp_date);
					$(".veteran").val(employee_info_dict.veteran);
					$(".veteran_of").val(employee_info_dict.veteran_of);
					$(".branch").val(employee_info_dict.branch);
					$(".seperation_date").val(employee_info_dict.separation_date);
					$(".armed_medal").val(employee_info_dict.service_medal);
					$(".special_veteran").val(employee_info_dict.disabled_veteran);
					$(".wartime").val(employee_info_dict.actv_wartime);
					$(".disable").val(employee_info_dict.disabled);
					$(".disable_type").val(employee_info_dict.disablity_type);
					$(".timesheet_cost").val(employee_info_dict.timesheet_cost);
					$(".account").val(employee_info_dict.account_id);
					$(".product").val(employee_info_dict.product_id);
					$(".analytic_journal").val(employee_info_dict.journal_id);
					$(".task").val(employee_info_dict.project_task);
					$(".company_id").val(employee_info_dict.company_id);
					$(".related_user").val(employee_info_dict.user_id);
					$(".benefits_status").val(employee_info_dict.benefit_status);
					$(".scheduled_hours").val(employee_info_dict.scheduled_hours);
					$(".enrollment_deadline").val(employee_info_dict.enrollment_deadline);
					$(".badge_id").val(employee_info_dict.barcode);
					$(".pin").val(employee_info_dict.pin);
					if(employee_info_dict.manual_attendance_checkbox == 1){
						$(".manual_attendance").attr('checked','checked');
					}
					$(".medical_exam").val(employee_info_dict.medic_exam);
					$(".company_vehicel").val(employee_info_dict.vehicle);
					$(".home_work_dist").val(employee_info_dict.vehicle_distance);
					$(".pay_type").val(employee_info_dict.pay_type);
					$(".exempt_overtime").val(employee_info_dict.overtime_pay);
					$(".start_date").val(employee_info_dict.start_date);
					$(".ben_sen_date").val(employee_info_dict.benefit_seniority_date);
					$(".hire_date").val(employee_info_dict.hire_date);
					$(".termination_date").val(employee_info_dict.termination_date);
					$(".termination_type").val(employee_info_dict.termination_type);
					$(".termination_reason").val(employee_info_dict.termination_reason);
					if(employee_info_dict.rehire_eligible_checkbox == 1){
						$(".eligible_rehire").attr('checked','checked');
					}
					if(employee_info_dict.cobra_eligible_checkbox == 1){
						$(".cobra_eligible").attr('checked','checked');
					}
					$(".emp_id").val(employee_info_dict.employee_id);
					$(".timeclock").val(employee_info_dict.time_clock);
					$(".hr_ststus").val(employee_info_dict.hr_status);
					$(".direct_deposit_status").val(employee_info_dict.direct_deposit);
					$(".date_added").val(employee_info_dict.date_added);
					$(".date_modified").val(employee_info_dict.date_modified);
					$(".rem_legal_leave").val(employee_info_dict.remaining_leaves);
					$(".timesheet_valid_limit").val(employee_info_dict.timesheet_validated);
					$(".corporate_credit_card").val(employee_info_dict.credit_card_id);
					$(".emergency_name").val(employee_info_dict.emergency_contact_name);
					$(".emergency_phone").val(employee_info_dict.emergency_contact_phone);
					$(".emergency_relationship").val(employee_info_dict.emergency_contact_relationship);
					$(".alias_first_name").val(employee_info_dict.first_name_alias);
					$(".alias_middle_name").val(employee_info_dict.middle_name_alias);
					$(".alias_last_name").val(employee_info_dict.last_name_alias);
				}
			});
	   }
});

var EmployeeView = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('employee_view', [[1], arg1]).then(function(res) {
			if(res){
				window.open($(".edit_employee_info_redirect").attr("test")+"&id="+res,'_blank');
			}else{

			}				
		});
   }
});

var WelcomeMailSendAll = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var welcome_email_info_vals = []
		var n=0;
		$('.welcome_mail_applicant_table tr').each(function(){
			if(n>=1){
				welcome_email_info_vals.push({
					welcome_applicant_tree_id:$(this).find('.welcome_applicant_tree_id').val(),
					form_welcome_applicant_documents:$(this).find('.form_welcome_applicant_documents').val(),
					welcome_applicant_link:$(this).find('.welcome_applicant_link').val(),
					welcome_applicant_status:$(this).find('.welcome_applicant_status').val(),
					welcome_applicant_date_sent:$(this).find('.welcome_applicant_date_sent').val(),
					welcome_applicant_expiration:$(this).find('.welcome_applicant_expiration').val(),
				});
			}
			n++;
		});
		var m=0;
		var survey_welcome_email_info_vals = []
		$('.welcome_mail_survey_table tr').each(function(){
			if(m>=1){
				survey_welcome_email_info_vals.push({
					welcome_survey_tree_id:$(this).find('.welcome_survey_tree_id').val(), 
					form_welcome_survey:$(this).find('.form_welcome_survey').val(),
					welcome_survey_link:$(this).find('.welcome_survey_link').val(),
					welcome_survey_status:$(this).find('.welcome_survey_status').val(),
					welcome_survey_date_sent:$(this).find('.welcome_survey_date_sent').val(),
					welcome_survey_expiration:$(this).find('.welcome_survey_expiration').val(),
				});
			}
			m++;
		});
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('welcome_mail_send_all', [[1], arg1,welcome_email_info_vals,survey_welcome_email_info_vals]).then(function() {

		});
   }
});

var BackgroundCheckSendAll = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var inine_applicant_info_vals =[]
		var n=0;
		$('.i9_applicant_table tr').each(function(){
			if(n>=1){
				inine_applicant_info_vals.push({
					applicant_tree_id:$(this).find('.applicant_tree_id').val(), 
					form_applicant_documents:$(this).find('.form_applicant_documents').val(),
					applicant_link:$(this).find('.applicant_link').val(),
					applicant_status:$(this).find('.applicant_status').val(),
					applicant_date_sent:$(this).find('.applicant_date_sent').val(),
					applicant_expiration:$(this).find('.applicant_expiration').val(),
				});
			}
			n++;
		});
		var m=0;
		var inine_employer_info_vals = []
		$('.i9_employer_table tr').each(function(){
			if(m>=1){
				inine_employer_info_vals.push({
					employer_tree_id:$(this).find('.employer_tree_id').val(), 
					form_employer_documents:$(this).find('.form_employer_documents').val(),
					employer_link:$(this).find('.employer_link').val(),
					employer_status:$(this).find('.employer_status').val(),
					employer_date_sent:$(this).find('.employer_date_sent').val(),
					employer_expiration:$(this).find('.employer_expiration').val(),
				});
			}
			m++;
		});
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('background_check_send_all', [[1], arg1,inine_applicant_info_vals,inine_employer_info_vals]).then(function() {

		});
   }
});

var ConsentSendAll = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var background_consent_info_vals = []
		var n=0;
		$('.background_check_consent_form_table tr').each(function(){
			if(n>=1){
				background_consent_info_vals.push({
					consent_form_tree_id:$(this).find('.consent_form_tree_id').val(), 
					form_consent_documents:$(this).find('.form_consent_documents').val(),
					background_check_consent_form_link:$(this).find('.background_check_consent_form_link').val(),
					background_check_consent_form_status:$(this).find('.background_check_consent_form_status').val(),
					background_check_consent_form_date_sent:$(this).find('.background_check_consent_form_date_sent').val(),
					background_check_consent_form_expiration:$(this).find('.background_check_consent_form_expiration').val(),
				});
			}
			n++;
		});
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('consent_send_all', [[1], arg1,background_consent_info_vals]).then(function() {
			new ConsentForm();
		});
   }
});


var CreateContract = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('create_contract_via_link', [[1], arg1]).then(function(res) {
			if(res){
				window.open($(".create_contract_link_redirect").attr("test")+"&id="+res,'_blank');
			}else{

			}				
		});
   }
});


var RemoveRecord = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var remove_tree_id = $('.hidden_value').val();
		var remove_model_id = $('.hidden_model').val();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('remove_record', [[1], arg1,remove_tree_id,remove_model_id])
		.then(function(res) {
	
		});
   }
});


var ContractInfo = Widget.extend ({
		init: function() {	
			var arg1=$(".form_id").text();			
		    var self = this;
			var hr_onboarding = new Model('hr.employee.onboarding');
			hr_onboarding.call('contract_info', [[1], arg1])
			.then(function(contract_info_dict) {
				if(contract_info_dict){
					$(".contract_name").val(contract_info_dict.name);
					$(".form_employee_name").val(contract_info_dict.employee_id);
					$(".contract_form_contract_type").val(contract_info_dict.type_id);
					$(".form_primary_job").val(contract_info_dict.job_id);
					$(".form_trial_start").val(contract_info_dict.trial_date_start);
					$(".form_scheduled_pay").val(contract_info_dict.schedule_pay);
					$(".form_trial_end").val(contract_info_dict.trial_date_end);
					$(".contract_form_job_sen_title").val(contract_info_dict.job_seniority_title);
					$(".form_duration_start").val(contract_info_dict.date_start);			
					$(".form_leave_plan").val(contract_info_dict.leave_holiday_plan);
					$(".form_duration_end").val(contract_info_dict.date_end);			
					$(".form_notice").val(contract_info_dict.notice);			
					$(".contract_form_pay_type").val(contract_info_dict.salary_computation_method);	
					$(".contract_form_wage").val(contract_info_dict.wage);			
					$(".contract_form_salary_structure").val(contract_info_dict.struct_id);			
					$(".form_draw_type").val(contract_info_dict.draw_type_id);			
					$(".form_production_basics").val(parseFloat(contract_info_dict.production_basis).toFixed(2));			
					$(".form_production_rate").val(parseFloat(contract_info_dict.production_rate).toFixed(2));			
					$(".form_discount_rate").val(parseFloat(contract_info_dict.discount_rate).toFixed(2));			
					$(".form_annual_draw").val(parseFloat(contract_info_dict.annual_draw).toFixed(2));			
					$(".form_payout_delay").val(contract_info_dict.payout_delay);	
					$(".form_notes").val(contract_info_dict.notes);		

				$.each(contract_info_dict, function(key_main,val_main) { 
				
					if(key_main=='job_position_list'){		
						var i=0;
							$.each(val_main, function(job_key,job_val) {
								if(i==0){
									$(".form_job_position_tree_id").val(job_val['job_position_tree_id']);
									$(".form_job_contract").val(job_val['job_id']);
									$(".form_job_seniority_title_contract").val(job_val['seniority_id']);
									$(".form_hourly_rate_class").val(job_val['hourly_rate_class_id']);
									$(".form_hourly_rate").val(parseFloat(job_val['hourly_rate']).toFixed(2));
									if(job_val['is_main_job'] == true){
										$(".main_job_position").attr('checked','checked');
									}else{														
										$(".main_job_position").prop('checked',false);
									}
									if(job_val['is_bonus'] == true){
										$(".contract_bonus").attr('checked','checked');
									}else{														
										$(".contract_bonus").prop('checked',false);
									}
									i++;
								}else{
									if(i==1){
										$(".job_position tbody").find("tr:gt(1)").remove();
									}
									$(".job_position tbody").append("<tr class='inc"+i+"'>"+$(".job_position tr").eq(1).html()+"</tr>");
									$(".inc"+i+" .form_job_position_tree_id").val(job_val['job_position_tree_id']);								
									$(".inc"+i+" .form_job_contract").val(job_val['job_id']);
									$(".inc"+i+" .form_job_seniority_title_contract").val(job_val['seniority_id']);
									$(".inc"+i+" .form_hourly_rate_class").val(job_val['hourly_rate_class_id']);
									$(".inc"+i+" .form_hourly_rate").val(parseFloat(job_val['hourly_rate']).toFixed(2));
									if(job_val['is_main_job'] == true){											
										$(".inc"+i+" .main_job_position").attr('checked','checked');
									}else{														
										$(".inc"+i+" .main_job_position").prop('checked',false);
									}
									if(job_val['is_bonus'] == true){
										$(".inc"+i+" .contract_bonus").attr('checked','checked');
									}else{														
										$(".inc"+i+" .contract_bonus").prop('checked',false);
									}
									i++;
								}

							});		
				

						}
					});

				$.each(contract_info_dict, function(key_main,val_main) { 
				
					if(key_main=='production_list'){		
						var i=0;
							$.each(val_main, function(pro_key,pro_val) {
								if(i==0){
									$(".form_production_tree_id").val(pro_val['production_tree_id']);
									$(".form_job").val(pro_val['job_id']);
									$(".form_code").val(pro_val['code_id']);
									$(".form_tag").val(pro_val['production_tag_id']);
									$(".form_type").val(pro_val['type_id']);
									$(".form_rate").val(parseFloat(pro_val['rate_id']).toFixed(2));
									$(".form_payout_period").val(pro_val['payout_period']);
									$(".form_salary_rule").val(pro_val['hourly_rate']);
									if(pro_val['is_bonus'] == true){
										$(".form_include").attr('checked','checked');
									}else{														
										$(".form_include").prop('checked',false);
									}
									if(pro_val['validation'] == true){
										$(".form_double_validation").attr('checked','checked');
									}else{														
										$(".form_double_validation").prop('checked',false);
									}
									if(pro_val['sub_amount'] == true){
										$(".form_subtract_amount").attr('checked','checked');
									}else{														
										$(".form_subtract_amount").prop('checked',false);
									}
									if(pro_val['deduct_draw'] == true){
										$(".form_deduce_draw").attr('checked','checked');
									}else{														
										$(".form_deduce_draw").prop('checked',false);
									}
									i++;
								}else{
									if(i==1){
										$(".contract_production_table tbody").find("tr:gt(1)").remove();
									}
									$(".contract_production_table tbody").append("<tr class='inc"+i+"'>"+$(".contract_production_table tr").eq(1).html()+"</tr>");
									
									$(".inc"+i+" .form_production_tree_id").val(pro_val['production_tree_id']);								
									$(".inc"+i+" .form_job").val(pro_val['job_id']);
									$(".inc"+i+" .form_code").val(pro_val['code_id']);
									$(".inc"+i+" .form_tag").val(pro_val['production_tag_id']);
									$(".inc"+i+" .form_type").val(pro_val['type_id']);
									$(".inc"+i+" .form_rate").val(pro_val['rate_id']);
									$(".inc"+i+" .form_payout_period").val(pro_val['payout_period']);
									$(".inc"+i+" .form_salary_rule").val(pro_val['hourly_rate']);
									if(pro_val['is_bonus'] == true){
										$(".inc"+i+" .form_include").attr('checked','checked');
									}else{														
										$(".inc"+i+" .form_include").prop('checked',false);
									}
									if(pro_val['sub_amount'] == true){
										$(".inc"+i+" .form_subtract_amount").attr('checked','checked');
									}else{														
										$(".inc"+i+" .form_subtract_amount").prop('checked',false);
									}
									if(pro_val['validation'] == true){
										$(".inc"+i+" .form_double_validation").attr('checked','checked');
									}else{														
										$(".inc"+i+" .form_double_validation").prop('checked',false);
									}
									if(pro_val['deduct_draw'] == true){
										$(".inc"+i+" .form_deduce_draw").attr('checked','checked');
									}else{														
										$(".inc"+i+" .form_deduce_draw").prop('checked',false);
									}
									i++;
								}
							});									
						}
					});

					$.each(contract_info_dict, function(key_main,val_main) { 
				
					if(key_main=='benefits_list'){		
						var i=0;
							$.each(val_main, function(ben_key,ben_val) {
								if(i==0){
									$(".form_employee_benefits_tree_id").val(ben_val['benefits_tree_id']);
									$(".form_benefits").val(ben_val['category_id']);
									$(".form_benefits_rate").val(ben_val['rate_id']);
									$(".form_employee_amount").val(ben_val['employee_amount']);
									$(".form_employer_amount").val(ben_val['employer_amount']);
									$(".form_amount_type").val(ben_val['amount_type']);
									$(".form_ben_start_date").val(ben_val['date_start']);
									$(".form_ben_end_date").val(ben_val['date_end']);
									i++;
								}else{
									if(i==1){
										$(".contract_employee_benefits tbody").find("tr:gt(1)").remove();
									}
									$(".contract_employee_benefits tbody").append("<tr class='inc"+i+"'>"+$(".contract_employee_benefits tr").eq(1).html()+"</tr>");
									
									$(".inc"+i+" .form_employee_benefits_tree_id").val(ben_val['benefits_tree_id']);								
									$(".inc"+i+" .form_benefits").val(ben_val['category_id']);
									$(".inc"+i+" .form_benefits_rate").val(ben_val['rate_id']);
									$(".inc"+i+" .form_employee_amount").val(ben_val['employee_amount']);
									$(".inc"+i+" .form_employer_amount").val(ben_val['employer_amount']);
									$(".inc"+i+" .form_amount_type").val(ben_val['amount_type']);
									$(".inc"+i+" .form_ben_start_date").val(ben_val['date_start']);
									$(".inc"+i+" .form_ben_end_date").val(ben_val['date_end']);
									i++;
								}
							});									
						}
					});

				}
			});
	   }
}); 



var ContractInfoNext = Widget.extend ({
		init: function() {	
			var arg1=$(".form_id").text();			
		    var self = this;
			var hr_onboarding = new Model('hr.employee.onboarding');
			hr_onboarding.call('contract_info', [[1], arg1])
			.then(function(contract_info_dict) {
				if(contract_info_dict){
					$(".contract_name").val(contract_info_dict.name);
					$(".form_employee_name").val(contract_info_dict.employee_id);
					$(".contract_form_contract_type").val(contract_info_dict.type_id);
					$(".form_primary_job").val(contract_info_dict.job_id);
					$(".form_trial_start").val(contract_info_dict.trial_date_start);
					$(".form_scheduled_pay").val(contract_info_dict.schedule_pay);
					$(".form_trial_end").val(contract_info_dict.trial_date_end);
					$(".contract_form_job_sen_title").val(contract_info_dict.job_seniority_title);
					$(".form_duration_start").val(contract_info_dict.date_start);			
					$(".form_leave_plan").val(contract_info_dict.leave_holiday_plan);
					$(".form_duration_end").val(contract_info_dict.date_end);			
					$(".form_notice").val(contract_info_dict.notice);			
					$(".contract_form_pay_type").val(contract_info_dict.salary_computation_method);	
					$(".contract_form_wage").val(contract_info_dict.wage);			
					$(".contract_form_salary_structure").val(contract_info_dict.struct_id);			
					$(".form_draw_type").val(contract_info_dict.draw_type_id);			
					$(".form_production_basics").val(parseFloat(contract_info_dict.production_basis).toFixed(2));			
					$(".form_production_rate").val(parseFloat(contract_info_dict.production_rate).toFixed(2));			
					$(".form_discount_rate").val(parseFloat(contract_info_dict.discount_rate).toFixed(2));			
					$(".form_annual_draw").val(parseFloat(contract_info_dict.annual_draw).toFixed(2));			
					$(".form_payout_delay").val(contract_info_dict.payout_delay);	
					$(".form_notes").val(contract_info_dict.notes);		

				$.each(contract_info_dict, function(key_main,val_main) { 
				
					if(key_main=='job_position_list'){		
						var i=0;
							$.each(val_main, function(job_key,job_val) {
								if(i==0){
									$(".form_job_position_tree_id").val(job_val['job_position_tree_id']);
									$(".form_job_contract").val(job_val['job_id']);
									$(".form_job_seniority_title_contract").val(job_val['seniority_id']);
									$(".form_hourly_rate_class").val(job_val['hourly_rate_class_id']);
									$(".form_hourly_rate").val(parseFloat(job_val['hourly_rate']).toFixed(2));
									if(job_val['is_main_job'] == true){
										$(".main_job_position").attr('checked','checked');
									}else{														
										$(".main_job_position").prop('checked',false);
									}
									if(job_val['is_bonus'] == true){
										$(".contract_bonus").attr('checked','checked');
									}else{														
										$(".contract_bonus").prop('checked',false);
									}
									i++;
								}else{
									if(i==1){
										$(".job_position tbody").find("tr:gt(1)").remove();
									}
									$(".job_position tbody").append("<tr class='inc"+i+"'>"+$(".job_position tr").eq(1).html()+"</tr>");
									$(".inc"+i+" .form_job_position_tree_id").val(job_val['job_position_tree_id']);								
									$(".inc"+i+" .form_job_contract").val(job_val['job_id']);
									$(".inc"+i+" .form_job_seniority_title_contract").val(job_val['seniority_id']);
									$(".inc"+i+" .form_hourly_rate_class").val(job_val['hourly_rate_class_id']);
									$(".inc"+i+" .form_hourly_rate").val(parseFloat(job_val['hourly_rate']).toFixed(2));
									if(job_val['is_main_job'] == true){											
										$(".inc"+i+" .main_job_position").attr('checked','checked');
									}else{														
										$(".inc"+i+" .main_job_position").prop('checked',false);
									}
									if(job_val['is_bonus'] == true){
										$(".inc"+i+" .contract_bonus").attr('checked','checked');
									}else{														
										$(".inc"+i+" .contract_bonus").prop('checked',false);
									}
									i++;
								}

							});		
							
							//alert(contract_info_dict.click_next);
							if(contract_info_dict.click_next=='con_summary'){
								var substate_name = 'con_summary';
								var state_name = 'contract';
							    var hr_onboarding_state = new Model('hr.employee.onboarding');
								hr_onboarding_state.call('change_status', [[1], arg1,substate_name,state_name])
								.then(function() {
								});
								$(".btn-next").click();		
							}

						}
					});

				$.each(contract_info_dict, function(key_main,val_main) { 
				
					if(key_main=='production_list'){		
						var i=0;
							$.each(val_main, function(pro_key,pro_val) {
								if(i==0){
									$(".form_production_tree_id").val(pro_val['production_tree_id']);
									$(".form_job").val(pro_val['job_id']);
									$(".form_code").val(pro_val['code_id']);
									$(".form_tag").val(pro_val['production_tag_id']);
									$(".form_type").val(pro_val['type_id']);
									$(".form_rate").val(parseFloat(pro_val['rate_id']).toFixed(2));
									$(".form_payout_period").val(pro_val['payout_period']);
									$(".form_salary_rule").val(pro_val['hourly_rate']);
									if(pro_val['is_bonus'] == true){
										$(".form_include").attr('checked','checked');
									}else{														
										$(".form_include").prop('checked',false);
									}
									if(pro_val['validation'] == true){
										$(".form_double_validation").attr('checked','checked');
									}else{														
										$(".form_double_validation").prop('checked',false);
									}
									if(pro_val['sub_amount'] == true){
										$(".form_subtract_amount").attr('checked','checked');
									}else{														
										$(".form_subtract_amount").prop('checked',false);
									}
									if(pro_val['deduct_draw'] == true){
										$(".form_deduce_draw").attr('checked','checked');
									}else{														
										$(".form_deduce_draw").prop('checked',false);
									}
									i++;
								}else{
									if(i==1){
										$(".contract_production_table tbody").find("tr:gt(1)").remove();
									}
									$(".contract_production_table tbody").append("<tr class='inc"+i+"'>"+$(".contract_production_table tr").eq(1).html()+"</tr>");
									
									$(".inc"+i+" .form_production_tree_id").val(pro_val['production_tree_id']);								
									$(".inc"+i+" .form_job").val(pro_val['job_id']);
									$(".inc"+i+" .form_code").val(pro_val['code_id']);
									$(".inc"+i+" .form_tag").val(pro_val['production_tag_id']);
									$(".inc"+i+" .form_type").val(pro_val['type_id']);
									$(".inc"+i+" .form_rate").val(pro_val['rate_id']);
									$(".inc"+i+" .form_payout_period").val(pro_val['payout_period']);
									$(".inc"+i+" .form_salary_rule").val(pro_val['hourly_rate']);
									if(pro_val['is_bonus'] == true){
										$(".inc"+i+" .form_include").attr('checked','checked');
									}else{														
										$(".inc"+i+" .form_include").prop('checked',false);
									}
									if(pro_val['sub_amount'] == true){
										$(".inc"+i+" .form_subtract_amount").attr('checked','checked');
									}else{														
										$(".inc"+i+" .form_subtract_amount").prop('checked',false);
									}
									if(pro_val['validation'] == true){
										$(".inc"+i+" .form_double_validation").attr('checked','checked');
									}else{														
										$(".inc"+i+" .form_double_validation").prop('checked',false);
									}
									if(pro_val['deduct_draw'] == true){
										$(".inc"+i+" .form_deduce_draw").attr('checked','checked');
									}else{														
										$(".inc"+i+" .form_deduce_draw").prop('checked',false);
									}
									i++;
								}
							});									
						}
					});

					$.each(contract_info_dict, function(key_main,val_main) { 
				
					if(key_main=='benefits_list'){		
						var i=0;
							$.each(val_main, function(ben_key,ben_val) {
								if(i==0){
									$(".form_employee_benefits_tree_id").val(ben_val['benefits_tree_id']);
									$(".form_benefits").val(ben_val['category_id']);
									$(".form_benefits_rate").val(ben_val['rate_id']);
									$(".form_employee_amount").val(ben_val['employee_amount']);
									$(".form_employer_amount").val(ben_val['employer_amount']);
									$(".form_amount_type").val(ben_val['amount_type']);
									$(".form_ben_start_date").val(ben_val['date_start']);
									$(".form_ben_end_date").val(ben_val['date_end']);
									i++;
								}else{
									if(i==1){
										$(".contract_employee_benefits tbody").find("tr:gt(1)").remove();
									}
									$(".contract_employee_benefits tbody").append("<tr class='inc"+i+"'>"+$(".contract_employee_benefits tr").eq(1).html()+"</tr>");
									
									$(".inc"+i+" .form_employee_benefits_tree_id").val(ben_val['benefits_tree_id']);								
									$(".inc"+i+" .form_benefits").val(ben_val['category_id']);
									$(".inc"+i+" .form_benefits_rate").val(ben_val['rate_id']);
									$(".inc"+i+" .form_employee_amount").val(ben_val['employee_amount']);
									$(".inc"+i+" .form_employer_amount").val(ben_val['employer_amount']);
									$(".inc"+i+" .form_amount_type").val(ben_val['amount_type']);
									$(".inc"+i+" .form_ben_start_date").val(ben_val['date_start']);
									$(".inc"+i+" .form_ben_end_date").val(ben_val['date_end']);
									i++;
								}
							});									
						}
					});

				}
			});

		
		
		

	   }
}); 

var InsertValsCompleteState = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var substate_name = 'completed';
		var state_name = 'complete';
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('change_status', [[1], arg1,substate_name,state_name])
		.then(function() {
		});
   }
}); 

var ApproveSummary = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		//alert($("#g1").text());
		if($("#g1").text()== '') {
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('approve_summary', [[1], arg1]).then(function(progress) {
			if(progress){
				var i=progress;
				var g1 = new JustGage({
		        id: 'g1',
		        value: i,
		        min: 0,
		        max: 100,
		        symbol: '%',
		        pointer: true,
		        gaugeWidthScale: 0.6,
		        customSectors: [{
		          color: '#ff0000',
		          lo: 50,
		          hi: 100
		        }, {
		          color: '#00ff00',
		          lo: 0,
		          hi: 50
		        }],
		        counter: true
		      });
			}
			else{
				var g1 = new JustGage({
		        id: 'g1',
		        value: 0,
		        min: 0,
		        max: 100,
		        symbol: '%',
		        pointer: true,
		        gaugeWidthScale: 0.6,
		        customSectors: [{
		          color: '#ff0000',
		          lo: 50,
		          hi: 100
		        }, {
		          color: '#00ff00',
		          lo: 0,
		          hi: 50
		        }],
		        counter: true
		      });
			}
		});
	}
   }
});

var RejectApplicant = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('reject_applicant_from_planner', [[1], arg1]).then(function() {
		});
   }
});  

$(document).ready(function(){


function calculateAge (birthDate, otherDate) {
    birthDate = new Date(birthDate);
    otherDate = new Date(otherDate);

    var years = (otherDate.getFullYear() - birthDate.getFullYear());

    if (otherDate.getMonth() < birthDate.getMonth() || 
        otherDate.getMonth() == birthDate.getMonth() && otherDate.getDate() < birthDate.getDate()) {
        years--;
    }

    return years;
}

$('[data-toggle="tooltip"]').tooltip(); 


// $('body').delegate('btn_initiate_everify','click',function(){
// 	alert(2324);
// 	var arg1 = $(".form_id").text();
// 	var hr_onboarding = new Model('hr.employee.onboarding');
// 	hr_onboarding.call('everify_check_initiate', [[1], arg1])
// 	.then(function(){
// 		});
// });


$('body').delegate('.btn_initiate_everify','click',function() {
	var arg1 = $(".form_id").text();
	var hr_onboarding = new Model('hr.employee.onboarding');
	hr_onboarding.call('everify_check_redirect', [[1], arg1])
	.then(function(result_vals){
		if(result_vals=='status'){
				alert("All documents are not Fully Signed");
			}
		});
});


$('body').delegate('.everify_case_result_reason','click',function() {
	var arg1 = $(".form_id").text();
	var reason_val = $('.everify_case_result_case_status_dialogue').find(":selected").val();
	var hr_onboarding = new Model('hr.employee.onboarding');
	hr_onboarding.call('close_everify_case', [[1], arg1,reason_val])
	.then(function(result_vals){
		if(result_vals == 1){
			$('#myModal_close').modal('hide');
			new BackgroundiNine();
		}

		});
});

$('body').on('focus',".datepicker_custom", function(){
    $(this).datepicker({
      changeMonth: true,
      changeYear: true,
      yearRange: "1940:2100",
      dateFormat: "yy-mm-dd"
    });
});

$('body').delegate('.form_dob','change',function() {
     $('.form_age').val(calculateAge($(this).val(),new Date()));
});

$('body').delegate('.form_country','change',function() {
     new ChangeState();
});

$('body').delegate('.form_state','change',function() {
     new ChangeCountry();
});

$('body').delegate('.btn_everify','click',function() {
	var arg1 = $(".form_id").text();
	var hr_onboarding = new Model('hr.employee.onboarding');
	hr_onboarding.call('everify_state', [[1], arg1])
	.then(function(result_vals) {
		if (result_vals){
			$(".everify_value").val(result_vals);
			$(".btn_everify").text("Re-Initiate");
			$(".btn_everify").attr("style","background:#e2e2e2;");
			$(".btn_everify").attr("class","btn btn-default btn_everify");
		}
	});	
});

$('body').delegate('.form_background_check_package_items','change',function() {
	
	var arg1=$(".form_id").text();
	var pack_id = $(this).val();
	var tree_id=$(this).parent().parent().find(".background_check_package_tree_id").val();
	var hr_onboarding = new Model('hr.employee.onboarding');
	hr_onboarding.call('add_package', [[1], arg1,tree_id,pack_id])
	.then(function(result_vals) {
		$("a[href='#BackgroundCheck6']").click();
	});
});

$('body').delegate('.form_background_check_items','change',function() {
	var arg1=$(".form_id").text();
	var service_id = $(this).val();
	var tree_id=$(this).parent().parent().find(".background_check_tree_id").val();
	var hr_onboarding = new Model('hr.employee.onboarding');
	hr_onboarding.call('add_service', [[1], arg1,tree_id,service_id])
	.then(function(result_vals) {
		$("a[href='#BackgroundCheck6']").click();
	});
});



		$('body').delegate('.edit_employee_info_redirect','click',function() {
			new EmployeeView();
		});

		$('body').delegate('.welcome_mail_send_all','click',function() {
			new WelcomeMailSendAll();
			setTimeout(function(){
				new WelcomeMail();
				$(".welcome_mail_send_all").text("Resend All");
				$(".welcome_mail_send_all").attr("style","background:#e2e2e2;");
				$(".welcome_mail_send_all").attr("class","btn btn-default welcome_mail_send_all");
			}, 2500);
		});

		$('body').delegate('.background_check_send_all','click',function() {
			new BackgroundCheckSendAll();
			setTimeout(function(){
				new BackgroundCheck();
				$(".background_check_send_all").text("Resend All");
				$(".background_check_send_all").attr("style","background:#e2e2e2;");
				$(".background_check_send_all").attr("class","btn btn-default background_check_send_all");
			}, 2000);
		});

		$('body').delegate('.background_check_summary_send_all','click',function() {
			new BackgroundCheckSendAll();
			setTimeout(function(){
				new BackgroundSummary();
				$(".background_check_summary_send_all").text("Resend All");
				$(".background_check_summary_send_all").attr("style","background:#e2e2e2;");
				$(".background_check_summary_send_all").attr("class","btn btn-default background_check_summary_send_all");
			}, 2000);
		});

		$('body').delegate('.i9_send_all','click',function() {
			new BackgroundCheckSendAll();
			setTimeout(function(){
				new BackgroundiNine();
				$(".i9_send_all").text("Resend All");
				$(".i9_send_all").attr("style","background:#e2e2e2;");
				$(".i9_send_all").attr("class","btn btn-default i9_send_all");
			}, 2000);
		});

		$('body').delegate('.consent_send_all','click',function() {
			new ConsentSendAll();
			setTimeout(function(){
				new ConsentForm();
				$(".consent_send_all").text("Resend All");
				$(".consent_send_all").attr("style","background:#e2e2e2;");
				$(".consent_send_all").attr("class","btn btn-default consent_send_all");
			}, 3000);
		});

		$('body').delegate('.e_verify_send_all','click',function() {
			new BackgroundCheckSendAll();
			setTimeout(function(){
				new HireEverify();
				$(".e_verify_send_all").text("Resend All");
				$(".e_verify_send_all").attr("style","background:#e2e2e2;");
				$(".e_verify_send_all").attr("class","btn btn-default e_verify_send_all");
			}, 2000);
		});

//		Table Row Deleting
		$('body').delegate('.custom_tab li','click',function() {
			var cls=$(this).attr('class');
			$(".tab-pane").removeClass('active');
			$("#"+cls).addClass('active');
		});
		$('body').delegate('.onboard_trash','click',function() {
			if($(this).parent().parent().find('tr').length>2){
		    	var r = confirm("Do you want to delete this record?");
		    	if (r == true) {

					var arg1=$(".form_id").text();
					var remove_tree_id = $('.hidden_value').val();
					var remove_model_id = $('.hidden_model').val();
					var hr_onboarding = new Model('hr.employee.onboarding');
					hr_onboarding.call('remove_record', [[1], arg1,$(this).parent().find('.form_tree_id').val(),$(this).parent().find('.form_tree_id').attr('data-model')])
					.then(function(res) {
						new BackgroundCheck();
					});
					
				}
			}
		});

		$('body').delegate('.smart_buttons_list button','click',function() {
			var arg1 = $(".form_id").text();	
			var hr_onboarding = new Model('hr.employee.onboarding');
			hr_onboarding.call('smart_buttons', [[1], arg1])
			.then(function(smart_button_dict) {
				if(smart_button_dict){
					window.open('web#view_type=form&model=hr.applicant&action=hr_recruitment.crm_case_categ0_act_job&menu_id=hr_recruitment.menu_crm_case_categ0_act_job'+"&id="+smart_button_dict.applicant_id,'_blank');
				}	
			});
			
		});

		$('body').delegate('.btn_welcome_package','click',function() {

			var arg1 = $(".form_id").text();
			var get_started = {con_typ:$(".form_contract_type").val(), pay_typ:$(".form_pay_type").val()};	
			var check_id = 'launch'
			var i=0;
		    $(".get_started .required_cls").each(function(){
		        if($(this).val()=='' || ($(this).val() == null)){
		        	i++;
		        	$(this).attr("style","border-bottom: 2px solid #f00 !important;");
		        }else{			        	
		        	$(this).attr("style","border-bottom: 2px solid #616161 !important");
		        }
		    });
			
			if(i>0){
				alert("Please fill all required fields");
			}
			var hr_onboarding = new Model('hr.employee.onboarding');
			hr_onboarding.call('send_launch_pack', [[1], arg1,check_id,get_started])
			.then(function(result_vals) {
				if(parseInt(result_vals)!=0){
					alert("Personal Information Document has been sent Successfully");
				}else{
					alert("Personal Information document is already sent");
				}
			});			
		});

		$('body').delegate('.btn_sent.btn_applicant','click',function() {

			var parent_val=$(this).parent();
			var arg1 = $(".form_id").text();	
			var tree_id = $(this).parent().find('.applicant_tree_id').val();
			var doc_id={
					applicant_tree_id:$(this).parent().find('.applicant_tree_id').val(), 
					form_applicant_documents:$(this).parent().find('.form_applicant_documents').val(),
					applicant_link:$(this).parent().find('.applicant_link').val(),
					applicant_status:$(this).parent().find('.applicant_status').val(),
					applicant_date_sent:$(this).parent().find('.applicant_date_sent').val(),
					applicant_expiration:$(this).parent().find('.applicant_expiration').val(),
					}
			var check_id = 'applicant'
			var hr_onboarding = new Model('hr.employee.onboarding');
			hr_onboarding.call('send_onboarding_documents_link', [[1], arg1,doc_id,tree_id,check_id])
			.then(function(result_vals) {
				$.each(result_vals, function(key_main,val_main) { 
					if(key_main == 'id')
					{
						parent_val.find(".applicant_tree_id").val(val_main);
					}
					if(key_main == 'link')
					{
						parent_val.find(".applicant_link").attr("href",val_main);
					}
					if(key_main == 'sent')
					{
						parent_val.find(".applicant_date_sent").val(val_main);
					}
					if(key_main == 'end')
					{
						parent_val.find(".applicant_expiration").val(val_main);
					}
					if(key_main == 'status')
					{
						parent_val.find(".applicant_status").val(val_main);
					}
					parent_val.find(".btn_sent.btn_applicant").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
					parent_val.find(".onboard_trash").hide();
				});
			});			
		});

		$('body').delegate('.btn_sent.btn_employer','click',function() {

			var parent_val=$(this).parent();
			var arg1 = $(".form_id").text();	
			var doc_id = {
				employer_tree_id:$(this).parent().find('.employer_tree_id').val(), 
				form_employer_documents:$(this).parent().find('.form_employer_documents').val(),
				employer_link:$(this).parent().find('.employer_link').val(),
				employer_status:$(this).parent().find('.employer_status').val(),
				employer_date_sent:$(this).parent().find('.employer_date_sent').val(),
				employer_expiration:$(this).parent().find('.employer_expiration').val()
			}
			var tree_id = $(this).parent().find('.employer_tree_id').val();
			var check_id = 'employer'
			var hr_onboarding = new Model('hr.employee.onboarding');
			hr_onboarding.call('send_onboarding_documents_link', [[1], arg1,doc_id,tree_id,check_id])
			.then(function(result_vals) {
				$.each(result_vals, function(key_main,val_main) { 
					if(key_main == 'id')
					{
						parent_val.find(".employer_tree_id").val(val_main);
					}
					if(key_main == 'link')
					{
						parent_val.find(".employer_link").attr("href",val_main);
					}
					if(key_main == 'sent')
					{
						parent_val.find(".employer_date_sent").val(val_main);
					}
					if(key_main == 'end')
					{
						parent_val.find(".employer_expiration").val(val_main);
					}
					if(key_main == 'status')
					{
						parent_val.find(".employer_status").val(val_main);
					}
					parent_val.find(".btn_sent.btn_employer").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
					parent_val.find(".onboard_trash").hide();
				});
			});			
		});

		$('body').delegate('.btn_sent.btn_consent','click',function() {

			var parent_val=$(this).parent();
			var arg1 = $(".form_id").text();	
			var doc_id = {
				consent_form_tree_id:$(this).parent().find('.consent_form_tree_id').val(), 
				form_consent_documents:$(this).parent().find('.form_consent_documents').val(),
				background_check_consent_form_link:$(this).parent().find('.background_check_consent_form_link').val(),
				background_check_consent_form_status:$(this).parent().find('.background_check_consent_form_status').val(),
				background_check_consent_form_date_sent:$(this).parent().find('.background_check_consent_form_date_sent').val(),
				background_check_consent_form_expiration:$(this).parent().find('.background_check_consent_form_expiration').val(),
			}
			var tree_id = $(this).parent().find('.consent_form_tree_id').val();
			var check_id = 'consent'
			var hr_onboarding = new Model('hr.employee.onboarding');
			hr_onboarding.call('send_onboarding_documents_link', [[1], arg1,doc_id,tree_id,check_id])
			.then(function(result_vals) {
				$.each(result_vals, function(key_main,val_main) { 
					if(key_main == 'id')
					{
						parent_val.find(".consent_form_tree_id").val(val_main);
					}
					if(key_main == 'link')
					{
						parent_val.find(".background_check_consent_form_link").attr("href",val_main);
					}
					if(key_main == 'sent')
					{
						parent_val.find(".background_check_consent_form_date_sent").val(val_main);
					}
					if(key_main == 'end')
					{
						parent_val.find(".background_check_consent_form_expiration").val(val_main);
					}
					if(key_main == 'status')
					{
						parent_val.find(".background_check_consent_form_status").val(val_main);
					}
					parent_val.find(".btn_sent.btn_consent").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
					parent_val.find(".onboard_trash").hide();
				});
			});			
		});

		$('body').delegate('.btn_sent.btn_adverse','click',function() {

			var parent_val=$(this).parent();
			var arg1 = $(".form_id").text();	
			var doc_id ={
				adverse_action_tree_id:$(this).parent().find('.adverse_action_tree_id').val(), 
				form_adverse_documents:$(this).parent().find('.form_adverse_documents').val(),
				adverse_action_link:$(this).parent().find('.adverse_action_link').val(),
				adverse_action_status:$(this).parent().find('.adverse_action_status').val(),
				adverse_action_date_sent:$(this).parent().find('.adverse_action_date_sent').val(),
				adverse_action_expiration:$(this).parent().find('.adverse_action_expiration').val()
			}
			var tree_id = $(this).parent().find('.adverse_action_tree_id').val();
			var check_id = 'adverse'
			var hr_onboarding = new Model('hr.employee.onboarding');
			hr_onboarding.call('send_onboarding_documents_link', [[1], arg1,doc_id,tree_id,check_id])
			.then(function(result_vals) {
				$.each(result_vals, function(key_main,val_main) { 
					if(key_main == 'id')
					{
						parent_val.find(".adverse_action_tree_id").val(val_main);
					}
					if(key_main == 'link')
					{
						parent_val.find(".adverse_action_link").attr("href",val_main);
					}
					if(key_main == 'sent')
					{
						parent_val.find(".adverse_action_date_sent").val(val_main);
					}
					if(key_main == 'end')
					{
						parent_val.find(".adverse_action_expiration").val(val_main);
					}
					if(key_main == 'status')
					{
						parent_val.find(".adverse_action_status").val(val_main);
					}
					parent_val.find(".btn_sent.btn_adverse").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
					parent_val.find(".onboard_trash").hide();
				});
			});			
		});

		$('body').delegate('.btn_send_approval','click',function() {
			var arg1 = $(".form_id").text();	
			var hr_onboarding = new Model('hr.employee.onboarding');
			hr_onboarding.call('benefits_state_send', [[1], arg1])
			.then(function() {
			});			
		});

		$('body').delegate('.btn_enrolled','click',function() {
			var arg1 = $(".form_id").text();
			var hr_onboarding = new Model('hr.employee.onboarding');
			hr_onboarding.call('benefits_state_enrolled', [[1], arg1])
			.then(function() {
			});			
		});

		$('body').delegate('.btn_sent.btn_welcome','click',function() {
			var parent_val=$(this).parent();
			var arg1 = $(".form_id").text();	
			var doc_id ={
				welcome_applicant_tree_id:$(this).parent().find('.welcome_applicant_tree_id').val(), 
				form_welcome_applicant_documents:$(this).parent().find('.form_welcome_applicant_documents').val(),
				welcome_applicant_link:$(this).parent().find('.welcome_applicant_link').val(),
				welcome_applicant_status:$(this).parent().find('.welcome_applicant_status').val(),
				welcome_applicant_date_sent:$(this).parent().find('.welcome_applicant_date_sent').val(),
				welcome_applicant_expiration:$(this).parent().find('.welcome_applicant_expiration').val()
			}
			var tree_id = $(this).parent().find('.welcome_applicant_tree_id').val();
			var check_id = 'welcome'
			var hr_onboarding = new Model('hr.employee.onboarding');
			hr_onboarding.call('send_onboarding_documents_link', [[1], arg1,doc_id,tree_id,check_id])
			.then(function(result_vals) {
				$.each(result_vals, function(key_main,val_main) { 
					if(key_main == 'id')
					{
						parent_val.find(".welcome_applicant_tree_id").val(val_main);
					}
					if(key_main == 'link')
					{
						parent_val.find(".welcome_applicant_link").attr("href",val_main);
					}
					if(key_main == 'sent')
					{
						parent_val.find(".welcome_applicant_date_sent").val(val_main);
					}
					if(key_main == 'end')
					{
						parent_val.find(".welcome_applicant_expiration").val(val_main);
					}
					if(key_main == 'status')
					{
						parent_val.find(".welcome_applicant_status").val(val_main);
					}
					parent_val.find(".btn_sent.btn_welcome").html('<button class="btn btn-default" style="background:#e2e2e2;">Resend</button>');
					parent_val.find(".onboard_trash").hide();
				});
			});			
		});

		$('body').delegate('.btn_sent.btn_survey','click',function() {
			var parent_val=$(this).parent();
			var arg1 = $(".form_id").text();	
			var survey_id ={
				welcome_survey_tree_id:$(this).parent().find('.welcome_survey_tree_id').val(), 
				form_welcome_survey:$(this).parent().find('.form_welcome_survey').val(),
				welcome_survey_link:$(this).parent().find('.welcome_survey_link').val(),
				welcome_survey_status:$(this).parent().find('.welcome_survey_status').val(),
				welcome_survey_date_sent:$(this).parent().find('.welcome_survey_date_sent').val(),
				welcome_survey_expiration:$(this).parent().find('.welcome_survey_expiration').val()
			}
			var tree_id = $(this).parent().find('.welcome_survey_tree_id').val();
			var hr_onboarding = new Model('hr.employee.onboarding');
			hr_onboarding.call('send_survey', [[1], arg1,survey_id,tree_id])
			.then(function(result_vals) {
				setTimeout(function(){
				new WelcomeMail();
			},3000);

			});			
		});

var encodeImageFileAsURL = Widget.extend ({
	init: function() {

    var filesSelected = document.getElementById("inputFileToLoad").files;

    	if (filesSelected[0].size >= 512000){
    		alert('Please upload image file less than 5MB');
    	}

    	else{

			if ((filesSelected[0].type != 'image/jpeg') && (filesSelected[0].type != 'image/png')){
				alert('Please select an Image file');
			}
			else{

		      	if (filesSelected.length > 0) {
			        var fileToLoad = filesSelected[0];

			        var fileReader = new FileReader();

			        fileReader.onload = function(fileLoadedEvent) {
			        var srcData = fileLoadedEvent.target.result; // <--- data: base64

			        var newImage = document.createElement('img');
			        newImage.src = srcData;

			        newImage.style="height:150px;"

			        document.getElementById("imgTest").innerHTML = newImage.outerHTML;
			        // alert("Converted Base64 version is " + document.getElementById("imgTest").innerHTML);
			        console.log( $("#imgTest img").attr("src"));
			        $(".image_value").val($("#imgTest img").attr("src"));
			        }
			        fileReader.readAsDataURL(fileToLoad);
		      	}

	      	}
      	}
    }
});

		$('body').delegate('#inputFileToLoad','change',function() {
			// alert(6565646545);
			new encodeImageFileAsURL();

		});


		$('body').delegate('.btn_background_check_initiate','click',function() {

			//$(".background_check_table tbody tr").each(function(){
//					if ( $(this).find('.form_background_check_items').length!==0) { 
//						var parent_val=$(this).parent();
//						var doc_id ={
//							background_check_tree_id:$(this).find('.background_check_tree_id').val(), 
//							background_check_status:$(this).find('.background_check_status').val(),
//							form_drug_test:$(".form_drug_test").val()
//						}
//					}
					var arg1 = $(".form_id").text();
					var hr_onboarding = new Model('hr.employee.onboarding');
					hr_onboarding.call('background_check_initiate', [[1], arg1])
					.then(function(result_vals) {
						if (result_vals){
							new BackgroundCheck();			
							$(".btn_background_check_initiate").text("Resend");
							$(".btn_background_check_initiate").attr("style","background:#e2e2e2;");
							$(".btn_background_check_initiate").attr("class","btn btn-default btn_background_check_initiate");							
						}
					});
			//});

		});


//		Offer Accepted Experience
		$('body').delegate('.add_more_academic','click',function() {
			$(".academic_exp_offer_accepted tbody").append('<tr>\
				<td style="display:none">\
					<input class="input_box form_academic_exp_tree_id" value="0" type="text">\
				</td>\
				<td>\
					<input class="input_box form_academic_exp" value="" type="text" placeholder="Academic Experiences" style="border:none">\
				</td>\
				<td>\
					<input class="input_box form_academic_institution" value="" type="text" placeholder="Institution" style="border:none">\
				</td>\
				<td>\
					<input class="input_box form_academic_diploma" value="" type="text" placeholder="Diploma" style="border:none">\
				</td>\
				<td>\
					<input class="input_box form_academic_fos" value="" type="text" placeholder="Field of study" style="border:none">\
				</td>\
				<td>\
					<input class="input_box form_academic_start_date datepicker_custom" value="" type="text" style="border:none">\
				</td>\
				<td>\
					<input class="input_box form_academic_end_date datepicker_custom" value="" type="text" style="border:none">\
				</td>\
				<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
			</tr>');
			$('body').on('focus',".datepicker_custom", function(){
		        $(this).datepicker({
		          changeMonth: true,
		          changeYear: true,
		          yearRange: "1940:2100",
		          dateFormat: "yy-mm-dd"
		        });
		    });
			$(".academic_exp_offer_accepted tbody").find("tr:last").find(".form_academic_exp_tree_id").val(0);
		});
		$('body').delegate('.add_more_professional','click',function() {
			$(".professional_exp_offer_accepted tbody").append('<tr>\
				<td style= "display:none">\
					<input class="input_box form_professional_exp_tree_id"  value="0"  type="text"/>\
				</td>\
				<td>\
					<input class="input_box form_professional_exp_position"  value=""  type="text" placeholder="Position" style="border:none" />\
				</td>\
				<td>\
					<input class="input_box form_professional_exp_employer"  value=""  type="text" placeholder="Employer" style="border:none" />\
				</td>\
				<td>\
					<input class="input_box form_professional_exp_start_date datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td>\
					<input class="input_box form_professional_exp_end_date datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
			</tr>');
			$('body').on('focus',".datepicker_custom", function(){
		        $(this).datepicker({
		          changeMonth: true,
		          changeYear: true,
		          yearRange: "1940:2100",
		          dateFormat: "yy-mm-dd"
		        });
		    });
			$(".professional_exp_offer_accepted tbody").find("tr:last").find(".professional_exp_offer_accepted").val(0);
		});
		$('body').delegate('.add_more_certification','click',function() {
			$(".certification_exp_offer_accepted tbody").append('<tr>\
				<td style= "display:none">\
					<input class="input_box form_certification_exp_tree_id"  value="0"  type="text"/>\
				</td>\
				<td>\
					<input class="input_box form_certification_exp_certificate"  value=""  type="text" placeholder="Certifications" style="border:none" />\
				</td>\
				<td>\
					<input class="input_box form_certification_exp_certificate_code"  value=""  type="text" placeholder="Certification #" style="border:none" />\
				</td>\
				<td>\
					<input class="input_box form_certification_exp_issued_by"  value=""  type="text" placeholder="Issued By" style="border:none" />\
				</td>\
				<td>\
					<input class="form_certification_exp_professional_license"  value="" type="checkbox" />\
				</td>\
				<td>\
					<select name="State Issued" class="form_certification_exp_state_issued ">\
					'+$(".certification_exp_offer_accepted tr").eq(1).find(".form_certification_exp_state_issued").html()+'\
					</select>\
				</td>\
				<td>\
					<input class="input_box form_certification_exp_start_date datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td>\
					<input class="input_box form_certification_exp_end_date datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
			</tr>');
			$('body').on('focus',".datepicker_custom", function(){
		        $(this).datepicker({
		          changeMonth: true,
		          changeYear: true,
		          yearRange: "1940:2100",
		          dateFormat: "yy-mm-dd"
		        });
		    });
			$(".certification_exp_offer_accepted tbody").find("tr:last").find(".certification_exp_offer_accepted").val(0);
		});
		
//		Offer Accepted Summary
		$('body').delegate('.add_more_academic','click',function() {
			$(".academic_exp_offer_accepted_summary tbody").append('<tr>\
				<td style= "display:none">\
					<input class="input_box form_academic_exp_tree_id"  value="0"  type="text" readonly="readonly"/>\
				</td>\
				<td>\
					<input class="input_box form_academic_exp"  value=""  type="text" placeholder="Academic Experiences" style="border:none" readonly="readonly" />\
				</td>\
				<td>\
					<input class="input_box form_academic_institution"  value=""  type="text" placeholder="Institution" style="border:none" readonly="readonly" />\
				</td>\
				<td>\
					<input class="input_box form_academic_diploma"  value=""  type="text" placeholder="Diploma" style="border:none" readonly="readonly" />\
				</td>\
				<td>\
					<input class="input_box form_academic_fos"  value=""  type="text" placeholder="Field of study" style="border:none" readonly="readonly" />\
				</td>\
				<td>\
					<input class="input_box form_academic_start_date datepicker_custom"  value=""  type="text" style="border:none" readonly="readonly" />\
				</td>\
				<td>\
					<input class="input_box form_academic_end_date datepicker_custom"  value=""  type="text" style="border:none" readonly="readonly" />\
				</td>\
				<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
			</tr>');
			$('body').on('focus',".datepicker_custom", function(){
		        $(this).datepicker({
		          changeMonth: true,
		          changeYear: true,
		          yearRange: "1940:2100",
		          dateFormat: "yy-mm-dd"
		        });
		    });
			$(".academic_exp_offer_accepted_summary tbody").find("tr:last").find(".academic_exp_offer_accepted_summary").val(0);
		});
		$('body').delegate('.add_more_professional','click',function() {
			$(".professional_exp_offer_accepted_summary tbody").append('<tr>\
				<td style="display:none">\
					<input class="input_box form_professional_exp_tree_id"  value="0"  type="text" readonly="readonly"/>\
				</td>\
				<td>\
					<input class="input_box form_professional_exp_position"  value=""  type="text" placeholder="Position" style="border:none" readonly="readonly" />\
				</td>\
				<td>\
					<input class="input_box form_professional_exp_employer"  value=""  type="text" placeholder="Employer" style="border:none" readonly="readonly" />\
				</td>\
				<td>\
					<input class="input_box form_professional_exp_start_date datepicker_custom"  value=""  type="text" style="border:none" readonly="readonly" />\
				</td>\
				<td>\
					<input class="input_box form_professional_exp_end_date datepicker_custom"  value=""  type="text" style="border:none" readonly="readonly" />\
				</td>\
				<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
			</tr>');
			$('body').on('focus',".datepicker_custom", function(){
		        $(this).datepicker({
		          changeMonth: true,
		          changeYear: true,
		          yearRange: "1940:2100",
		          dateFormat: "yy-mm-dd"
		        });
		    });
			$(".professional_exp_offer_accepted_summary tbody").find("tr:last").find(".professional_exp_offer_accepted_summary").val(0);
		});
		$('body').delegate('.add_more_certification','click',function() {
			$(".certification_exp_offer_accepted_summary tbody").append('<tr>\
				<td style="display:none">\
					<input class="input_box form_certification_exp_tree_id"  value="0"  type="text" readonly="readonly"/>\
				</td>\
				<td>\
					<input class="input_box form_certification_exp_certificate"  value=""  type="text" placeholder="Certifications" style="border:none" readonly="readonly" />\
				</td>\
				<td>\
					<input class="input_box form_certification_exp_certificate_code"  value=""  type="text" placeholder="Certification #" style="border:none" readonly="readonly" /> \
				</td>\
				<td>\
					<input class="input_box form_certification_exp_issued_by"  value=""  type="text" placeholder="Issued By" style="border:none" readonly="readonly" />\
				</td>\
				<td>\
					<input class="form_certification_exp_professional_license"  value="" type="checkbox" />\
				</td>\
				<td>\
					<select name="State Issued" class="form_certification_exp_state_issued ">\
					'+$(".certification_exp_offer_accepted_summary tr").eq(1).find(".form_certification_exp_state_issued").html()+'\
					</select>\
				</td>\
				<td>\
				<td>\
					<input class="input_box form_certification_exp_start_date datepicker_custom"  value=""  type="text" style="border:none" readonly="readonly" />\
				</td>\
				<td>\
					<input class="input_box form_certification_exp_end_date datepicker_custom"  value=""  type="text" style="border:none" readonly="readonly" />\
				</td>\
				<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
			</tr>');
			$('body').on('focus',".datepicker_custom", function(){
		        $(this).datepicker({
		          changeMonth: true,
		          changeYear: true,
		          yearRange: "1940:2100",
		          dateFormat: "yy-mm-dd"
		        });
		    });
			$(".certification_exp_offer_accepted_summary tbody").find("tr:last").find(".certification_exp_offer_accepted_summary").val(0);
		});

//		Background Check i9
		$('body').delegate('.add_more_i9_applicant','click',function() {
			$(".i9_applicant_table tbody").append('<tr>\
				<td style="display:none">\
					<input class="input_box applicant_tree_id"  value="0"  type="text"/>\
				</td>\
				<td>\
					<select name="Document" class="form_applicant_documents">\
						'+$(".i9_applicant_table tr").eq(1).find(".form_applicant_documents").html()+'\
					</select>\
				</td>\
				<td>\
					<a class="input_box applicant_link" href="" target="_blank">Link</a>\
				</td>\
				<td>\
					<select name="Status" class="applicant_status" disabled="disabled">\
						<option value=""></option>\
						<option value="draft">Open</option>\
						<option value="sent">Signatures in Progress</option>\
						<option value="signed">Fully Signed</option>\
						<option value="canceled">Cancelled</option>\
					</select>\
				</td>\
				<td>\
					<input class="input_box applicant_date_sent datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td>\
					<input class="input_box applicant_expiration datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
				<td class="btn_sent btn_applicant"><button class="btn btn-primary">Send</button></td>\
			</tr>');
			$('body').on('focus',".datepicker_custom", function(){
		        $(this).datepicker({
		          changeMonth: true,
		          changeYear: true,
		          yearRange: "1940:2100",
		          dateFormat: "yy-mm-dd"
		        });
		    });
			$(".i9_applicant_table tbody").find("tr:last").find(".i9_applicant_table").val(0);
		});
		$('body').delegate('.add_more_i9_employer','click',function() {
			$(".i9_employer_table tbody").append('<tr>\
				<td style="display:none">\
					<input class="input_box employer_tree_id"  value="0"  type="text"/>\
				</td>\
				<td>\
					<select name="Document" class="form_employer_documents">\
						'+$(".i9_employer_table tr").eq(1).find(".form_employer_documents").html()+'\
					</select>\
				</td>\
				<td>\
					<a class="input_box employer_link" href="" target="_blank">Link</a>\
				</td>\
				<td>\
					<select name="Status" class="employer_status" disabled="disabled">\
						<option value=""></option>\
						<option value="draft">Open</option>\
						<option value="sent">Signatures in Progress</option>\
						<option value="signed">Fully Signed</option>\
						<option value="canceled">Cancelled</option>\
					</select>\
				</td>\
				<td>\
					<input class="input_box employer_date_sent datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td>\
					<input class="input_box employer_expiration datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
				<td class="btn_sent btn_employer"><button class="btn btn-primary">Send</button></td>\
			</tr>');
			$('body').on('focus',".datepicker_custom", function(){
		        $(this).datepicker({
		          changeMonth: true,
		          changeYear: true,
		          yearRange: "1940:2100",
		          dateFormat: "yy-mm-dd"
		        });
		    });
			$(".i9_employer_table tbody").find("tr:last").find(".i9_employer_table").val(0);
		});

		// Background Chcek 1st 
		$('body').delegate('.add_more_background_check_applicant','click',function() {
			$(".background_check_applicant_table tbody").append("<tr>"+$(".background_check_applicant_table tr").eq(1).html()+"</tr>");
			$(".background_check_applicant_table tbody").find("tr:last").find(".background_check_applicant_table").val(0);
		});
		$('body').delegate('.add_more_background_check_employer','click',function() {
			$(".background_check_employer_table tbody").append("<tr>"+$(".background_check_employer_table tr").eq(1).html()+"</tr>");
			$(".background_check_employer_table tbody").find("tr:last").find(".background_check_employer_table").val(0);
		});

//		Background Check Consent
		$('body').delegate('.add_more_background_check_consent_form','click',function() {

			$(".background_check_consent_form_table tbody").append('<tr>\
				<td style= "display:none">\
					<input class="input_box consent_form_tree_id"  value="0"  type="text" placeholder="ID" style="border:none" readonly="readonly"/>\
				</td>\
				<td>\
					<select name="Document" class="form_consent_documents">\
						'+$(".background_check_consent_form_table tr").eq(1).find(".form_consent_documents").html()+'\
					</select>\
				</td>\
				<td>\
					<a class="input_box background_check_consent_form_link" href="" target="_blank">Link</a>\
				</td>\
				<td>\
					<select name="Status" class="background_check_consent_form_status" disabled="disabled">\
						<option value=""></option>\
						<option value="draft">Open</option>\
						<option value="sent">Signatures in Progress</option>\
						<option value="signed">Fully Signed</option>\
						<option value="canceled">Cancelled</option>\
					</select>\
				</td>\
				<td>\
					<input class="input_box background_check_consent_form_date_sent datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td>\
					<input class="input_box background_check_consent_form_expiration datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
				<td class="btn_sent btn_consent"><button class="btn btn-primary">Send</button></td>\
			</tr>');
			$('body').on('focus',".datepicker_custom", function(){
		        $(this).datepicker({
		          changeMonth: true,
		          changeYear: true,
		          yearRange: "1940:2100",
		          dateFormat: "yy-mm-dd"
		        });
		    });
			$(".background_check_consent_form_table tbody").find("tr:last").find(".background_check_consent_form_table").val(0);
		});

//		Background Check
		$('body').delegate('.add_more_background_check','click',function() {
			$(".background_check_table tbody").append("<tr>"+$(".background_check_table tr").eq(1).html()+"</tr>");
			$(".background_check_table tbody").find("tr:last").find(".background_check_table").val(0);
		});
//		Background Check Package
		$('body').delegate('.add_more_background_check_package','click',function() {
			$(".background_check_package_table tbody").append("<tr>"+$(".background_check_package_table tr").eq(1).html()+"</tr>");
			$(".background_check_package_table tbody").find("tr:last").find(".background_check_package_table").val(0);
		});

//		Adverse Action
		$('body').delegate('.add_more_adverse_action','click',function() {
			$(".adverse_action_table tbody").append('<tr>\
				<td style= "display:none">\
					<input class="input_box adverse_action_tree_id"  value="0"  type="text" placeholder="ID" style="border:none" />\
				</td>\
				<td>\
					<select name="Document" class="form_adverse_documents">\
						'+$(".adverse_action_table tr").eq(1).find(".form_adverse_documents").html()+'\
					</select>\
				</td>\
				<td>\
					<a class="input_box adverse_action_link" href="" target="_blank">Link</a>\
				</td>\
				<td>\
					<select name="Status" class="adverse_action_status" disabled="disabled">\
						<option value=""></option>\
						<option value="draft">Open</option>\
						<option value="sent">Signatures in Progress</option>\
						<option value="signed">Fully Signed</option>\
						<option value="canceled">Cancelled</option>\
					</select>\
				</td>\
				<td>\
					<input class="input_box adverse_action_date_sent datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td>\
					<input class="input_box adverse_action_expiration datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
				<td class="btn_sent btn_adverse"><button class="btn btn-primary">Send</button></td>\
			</tr>');
			$('body').on('focus',".datepicker_custom", function(){
		        $(this).datepicker({
		          changeMonth: true,
		          changeYear: true,
		          yearRange: "1940:2100",
		          dateFormat: "yy-mm-dd"
		        });
		    });
			$(".adverse_action_table tbody").find("tr:last").find(".adverse_action_table").val(0);
		});

//		Welcome Mail
		$('body').delegate('.add_more_welcome_mail_applicant','click',function() {
			$(".welcome_mail_applicant_table tbody").append('<tr>\
				<td style="display:none">\
					<input class="input_box welcome_applicant_tree_id"  value="0"  type="text"/>\
				</td>\
				<td>\
					<select name="Document" class="form_welcome_applicant_documents">\
						'+$(".welcome_mail_applicant_table tr").eq(1).find(".form_welcome_applicant_documents").html()+'\
					</select>\
				</td>\
				<td>\
					<a class="input_box welcome_applicant_link" href="" target="_blank">Link</a>\
				</td>\
				<td>\
					<select name="Status" class="welcome_applicant_status">\
						<option value=""></option>\
						<option value="draft">Open</option>\
						<option value="sent">Signatures in Progress</option>\
						<option value="signed">Fully Signed</option>\
						<option value="canceled">Cancelled</option>\
					</select>\
				</td>\
				<td>\
					<input class="input_box welcome_applicant_date_sent datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td>\
					<input class="input_box welcome_applicant_expiration datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
				<td class="btn_sent btn_welcome"><button class="btn btn-primary">Send</button></td>\
			</tr>');
			$('body').on('focus',".datepicker_custom", function(){
		        $(this).datepicker({
		          changeMonth: true,
		          changeYear: true,
		          yearRange: "1940:2100",
		          dateFormat: "yy-mm-dd"
		        });
		    });
			$(".welcome_mail_applicant_table tbody").find("tr:last").find(".welcome_mail_applicant_table").val(0);
		
		});

		$('body').delegate('.add_more_welcome_mail_survey','click',function() {
			$(".welcome_mail_survey_table tbody").append('<tr>\
				<td style= "display:none">\
					<input class="input_box welcome_survey_tree_id"  value="0"  type="text"/>\
				</td>\
				<td>\
					<select name="Survey" class="form_welcome_survey">\
					'+$(".welcome_mail_survey_table tr").eq(1).find(".form_welcome_survey").html()+'\
					</select>\
				</td>\
				<td>\
					<a class="input_box welcome_survey_link" href="" target="_blank">Link</a>\
				</td>\
				<td>\
					<select name="Status" class="welcome_survey_status">\
						<option value=""></option>\
						<option value="new">Not Yet Started</option>\
						<option value="skip">Partially Completed</option>\
						<option value="done">Completed</option>\
					</select>\
				</td>\
				<td>\
					<input class="input_box welcome_survey_date_sent datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td>\
					<input class="input_box welcome_survey_expiration datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
				<td class="btn_sent btn_survey"><button class="btn btn-primary">Send</button></td>\
			</tr>');
			$('body').on('focus',".datepicker_custom", function(){
		        $(this).datepicker({
		          changeMonth: true,
		          changeYear: true,
		          yearRange: "1940:2100",
		          dateFormat: "yy-mm-dd"
		        });
		    });

		
			$(".welcome_mail_survey_table tbody").find("tr:last").find(".welcome_mail_survey_table").val(0);
		
		});

		$('body').delegate('.add_more_everify_case_result','click',function() {
			$(".everify_case_result tbody").append('<tr>\
				<td style= "display:none">\
					<input class="input_box form_tree_id everify_case_result_tree_id" value="0" type="text"/>\
				</td>\
				<td>\
					<input class="input_box everify_case_result_case_number" value="" type="text"/>\
				</td>\
				<td>\
					<input class="input_box everify_case_result_status" value="" type="text"/>\
				</td>\
				<td>\
					<input class="input_box everify_case_result_message_code" value="" type="text"/>\
				</td>\
				<td>\
					<input class="input_box everify_case_result_eligiblity_statement" value="" type="text"/>\
				</td>\
				<td>\
					<input class="input_box everify_case_result_statement_details" value="" type="text"/>\
				</td>\
				<td>\
					<input class="input_box everify_case_result_date_sent datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td>\
					<input class="input_box everify_case_result_date_received datepicker_custom"  value=""  type="text" style="border:none" />\
				</td>\
				<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
				<td class="btn_close_case btn_everify_case_result"><button class="btn btn-primary">Close Case</button></td>\
			</tr>');
			$('body').on('focus',".datepicker_custom", function(){
		        $(this).datepicker({
		          changeMonth: true,
		          changeYear: true,
		          yearRange: "1940:2100",
		          dateFormat: "yy-mm-dd"
		        });
		    });

		    $(".everify_case_result tbody").find("tr:last").find(".everify_case_result").val(0);
		
		});

		$('body').delegate('.create_contract_link_redirect','click',function() {
			new CreateContract();
		});

		$('body').delegate('.btn_completion_bar_new','click',function() {
			var page_id = $(".substate_value.o_form_field").text();
			// utils.set_cookie('planner_onboarding_last_page', page_id);
			
			$(".progress").click();

			$("a[href='#"+page_id+"']").click();

			$(".btn-next").hide();

			$('.o_planner_menu ul li').attr("style","pointer-events:none");

			new GetStarted();	
			if (page_id =='PersonalInformation1'){
				$('.o_planner_menu ul li:lt(2)').attr("style","pointer-events:stroke");
				new GetStarted();
				new PersonalInfo();
			}
			if (page_id =='ExperienceandCertifications2'){
				$('.o_planner_menu ul li:lt(3)').attr("style","pointer-events:stroke");
				new GetStarted();
				new ExperienceInfo();
			}
			if (page_id =='EmployementInformation3'){
				$('.o_planner_menu ul li:lt(4)').attr("style","pointer-events:stroke");
				new GetStarted();
				new EmployementInfo();
			}
			if (page_id =='Summary4'){
				$('.o_planner_menu ul li:lt(5)').attr("style","pointer-events:stroke");
				new GetStarted();	
				new OfferSummary();			
				setTimeout(function(){ 
					new EmployementInfo();
				});
			}
			if (page_id =='BackgroundCheckConsent5'){
				$('.o_planner_menu ul li:lt(6)').attr("style","pointer-events:stroke");
				new GetStarted();
				new BackgroundiNine();
				new ConsentForm();			
				setTimeout(function(){ 
					new BackgroundCheck();
				},2000);
			}
			if (page_id =='BackgroundCheck6'){
				$('.o_planner_menu ul li:lt(7)').attr("style","pointer-events:stroke");
				new GetStarted();
				new BackgroundiNine();
				new BackgroundCheck();
				new ConsentForm();
			}
			if (page_id =='Summary7'){
				$('.o_planner_menu ul li:lt(8)').attr("style","pointer-events:stroke");
				new GetStarted();
				new BackgroundiNine();	
				new BackgroundCheck();		
				new BackgroundSummary();
			}
			if (page_id =='AdverseAction8'){
				$('.o_planner_menu ul li:lt(9)').attr("style","pointer-events:stroke");
				new GetStarted();
				new BackgroundiNine();
				new BackgroundSummary();
				new AdverseAction();
			}
			if (page_id =='i99'){
				$('.o_planner_menu ul li:lt(10)').attr("style","pointer-events:stroke");
				new GetStarted();
				new BackgroundiNine();
			}
			if (page_id =='E-Verify10'){
				$('.o_planner_menu ul li:lt(11)').attr("style","pointer-events:stroke");
				new GetStarted();
				new BackgroundiNine();
				new HireEverify();
			}
			if (page_id =='ApplicantSummary/Hire11'){
				$('.o_planner_menu ul li:lt(12)').attr("style","pointer-events:stroke");
				new GetStarted();	
				new HireSummary();
				setTimeout(function(){ 
					new ExperienceInfo();
					new BackgroundiNine();
					new OfferSummary();
					new EmployementInfo();
				});
			}
			if (page_id =='BenefitsEligibility12'){
				$('.o_planner_menu ul li:lt(13)').attr("style","pointer-events:stroke");
				new GetStarted();				
				new BenefitsEligibility();
			}
			if (page_id =='WelcomeEmail13'){
				$('.o_planner_menu ul li:lt(14)').attr("style","pointer-events:stroke");
				new GetStarted();
				new BackgroundiNine();
				new WelcomeMail();
			}
			if (page_id =='AppraisalPlan14'){
				$('.o_planner_menu ul li:lt(15)').attr("style","pointer-events:stroke");
				new GetStarted();
				new AppraisalInfo();
			}
			if (page_id =='Summary15'){
				$('.o_planner_menu ul li:lt(16)').attr("style","pointer-events:stroke");
				new GetStarted();
				new BackgroundiNine();
				new welcomeSummary();
				new ApproveSummary();
				new BenifitsSurveyInfo();
			}
			if (page_id =='BenefitsSurveyResults16'){
				$('.o_planner_menu ul li:lt(17)').attr("style","pointer-events:stroke");
				new GetStarted();
				// new BenifitsSurveyInfo();
				new BenifitsSurveyResultsInfo();
			}
			if (page_id =='EmployeeSummary17'){
				$('.o_planner_menu ul li:lt(18)').attr("style","pointer-events:stroke");
				new GetStarted();
				new EmployeeInfo();
				new AppraisalInfo();
			}
			if (page_id == 'CreateContract18'){
				$('.o_planner_menu ul li:lt(19)').attr("style","pointer-events:stroke");
			}
			if (page_id =='ContractSummary19'){
				$('.o_planner_menu ul li:lt(20)').attr("style","pointer-events:stroke");
				new GetStarted();
				new ContractInfo();
			}
			if (page_id =='Complete20'){
				$('.o_planner_menu ul li:lt(21)').attr("style","pointer-events:stroke");
				new GetStarted();
			} 
			
			function load_records(page_id){

				new GetStarted();	
				if (page_id =='PersonalInformation1'){
					$('.o_planner_menu ul li:lt(2)').attr("style","pointer-events:stroke");
					new GetStarted();
					new PersonalInfo();
				}
				if (page_id =='ExperienceandCertification2'){		
					$('.o_planner_menu ul li:lt(3)').attr("style","pointer-events:stroke");	
					new GetStarted();
					new ExperienceInfo();
				}
				if (page_id =='EmployementInformation3'){
					$('.o_planner_menu ul li:lt(4)').attr("style","pointer-events:stroke");
					new GetStarted();
					new EmployementInfo();
				}
				if (page_id =='Summary4'){
					$('.o_planner_menu ul li:lt(5)').attr("style","pointer-events:stroke");
					new GetStarted();	
					new OfferSummary();			
					setTimeout(function(){ 
						new EmployementInfo();
					});
				}
				if (page_id =='BackgroundCheckConsent5'){
					$('.o_planner_menu ul li:lt(6)').attr("style","pointer-events:stroke");
					new GetStarted();
					new BackgroundiNine();
					new ConsentForm();			
					setTimeout(function(){ 
						new BackgroundCheck();
					},2000);
				}
				if (page_id =='BackgroundCheck6'){
					$('.o_planner_menu ul li:lt(7)').attr("style","pointer-events:stroke");
					new GetStarted();
					new BackgroundiNine();
					new BackgroundCheck();
					new ConsentForm();
				}
				if (page_id =='Summary7'){
					$('.o_planner_menu ul li:lt(8)').attr("style","pointer-events:stroke");
					new GetStarted();
					new BackgroundiNine();	
					new BackgroundCheck();		
					new BackgroundSummary();
				}
				if (page_id =='AdverseAction8'){
					$('.o_planner_menu ul li:lt(9)').attr("style","pointer-events:stroke");
					new GetStarted();
					new BackgroundiNine();
					new BackgroundSummary();
					new AdverseAction();
				}
				if (page_id =='i99'){
					$('.o_planner_menu ul li:lt(10)').attr("style","pointer-events:stroke");
					new GetStarted();
					new BackgroundiNine();
				}
				if (page_id =='E-Verify10'){
					$('.o_planner_menu ul li:lt(11)').attr("style","pointer-events:stroke");
					new GetStarted();
					new BackgroundiNine();
					new HireEverify();
				}
				if (page_id =='ApplicantSummary/Hire11'){
					$('.o_planner_menu ul li:lt(12)').attr("style","pointer-events:stroke");
					new GetStarted();	
					new HireSummary();
					setTimeout(function(){ 
						new ExperienceInfo();
						new BackgroundiNine();
						new OfferSummary();
						new EmployementInfo();
					});
				}
				if (page_id =='BenefitsEligibility12'){
					$('.o_planner_menu ul li:lt(13)').attr("style","pointer-events:stroke");
					new GetStarted();
					new BenefitsEligibility();
				}
				if (page_id =='WelcomeEmail13'){
					$('.o_planner_menu ul li:lt(14)').attr("style","pointer-events:stroke");
					new GetStarted();
					new BackgroundiNine();
					new WelcomeMail();
				}
				if (page_id =='AppraisalPlan14'){
					$('.o_planner_menu ul li:lt(15)').attr("style","pointer-events:stroke");
					new GetStarted();
					new AppraisalInfo();
				}
				if (page_id =='Summary15'){
					$('.o_planner_menu ul li:lt(16)').attr("style","pointer-events:stroke");
					new GetStarted();
					new BackgroundiNine();
					new welcomeSummary();
					new ApproveSummary();
					new BenifitsSurveyInfo();
				}
				if (page_id =='BenefitsSurveyResults16'){
					$('.o_planner_menu ul li:lt(17)').attr("style","pointer-events:stroke");
					new GetStarted();
					// new BenifitsSurveyInfo();
					new BenifitsSurveyResultsInfo();
				}
				if (page_id =='EmployeeSummary17'){
					$('.o_planner_menu ul li:lt(18)').attr("style","pointer-events:stroke");
					new GetStarted();
					new EmployeeInfo();
					new AppraisalInfo();
				}
				if (page_id == 'CreateContract18'){
					$('.o_planner_menu ul li:lt(19)').attr("style","pointer-events:stroke");
				}
				if (page_id =='ContractSummary19'){
					$('.o_planner_menu ul li:lt(20)').attr("style","pointer-events:stroke");
					new GetStarted();
					new ContractInfo();
				}
				if (page_id =='Complete20'){
					$('.o_planner_menu ul li:lt(21)').attr("style","pointer-events:stroke");
					new GetStarted();
				} 
				
			}
			

			$('body').delegate('.o_planner_menu ul li','click', async function() {

				//sub_state($(this).find('a').attr('href').replace("#",""));
				var click_page_id=$(this).find('a').attr('href').replace("#","");

					
				  let promise = new Promise((resolve, reject) => {
					  var arg1=$(".form_id").text();
					  var hr_onboarding = new Model('hr.employee.onboarding');
						hr_onboarding.call('get_sub_state_id', [[1], arg1])
						.then(function(result_vals) {							
							resolve(result_vals);							
						});
						
				  });


				let result = await promise; // wait till the promise resolves (*)
				var current_page_id = result;

				load_records(click_page_id);
				
				if(click_page_id==current_page_id){
					$(".btn_onboarding_next,.onboard_trash").show();
				}else{
					if(click_page_id!='BackgroundCheck6'){
						$(".btn_onboarding_next,.onboard_trash").hide();
					}else{
						$(".btn_onboarding_next,.onboard_trash").show();
					}
				}

				  
			});
			
			

			$(".smart_buttons_list").html("");
			$(".o_planner_page").prepend("<div class='smart_buttons_list'>"+$(".smart_buttons").html()+"</div>");
			$(".top_section").html("");
			$(".top_section").append($(".top_section_main").html());

			$('.o_planner_close_block').on('click',function(){
				location.reload();
			});
			
			
			
		});

		$('body').delegate('.btn_onboarding_reject','click',function() {
			new RejectApplicant();
			$(".close").click();
		});

		$('body').delegate('.btn_onboarding_next','click',function() {
			if($(this).attr('data_page_id')=='1'){
				var i=0;
			    $(".get_started .required_cls").each(function(){
			        if($(this).val()=='' || ($(this).val() == null)){
			        	i++;
			        	$(this).attr("style","border-bottom: 2px solid #f00 !important;");
			        }else{			        	
			        	$(this).attr("style","border-bottom: 2px solid #616161 !important");
			        }
			    });
				
				if(i>0){
					alert("Please fill all required fields");
				}
				else{
					new InsertValsGetStarted();
					setTimeout(function(){ 
						$('.o_planner_menu ul li:lt(1)').attr("style","pointer-events:stroke");
						new PersonalInfo();
						// $(".btn-next").click();
						$(".btn-next").hide();
					});
				}
			}
			if($(this).attr('data_page_id')=='2'){
				var i=0;
			    $(".personal_info .required_cls").each(function(){
			        if($(this).val()=='' || ($(this).val() == null)){
			        	i++;
			        	$(this).attr("style","border-bottom: 2px solid #f00 !important;");
			        }else{			        	
			        	$(this).attr("style","border-bottom: 2px solid #616161 !important");
			        }
			    });
				
				if(i>0){
					alert("Please fill all required fields");
				}
				else{
					$('.o_planner_menu ul li:lt(2)').attr("style","pointer-events:stroke");
					new InsertValsPersonalInfo();
					setTimeout(function(){ 
						new ExperienceInfo();
						$(".btn-next").hide();
					});
				}
			}
			if($(this).attr('data_page_id')=='3'){
				var i=0;
			    $(".academic_exp_offer_accepted .required_cls").each(function(){
			        if($(this).val()=='' || ($(this).val() == null)){
			        	i++;
			        	$(this).attr("style","border-bottom: 2px solid #f00 !important;");
			        }else{			        	
			        	$(this).attr("style","border-bottom: 2px solid #616161 !important");
			        }
			    });
				
				if(i>0){
					alert("Please fill all required fields");
				}
				else{
					$('.o_planner_menu ul li:lt(2)').attr("style","pointer-events:stroke");
					new InsertValsExpirenceInfo();
					setTimeout(function(){ 
						$('.o_planner_menu ul li:lt(3)').attr("style","pointer-events:stroke");
						new EmployementInfo();	
						// $(".btn-next").click();
						$(".btn-next").hide();
					});
				}
			}
			if($(this).attr('data_page_id')=='4'){
				var i=0;
			    $(".employement_info .required_cls").each(function(){
			        if($(this).val()=='' || ($(this).val() == null)){
			        	i++;
			        	$(this).attr("style","border-bottom: 2px solid #f00 !important;");
			        }else{			        	
			        	$(this).attr("style","border-bottom: 2px solid #616161 !important");
			        }
			    });
				
				if(i>0){
					alert("Please fill all required fields");
				}
				else{
					$('.o_planner_menu ul li:lt(4)').attr("style","pointer-events:stroke");
					new InsertValsEmployementInfo();
					setTimeout(function(){ 
						new OfferSummary();
						// new EmployementInfo();	
						// $(".btn-next").click();
						$(".btn-next").hide();
					},500);
				}
			}
			if($(this).attr('data_page_id')=='5'){
				var i=0;
			    $(".offer_summary_info .required_cls").each(function(){
			        if($(this).val()=='' || ($(this).val() == null)){
			        	i++;
			        	$(this).attr("style","border-bottom: 2px solid #f00 !important;");
			        }else{			        	
			        	$(this).attr("style","border-bottom: 2px solid #616161 !important");
			        }
			    });
				
				if(i>0){
					alert("Please fill all required fields");
				}
				else{
					$('.o_planner_menu ul li:lt(5)').attr("style","pointer-events:stroke");
					new InsertValsOfferSummary();
					setTimeout(function(){ 
						new ConsentForm();	
						$(".btn-next").click();
						$(".btn-next").hide();
					});
				}
			}
			if($(this).attr('data_page_id')=='6'){
				new InsertValsConsentInfo();
				setTimeout(function(){ 
					$('.o_planner_menu ul li:lt(6)').attr("style","pointer-events:stroke");
					new BackgroundCheck();
					$(".btn-next").click();
					$(".btn-next").hide();
				},2000);
			}
			if($(this).attr('data_page_id')=='7'){
				new InsertValsBackgroundcheckInfo();
				setTimeout(function(){ 
					$('.o_planner_menu ul li:lt(7)').attr("style","pointer-events:stroke");
					new BackgroundSummary();
					$(".btn-next").hide();
				},600);
			}
			if($(this).attr('data_page_id')=='8'){
				new InsertValsBackgroundSummaryInfo();
				setTimeout(function(){ 
					$('.o_planner_menu ul li:lt(8)').attr("style","pointer-events:stroke");
					new AdverseAction();
					$(".btn-next").hide();
				});
			}
			if($(this).attr('data_page_id')=='9'){
				new InsertValsAdverseActionInfo();
				setTimeout(function(){ 
					$('.o_planner_menu ul li:lt(9)').attr("style","pointer-events:stroke");
					new BackgroundiNine();
					$(".btn-next").click();
					$(".btn-next").hide();
				});
			}
			if($(this).attr('data_page_id')=='10'){
				new InsertValsInineInfo();
				setTimeout(function(){ 
					$('.o_planner_menu ul li:lt(10)').attr("style","pointer-events:stroke");
					new HireEverify();
					$(".btn-next").click();
					$(".btn-next").hide();
				});
			}
			if($(this).attr('data_page_id')=='11'){
				new InsertValsEverifyInfo();
				setTimeout(function(){ 
					$('.o_planner_menu ul li:lt(11)').attr("style","pointer-events:stroke");
					new HireSummary();
					new OfferSummary();
					new ExperienceInfo();
					new EmployementInfo();	
					$(".btn-next").hide();
					// location.reload();
				});
			}
			if($(this).attr('data_page_id')=='12'){
				var i=0;
			    $(".hire_applicant_form .required_cls").each(function(){
			        if($(this).val()=='' || ($(this).val() == null)){
			        	i++;
			        	$(this).attr("style","border-bottom: 2px solid #f00 !important;");
			        }else{			        	
			        	$(this).attr("style","border-bottom: 2px solid #616161 !important");
			        }
			    });
				
				if(i>0){
					alert("Please fill all required fields");
				}
				else{
					new InsertValsHireInfo();
					setTimeout(function(){ 
						$('.o_planner_menu ul li:lt(12)').attr("style","pointer-events:stroke");
						new BenefitsEligibility();
						new EmployementInfo();	
						$(".btn-next").click();
						$(".btn-next").hide();
					});
				}
			}
			if($(this).attr('data_page_id')=='13'){
				new InsrtValsBenefitsEligibility();
				setTimeout(function(){ 
					$('.o_planner_menu ul li:lt(13)').attr("style","pointer-events:stroke");
					new WelcomeMail();
					$(".btn-next").click();
					$(".btn-next").hide();
				});
			}
			if($(this).attr('data_page_id')=='14'){
				new InsertValsWelcomeEmailInfo();
				setTimeout(function(){ 
					$('.o_planner_menu ul li:lt(14)').attr("style","pointer-events:stroke");
					new AppraisalInfo();
					$(".btn-next").click();
					$(".btn-next").hide();
				});
			}
			if($(this).attr('data_page_id')=='15'){
				new InsertValsAppraisalInfo();
				setTimeout(function(){ 
					$('.o_planner_menu ul li:lt(15)').attr("style","pointer-events:stroke");
					new HireSummary();
					new welcomeSummary();
					new ApproveSummary();
					$(".btn-next").click();
					$(".btn-next").hide();
				});
			}
			if($(this).attr('data_page_id')=='16'){
				// new InsertValsHireSummary();
				new InsertValsBenefitsState();
				setTimeout(function(){ 
					$('.o_planner_menu ul li:lt(16)').attr("style","pointer-events:stroke");
					new BenifitsSurveyInfo();
					// new BenifitsSurveyResultsInfo();
					$(".btn-next").click();
					$(".btn-next").hide();
				});
			}
			if($(this).attr('data_page_id')=='17'){
				// new BenifitsSurveyInfo();
				// new BenifitsSurveyResultsInfo();
				new InsertValsEmployeeSummaryState();
				setTimeout(function(){ 
					$('.o_planner_menu ul li:lt(17)').attr("style","pointer-events:stroke");
					new EmployeeInfo();
					new AppraisalInfo();
					$(".btn-next").click();
					$(".btn-next").hide();
					// location.reload();
				});
			}
			if($(this).attr('data_page_id')=='18'){
				new InsertValsContract();
				setTimeout(function(){ 
					$('.o_planner_menu ul li:lt(18)').attr("style","pointer-events:stroke");
					$(".btn-next").click();
					$(".btn-next").hide();
				});
			}
			if($(this).attr('data_page_id')=='19'){
				new ContractInfoNext();
				setTimeout(function(){ 
					$('.o_planner_menu ul li:lt(19)').attr("style","pointer-events:stroke");
					$(".btn-next").hide();
				});
				// location.reload();
			}
			if($(this).attr('data_page_id')=='20'){
				//new ContractInfo();
				new InsertValsCompleteState();
				setTimeout(function(){ 
					$('.o_planner_menu ul li:lt(20)').attr("style","pointer-events:stroke");
					$(".btn-next").click();
					$(".btn-next").hide();
				});
			}
		});
	});
});
