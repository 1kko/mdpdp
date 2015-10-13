from peewee import *

database = MySQLDatabase('MEDDB', **{'password': 'qwe123', 'user': 'asduser03'})

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

class MedFile(BaseModel):
    av_scan = TextField(db_column='AV_Scan')
    ctime = DateTimeField(db_column='CTIME')
    file_name = TextField(db_column='File_Name')
    file_tag = CharField(db_column='File_Tag')
    md5_key = CharField(db_column='MD5_Key', index=True)
    mdp_rule = TextField(db_column='MDP_Rule')
    report_pc_count = IntegerField(db_column='REPORT_PC_Count')
    result_number = TextField(db_column='Result_Number')
    saved_size = IntegerField(db_column='Saved_Size')
    sign_credit = IntegerField(db_column='Sign_Credit')
    virus_name = TextField(db_column='Virus_Name')
    idx = PrimaryKeyField()

    class Meta:
        db_table = 'med_file'

