# Continual Learning for Time-Series (and EHR)
Continual Learning repo for DPhil work

Project layout:

1.
    1. Adapt van de Ven [pytorch implementations](https://github.com/GMvandeVen/continual-learning) of main CL methods for ingesting time-series data as opposed to image  
         - (i.e. convert CNN to RNN - code is not simple, easier said than done)
    2. Adapt proposed benchmarking datasets from [Harutyunyan et al](https://www.nature.com/articles/s41597-019-0103-9) (for *multi-task* learning on time-series EHR) into CL appropriate datasets.  
         - (i.e. task incremental, where appropriate class/domain incremental by splitting on label/demographic)  
         - (for DIL need to be careful of potential colinear variables acting as 'labels' for the domain e.g. splitting on "hospital" but "country of birth" is present as variable)
    5. Adapt ii. into format ingestible by i. 
    6. Evaluate i. on ii.
2. Evaluate 1 on curated Oxford / Haven etc dataset. 
    - e.g. class-incremental learning predicting different health events
    - e.g. domain-incremental predicting generic health event from different specific events (respiratory failure, cardiac arrest etc).
4. Further development of superior techniques on more advanced dataset (domain-incremental learning with different datasets from oxford vs America vs SA etc).
5. *(Ambitious) pursue rigorous theoretically driven novel technique (as opposed to vague biological motivations / empirical architectures proposed).*