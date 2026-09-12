from django.core.management.base import BaseCommand
from exams.models import Exam,Question
class Command(BaseCommand):
    help='Create original five-question Reading demo; never overwrite existing content.'
    def handle(self,*args,**options):
        if Exam.objects.filter(title='Urban gardens — original demo').exists():self.stdout.write('Already seeded.');return
        e=Exam.objects.create(title='Urban gardens — original demo',section='Reading',duration_seconds=600,passage='Urban gardens can be found on rooftops and school grounds. Residents manage many gardens together. A study of twelve gardens found that participants valued social contact as much as fresh vegetables. It did not compare the cost of garden produce with supermarket prices. Some gardens collect rainwater, but still need additional water during long dry periods. Gardens alone cannot feed an entire city.')
        items=[('Urban gardens can be located on rooftops.','TRUE','Urban gardens can be found on rooftops and school grounds.','Matnda tomlar aniq keltirilgan.'),('Participants only valued vegetables.','FALSE','Participants valued social contact as much as fresh vegetables.','Ijtimoiy aloqani ham qadrlashgan.'),('Garden produce is cheaper than supermarket food.','NOT GIVEN','It did not compare the cost of garden produce with supermarket prices.','Narxlar taqqoslanmagan.'),('Gardens with rainwater tanks never need additional water.','FALSE','Still need additional water during long dry periods.','Qo‘shimcha suv talab qilinadi.'),('Gardens alone can feed an entire city.','FALSE','Gardens alone cannot feed an entire city.','Da’vo matnga zid.')]
        for i,(prompt,answer,evidence,explanation) in enumerate(items,1):Question.objects.create(exam=e,position=i,prompt=prompt,choices=['TRUE','FALSE','NOT GIVEN'],accepted_answers=[answer],evidence=evidence,explanation=explanation,skill_tag='True / False / Not Given')
        e.published=True;e.save();self.stdout.write('Created original Reading demo.')
