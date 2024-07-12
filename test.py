import math
import wandb
import curriculums as curriculums

curriculum = getattr(curriculums, 'lock')
metadata = curriculums.extract_metadata(curriculum, 0)




print('a')