import datetime
from odoo import fields, models, api, _
from odoo.tools.translate import _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.tools import float_compare, float_is_zero
from dateutil.relativedelta import relativedelta


class survey_question(models.Model):
    _inherit = 'survey.question'
    _description = 'Survey Question'
    
    type = fields.Selection([
                ('free_text', 'Long Text Zone'),
                ('textbox', 'Text Input'),
                ('numerical_box', 'Numerical Value'),
                ('datetime', 'Date and Time'),
                ('simple_choice', 'Multiple choice: only one answer'),
                ('multiple_choice', 'Multiple choice: multiple answers allowed'),
                ('matrix', 'Matrix with Description'),
                ],required=True)
    descriptions_id=fields.One2many('x_survey.description', 'question_id_3', string='Matrix Description')
    check=fields.Boolean("Check")
    
    _rec_name = "type"
    
    def add_description(self):
        self.write({'check': True})
        statement_line_obj = self.pool.get('survey.label')
        for statement in self:
            statement_lines = statement.labels_ids_2
            statement_line_ids = map(lambda x: x.id, statement_lines)
            print statement_line_ids
#             statement_line_obj.write(cr, uid, statement_line_ids, {'line': True}, context=context)

        line_obj = self.pool.get('survey.label')
#         survey = self.browse(cr, uid,ids)
        desc_seq = 0
        for line in self.labels_ids:
            if line.value:
                desc_seq += 1
                print line.id
#                 self.pool.get('survey.label').write(cr, uid, line.id, {'sequence':desc_seq})
                line.sequence=desc_seq
        return True
    

class x_survey_description(models.Model):
    _name = 'x_survey.description'
    _description = 'Survey Description'

    def onchange_ans(self, cr, uid, ids, label_id, used_ans, context=None):
        res = {}
        if label_id:
            lable=[]
            unique_lable=[]
            label_ids=self.pool.get('survey.label').search(cr, uid,[])
            for record in label_ids:
                lable_obj=self.pool.get('survey.label').browse(cr,uid,record)
                lable.append(lable_obj.id)
            if used_ans:
                new_list=[]
                used_tag=used_ans.split(",")
                new_list=list(set(lable) - set(used_tag))
                if unique_lable:
                    res['domain'] = {'label_id': unique_lable}
                    used_ans=used_ans+','+str(label_id)+','
            else:
                new_list=[]
                for line in lable:
                    if label_id != line:
                        new_list.append(line)
                res['domain'] = {'label_id': [('id', 'in', new_list)]}
                used_ans=str(label_id)+','
            res['value'] = {'used_ans': used_ans}
        return res

    sequence_no= fields.Integer('Sequence')
    question_id_3= fields.Many2one('survey.question', 'question_id', String='Question', ondelete='cascade')
    label_id_que= fields.Many2one('survey.label',String='Question', ondelete='cascade', domain=[('line', '=', True)])
    label_id=fields.Many2one('survey.label',String='Answers | Choice',  ondelete='cascade', domain=[('line', '=', False)])
    description= fields.Char(String="Description", translate=True, required=True)


    _rec_name = "sequence_no"

x_survey_description()

class survey_label(models.Model):
    _inherit = 'survey.label'
    _description = 'Survey Label'

    
    x_weight= fields.Integer('Weightage')
    sequence= fields.Integer('Sequence', default=0)
    line= fields.Boolean('Line')    
    value = fields.Char('Suggested value', translate=True, required=True)
    
    _rec_name = "value"

survey_label()
#\\ To show score for the quiz
class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input_line'

    weightage_cal = fields.Integer("Total Weightage",compute="_compute_weight")
    weightage_val = fields.Integer("Total Weightage",compute="_compute_weight")
    
    def _compute_weight(self):
        for line in self:
            line.weightage_cal = line.quizz_mark *  line.value_suggested_row.x_weight
            line.weightage_val = line.value_suggested_row.x_weight
    
class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"
    
    @api.depends('user_input_line_ids.quizz_mark')
    def _compute_quizz_score(self):
        for user_input in self:
            n=i=0
            for ans in user_input.user_input_line_ids:
                if ans.question_id.type=='matrix':
                    i=1
                elif ans.question_id.type=='multiple_choice' or ans.question_id.type=='simple_choice':
                    n+=1
                    

            quizz_mark_value = sum(user_input.user_input_line_ids.mapped('quizz_mark'))
            if i==1:
                weightage_val = sum(user_input.user_input_line_ids.mapped('weightage_val'))
                weightage_cal_value = sum(user_input.user_input_line_ids.mapped('weightage_cal'))
                 
                if weightage_val > 0:
                    user_input.quizz_score = weightage_cal_value/weightage_val
                else:
                    user_input.quizz_score = 0
            else:
                if quizz_mark_value>0:
                    user_input.quizz_score = quizz_mark_value/n
                else:
                    user_input.quizz_score = 0
                    